# Artifact Evaluation — Claims and Evidence

Written from a reviewer's perspective: which claims the frozen artifact
supports, and which it does not.

## Claims supported by this artifact

- **Table 1 — external immediate-execution projection.** Over the same 2,240
  NATURAL events, DRIFT, APC (minimal-scope adapter), and Ours are compared
  under a single binary execute-now / deny-now projection. Counts and rates
  are recomputed from `predictions/external_binary_predictions.jsonl`; the
  772 allow / 1,468 deny-now split and the 140 effect opportunities are fixed
  by the labels.
- **Table 2 — NATURAL controlled SOC result.** GovAcc (over 2,240), BTS (over
  420), HITL/session, Unauthorized (count and rate over 517 NATURAL
  opportunities), Unsafe (count and rate over 140), and IARR (over 1,182) are
  recomputed for all 7 internal methods.
- **Table 3 — clean component ablation.** GCC (over 420), Unauthorized (over
  1,160), Unsafe (over 140), and HITL are recomputed for the full protocol and
  five component removals, isolating which mechanism prevents which failure.
- **Table 4 — external task-success validation.** On 97 benign AgentDojo tasks
  across four suites, task success is recomputed per suite (64/97 baseline vs
  71/97 Stateful Delegation).
- **Reproducibility and provenance.** The numbers reproduce deterministically
  with no API calls; gold and runtime use separate decision implementations
  over a shared specification (`audit/provenance_c1_gold_runtime.md`);
  denominators are documented (`audit/denominator_notes.md`).

## Claims NOT supported by this artifact

- **Production-scale deployment.** The workload is a controlled, synthetic
  benchmark; it does not establish performance, latency, or operational
  readiness in a production SOC.
- **Formal safety or security guarantee.** There is no proof that the protocol
  is safe under all policies, adversaries, or inputs. The paper reports
  observed outcomes ("no observed unauthorized executions or unsafe effects in
  the evaluated workload"), not a guarantee.
- **Generalization to unseen authorization policies.** Tables measure
  conformance to a fixed, externally specified policy, not transfer to new
  policies or organizations.
- **Complete reproduction of the proprietary Splunk environment.** The
  real-tool Qwen/Splunk runs are small-scale end-to-end validation and are not
  fully reproduced here; no Splunk hosts, credentials, or private data are
  included.
- **Full fidelity reproduction of DRIFT or APC native semantics.** The
  adapters map scope/resource fields and a common projection; they do not
  reconstruct every native component (e.g., APC approval/intent), so the
  comparison must not be read as a native head-to-head beyond that projection.
- **An independent learned effect detector.** Effect verification is evaluated
  as an enforcement step over benchmark-provided post-execution observations,
  not as the accuracy of a separate detector.

## How to verify

```bash
python scripts/validate_schema.py
python scripts/reproduce_tables.py --out results_reproduced
```

A valid artifact ends with `SCHEMA VALIDATION PASSED` and `ALL CHECKS PASSED`,
and every table is reported `IDENTICAL to frozen reference`.
