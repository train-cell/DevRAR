# DevRAR full-vision implementation

Owner authorization: 27 October 2026. Continue autonomously with Luna agents,
prioritizing adapters, deeper assessment, longitudinal progress and richer
metrics. Preserve the accepted UI, local privacy and existing report contract.

## Design

Extend report schema v1 additively; existing counters retain their definitions.
Keep vendor readers, streaming work metrics, outcome-aware assessment, report
comparison and presentation in separate modules. Unsupported native formats
remain explicit; do not label an export reader as a universal native reader.

Transient normalized events use the shared `SymvanErgasias` contract in
`symvanta.py`: source/id/session/parent, aware ISO timestamp or null, role/kind,
redacted text and evidence locator, plus optional recorded tool/model/exit code.
Events are not executed or automatically persisted. A streaming accumulator
receives only accepted, deduplicated in-scope events. It emits bounded episode
summaries and activity aggregates with explicit evidence/coverage metadata.

New report keys:

- `metrika_ergasias`: hourly/day aggregates, observed-event interval estimate,
  tool-result test summaries and source/session episodes. The estimate is not
  actual human PC time. Human prompt counts drive hourly patterns.
- `sygkrisi`: explicit baseline report comparison, compatibility decisions and
  nullable deltas. Never embed the baseline's private excerpts.
- `epeisodia_ergasias`: bounded outcome summaries with exact citations and
  observed/unknown status, distinct from prompt intent or claims of success.

Numerical grades remain gated pending real representative human calibration.
Cloud inference requires an explicit option/provider choice; local is default.
Active-time/cost imports require supplied recorded data and source semantics.

## Ordered slices

1. Define contracts and acceptance; inspect official/native source formats.
2. Implement supported OpenCode/Gemini/export adapters and explicit unsupported
   states; integrate without disturbing legacy Claude/Codex deduplication.
3. Collect hourly/day/event-span/test-result/episode metrics on the full selected
   stream; add Git changed-line/file metadata with merge/binary limits.
4. Add evidence-linked outcome observations and compatible report comparisons.
5. Integrate CLI flags and UI: heatmap, peak hours, outcome cards, progress deltas,
   useful details and limited filters with truthful scope.
6. Add active-time/cost inputs, richer narrative/archetypes, export/theme/language
   or provider options in independent verified slices where feasible.
7. Independent review, full checks/build/browser/live smoke, docs and feature PR
   push without merge. Keep incomplete/external gates explicitly recorded.

## Ownership, wave one

- Source worker: new `piges/` readers and `tests/test_nees_piges.py`; owns legacy
  collector integration only after notifying root. Root owns CLI and shared type.
- Metrics worker: `metrika.py` and its tests; no collector/UI edits.
- Growth worker: `proodos.py`, outcome analysis module and their tests; no CLI,
  collector, existing renderer or frontend edits.
- Root: shared contracts, CLI/renderer/frontend integration, imports, docs,
  verification and repository publication. No worker commits/pushes.

Each meaningful behavior requires a failing regression before implementation.
Unknown data stays null; malformed/truncated input exposes partial coverage.
Independent changes may run concurrently; integration follows dependencies.
