# Expanded recap: inputs, interpretation and boundaries

The 0.2 preview extends the local CLI and the existing offline Story/Explore
experience. The two product pillars remain equal: recognise the recorded work,
then show evidence and useful next actions. It does not turn activity volume
into a programmer grade.

## Application history

Select sources with repeated `--source` flags. An explicit `--opencode-path`,
`--gemini-path` or `--antigravity-path` also selects its source.

| Source | Default discovery | Supported input and limits |
|---|---|---|
| OpenCode | `~/.local/share/opencode/opencode.db`; `OPENCODE_DB` overrides | Read-only SQLite snapshot of supported `session` or `session_v2`, `message`, `part` layouts. Text, tool invocation/result and explicit parent metadata; unsupported parts remain partial. |
| Gemini CLI | `~/.gemini/tmp` | Only `chats/session-*.jsonl` files are discovered. Supported user/gemini session records and tool calls; an explicit JSON `messages` or `conversation.messages` export can also be supplied. Other Gemini products/exports are not a universal compatibility claim. |
| Antigravity | Existing `~/.gemini/antigravity{,-cli,-ide}/brain` roots | Only `.system_generated/logs/transcript.jsonl` files are discovered. The hook transcript path is documented; row mapping is observed, not a versioned public schema, so native coverage remains partial. Explicit role-based JSON/JSONL and Markdown exports are separate adapters. Native `.pb` files remain unsupported. |

Claude and Codex retain their existing deduplication rules. Recognised Claude
API request replay envelopes are auxiliary data, not extra user/assistant turns.
Recognised Codex lifecycle/world/compaction/usage envelopes are not chat activity.
Supported modern Codex `event_msg/item_completed` records project assistant
messages with preserved vendor IDs and deduplicate legacy message replays.
Commands, patch metadata, collaboration and inter-agent metadata have a separate
`codex_native` observed-subset channel. Commands do not inflate legacy/global
tool totals; patch records are not commits and linked threads do not prove
parent/child delegation. Inter-agent message bodies are omitted.
Validated `token_usage_record` request counters are deduplicated by session and
response ID. Recorded totals and cached/reasoning subsets are shown separately,
never added to global tokens or cumulative snapshots. Coverage remains incomplete;
no known request records means null sums. Unknown substantive records remain partial.
Native commands use the same selected `--idle-minutes` as the main event stream.

No request/response scratch artifacts are treated as chat just because their
filename ends in JSON. Readers never execute imported instructions or rewrite
history. Each selected source exposes its adapter, formats and coverage.

Primary format references:

