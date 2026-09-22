#!/usr/bin/env python3
"""Reproduce the paper tables from frozen traces / labels / predictions.

Standard library only; no network and no model calls.

Usage:
    python scripts/reproduce_tables.py \
        --input traces/ --labels labels/ --predictions predictions/ \
        --out results_reproduced/

It writes table1..table4 CSVs into --out, compares them cell-by-cell against
the frozen reference in results/ (when present), and checks every cell against
the paper's expected values. Exit code is non-zero on any mismatch.
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compute_metrics as cm  # noqa: E402


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json_loads(line) for line in f if line.strip()]


def json_loads(line):
    import json
    return json.loads(line)


# ---- paper-expected frozen values (used as an independent guard) -----------
INTERNAL_ORDER = [
    ("reapprove_every_step", "Re-approve Every Step"),
    ("approval_on_deny", "Approval-on-Deny"),
    ("boundary_only", "Boundary Only"),
    ("boundary_static_risk", "Boundary + Static Risk"),
    ("boundary_dynamic_risk", "Boundary + Dynamic Risk"),
    ("hitl_without_approval_auth", "HITL w/o Approval Auth"),
    ("full_stateful_delegation", "Ours (Stateful Delegation)"),
]
EXPECTED_TABLE2 = {
    "reapprove_every_step": (89.38, 68.6, 5.333, 0, 0.0, 0, 0.0, 100.0),
    "approval_on_deny":      (89.38, 68.6, 3.495, 0, 0.0, 0, 0.0, 100.0),
    "boundary_only":         (66.70, 25.5, 3.298, 185, 35.8, 38, 27.1, 71.5),
    "boundary_static_risk":  (76.65, 36.2, 4.555, 0, 0.0, 13, 9.3, 100.0),
    "boundary_dynamic_risk": (78.62, 37.1, 4.450, 0, 0.0, 13, 9.3, 100.0),
    "hitl_without_approval_auth": (62.59, 21.2, 4.267, 67, 13.0, 29, 20.7, 87.0),
    "full_stateful_delegation":   (89.38, 68.6, 2.743, 0, 0.0, 0, 0.0, 100.0),
}
ABLATION_ORDER = [
    ("full", "Full (Stateful Delegation)", (420, 0, 0, 2.78)),
    ("no_risk_authority_separation", "w/o Risk/Authority Sep.", (317, 107, 0, 2.53)),
    ("no_approver_coverage_Gh", "w/o Approver Coverage G_h", (259, 243, 0, 2.20)),
    ("no_lifecycle", "w/o Lifecycle", (271, 239, 0, 2.21)),
    ("no_exact_binding", "w/o Exact Binding", (222, 458, 0, 1.69)),
    ("no_effect_check", "w/o Effect Check", (280, 0, 140, 2.76)),
]
EXPECTED_TABLE1 = {
    "drift": (37.14, 91.96, 7.51, 1350, 121),
    "apc":   (61.29, 34.06, 47.54, 500, 40),
    "ours":  (100.00, 0.00, 0.00, 0, 0),
}
TABLE1_ORDER = [("drift", "DRIFT"), ("apc", "APC (minimal-scope adapter)"),
                ("ours", "Ours (Stateful Delegation)")]


def f2(x): return f"{x:.2f}"
def f1(x): return f"{x:.1f}"
def f3(x): return f"{x:.3f}"


def build_table1(labels, ext_pred):
    rows = [["Method", "Exec Acc.", "FAR", "FDR", "Unauthorized",
             "Unsafe", "Allow events", "Deny-now events"]]
    got = {}
    for key, name in TABLE1_ORDER:
        m = cm.external_binary_metrics(labels, ext_pred, key)
        got[key] = (round(m["exec_accuracy"], 2), round(m["far"], 2),
                    round(m["fdr"], 2), m["unauthorized"], m["unsafe"])
        rows.append([name, f2(m["exec_accuracy"]), f2(m["far"]), f2(m["fdr"]),
                     str(m["unauthorized"]), f"{m['unsafe']}/{m['unsafe_denominator']}",
                     str(m["allow_events"]), str(m["deny_events"])])
    return rows, got


def build_table2(nat_traces, nat_labels, clean_labels, nat_pred):
    rows = [["Method", "GovAcc", "BTS", "HITL/session",
             "Unauthorized count", "Unauthorized rate (%)",
             "Unsafe count", "Unsafe rate (%)", "IARR (%)"]]
    got = {}
    for key, name in INTERNAL_ORDER:
        m = cm.internal_workload_metrics(nat_traces, nat_labels, clean_labels,
                                         nat_pred, key)
        got[key] = (round(m["govacc"], 2), round(m["bts"], 1),
                    round(m["hitl_per_session"], 3), m["unauthorized"],
                    round(m["unauthorized_rate"], 1), m["unsafe"],
                    round(m["unsafe_rate"], 1), round(m["iarr"], 1))
        rows.append([name, f2(m["govacc"]), f1(m["bts"]), f3(m["hitl_per_session"]),
                     str(m["unauthorized"]), f1(m["unauthorized_rate"]),
                     str(m["unsafe"]), f1(m["unsafe_rate"]), f1(m["iarr"])])
    return rows, got


def build_table3(clean_traces, clean_labels, clean_pred):
    rows = [["Variant", "GCC", "Unauthorized", "Unsafe", "HITL/session"]]
    got = {}
    for key, name, _ in ABLATION_ORDER:
        m = cm.clean_ablation_metrics(clean_traces, clean_labels, clean_pred, key)
        got[key] = (m["gcc_sessions"], m["unauthorized"], m["unsafe"],
                    round(m["hitl_per_session"], 2))
        rows.append([name, f"{m['gcc_sessions']}/{m['sessions']}",
                     f"{m['unauthorized']}/{m['unauthorized_denominator']}",
                     f"{m['unsafe']}/{m['unsafe_denominator']}",
                     f"{m['hitl_per_session']:.2f}"])
    return rows, got


def build_table4(ado):
    m = cm.agentdojo_metrics(ado)
    rows = [["Suite", "Baseline success", "Stateful Delegation success"]]
    for suite, (b, o, t) in m["suites"].items():
        rows.append([suite, f"{b}/{t}", f"{o}/{t}"])
    rows.append(["Total", f"{m['baseline_success']}/{m['total']} ({f1(m['baseline_rate'])}%)",
                 f"{m['ours_success']}/{m['total']} ({f1(m['ours_rate'])}%)"])
    return rows, m


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


def compare_reference(out_dir, ref_dir, names):
    failures = 0
    if not os.path.isdir(ref_dir):
        print(f"[reference] no reference directory {ref_dir}; skipping diff")
        return failures
    for name in names:
        rp, op = os.path.join(ref_dir, name), os.path.join(out_dir, name)
        a = list(csv.reader(open(rp, encoding="utf-8")))
        b = list(csv.reader(open(op, encoding="utf-8")))
        if a == b:
            print(f"[reference] {name}: IDENTICAL to frozen reference")
        else:
            failures += 1
            print(f"[reference] {name}: MISMATCH vs frozen reference")
            for i, (ra, rb) in enumerate(zip(a, b)):
                if ra != rb:
                    print(f"    row {i}: ref={ra} reproduced={rb}")
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="traces")
    ap.add_argument("--labels", default="labels")
    ap.add_argument("--predictions", default="predictions")
    ap.add_argument("--out", default="results_reproduced")
    ap.add_argument("--reference", default="results")
    args = ap.parse_args()

    nat_traces = read_jsonl(os.path.join(args.input, "natural_v1_candidate_actions.jsonl"))
    clean_traces = read_jsonl(os.path.join(args.input, "clean_candidate_actions.jsonl"))
    ado = read_jsonl(os.path.join(args.input, "agentdojo_benign_tasks.jsonl"))
    nat_labels = read_jsonl(os.path.join(args.labels, "natural_v1_labels.jsonl"))
    clean_labels = read_jsonl(os.path.join(args.labels, "clean_labels.jsonl"))
    nat_pred = read_jsonl(os.path.join(args.predictions, "natural_internal_predictions.jsonl"))
    clean_pred = read_jsonl(os.path.join(args.predictions, "clean_ablation_predictions.jsonl"))
    ext_pred = read_jsonl(os.path.join(args.predictions, "external_binary_predictions.jsonl"))

    os.makedirs(args.out, exist_ok=True)
    failures = 0

    t1, g1 = build_table1(nat_labels, ext_pred)
    write_csv(os.path.join(args.out, "table1_external_baselines.csv"), t1)
    for k, exp in EXPECTED_TABLE1.items():
        if g1[k] != exp:
            failures += 1; print(f"[expected] table1 {k}: got {g1[k]} expected {exp}")
    print("Table 1 (external immediate-execution projection):")
    for r in t1: print("   ", " | ".join(r))

    t2, g2 = build_table2(nat_traces, nat_labels, clean_labels, nat_pred)
    write_csv(os.path.join(args.out, "table2_natural_results.csv"), t2)
    for k, exp in EXPECTED_TABLE2.items():
        if g2[k] != exp:
            failures += 1; print(f"[expected] table2 {k}: got {g2[k]} expected {exp}")
    print("\nTable 2 (NATURAL controlled SOC workload):")
    for r in t2: print("   ", " | ".join(r))

    t3, g3 = build_table3(clean_traces, clean_labels, clean_pred)
    write_csv(os.path.join(args.out, "table3_ablation_results.csv"), t3)
    for key, _name, exp in ABLATION_ORDER:
        if g3[key] != exp:
            failures += 1; print(f"[expected] table3 {key}: got {g3[key]} expected {exp}")
    print("\nTable 3 (clean component ablation):")
    for r in t3: print("   ", " | ".join(r))

    t4, g4 = build_table4(ado)
    write_csv(os.path.join(args.out, "table4_agentdojo.csv"), t4)
    if (g4["baseline_success"], g4["ours_success"]) != (64, 71):
        failures += 1
        print(f"[expected] table4: got {g4['baseline_success']},{g4['ours_success']}")
    print("\nTable 4 (AgentDojo 97 benign tasks):")
    for r in t4: print("   ", " | ".join(r))

    names = ["table1_external_baselines.csv", "table2_natural_results.csv",
             "table3_ablation_results.csv", "table4_agentdojo.csv"]
    failures += compare_reference(args.out, args.reference, names)

    print("\n" + ("ALL CHECKS PASSED" if failures == 0
                   else f"{failures} CHECK(S) FAILED"))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
