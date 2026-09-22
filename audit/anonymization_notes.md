# Anonymization Notes

The benchmark is fully synthetic. This package is sanitized for public release.

## Included

- Synthetic candidate actions, permissions, domains, risk values, and
  benchmark-provided effects.
- Synthetic approval roles and tokens: roles such as `ciso`, `security_lead`,
  `dba`, `data_owner`, `sre`, `network_admin`, and `compliance`, and random
  hex `token_id` values. The substring `admin` only ever occurs inside the
  permission string `optional_admin` and the synthetic role `network_admin`.
- The fixed authorization specification `traces/policies.json`.
- Per-event gold labels and per-event frozen decisions.
- AgentDojo per-task success labels (the upstream AgentDojo persona text is not
  shipped here).

## Excluded on purpose

- Any API key or credential file (e.g. runtime key files) and run logs that may
  contain them.
- DRIFT raw model outputs, prompts, trajectories, checklists, user queries, and
  initial trajectories; APC initial scopes. The external prediction files
  contain only `event_id`, the binary decision, and the effect-detection flag.
- The Qwen-Plus / real-Splunk end-to-end trajectories (small-scale validation
  outside Tables 1–3).
- Real hosts, Splunk endpoints, usernames, email addresses, IP addresses,
  company domains, and URLs.

## Automated check

`scripts/validate_schema.py` scans every shipped `.jsonl/.json/.csv/.md/.py`
file for secret-key patterns, Aliyun AccessKey patterns, email addresses, IPv4
addresses, and hard-coded URLs, and fails if any are found. Re-run it after any
edit and before making the repository public.

## Release checklist (human)

1. `python scripts/validate_schema.py` passes.
2. `python scripts/reproduce_tables.py --out results_reproduced/` reports all
   tables `IDENTICAL` and `ALL CHECKS PASSED`.
3. Choose and add a real `LICENSE` (the committed file is a placeholder).
4. Replace the repository-URL placeholder in the paper with the final URL.
5. Keep the repository private until 1–4 are complete.
