# Metrics and compatibility

DevRAR reads selected files and Git metadata. It does not monitor your computer,
execute imported instructions or contact a model provider in rules mode.

## Supported inputs

| Source | Shapes handled by the initial adapter | Scope |
|---|---|---|
| Claude Code | JSONL user/assistant messages, text and tool-use blocks, explicit session and child metadata | Selected `--claude-path`, otherwise `~/.claude/projects` |
| Codex | JSONL session metadata, turn context, user/agent events and response items | Selected `--codex-path`, otherwise `~/.codex/sessions` |
| Compressed JSONL | The same shapes in `.jsonl.zst` | Requires the `compressed` extra |
| Git | Commit IDs, author identity/date and tracked file inventory | Selected repository HEAD; optional author substring filter |

An explicit source path can be a file or directory. There is no drive-wide scan.
JSONL shape support is tested with synthetic fixtures; vendor formats can change.
Cloud chat exports, SQLite histories and OpenCode/Gemini/Antigravity formats are
outside this version's compatibility claim. Source coverage describes selected
inputs, not everything you have ever done.

## Definitions

| Metric | Definition and limit |
|---|---|
| Sessions | Distinct source/session identities represented by supported records in the selected scope. A session is not a person or a proven completed task. |
| Root sessions / subagents | Explicit parent or subagent metadata. Changing models does not create a child agent. Missing relationships cannot establish total agent use. |
| Human prompts | Recognized human inputs, excluding tool results, internal-agent tasks and injected context. Explicit image-only inputs can count without creating fabricated text evidence. |
| Assistant replies | Supported assistant text, reconciled across Codex channels using explicit turn linkage. Ambiguous matching channels yield an unavailable total; a reply does not establish successful work. |
| Tool calls | Supported tool-use/function-call records. Their presence does not prove a successful command or passing test. |
| Models | Recorded model IDs only. A model record count is not a billable API-call count. |
| Tokens | Complete Claude API-message usage is deduplicated by message ID and component maxima. Unknown or cumulative Codex usage stays unavailable; no subscription cost is derived. |
| Commits | Unique commit IDs reachable from selected HEADs. Shared commits do not increase the combined count. Without `--author`, these are repository totals across authors. |
| Project files | Current tracked file inventory at HEAD, not lines changed or historical author ownership. |
| Active days | Distinct dates with supported activity in the chosen IANA timezone. This is not elapsed or active PC time. |

`--author` matches a case-insensitive substring of the recorded author name or
email. Choose an identity-specific value; a short common name can match several
people. No author filter is silently inferred from your Git configuration.

Date bounds are inclusive calendar dates in `--timezone` (default
`Europe/Athens`). Unknown timestamps are excluded when a date filter is active,
and that source is marked partial. Without a filter, supported undated records
can contribute to counters but cannot establish an active day.

## Evidence and assessment

Full-stream activity counting and semantic evidence selection are separate.
Workflow coaching uses a bounded deterministic sample, with included/eligible
counts and truncation explicitly recorded. Exact evidence locators remain in the
private report. Review the [rubric](rubric.md) for attribution, pattern thresholds
and score gates.

Generic recognition of recorded effort is different from evidence of code
quality, correctness or causation. No marker occurrence proves that the requested
practice actually happened. Missing markers do not prove a developer omitted it.

## Artifacts

Each run first creates a private `.gitignore` guard, then `index.html`, `anafora.md`,
`apotelesmata.json`, `piges.json`, `tekmiria.jsonl`, `run.json` and
`share/scorecard.svg`. The HTML works directly from the filesystem. Private
artifacts can contain selected evidence and project labels. The SVG allowlist
contains only sessions, prompts, active days and commits, plus a mandatory demo
watermark for synthetic runs; it omits exact dates, source paths and quotes.

Common credential patterns are redacted from evidence, but automated redaction
is not a guarantee of anonymization. Keep full reports private. Raw source files
are never rewritten.
