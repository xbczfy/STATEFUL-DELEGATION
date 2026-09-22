# Stateful Delegation Benchmark

This repository contains the benchmark traces, labels, evaluation scripts,
metric definitions, and anonymized audit records for the paper
**"Stateful Delegation: Scoped Runtime Authorization for Multi-Step Security
Agents."**

It lets a reviewer independently re-compute every number in Tables 1–3 (and the
AgentDojo external check) from frozen per-event traces, labels, and per-event
predictions. No model or API call is needed: the shipped predictions are the
frozen outputs of the deterministic authorization protocol, and the scripts
only aggregate them.

## Reproduce paper tables

```bash
python scripts/validate_schema.py
python scripts/reproduce_tables.py \
    --input traces/ --labels labels/ --predictions predictions/ \
    --out results_reproduced/
```

Expected outputs (written to `results_reproduced/` and compared cell-by-cell
against the frozen reference in `results/`):

- **Table 1** — external immediate-execution baseline comparison (DRIFT, APC, Ours)
- **Table 2** — NATURAL controlled SOC workload results (7 internal methods)
- **Table 3** — clean-workload component ablation (6 variants)
- **Table 4** — AgentDojo 97 benign tasks (external task-success check)

A successful run prints `ALL CHECKS PASSED` and every table is reported
`IDENTICAL to frozen reference`, and the process exits with code 0.

Only the Python standard library is required (Python 3.8+).

## Repository layout

| Path | Contents |
|---|---|
| `traces/natural_v1_candidate_actions.jsonl` | 2,240 NATURAL candidate actions (runtime-visible fields only) |
| `traces/clean_candidate_actions.jsonl` | 2,240 pristine-clean candidate actions |
| `traces/agentdojo_benign_tasks.jsonl` | 97 AgentDojo benign tasks with per-task success |
| `traces/policies.json` | the fixed authorization specification (`p1`, `p2`) |
| `labels/natural_v1_labels.jsonl`, `labels/clean_labels.jsonl` | gold decisions and evaluation-opportunity flags |
| `predictions/natural_internal_predictions.jsonl` | 7 internal methods × 2,240 frozen decisions |
| `predictions/clean_ablation_predictions.jsonl` | 6 ablation variants × 2,240 frozen decisions |
| `predictions/external_binary_predictions.jsonl` | DRIFT / APC / Ours × 2,240 binary decisions |
| `results/` | frozen reference tables (the paper's numbers) |
| `scripts/` | `validate_schema.py`, `reproduce_tables.py`, `compute_metrics.py` |
| `baselines/` | DRIFT/APC adapter scope and the binary projection definition |
| `audit/` | review, perturbation, denominator, anonymization, provenance notes |
| `schemas/` | JSON schemas for traces, labels, predictions |
| `DATA_CARD.md`, `REPRODUCIBILITY.md` | dataset card and metric/denominator definitions |

## Scope and honesty of the evaluation

- Gold and runtime decisions follow the **same fixed authorization
  specification** but use **separate decision implementations**
  (`audit/provenance_c1_gold_runtime.md`).
- The binary Table 1 measures **execution-boundary conformance under the
  evaluated specification**, not generalization to unseen policies.
- Effect verification assumes benchmark-provided post-execution observations;
  the benchmark evaluates **enforcement of the verification step**, not the
  accuracy of an independent effect detector.
- DRIFT and APC are evaluated through documented adapters
  (`baselines/`); these do not reconstruct every native semantic of the
  external systems and must not be read as "method X is worse" beyond the
  common projection.

## Release status

This package is prepared for a **private** repository first. Validate and
reproduce locally before making it public. Before release, the author must:
choose a license (`LICENSE` is currently a placeholder), set the final
repository URL, and re-run the two commands above on a clean checkout.
