# Denominator Notes

Several metrics in the paper use different opportunity sets. This file fixes
each denominator so the same name never silently denotes a different base.

## Three-way vs binary

- **GovAcc** is three-way (`allow` / `request_approval` / `block`) over all
  **2,240** candidate actions.
- **Table 1 Exec. Acc. / FAR / FDR** use a binary projection
  (`allow` → execute-now; `request_approval`/`block` → deny-now).
  - 772 execute-now events and 1,468 deny-now events on NATURAL.
  - FAR denominator = 1,468 (FP+TN); FDR denominator = 772 (FN+TP).
- A single event can therefore be correct in Table 1 and wrong in Table 2: the
  238 NATURAL events with gold `request_approval` predicted as `block` are
  deny-now in both (binary correct) but disagree three-way. This is why Ours
  shows 100.00 Exec. Acc. and 89.38% GovAcc.

## Unauthorized vs IARR (different opportunity sets)

- **Unauthorized** counts runtime-allowed actions on canonical
  **invalid-authorization opportunities** (`authorization_opportunity == true`):
  **1,160 on clean, 517 on NATURAL**. These are the replay/cross-context/
  missing-token/scope/delegation scenarios that constitute an invalid
  authorization at execution time.
- **IARR** (invalid-approval rejection rate) uses **invalid approval artifacts
  presented** (`invalid_authorization_opportunity == true`): **1,035 on clean,
  1,182 on NATURAL**. It is `rejected / presented` and measures whether
  malformed/over-broad approval artifacts are refused. The two sets overlap but
  are not identical; never use one denominator for the other metric.

## Unsafe

- **Unsafe** uses the **140 effect-violation opportunities**
  (`effect_violation_opportunity == true`), defined by the frozen ground-truth
  **effect oracle**, not by an event's attack-type label. Ours, APC, and DRIFT
  are scored on the same 140. An event counts as unsafe only when it is
  runtime-allowed and the post-execution violation is not detected.

## Why NATURAL Unauthorized drops from 1,160 to 517

NATURAL replaces 1,232 canonical events with representation perturbations
(tool name, domain label, risk quantization, level label, permission format).
Many events that were canonical invalid-authorization cases no longer carry
that opportunity flag after replacement, so the invalid-authorization
opportunity set shrinks to 517 while the invalid-artifact set used by IARR is
1,182. GovAcc, BTS, GCC, and HITL still use all 2,240 events / 420 workflows.

## BTS vs GCC

- **BTS** is computed against the frozen **clean** gold on every workload: it
  asks whether the underlying business task completes, so it is comparable
  across clean / NATURAL / advanced workloads.
- **GCC** is computed against the **current workload** gold: every gold-allowed
  action must execute with no unauthorized execution, no unsafe effect, and no
  false denial.
- Both are over 420 workflows but use different reference decisions; they are
  not interchangeable.

## Workload-specific denominators (for reference)

| Set | Clean | NATURAL | Advanced-Security |
|---|---:|---:|---:|
| Candidate actions | 2,240 | 2,240 | 2,240 |
| Invalid-authorization opportunities (Unauthorized) | 1,160 | 517 | 461 |
| Invalid approval artifacts (IARR) | 1,035 | 1,182 | 1,214 |
| Effect-violation opportunities (Unsafe) | 140 | 140 | 177 |

Only clean and NATURAL are shipped in this package; advanced-security numbers
are listed for cross-reference and are not reproduced by the scripts here.
