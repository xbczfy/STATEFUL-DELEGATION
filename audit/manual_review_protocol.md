# Manual Review and Ground-Truth Protocol

## How a gold decision is produced

1. A candidate action is generated from human-designed, rule-generated,
   public-context, or Qwen-assisted scenario material. Qwen is used only to
   draft scenarios and candidate plans, never to assign a gold decision.
2. The action is evaluated against the **predefined authorization
   specification** (`traces/policies.json`, policies `p1`/`p2`): the current
   task boundary, required scope, risk thresholds (0.6 / 0.93), approver
   coverage, delegation chain, token lifecycle, exact binding, and the expected
   post-execution effect.
3. The resulting three-way label (`allow` / `request_approval` / `block`),
   effect-violation flag, invalid-authorization flag, and invalid-artifact
   flag are **manually reviewed and curated** before the workload is frozen.
4. After curation the workflows, specification, and labels are frozen; all
   reported numbers come from the frozen artifacts, not from re-generation.

Every shipped label carries `audit_status: "reviewed"`.

## What is and is not claimed

- The package records that labels passed manual review; it does not publish
  per-reviewer identities or inter-rater statistics, which were not part of the
  frozen experiment record. No such statistics should be inferred.
- The gold evaluator and the runtime decision code are separate
  implementations that share the fixed specification; see
  `provenance_c1_gold_runtime.md`.
- Effect labels come from a benchmark-provided effect oracle
  (`observed_effect.violations`). The experiment evaluates whether the runtime
  **enforces** post-execution verification given these observations, not the
  accuracy of an independent learned effect detector.

## Freeze identifiers

- NATURAL benchmark SHA256:
  `5ce3723e0e25e27ca7eded2972916645598e4ba53e55d786945aeb4dceb9e1d1`
- DRIFT adapter `drift-adapter-v1.0`, checkpoint protocol
  `checkpoint-protocol-v1.0`; checkpoint integrity audit reports 420/420
  sessions and 2,240/2,240 events with zero missing or duplicate ids.
- AgentDojo tasks record benchmark version `v1.2.2`.
