# Stateful Delegation Benchmark

Artifact for the paper **"Stateful Delegation: Scoped Runtime Authorization for
Multi-Step Security Agents"** (Feiyang Zheng, University of Chinese Academy of
Sciences).

> **The submitted paper refers to release
> [`v1.0-submission`](https://github.com/xbczfy/STATEFUL-DELEGATION/releases/tag/v1.0-submission).**
> That release is the frozen artifact; the `main` branch may continue to change
> afterward.

This repository contains the frozen benchmark **traces, labels, per-event
predictions, evaluation scripts, metric definitions, and anonymized audit
records**. A reviewer can re-compute every number in Tables 1–4 without any
model or API call: the shipped predictions are the frozen outputs of the
deterministic authorization protocol, and the scripts only aggregate them.

## One-click reproduction

```bash
git clone https://github.com/xbczfy/STATEFUL-DELEGATION.git
cd STATEFUL-DELEGATION
python scripts/validate_schema.py
python scripts/reproduce_tables.py --out results_reproduced
```

Only the Python standard library is required (Python 3.8+).

**Expected output:** `validate_schema.py` ends with `SCHEMA VALIDATION PASSED`
(exit 0); `reproduce_tables.py` reports each table `IDENTICAL to frozen
reference`, ends with `ALL CHECKS PASSED` (exit 0), and writes the four tables
to `results_reproduced/`.

## Tables and their files

| Paper table | What it shows | Reproduced from | Frozen reference |
|---|---|---|---|
| Table 1 | External immediate-execution projection (DRIFT, APC, Ours) on NATURAL | `predictions/external_binary_predictions.jsonl` | `results/table1_external_baselines.csv` |
| Table 2 | NATURAL controlled SOC workload, 7 internal methods | `predictions/natural_internal_predictions.jsonl` | `results/table2_natural_results.csv` |
| Table 3 | Clean-workload component ablation, 6 variants | `predictions/clean_ablation_predictions.jsonl` | `results/table3_ablation_results.csv` |
| Table 4 | AgentDojo 97 benign tasks, external task-success check | `traces/agentdojo_benign_tasks.jsonl` | `results/table4_agentdojo.csv` |

Inputs: `traces/` (2,240 NATURAL + 2,240 clean candidate actions, 97 AgentDojo
tasks, `policies.json`) and `labels/` (gold decisions and opportunity flags).
Metric formulas and denominators are defined in `REPRODUCIBILITY.md` and
`audit/denominator_notes.md`. The boundary between supported and unsupported
claims is stated in `ARTIFACT_EVAL.md`.

## Data is sanitized

This package contains **no real security logs, no API keys, no Splunk hosts or
credentials, no usernames, IP addresses, company domains, raw model outputs, or
private configuration**. The traces are synthetic, retain structure only, and
keep evaluator-only fields (`reference_state`, gold decisions) out of the
runtime-visible records. `scripts/validate_schema.py` scans every shipped file
for key/email/IP/URL patterns. See `audit/anonymization_notes.md`.

## License

Code and scripts are released under the **MIT License** (`LICENSE`). The
`traces/` and `labels/` data are provided for **research and paper-result
reproduction**; they are synthetic and contain no real customer data.

## Scope and honesty of the evaluation

- Gold and runtime decisions follow the **same fixed authorization
  specification** but use **separate decision implementations**
  (`audit/provenance_c1_gold_runtime.md`).
- The binary Table 1 measures **execution-boundary conformance under the
  evaluated specification**, not generalization to unseen policies.
- Effect verification assumes benchmark-provided post-execution observations;
  the benchmark evaluates **enforcement of the verification step**, not the
  accuracy of an independent effect detector.
- DRIFT and APC are evaluated through documented adapters (`baselines/`); these
  do not reconstruct every native semantic of the external systems and must not
  be read as "method X is worse" beyond the common projection.

## Verified fresh-clone run

The log below is the captured output of the two commands above on a clean
checkout of release `v1.0-submission`.

<details>
<summary>Click to expand the full reproduction log</summary>

```text
$ python scripts/validate_schema.py
PASS  NATURAL traces: 2240 records (expected 2240)
PASS  NATURAL traces: unique candidate_action_id
PASS  NATURAL: 420 workflows (expected 420)
PASS  NATURAL: step lengths only 4/5/12 (found {4: 280, 5: 80, 12: 60})
PASS  NATURAL gold distribution {'allow': 772, 'request_approval': 1390, 'block': 78}
PASS  NATURAL Unauthorized denominator = 517
PASS  NATURAL IARR denominator = 1182
PASS  NATURAL Unsafe denominator = 140
PASS  NATURAL perturbed events = 1232
PASS  clean Unauthorized denominator = 1160
PASS  clean IARR denominator = 1035
PASS  clean Unsafe denominator = 140
PASS  NATURAL internal predictions: 7 methods x 2240
PASS  clean ablation predictions: 6 variants x 2240
PASS  external predictions: 3 methods x 2240
PASS  AgentDojo tasks: 97 (expected 97)
PASS  AgentDojo baseline successes = 64/97
PASS  AgentDojo Stateful Delegation successes = 71/97
PASS  no secrets / emails / IPs / URLs in shipped files

SCHEMA VALIDATION PASSED
exit=0

$ python scripts/reproduce_tables.py --out results_reproduced
Table 1 (external immediate-execution projection):
    DRIFT | 37.14 | 91.96 | 7.51 | 1350 | 121/140 | 772 | 1468
    APC (minimal-scope adapter) | 61.29 | 34.06 | 47.54 | 500 | 40/140 | 772 | 1468
    Ours (Stateful Delegation) | 100.00 | 0.00 | 0.00 | 0 | 0/140 | 772 | 1468

Table 2 (NATURAL controlled SOC workload):
    Re-approve Every Step | 89.38 | 68.6 | 5.333 | 0 | 0.0 | 0 | 0.0 | 100.0
    Approval-on-Deny | 89.38 | 68.6 | 3.495 | 0 | 0.0 | 0 | 0.0 | 100.0
    Boundary Only | 66.70 | 25.5 | 3.298 | 185 | 35.8 | 38 | 27.1 | 71.5
    Boundary + Static Risk | 76.65 | 36.2 | 4.555 | 0 | 0.0 | 13 | 9.3 | 100.0
    Boundary + Dynamic Risk | 78.62 | 37.1 | 4.450 | 0 | 0.0 | 13 | 9.3 | 100.0
    HITL w/o Approval Auth | 62.59 | 21.2 | 4.267 | 67 | 13.0 | 29 | 20.7 | 87.0
    Ours (Stateful Delegation) | 89.38 | 68.6 | 2.743 | 0 | 0.0 | 0 | 0.0 | 100.0

Table 3 (clean component ablation):
    Full (Stateful Delegation) | 420/420 | 0/1160 | 0/140 | 2.78
    w/o Risk/Authority Sep. | 317/420 | 107/1160 | 0/140 | 2.53
    w/o Approver Coverage G_h | 259/420 | 243/1160 | 0/140 | 2.20
    w/o Lifecycle | 271/420 | 239/1160 | 0/140 | 2.21
    w/o Exact Binding | 222/420 | 458/1160 | 0/140 | 1.69
    w/o Effect Check | 280/420 | 0/1160 | 140/140 | 2.76

Table 4 (AgentDojo 97 benign tasks):
    Total | 64/97 (66.0%) | 71/97 (73.2%)

[reference] table1_external_baselines.csv: IDENTICAL to frozen reference
[reference] table2_natural_results.csv: IDENTICAL to frozen reference
[reference] table3_ablation_results.csv: IDENTICAL to frozen reference
[reference] table4_agentdojo.csv: IDENTICAL to frozen reference

ALL CHECKS PASSED
exit=0
```

</details>
