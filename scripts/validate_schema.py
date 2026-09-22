#!/usr/bin/env python3
"""Validate the benchmark artifact: schema, counts, denominators, coverage.

Standard library only. Exits non-zero on the first failed check category.
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

N_SESSIONS = 420
N_EVENTS = 2240
N_ADO = 97
DECISIONS = {"allow", "request_approval", "block"}
BINARY = {"allow", "deny"}
SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9]{12,}", "openai-style secret key"),
    (r"LTAI[0-9A-Za-z]{10,}", "Aliyun AccessKey id"),
    (r"8Xkr[A-Za-z0-9]{6,}", "Aliyun AccessKey secret fragment"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "email address"),
    (r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "IPv4 address"),
    # JSON Schema meta-schema URLs in schemas/*.json are allowed.
    (r"https?://(?!json-schema\.org)[^\s\"']+", "hard-coded URL"),
]


def read_jsonl(rel):
    path = os.path.join(ROOT, rel)
    rows = []
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def require(cond, msg, failures):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        failures.append(msg)


def check_ids(rows, required, name, failures, unique_key="candidate_action_id"):
    ids = [r[unique_key] for r in rows]
    require(len(rows) == N_EVENTS, f"{name}: {len(rows)} records (expected {N_EVENTS})", failures)
    require(len(set(ids)) == len(ids), f"{name}: unique {unique_key}", failures)
    missing = [k for r in rows for k in required if k not in r]
    require(not missing, f"{name}: required fields present ({required})", failures)


def main():
    failures = []

    nat_t = read_jsonl("traces/natural_v1_candidate_actions.jsonl")
    clean_t = read_jsonl("traces/clean_candidate_actions.jsonl")
    ado = read_jsonl("traces/agentdojo_benign_tasks.jsonl")
    nat_l = read_jsonl("labels/natural_v1_labels.jsonl")
    clean_l = read_jsonl("labels/clean_labels.jsonl")
    nat_p = read_jsonl("predictions/natural_internal_predictions.jsonl")
    clean_p = read_jsonl("predictions/clean_ablation_predictions.jsonl")
    ext_p = read_jsonl("predictions/external_binary_predictions.jsonl")

    trace_fields = ["candidate_action_id", "workflow_id", "step_id", "task_family",
                    "tool", "target", "resource", "operation", "required_level",
                    "risk_level", "permission_scope", "natural_perturbations",
                    "visible_to_runtime"]
    label_fields = ["candidate_action_id", "gold_decision", "gold_binary",
                    "effect_violation_opportunity", "invalid_authorization_opportunity",
                    "authorization_opportunity", "attack_type", "audit_status"]

    check_ids(nat_t, trace_fields, "NATURAL traces", failures)
    check_ids(clean_t, trace_fields, "clean traces", failures)
    check_ids(nat_l, label_fields, "NATURAL labels", failures)
    check_ids(clean_l, label_fields, "clean labels", failures)

    # workflow counts and step-length distribution
    for name, rows in (("NATURAL", nat_t), ("clean", clean_t)):
        wf = collections.defaultdict(list)
        for r in rows:
            wf[r["workflow_id"]].append(r["step_id"])
        require(len(wf) == N_SESSIONS, f"{name}: {len(wf)} workflows (expected {N_SESSIONS})",
                failures)
        lens = collections.Counter(len(v) for v in wf.values())
        require(set(lens) <= {4, 5, 12},
                f"{name}: step lengths only 4/5/12 (found {dict(lens)})", failures)
        require(lens.get(4) == 280 and lens.get(5) == 80 and lens.get(12) == 60,
                f"{name}: 280x4 + 80x5 + 60x12 (found {dict(lens)})", failures)

    # gold enums and binary projection
    for name, labs in (("NATURAL", nat_l), ("clean", clean_l)):
        require(all(l["gold_decision"] in DECISIONS for l in labs),
                f"{name} labels: gold_decision in {DECISIONS}", failures)
        require(all(l["gold_binary"] in BINARY for l in labs),
                f"{name} labels: gold_binary in {BINARY}", failures)
        require(all(l["gold_binary"] == ("allow" if l["gold_decision"] == "allow" else "deny")
                    for l in labs),
                f"{name} labels: binary projection allow->allow, request/block->deny", failures)

    # NATURAL denominators
    nd = collections.Counter(l["gold_decision"] for l in nat_l)
    require(nd == collections.Counter({"request_approval": 1390, "allow": 772, "block": 78}),
            f"NATURAL gold distribution {dict(nd)}", failures)
    require(sum(l["authorization_opportunity"] for l in nat_l) == 517,
            "NATURAL Unauthorized denominator = 517", failures)
    require(sum(l["invalid_authorization_opportunity"] for l in nat_l) == 1182,
            "NATURAL IARR denominator = 1182", failures)
    require(sum(l["effect_violation_opportunity"] for l in nat_l) == 140,
            "NATURAL Unsafe denominator = 140", failures)
    require(sum(bool(t["natural_perturbations"]) for t in nat_t) == 1232,
            "NATURAL perturbed events = 1232", failures)
    require(not any(t["natural_perturbations"] for t in clean_t),
            "clean traces: no NATURAL perturbation annotation", failures)

    # clean denominators
    cd = collections.Counter(l["gold_decision"] for l in clean_l)
    require(cd == collections.Counter({"request_approval": 1168, "allow": 991, "block": 81}),
            f"clean gold distribution {dict(cd)}", failures)
    require(sum(l["authorization_opportunity"] for l in clean_l) == 1160,
            "clean Unauthorized denominator = 1160", failures)
    require(sum(l["invalid_authorization_opportunity"] for l in clean_l) == 1035,
            "clean IARR denominator = 1035", failures)
    require(sum(l["effect_violation_opportunity"] for l in clean_l) == 140,
            "clean Unsafe denominator = 140", failures)

    # prediction coverage
    nat_ids = {t["candidate_action_id"] for t in nat_t}
    clean_ids = {t["candidate_action_id"] for t in clean_t}
    nat_methods = collections.Counter(p["method"] for p in nat_p)
    require(len(nat_methods) == 7 and all(v == N_EVENTS for v in nat_methods.values()),
            f"NATURAL internal predictions: 7 methods x {N_EVENTS} ({dict(nat_methods)})",
            failures)
    require(all(p["pred_decision"] in DECISIONS for p in nat_p),
            "NATURAL internal predictions: decision enum", failures)
    abl = collections.Counter(p["variant"] for p in clean_p)
    require(len(abl) == 6 and all(v == N_EVENTS for v in abl.values()),
            f"clean ablation predictions: 6 variants x {N_EVENTS} ({dict(abl)})", failures)
    require(all(p["candidate_action_id"] in clean_ids for p in clean_p),
            "clean ablation predictions reference known ids", failures)
    ext = collections.Counter(p["method"] for p in ext_p)
    require(len(ext) == 3 and all(v == N_EVENTS for v in ext.values()),
            f"external predictions: 3 methods x {N_EVENTS} ({dict(ext)})", failures)
    require(all(p["pred_binary"] in BINARY for p in ext_p),
            "external predictions: binary enum", failures)
    require(all(p["candidate_action_id"] in nat_ids for p in ext_p),
            "external predictions reference NATURAL ids", failures)

    # AgentDojo
    require(len(ado) == N_ADO, f"AgentDojo tasks: {len(ado)} (expected {N_ADO})", failures)
    suites = collections.Counter(r["suite"] for r in ado)
    require(suites == collections.Counter({"workspace": 40, "slack": 21, "travel": 20,
                                           "banking": 16}),
            f"AgentDojo suites {dict(suites)}", failures)
    require(sum(r["baseline_task_success"] for r in ado) == 64,
            "AgentDojo baseline successes = 64/97", failures)
    require(sum(r["stateful_delegation_task_success"] for r in ado) == 71,
            "AgentDojo Stateful Delegation successes = 71/97", failures)

    # secret / PII scan over the whole package (excluding .git)
    bad = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            if fn.endswith((".jsonl", ".json", ".csv", ".md", ".py")):
                text = open(os.path.join(dirpath, fn), encoding="utf-8",
                            errors="ignore").read()
                for pat, label in SECRET_PATTERNS:
                    if re.search(pat, text):
                        bad.append(f"{os.path.relpath(os.path.join(dirpath, fn), ROOT)}: {label}")
    require(not bad, "no secrets / emails / IPs / URLs in shipped files", failures)
    for b in bad[:10]:
        print("      LEAK", b)

    print("\n" + ("SCHEMA VALIDATION PASSED" if not failures
                   else f"{len(failures)} VALIDATION FAILURE(S)"))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
