# NATURAL Perturbation Protocol

NATURAL tests whether authorization decisions stay stable when the same
underlying action is represented in a non-canonical way. Perturbations change
the **input representation only**; the intended authorization semantics (and
therefore the gold decision) are preserved.

## Perturbation classes

Exactly 1,232 of the 2,240 events are perturbed, in five classes:

| Class (`attack_type`) | Events | What is changed |
|---|---:|---|
| `natural_tool_name` | 247 | non-canonical tool name / alias |
| `natural_domain_label` | 247 | non-canonical domain label |
| `natural_risk_quantization` | 246 | risk value expressed in a different quantization |
| `natural_level_label` | 246 | authority level expressed as a label rather than canonical form |
| `natural_permission_format` | 246 | permission string in a non-canonical format |
| **Total perturbed** | **1,232** | 55% of events |

The remaining 1,008 events are unperturbed (`valid`) or carry one of the
non-representation scenario classes (replay, cross-session/task/action,
missing/expired/exhausted token, wrong type, scope/delegation/effect cases).

The perturbation class of each event is recorded for reviewers as
`natural_perturbations` in the trace (an annotation); at runtime the agent only
sees the resulting (perturbed) field values, not this label. The pristine
**clean** workload has `natural_perturbations == []` for every event.

## Seeds and determinism

- Clean workload generation seed: `20260906`.
- NATURAL / dirty-workload seed: `20260907`.
- The frozen NATURAL benchmark hash is
  `5ce3723e0e25e27ca7eded2972916645598e4ba53e55d786945aeb4dceb9e1d1`
  (420 sessions / 2,240 events).

## Observed effect

All 238 NATURAL GovAcc errors of the full protocol are conservative
false denials concentrated in `natural_permission_format`: gold is
`request_approval` while the runtime returns `block`. They are correct at the
binary execution boundary and produce no unauthorized execution or unsafe
effect. Component ablations are run on clean so that individual-component
failures are not confounded with representation errors.
