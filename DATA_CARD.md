# Data Card

## What this is

A controlled, fully synthetic benchmark of multi-step Security Operations
Center (SOC) workflows for evaluating runtime authorization decisions of
tool-using agents. It is **not** production telemetry.

- 420 independent workflows, 2,240 candidate actions (one primary candidate per
  step), eight SOC task families: suspicious login, data exfiltration,
  malware process, port anomaly, configuration tampering, credential
  compromise, database anomaly, and host containment.
- Step-length distribution: 280 workflows of 4 steps, 80 of 5 steps, and 60
  long-horizon workflows of 12 steps (min 4, max 12).
- Splits used for the test set: seen, compositional, unseen-workflow,
  unseen-policy, and long-horizon.
- Two workloads share the same candidate-action skeleton:
  - **clean** — canonical field representations;
  - **NATURAL** — 1,232 of the 2,240 events carry non-canonical upstream
    representations (tool names, domain labels, risk quantization, level
    labels, permission formats) while preserving authorization semantics.

The benchmark was constructed from human-designed, rule-generated,
public-context, and Qwen-assisted cases, followed by manual auditing and
curation; the resulting workflows and authorization specification were then
frozen for deterministic evaluation. Qwen was used to generate scenarios and
candidate plans only, never ground-truth authorization decisions.

## Authorization specification

`traces/policies.json` is the fixed specification used by both the gold
evaluator and the runtime. It defines two policies (`p1`, `p2`), risk
thresholds (0.6 approval / 0.93 block), synthetic principals and their
authority ceilings/domains, delegation chains, and multi-principal rules. The
principal names (`ciso`, `security_lead`, `dba`, `data_owner`, `sre`,
`network_admin`, `compliance`) are synthetic roles, not real identities.

## Trace records (`traces/*.jsonl`)

Runtime-visible fields only. Evaluator-only state (`reference_state`) is
excluded; gold decisions and attack/failure labels live in `labels/`.

| Field | Meaning |
|---|---|
| `candidate_action_id` | unique event id, e.g. `v4_0084:step_03` |
| `workflow_id`, `step_id` | workflow grouping and order |
| `split`, `task_family`, `policy_id` | provenance tags |
| `tool` / `resource` | the synthetic tool surface |
| `target` | authorization domain |
| `operation` | permission action suffixes (e.g. `execute`) |
| `required_level`, `risk_level` | authority level and numeric risk |
| `permission_scope` | required normalized permissions |
| `action_permissions`, `requested_permissions`, `candidate_plans`, `permission_costs` | candidate plan bundle |
| `required_approver_groups` | approver requirement |
| `execution_capability` | whether the action is executable |
| `observed_effect` | benchmark-provided post-execution effect (violation labels) |
| `approval_token` | synthetic approval/delegation token presented at runtime |
| `natural_perturbations` | annotation of which NATURAL perturbation applies (`[]` on clean); the perturbation itself is realized through the field values |
| `visible_to_runtime` | always `true` for the shipped trace fields |

## Label records (`labels/*.jsonl`)

| Field | Meaning |
|---|---|
| `gold_decision` | `allow` / `request_approval` / `block` |
| `gold_binary` | `allow` for allow, else `deny` |
| `authorization_opportunity` | canonical invalid-authorization opportunity (Unauthorized denominator) |
| `invalid_authorization_opportunity` | invalid approval artifact presented (IARR denominator) |
| `effect_violation_opportunity` | one of the 140 effect-violation opportunities (Unsafe denominator) |
| `attack_type` | evaluator scenario/perturbation class (not visible to the runtime) |
| `audit_status` | review state (`reviewed`) |

## Prediction records (`predictions/*.jsonl`)

Frozen per-event decisions only: method/variant, candidate-action id, decision,
the per-event human-intervention flag, and whether a post-execution effect
violation was detected. Raw model transcripts, prompts, checklists, and
adapter debug text are deliberately not shipped (see
`audit/anonymization_notes.md`).

## Synthetic data and privacy

All hosts, users, logs, SQL, tokens, and identifiers are synthetic. No real
secrets, API keys, Splunk hosts, usernames, IP addresses, email addresses, or
external URLs are included; `scripts/validate_schema.py` scans every shipped
text file for these patterns.
