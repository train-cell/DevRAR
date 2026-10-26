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
