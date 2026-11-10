# v3 — v2 + routing guardrails and selectable UI

## Scope

v3 keeps the v2 `deduplicate` tool, tests, and group eval. It improves the
system prompt and evaluation contract in two focused areas:

- Missing-account requests must use `clarify`, never a guessed account or
  topic search.
- A latest-turn intent change emits only the minimum required call; a topic
  such as `robotics` is not treated as an account for `timeline`.
- Telegram confirmation is two-stage: request the missing draft first, then
  ask for `yes_no` confirmation for the exact draft.

The Streamlit UI now lets the user select v1, v2, or v3 before starting a
conversation. The selected artifact paths and hashes are stored in the
transcript.

## Evaluation

| Suite | Passed | Accuracy | Routing | Arguments | Multi-turn |
|---|---:|---:|---:|---:|---:|
| Base | 20/20 | 100% | 100% | 100% | 100% |
| Group | 10/10 | 100% | 100% | 100% | 100% |

Evidence:

- `runs/v3_B_base_openai_20261110T124518116114.json`
- `runs/v3_B_group_openai_20261110T124432527353.json`

## Verification

The offline suite remains green with 109 passed tests.
