---
last_modified: 2026-10-26
tags: [feature, handoff]
---

# DevRAR v0.1 state

Workspace: `C:/Users/skyd3/antigarvity/DevRAR`.
Repository: https://github.com/train-cell/DevRAR.
Branch: `codex/initial-mvp`. Agents must not merge it.
Pull request: https://github.com/train-cell/DevRAR/pull/1 (open, attached to the chat).
Initial implementation commit: `1f61f1b44f29e0f4d3369b7fa06e721012b32920`.
The subsequent [delivery audit](docs/audit.md) corrects defects missed by the
initial acceptance checks. Current source and checks are on PR #1.

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
- [x] Publish feature branch/PR and verify the public installation path and GitHub CI.

## Validation

- Windows / Python 3.11.9: 248 passed, 2 skipped; 100% line coverage
  (1,910 source statements). Skips are the optional browser collection and one
  POSIX-specific case-sensitive repository test.
- Ruff and strict mypy passed for all 11 source modules.
- Chromium: 10 browser tests passed. Desktop/mobile, all chapters, real animation
  restart/pause, accessible counters/dialog names, actual font loading,
  source-chart/null handling, preview/cancel/save, reduced motion, print, roast
  and analysis-method status exercised. Synthetic screenshots were inspected.
- The initial version also produced a three-page synthetic print PDF whose first
  page was inspected; the audited version passes the browser print-style checks.
  Browser screenshots/recordings remain ignored except the synthetic README preview.
- Full synthetic CLI local analysis succeeded with installed phi4-mini:latest
  and Ollama 0.40.11; the provider returned valid citations and no cloud fallback.
  Timeout, malformed-output and attribution failures also preserved a clear partial report.
- Two bounded native Codex samples matched independent human/canonical reply
  counts and source hashes remained unchanged. Native data is not committed.
- Final audited wheel and sdist built. A new clean virtual environment ran the
  installed CLI outside the source tree; all 20 package files matched source
  bytes, including fonts/notices, and the private ignore guard was verified.
  Package metadata declares MIT AND OFL-1.1 and includes four license notices.
- A fresh clone of the public implementation branch followed the README's venv,
  editable installation and demo commands successfully, with only runtime
  dependencies installed. All eight expected artifacts existed, the package
  imported from that clone, and its Git working tree stayed clean after the run.
- GitHub Actions passed all five jobs: Linux/Windows with Python 3.11/3.12,
  including Ruff, strict mypy, full coverage, build and demo, plus Chromium.
  Implementation evidence: https://github.com/train-cell/DevRAR/actions/runs/40398383268.
  Those URLs document the initial implementation. The audit push's current-head
  checks are verified separately before handoff and shown on the pull request.
- A separate headless Chromium 151 smoke traversed all nine chapters at 1440x1000:
  278 frame intervals, p95 16.8 ms, max 33.4 ms, no interval above 50 ms and no
  unexpected layout shift. One 111 ms long task was recorded. These are local
  observations, not a performance guarantee or a physical-device benchmark.

Final audited wheel SHA256:
`75a5b0ff6de25d6d79c19b2e95425684eeb6d92bb50a4eaa2e1d68bba48eedf3`.

## Limits

Grades remain null until rubric calibration and human agreement are validated.
Candidate interpretations do not prove execution, code quality, outcomes or
seniority. No PC-hours, subscription charges or cohort percentiles are invented.
OpenCode/Gemini/Antigravity and actual PC-time imports are future adapters.

Full-stream metrics and bounded evidence are separate. Up to 600 redacted
500-character excerpts feed rules analysis; local inference sees a smaller,
explicitly bounded sample. Automated redaction does not imply anonymization.

## NEXT_STEP_TO_EXECUTE

Owner review of PR #1 and a personal pilot with explicitly selected local
sources. Merge is the owner's action. The implementation branch is usable now
through the README installation instructions. No package-registry publication
or tagged release is claimed.

Human pilot feedback on the narrative and coaching remains useful before
expanding adapters or calibrating numerical scores. Physical-device performance
benchmarking and accessibility certification are not claimed by browser tests.

Read PLAN.md, docs/report-schema.md, docs/rubric.md and docs/acceptance.md.
No database migration, cloud key, automatic model download or background tracker
is required. DEVRAR_BROWSER_TESTS only enables optional browser verification.
