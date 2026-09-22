# DRIFT Adapter

## Source method

DRIFT — *Dynamic Rule-Based Defense with Injection Isolation for Securing LLM
Agents* (Li et al., NeurIPS 2025). DRIFT is a runtime **plan / trajectory
validation** defense with injection isolation: for a task it builds an initial
function trajectory and a per-node checklist, then validates each candidate
action against the trajectory and checklist before allowing execution.

## What the adapter does

- Wraps the official DRIFT implementation (`DRIFTLLM`) unchanged.
- For each workflow it constructs the initial function trajectory and node
  checklist once (cached per session), maps the benchmark candidate action to
  DRIFT's tool-call representation, and runs DRIFT's trajectory-constraint and
  checklist-constraint validation.
- A candidate is projected to binary `allow` only when both the trajectory and
  checklist checks pass; any failure is `deny`.
- The adapter runs on the **same 2,240 NATURAL candidate actions** and the same
  gold binary labels and the **same 140 effect-violation opportunities** as
  Ours and APC.
- Adapter version: `drift-adapter-v1.0`; checkpoint protocol
  `checkpoint-protocol-v1.0`; 420/420 sessions and 2,240/2,240 events present
  with no missing or duplicate ids.

## What is not reconstructed / fairness limits

- DRIFT does not maintain a task-level authorization boundary, approver scope
  (`G_h`), approval lifecycle, exact binding, or a post-execution effect check.
  It validates plan conformance and injection isolation, so its `effect_detected`
  flag is false throughout; the 121/140 unsafe count reflects allowed
  effect-violation opportunities under this projection.
- DRIFT's native outputs are trajectory/checklist decisions, not the three-way
  `allow / request_approval / block` interface, so it is only compared under the
  binary immediate-execution projection (`immediate_execution_projection.md`).
- Raw model transcripts, prompts, checklists, and debug trajectories are not
  shipped; only the per-event binary decision is included in
  `predictions/external_binary_predictions.jsonl`.

## Frozen result (Table 1)

Exec. Acc. 37.14, FAR 91.96, FDR 7.51, Unauthorized 1,350, Unsafe 121/140.
