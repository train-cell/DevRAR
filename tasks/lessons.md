# Project-scoped engineering observations

These are local project lessons, not a background observer deployment. No raw
conversations, identities or credentials are stored here. Observed 27 Oct 2026;
scope: DevRAR; confidence 0.7; no global promotions.

| Trigger | Action | Domain | Evidence |
|---|---|---|---|
| Import has a parent identifier | Establish whether it points to a session, message or tool call before counting agents. Keep peer targets distinct from children. | ingestion | Native adapter regressions now reject message/tool parent IDs as subagent links. |
| A message has multiple persisted text parts | Count the message once, retain its supported text, and exclude explicitly synthetic/ignored user context. | metrics | OpenCode multipart fixture previously produced three prompts for one input. |
| Persisted tool state is terminal | Preserve separate invocation/output evidence where input is explicit; do not invent linkage across unrelated projections. | ingestion | Completed OpenCode input/output fixture plus modern Codex protocol review. |
| Evidence output is long or the sample cap is full | Parse outcomes before truncating display text; prioritise exact successful/failed check citations. | assessment | Long-output and late-check regressions; unrelated citations cannot prove aggregate outcomes. |
| Baseline scope is incomplete | Require comparable mode, schema, rubric, timezone, source/repository/author scope and non-overlapping dates. | evaluation | AI-only scope, all-author null, repository mismatch and partial Git regressions. |
| Ledger decimals exceed normal numeric precision | Bound magnitudes and sum in an adequate local Decimal context; keep currencies/kinds separate. | arithmetic | Long decimal/exponent regression and exact string totals. |
| Renaming internal identifiers | Preserve external keyword names, inspect f-string expressions and avoid collisions; run types/tests before integrating. | code-style | Root's naming refactor exposed and corrected keyword/f-string/source-name collisions. |

New project observations: seven. None claims a confidence above 0.8 or changes
user-wide rules/hooks. Regression tests and the report contract carry the actual
enforcement.
