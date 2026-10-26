---
last_modified: 2026-10-26
tags: [feature, handoff]
---

# DevRAR v0.1 state

Workspace: `C:/Users/skyd3/antigarvity/DevRAR`.
Repository: https://github.com/train-cell/DevRAR.
Branch: `codex/initial-mvp`. Agents must not merge it.

## Verified implementation

- [x] Claude/Codex JSONL and optional ZST readers; selected Git HEADs and author scope.
- [x] Root/child sessions, human inputs, tool calls, turn-aware reply reconciliation,
  date/timezone filters, shared-commit deduplication and tracked-file inventory.
- [x] Source format/adapter/date provenance and explicit partial/unknown coverage.
- [x] Claude API-message usage maxima and deduplication; ambiguous Codex usage stays null.
- [x] Five workflow dimensions, cited candidate observations, alternatives,
  code-derived source authorship and closed numerical calibration gates.
- [x] Optional installed-model analysis in an owned cloud-disabled Ollama process,
  bounded excerpts, strict JSON/citations, 150-second deadline and cleanup.
- [x] Nine Story chapters, Explore/Details, keyboard/touch, play/pause/replay,
  reduced motion, recognition badges, opt-in roast and print layout.
- [x] Offline HTML, Markdown, JSON/JSONL/run metadata and aggregate-only SVG.
  Every run creates its Git ignore guard before writing private evidence.
- [x] Independent review, native-source spot-checks, package build and local installation.
- [ ] Publish feature branch/PR and verify the public installation path and GitHub CI.

## Validation

- Windows / Python 3.11.9: 231 passed, 2 skipped; 100% line coverage
  (1,876 source statements). Skips are the optional browser collection and one
  POSIX-specific case-sensitive repository test.
- Ruff and strict mypy passed for all 11 source modules.
- Chromium: 5 browser tests passed. Desktop, mobile, all chapters, focus return,
  source-chart filter, share download, reduced motion, print and roast exercised.
- A three-page synthetic print PDF was generated and its first page inspected;
  all pages contain text. Browser screenshots/recordings remain ignored.
- Full synthetic CLI local analysis succeeded with installed phi4-mini:latest
  and Ollama 0.40.11; the provider returned valid citations and no cloud fallback.
  Timeout, malformed-output and attribution failures also preserved a clear partial report.
- Two bounded native Codex samples matched independent human/canonical reply
  counts and source hashes remained unchanged. Native data is not committed.
- Wheel and sdist built. A clean virtual environment ran the installed CLI from
  outside the source tree; package resources matched source bytes. The final
  rebuilt wheel and public clone path are checked again before publication completes.

## Limits

Grades remain null until rubric calibration and human agreement are validated.
Candidate interpretations do not prove execution, code quality, outcomes or
seniority. No PC-hours, subscription charges or cohort percentiles are invented.
OpenCode/Gemini/Antigravity and actual PC-time imports are future adapters.

Full-stream metrics and bounded evidence are separate. Up to 600 redacted
500-character excerpts feed rules analysis; local inference sees a smaller,
explicitly bounded sample. Automated redaction does not imply anonymization.

## NEXT_STEP_TO_EXECUTE

Commit and push `codex/initial-mvp`, create and attach its pull request without
merging, then run the README installation from a fresh public clone and verify
all GitHub checks. Record URLs and final evidence here.

Read PLAN.md, docs/report-schema.md, docs/rubric.md and docs/acceptance.md.
No database migration, cloud key, automatic model download or background tracker
is required. DEVRAR_BROWSER_TESTS only enables optional browser verification.