- [OpenCode storage and troubleshooting](https://dev.opencode.ai/docs/troubleshooting/)
- [OpenCode session schema](https://github.com/anomalyco/opencode/blob/dev/packages/schema/src/session.ts)
- [Gemini CLI recording types](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/services/chatRecordingTypes.ts)
- [Antigravity hooks and transcript path](https://antigravity.google/docs/hooks?tab=ide)

## Work patterns and check outcomes

`metrika_ergasias` is accumulated from the full accepted, deduplicated, in-scope
event stream. It is separate from the bounded 600-row semantic sample.

- The 24 hourly buckets count human prompts in the selected timezone. The
  calendar uses dated prompt rows; absent recorded activity is not proof of a
  day off. Unknown timestamps are counted separately.
- `interval_estimate_minutes` unions adjacent event pairs within each
  source/session when the gap is at most `--idle-minutes` (default 15). Overlap
  across sessions is not double-counted. No tail is invented. This estimates
  observed-event spans, **not actual human PC time**. No usable pair means null.
- Only actual tool-result text can provide recognised pytest, unittest or TAP
  test summaries. Assistant claims do not count. Identical summaries within one
  output are deduplicated; distinct reruns count again. These are recorded test
  executions, not unique tests, product test coverage or a pass-rate grade.
- Source/session episodes retain at most 500 summaries and five exact citations
  each. Citation selection favours actual check/exit evidence and preserves
  different observed outcome kinds. Full counters continue after caps.
- The growth analyser presents at most 100 episode summaries and three
  citations per observation. Its status comes from the **shown** tool output or
  recorded exit codes; unrelated excerpts plus aggregate counters cannot prove
  an outcome. Success, failure, mixed and unknown describe checks only. Failed
  checks do not establish blame, cause or overall task completion. Priorities
  are conditional actions, distinct from prompt-wording cues.

The UI source filter still applies to the prompts-by-source chart. Other
sections explicitly retain report-wide scope. Full arbitrary date/project
filtering inside an already generated report is not implemented.

## Git changes

Existing `synola.commits` counts unique commits across all selected HEAD history.
New `git_diafores` is a **separate first-parent** view: merges are diffed against
their first parent and counted separately; side-branch-only commits are omitted.
It includes additions, deletions, changed-file occurrences, binary changes and
current tracked inventory. Renames use delete/add semantics. Binary files add
no fabricated line counts. The 10,000-commit per-repository cap, errors and
unknown dates make coverage partial. Shared commit IDs and identical inventory
trees are deduplicated in combined totals. Line volume does not imply quality.

## Comparing periods

~~~console
devrar wrap --source claude --since 2026-10-01 --until 2026-10-31 --compare ./september/apotelesmata.json
~~~

Supply explicit non-overlapping dates and the same demo/live mode, schema,
rubric, timezone, source set, repository selection and author filter. The
comparison stores decisions and scalar deltas, never baseline excerpts.
Repository identities are hashes of normalised absolute selected paths, private
scope identifiers rather than anonymisation. Moving/cloning a checkout can make
reports incompatible. An explicit empty selection allows AI-only comparisons;
older reports lacking scope metadata remain unavailable for comparison.

Unknown metrics retain null. Zero baselines have no percent change. Partial or
truncated evidence remains labelled. Totals are not normalised for period
length; a larger delta does not establish skill improvement or causality.

## Supplied active time

`--activitywatch-path` reads an explicit ActivityWatch JSON bucket export of
`afkstatus` events (`not-afk` and `afk`), or an interval CSV:

~~~csv
start,end,status
2026-10-01T09:00:00+03:00,2026-10-01T10:00:00+03:00,active
2026-10-01T09:40:00+03:00,2026-10-01T09:50:00+03:00,afk
~~~

Intervals are unioned, AFK overlap is subtracted, and inclusive local date bounds
clip the input, including DST. Only supplied watcher intervals are established;
gaps, unsupported states, naive timestamps and missing data remain unknown.
This is not a background monitor or a complete historical PC-time measurement.
Read [ActivityWatch's data model](https://docs.activitywatch.net/en/latest/buckets-and-events.html).

## Supplied costs

`--cost-path` accepts CSV with the following columns, or a JSON array / object
with a `records` array containing the same fields:

~~~csv
timestamp,provider,model,amount,currency,kind
2026-10-01T10:00:00Z,example,recorded-model,0.123456789,USD,billed
2026-10-01T10:00:00Z,example,recorded-model,0.2,EUR,estimated
~~~

Amounts are exact decimal strings. Billed and estimated entries and different
currencies remain separate; there is no exchange-rate, live pricing,
subscription or missing-bill inference. Numeric bounds are 128 digits and an
absolute decimal exponent at most 128; out-of-range rows remain partial. A
bounded local Decimal context preserves exact addition within those limits.
Imports are limited to 20 MiB and 100,000 rows with explicit coverage.
Import-only live runs work; imports cannot contaminate the synthetic demo.

## Recognition and sharing

The report derives a playful activity label such as “Multi-tool conductor”,
with its exact count-based basis and inference limits. Labels describe the
selected report, not personality, skill, seniority or code quality. Highlights
recognise recorded days, source activity, peak dated prompts and check results.

HTML and Markdown show the same new summary domains; JSON retains the full
bounded payload. Markdown shows at most 20 included outcome summaries and says
how many were omitted. `tekmiria.jsonl` distinguishes workflow cues and recorded
checks. No raw event stream is archived automatically.

The share dialog previews the aggregate-only card, then offers SVG or a local
1080×1350 PNG rasterisation of that same card. It does not screenshot the private
report. PNG failure keeps the dialog and SVG available. The downloadable card
continues to exclude names, dates, source paths, quotes, imports and comparisons.

Original is the default appearance; Blue hour changes the app frame and Explore
panels, with an accessible in-memory selector. Story colours and share cards keep
their existing appearance.

## Explicit cloud mode

`--analysis cloud` requires `--cloud-endpoint`, `--cloud-model` and
`--allow-cloud-evidence` before collection/network access. The key comes from
`DEVRAR_CLOUD_API_KEY` or the name supplied by `--cloud-key-env`. The HTTPS endpoint
must end in `/chat/completions`, without credentials, query or fragment.
The bounded request contains redacted evidence `id/role/kind/excerpt`, without
source/session/locator metadata or activity totals. Excerpts can still contain
private work; redaction is not anonymisation. Never enable this automatically.
There is one non-streamed request, no redirects/retries, normal TLS, a 120-second
socket timeout, a 64,000-byte request cap and a 256,000-byte response cap. The
socket timeout is not a guaranteed total wall-clock deadline. Strict schema and
exact-citation validation apply; metrics and numerical grading gates stay unchanged.
Failures preserve rules/metrics and yield partial exit code 3. Verification uses
synthetic mocked transport only; no actual cloud provider call is claimed.

Native Codex details are currently available in HTML/JSON. Markdown and
`tekmiria.jsonl` native-channel parity remain pending; existing workflow/main
check exports are unchanged. Additional UI languages, richer task/code-outcome
correlation, a licensed/original visual mascot and broader native coverage remain
pending. Numerical ratings require representative human calibration/agreement.
