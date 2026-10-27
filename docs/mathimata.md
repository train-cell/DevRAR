# Project observations

These are project-scoped engineering notes. They contain no imported transcript
content and do not install observers or alter another application's settings.

| Trigger | Action | Confidence | Evidence |
|---|---|---|---|
| A new source schema appears | Prove recognized shape coverage; unknown-only input must not become valid zero activity | 0.9 | Synthetic future-schema regression exposed false `ok` coverage |
| A session starts outside a selected period | Preserve relationship metadata before filtering activity | 0.9 | Child metadata outside the date range initially reclassified in-range activity as a root |
| A report gains a second export path | Apply the same aggregate allowlist and synthetic watermark to both exports | 0.9 | Browser SVG initially included exact dates while the static SVG omitted them |
| UI classes or identifiers change | Verify rendered selectors, computed styles, external properties and English product copy | 0.9 | Naming changes exposed unstyled cards, property drift and untranslated copy despite valid JS syntax |
| CSS introduces explicit display rules | Check the `hidden` contract in a browser | 0.9 | Story flex layout overrode the browser's hidden display state |
| A local Python check passes | Repeat the release checks inside the declared development environment | 0.9 | Host mypy without the optional decoder missed errors found by the installed dev+compressed environment |
| A prompt contains a verification cue | Keep stated intent separate from execution and handle negation conservatively | 0.9 | “Do not skip tests” initially triggered an opposite skip candidate |

Scope: DevRAR only. These observations guide regression protection, not automatic
assessment of any developer's ability.

## Delivery audit observations

Scope: project. These four new observations come from synthetic reproductions
and the delivery audit; no background observer or global rule is installed.

| Trigger | Action | Domain | Confidence | Evidence |
|---|---|---|---|---|
| otan_elegxeis_animation_controls | Assert actual animation play state and clock progression, not only button labels | testing | 0.9 | Replay and Pause controls passed earlier checks while CSS reveals did not restart and ambient motion continued |
| otan_filtrareis_stream_me_orio_eggrafis | Test alternating valid/invalid records and preserve the next record boundary | data-parsing | 0.9 | A date-filter fix skipped the next valid Git header; an alternating fixture caught it |
| otan_katharizeis_assigned_credentials | Exercise quoted keys, quoted values with spaces and known-token formats | security | 0.9 | JSON keys and spaced passwords bypassed the original assignment redactor |
| otan_cli_typonei_diadromes | Exercise a real subprocess with Unicode paths and a restricted redirected encoding | testing | 0.9 | CP1252 output raised UnicodeEncodeError after the report was already written |
| otan_metras_pafsi_animation | Await the current ready promise and assert paused/not-pending before comparing exact animation clocks | testing | 0.9 | Two CI runs sampled a pending CSS pause one frame early; a running-animation mutation still fails the synchronized assertion |
