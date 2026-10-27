# Report schema v1 — integration contract

This JSON contract is shared by ingestion, demo, CLI and renderer. Fields and Python/JS implementation identifiers use Greeklish. UI strings are English.

The top-level object contains:

~~~json
{
  "ekdosi_sximatos": "1",
  "leitourgia": "demo",
  "periodos": {"apo": "2026-01-01", "eos": "2026-10-26", "zoni": "Europe/Athens"},
  "synola": {
    "synedries": 0, "rizikes": 0, "ypopraktores": 0,
    "minimata_xristi": 0, "apantiseis": 0, "kliseis_ergaleion": 0,
    "tokens": null, "commits": null, "imeres": 0
  },
  "ergaleia": [
    {"onoma": "Claude Code", "synedries": 0, "prompts": 0, "tokens": null}
  ],
  "montela": [{"onoma": "recorded-model-id", "kliseis": 0, "tokens": null}],
  "drastiriotita": [{"imerominia": "2026-10-01", "prompts": 0, "commits": 0}],
  "projects": [{"onoma": "example", "commits": 0, "arxeia": 0}],
  "axiologisi": {
    "diathesimi": false, "synoliko": null,
    "aitia": "Not enough verified evidence to calculate an engineering score.",
    "diastaseis": []
  },
  "eyrimata": [
    {
      "id": "E001", "titlos": "Example", "epipedo": "strength",
      "keimeno": "Observation", "protasi": "Next action",
      "tekmiria": [{"pigi": "source label", "locator": "record id", "apospasma": "safe excerpt"}]
    }
  ],
  "oroshma": [{"titlos": "Example", "keimeno": "Verified milestone"}],
  "piges": [{"onoma": "Claude Code", "katastasi": "ok", "arxeia": 0, "sfalmata": 0, "simeiosi": ""}],
  "simeioseis": []
}
~~~

- This sample illustrates shape; zero values are not a real dataset.
- leitourgia: demo or live. Only demo can contain synthetic activity.
- piges.katastasi: ok, partial or missing. Overall partial is any non-ok selected source.
- null means not recorded / unavailable. It must not display as an asserted zero.
- Dates are ISO strings. No PC-hours or actual-money fields are asserted without a source.
- eyrimata.epipedo: strength, growth or info. Initial rules report observations and bounded recommendations, not psychological traits or unproven causality.
- Private source locators stay in the private report. Share exports include aggregate fields only.
- Additional fields may be added by agreement; existing keys are stable for this implementation.

## Evidence additions

All numeric activity fields may be null when the selected sources cannot establish
them. Internal collector counters do not turn missing source coverage into an
asserted zero. Counts from readable subsets remain explicitly partial.

`deigmata` is a bounded list of normalized, redacted evidence records:

~~~json
{
  "id": "E001", "pigi": "Claude Code", "synedria": "session-id",
  "rolos": "user", "eidos": "prompt", "keimeno": "Run targeted tests.",
  "locator": "synthetic.jsonl:12", "imerominia": "2026-10-12"
}
~~~

Roles are `user`, `assistant` or `tool`. Kinds are `prompt`, `response`,
`tool_call` or `tool_result`. The activity reader exports at most 600 eligible
evidence rows, each excerpt at most 500 characters after credential redaction.
Metric counting continues over the full stream. Sampling is deterministic and
bounded; it does not establish representative coverage of every task.

`kalypsi_analysi` has `epilegmena` (rows included), `diathesima` (eligible rows
before truncation) and `perikopi` (true when eligible exceeds included).
`scope_git` records `rev: "HEAD"` and the explicit `author` filter or null.

Assessment adds five `axiologisi.diastaseis` entries with stable IDs, `onoma`,
nullable `bathmos`, `aitia`, `episodia` and `tekmiria`. Prompt markers can establish
an observed wording signal; they cannot establish execution or code quality.
Findings carry attribution, confidence, an alternative explanation and references
to evidence. Their public interpretation is constrained by [rubric.md](rubric.md).

`analysi` records method/version/rubric and evaluation limits. A populated
dimension profile does not imply a validated numerical grade. Exact evidence,
analysis metadata and source labels belong to private artifacts; share exports
continue to use their fixed aggregate allowlist.

Source rows also expose `adapter`, `morfes`, and `periodos_diathesimon` (observed
date bounds before the requested filter). `kalypsi_tokens` separates known Claude
API messages, incomplete identities and unknown records; see [usage.md](usage.md).
Model rows include `pigi` where provider attribution is known.

Optional local `analysi` records `katastasi`, `model_id`, `provider_version`,
`ekdosi_prompt` and sampling limits. On failure its status is `failed` and the
report explicitly retains the original metrics/rules observations. Model prose
is never used for arithmetic or score activation. Finding source authorship is
derived from validated citation roles, rather than supplied by the model.

## Additive 0.2 fields

These keys remain optional so v0.1 reports render. Null is never an asserted
zero. Definitions and input examples: [expanded recap](expanded-recap.md).

`scope_git` in the full collector is always explicit: `rev`, nullable `author`
and sorted `repositories` (SHA-256 of normalised absolute selected paths). An
empty repository list means no selected repositories; absent metadata is unknown.
Identifiers are private scope metadata, not an anonymisation guarantee.

### Work metrics

`metrika_ergasias` contains:

