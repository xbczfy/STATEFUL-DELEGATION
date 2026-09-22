# APC Adapter (minimal-scope, daggered in the paper)

## Source method

APC denotes the **Agentic Principal Chain** mechanism of *Bounded Agents:
Delegation Security for Multi-Agent AI Systems* (2026, concurrent work;
arXiv:2608.15888; reference implementation `xmuruaga/bounded-agents`). APC
tracks principal-to-principal delegated authority and enforces **authority
attenuation** (a child's scope is a subset of its parent's), delegation
budgets, composition closure, intent binding, and conjunctive authorization
checks. Its native decision object is a **delegation request**, not a
candidate tool action.

## What the adapter does

- Runs the **unmodified** APC `PolicyDecisionPoint` deterministically (no LLM
  calls; no APC rule is added or changed).
- Maps each benchmark permission string to an APC `Scope` by splitting
  `resource:action` pairs (resources and actions), sets a generous delegation
  budget so that budget limits are not the deciding factor, and initializes the
  bounded delegation from the first step's reference authorization.
- Converts the APC allow/deny outcome to the binary immediate-execution
  decision on the **same 2,240 NATURAL candidate actions**, same gold binary
  labels, and same **140 effect-violation opportunities** as Ours and DRIFT.

## What is deliberately not reconstructed

This is a **minimal-scope adapter** (the dagger in Table 1). It maps scope and
resource fields only and does **not** reconstruct:

- APC's approval semantics (its C4 approval check) and intent semantics
  (C6 intent binding) in the benchmark's task-action form;
- any runtime **authority expansion** path, because APC authority only narrows
  and the benchmark contains actions that legitimately require in-task
  expansion;
- a post-execution effect check (`effect_detected` is false throughout).

As a consequence APC fails closed on out-of-initial-scope actions, which
manifests as a high FDR. The row characterizes how an unmodified
attenuation-based bounded-delegation policy behaves under the common binary
projection; it **must not** be stated as "APC is worse", and it is not a
faithful end-to-end reproduction of APC on its native delegation-request
benchmark (its official 99-scenario suite).

## Frozen result (Table 1)

Exec. Acc. 61.29, FAR 34.06, FDR 47.54, Unauthorized 500, Unsafe 40/140.
