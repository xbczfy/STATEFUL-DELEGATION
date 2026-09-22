# Provenance: Gold Decisions vs Runtime Decisions (C1 audit)

Question: is Ours' 2,240/2,240 binary immediate-execution agreement
"guaranteed by construction" because the ground truth and the runtime
authorization checker share the same code?

## Conclusion: class B — specification-shared, implementation-independent

The gold evaluator and the runtime decision logic **follow the same fixed
authorization specification but use separate decision implementations**. They
share (a) the policy specification (`traces/policies.json`, policies `p1`/`p2`,
risk thresholds, principals, delegation rules) and (b) one permission-string
normalization helper. They do **not** share an authorization-decision function,
and the runtime never reads evaluator-only fields.

## What is shared and what is independent (verified in the frozen code)

| Component | Gold path | Runtime path |
|---|---|---|
| Decision entry point | `protocol.evaluate(event, policy)` | `methods.FullProtocol.decide` / `strengthening/methods_v41.HardenedProtocol.decide` |
| Reads `event["reference_state"]` (evaluator-only) | yes | **no** |
| Imports the other side's decision module | `protocol.py` does not import `candidate_logic`/`methods` | `candidate_logic.py` does not import `protocol.py` |
| Shared modules | `permission_normalize.normalize_permission_set` | same helper |
| Shared data | policy JSON `p1`/`p2` | same policy JSON |
| Reads gold decision / attack type / failure type | n/a (produces gold) | **no** |

`candidate_logic.py` imports only `permission_normalize`; `protocol.py` imports
only `permission_normalize`. Runtime methods import `candidate_logic`
(`infer_needs`, `verify_approval`) and operate on a `deepcopy` of the visible
event/state; they never reference `reference_state`, the gold decision,
`attack_type`, or failure labels. The initial task boundary is the externally
specified delegation for that task (what the user chose to delegate), not a
per-event gold label.

## Provenance diagram

```
scenario / candidate-plan sources (human, rule-generated, public context, Qwen-assisted)
        |  (Qwen drafts scenarios/plans only; no gold)
        v
candidate action  (runtime-visible fields; reference_state kept evaluator-only)
        |
        |-------------------- [gold path] --------------------|
        |  protocol.evaluate(event, policy)                   |
        |    reads reference_state + policies.json            |
        |    + permission_normalize                           |
        v                                                      v
   gold decision (allow / request_approval / block) ----> evaluator
        ^                                                      ^
        |                  [runtime path]                      |
        |  HardenedProtocol.decide(visible event, state, policy)
        |    + candidate_logic (infer_needs, verify_approval)
        |    + permission_normalize ; deepcopy; no reference_state
        v
predicted decision (allow / request_approval / block) ---------|

shared: policies.json, permission_normalize
independent: gold decision function vs runtime decision function
```

## Empirical counter-evidence against "conformance by construction"

If the runtime copied the gold, the three-way decisions would agree on every
event. They do not:

- Binary immediate-execution agreement is 2,240/2,240 (100.00%).
- Three-way GovAcc is 2,002/2,240 = 89.38%.
- The 238 disagreements are all `request_approval` (gold) vs `block`
  (runtime), concentrated in non-canonical permission-format perturbations.

These are conservative false denials: correct at the execution boundary,
counted as GovAcc errors. A shared decision function could not produce this
systematic divergence.

## Effect oracle

The 140 effect-violation opportunities come from the benchmark-provided
`observed_effect` labels. The runtime's post-execution check is an enforcement
step over these observations; the benchmark does not evaluate an independent
learned effect detector, and the runtime cannot see the gold effect labels
before execution.

## Scope of the claim

The tables measure **conformance to a fixed, externally specified authorization
policy**, not generalization to unseen policies. The paper states this
directly:

> Gold and runtime decisions follow the same fixed authorization specification
> but use separate decision implementations.

> The binary evaluation measures execution-boundary conformance under the
> evaluated specification rather than generalization to unseen policies.

> Effect verification assumes benchmark-provided post-execution observations;
> we evaluate enforcement of the verification step rather than the accuracy of
> an independent effect detector.

## Superseded audits

An earlier adapter-vs-benchmark audit (predating the frozen `v41_env`) described
field leakage in an older benchmark/adapter combination. It concerns the
superseded v420 adapter setup, not the shipped Ours runtime above, and is not
part of this package.
