# Token usage collection

The live report can expose token usage only when the selected source records
support per-message attribution. It does not estimate cost or multiply token
counts by model prices.

## Claude Code

Claude JSONL assistant records are eligible when they contain an API
`message.id`, a consistent non-empty `message.model`, a completed non-empty
`message.stop_reason`, and all four non-negative integer usage components:

- `input_tokens`
- `cache_creation_input_tokens`
- `cache_read_input_tokens`
- `output_tokens`

Boolean values are rejected even though Python treats `bool` as an integer.
For one API message ID repeated in copied or forked transcripts, DevRAR dedupes
by that API ID and uses the maximum reported value for each component. It does
not add repeated snapshots. Conflicting model/stop-reason values, invalid
components, missing components or missing IDs prevent a complete total.

The total is the sum of the four distinct components. Claude defines total input
as uncached input plus cache-creation input plus cache-read input; output usage
includes generated reasoning tokens. See the [Claude streaming usage
documentation](https://platform.claude.com/docs/en/build-with-claude/streaming)
and the [Messages API type definitions](https://platform.claude.com/docs/en/api/typescript/messages).

## Codex

The supported Codex `token_count` events report cumulative session counters,
not independently attributable API-message usage. DevRAR reports how many such
snapshot records it observed in `kalypsi_tokens.piges.codex.agnosta_records`,
but does not convert them to requests or tokens.

Codex assistant replies reconcile `response_item`, `agent_message` and
`task_complete` channels by session, active turn ID and exact normalized text.
The channel with the greatest multiplicity is retained; ties prefer canonical
`response_item` rows. Distinct canonical records with distinct IDs remain
distinct even when their text matches. If matching channels lack turn linkage,
DevRAR preserves the observed evidence, marks the Codex source partial and
returns the aggregate reply count as unavailable instead of guessing.

## Coverage and periods

Claude and Codex user records with
`internal_chat_message_metadata_passthrough` are classified from
`content_item_kinds` when that marker is available. Known environment-context
and opened-page items do not count as human prompts. For a mixed record, only
aligned `user.*` content blocks are retained; ambiguous mixed records are
excluded. The `client_authored` flag is not used alone to reject a record
because native human records can set it to false. Image-only human prompts
count toward prompt activity but do not create quoted text evidence; a report
note makes this limitation explicit. If the marker is absent, the reader uses
the legacy source content interpretation.

`kalypsi_tokens.piges.claude` reports `gnostes_aitiseis` (unique message IDs
with complete usage), `elleipeis_aitiseis` (known IDs without complete,
consistent usage), `agnosta_records` (assistant records without a reliable API
message shape or ID), `methodos` and `pliris`. Missing or unreadable sources
have null counts; absence is not reported as zero. A readable source with no
observed API messages also has null token totals and incomplete coverage.

Claude per-tool and per-model token counts may remain known when Claude usage
coverage is complete, even if another selected source is incomplete. Model rows
include `pigi` to keep providers separate. The aggregate `synola.tokens`
requires complete usage coverage from every selected AI source; a selected
Codex source therefore keeps the aggregate null. Date filters apply before
usage records are ingested; records outside the selected period cannot reserve
an API message ID or contribute to its token maxima. Records with unknown dates
are excluded under an active date filter and make source coverage partial.

Each `piges` row also records provenance: `adapter` identifies the reader
version (`claude-jsonl-v1`, `codex-jsonl-v1` or `git-head-v1`), `morfes` lists
the selected input formats (`jsonl`, `jsonl.zst` or `git`), and
`periodos_diathesimon` holds the minimum and maximum valid local dates observed
in recognized records before applying the selected report date filter. Missing
formats or unparseable date bounds are represented by an empty list or null
bound, respectively. Git bounds cover valid author dates in all history
reachable from `HEAD`, independent of report date and author filters. If no
commit dates can be parsed, the Git source row explains that the period is
unavailable. Partial source reads can establish bounds only from the readable
subset.