- `zoni`, `ora: [{ora, prompts}]` (24 local-hour human-prompt counters when AI
  coverage is available, empty when selected AI history is unavailable),
  `imeres: [{imerominia, prompts}]`, `timestamps_unknown` and accepted `events`.
- Nullable `interval_estimate_minutes` and `interval_estimate_status`. This is
  the union of bounded adjacent recorded-event pairs, not human PC time.
- `sources` rows: `pigi`, `events`, `prompts`, `tool_calls`, `tool_results` and
  nullable `tests_passed/failed/skipped`.
- `test_summary: {status, passed, failed, skipped}` with optional `todo` when
  TAP TODO records exist. Only recognised tool-result output supplies counts.
  Different executions/reruns count again; these are not unique tests. Supported
  top-level TAP lines follow the [TAP13 spec](https://testanything.org/tap-version-13-specification.html);
  TODO is separate from failures/skips and nested child points are not added.
- `epeisodia` (at most 500) with `id`, `pigi`, `synedria`, prompt/call/result
  counters, `tests_status`, nullable test counts, `exit_success/exit_failure`,
  `tekmiria` (at most five), `tekmiria_included/eligible/truncated`.
- `episodes_included/eligible/truncated`; full global/source counters continue.

Episode citations have `id`, `pigi`, `synedria`, `locator`, `rolos`, `eidos`,
`apospasma` (at most 500 characters) and nullable integer `kodikos_exodou`.
Check output/exit evidence has priority over generic early transcript excerpts;
different observed outcome kinds are retained within the cap. Source readers
send full redacted text transiently; they do not archive a raw event stream.

### Outcome analysis

`epeisodia_ergasias` contains `ekdosi`, `katastasi`, `kalypsi`,
`paratiriseis` (at most 100), `dynata_simeia`, `proteraiotites` (at most three),
`vathmologisi_energi: false` and `periorismoi`. Observations include:

- `id`, `pigi`, `synedria`, `katastasi` (`observed_success`, `observed_failure`,
  `mixed`, `unknown`), `apotelesma`, `metrisi`, exact bounded `tekmiria` (three),
  `kalypsi_tekmirion`, strengths, alternatives, conditional actions and limits.
- Status derives from the shown output/exit citations, not uncited aggregate
  counters. Summaries concern recorded checks, not task completion or blame.

Markdown shows at most 20 included summaries with the count explicitly stated.
JSON retains the full bounded analysis. `tekmiria.jsonl` exports `eyrima_id` and
`katigoria` (`workflow_cue` / `observed_check`) alongside citation fields.

### Comparison

`sygkrisi` contains `ekdosi`, `katastasi`, `symvatotita`, `metrika`,
`periorismoi`. Compatibility factors cover demo/live mode, schema, rubric,
timezone, source set, author, repository identities, non-overlapping periods and
coverage. Metric rows contain nullable `trexousa`, `proigoumeni`, `delta`,
`pososto`, `katastasi`, `kalypsi`, `aitia`. Zero baseline has no percent change.
No baseline excerpts are embedded. Totals are not normalised for period length.

### Git and supplied records

`git_diafores` contains `adapter`, `katastasi`, `periodos`, `filtro`,
`semantics`, `apothikies`, `synola`, `kalypsi`. Totals/rows include additions,
deletions, file-change occurrences, binary changes, merge counts and tracked
HEAD inventory. First-parent scope, merge/rename/binary semantics and truncation
are explicit. It remains distinct from the existing all-history commit total.

`energos_xronos` contains `status`, `source`, `method`, `scope`, `note`, nullable
`active_seconds/afk_seconds`, `coverage` and `by_day` rows (`date` and seconds).
Coverage reports total/used/ignored events, unknown timestamps/intervals and
partial status. Only supplied intervals are established.

`kostos` contains `status`, `source`, optional `note`, `coverage`, nullable
`totals: [{currency, kind, amount}]`. Coverage reports total/used/ignored rows,
unknown timestamps and partial status. `amount` is an exact bounded decimal
string; `kind` is `billed` or `estimated`. Different currencies/kinds stay separate.

### Recognition

The renderer derives `anagnorisi: {ekdosi, profile: {titlos, aitia}, highlights,
periorismos}` from selected activity. Up to four highlights have `titlos` and
`keimeno`. The profile is a playful descriptive label, never a validated skill or
personality classification. The SVG/PNG share allowlist remains unchanged.

### Modern Codex and cloud additions

`codex_native` is an optional separate observed-subset channel with `adapter`,
`coverage`, assistant/command/exit/patch/collaboration/inter-agent counters,
`linked_agent_threads`, `usage`, `metrika_ergasias`, and `epeisodia_ergasias`.
Coverage always declares incomplete. `usage.method` is `per_response_id_dedup`;
`known_records`, `duplicate_records`, `invalid_records` accompany nullable `sums`.
Sums contain recorded input/cached/cache-write/output/reasoning/total fields;
subset counters are not added to each other or to global token totals.
Native command metrics/outcomes do not merge into the main check channel.
Main and native `metrika_ergasias.idle_minutes` record the selected threshold.
Native-channel Markdown/evidence-JSONL parity remains pending.

Explicit cloud coaching records `analysi.methodos: cloud`, state, provider,
`model_id`, `endpoint_host`, `cloud_opt_in`, prompt version and bounded sampling
metadata. Secrets and endpoint credentials are never report fields. Failed
analysis retains rules and its explicit fallback state; no grade becomes active.
