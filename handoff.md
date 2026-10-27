---
last_modified: 2026-10-27
tags: [feature, handoff]
---

# DevRAR current state — v0.2 candidate

## Paused checkpoint — 27 October 2026, 23:03 Europe/Athens

The owner explicitly requested the nearest checkpoint, handoff and closure for
today. The goal tool returned **paused**. Do not resume the full-vision loop
without a new owner instruction. No agents or application servers remain active.
This is a verified development checkpoint, not full-vision completion or release.

Workspace: `C:/Users/skyd3/antigarvity/DevRAR`.
Branch: `codex/full-vision-recap`, based on `origin/main` `df6a39b` (same tree as
baseline `c14927a`). Version: **0.2.0 preview**. PR #1 was merged by the owner;
the expansion belongs in a NEW draft PR, never PR #1. No agent merge is allowed.
Closure commits/push are restricted to this repository. Use Git to read the
checkpoint SHA; private reports/build environments remain ignored. No stashes.

### Read first

- `C:/Users/skyd3/antigarvity/DevRAR/AGENTS.md`
- `C:/Users/skyd3/antigarvity/DevRAR/tasks/todo.md`
- `C:/Users/skyd3/antigarvity/DevRAR/tasks/wave-two.md`
- `C:/Users/skyd3/antigarvity/DevRAR/docs/expanded-recap.md`
- `C:/Users/skyd3/antigarvity/DevRAR/docs/report-schema.md`
- `C:/Users/skyd3/antigarvity/DevRAR/docs/checkpoint-20261027.md`

### Implemented and locally verified

- [x] OpenCode read-only SQLite; scoped Gemini and Antigravity adapters.
- [x] Full-stream hourly/day/interval/check metrics, evidence-linked outcomes,
  compatible comparisons, Git deltas and supplied time/cost imports.
- [x] Recognition/profile, richer demo, Markdown for main domains, SVG/PNG.
- [x] Original default and Blue hour; offline, mobile, keyboard and share privacy.
- [x] Modern Codex assistant deduplication plus separate commands, patches,
  collaboration and request-usage subset. No duplicate global tool/token counts.
- [x] Separate native command coaching in HTML/JSON; null usage if no known rows.
- [x] Explicit opt-in cloud CLI/provider with strict citations, bounded redacted
  requests, safe failure/rules fallback. Synthetic mocked network tests only.
- [x] Final idle-threshold regression fixed: main/native channels both use the
  CLI value and report `idle_minutes`; 20-minute pair accepted at threshold 30.

Fresh closure results: **518 passed, 2 skipped, 100% line coverage (4,442
statements)**; **23 browser tests passed**; Ruff, strict source mypy and JS syntax
passed; wheel/sdist built; a separate venv installed the wheel. Installed demo
exit 0 and actual native Codex exit 3 (documented incomplete coverage) passed.
Native commands/request usage appeared, nested outcomes were generated, threshold
30 propagated, and source SHA-256 stayed unchanged. No cloud request was made.
Local proof: `C:/Users/skyd3/antigarvity/DevRAR/artifacts/checkpoint-20261027/`.
Older native/import/compare and rendered proof lives in ignored
`artifacts/vision-check` and `artifacts/vision-review`; do not publish these.

### Pending / known limits

- [ ] Remote CI for the newly pushed checkpoint is not yet verified here.
- [ ] Complete modern Codex native-channel Markdown/`tekmiria.jsonl` parity in
  `src/devrar/report_extras.py` / `src/devrar/anafora.py`; HTML/JSON already work.
- [ ] Independent integrated wave-two review; source/UI/backend review happened
  in slices. UI worker hit a quota limit; root inspected/integrated its output
  and all 23 browser checks passed. Do not infer a final independent sign-off.
- [ ] Broader native-format validation, richer task/code-outcome correlation,
  arbitrary date/project interaction filters, extra UI languages and visual mascot.
- [ ] Real human calibration/agreement before numerical grades. Scores stay null.
- [ ] Real provider interoperability pilot if explicitly authorised; synthetic
  cloud transport tests do not prove support for every provider/model.

No unresolved failing local test is known. The first closure coverage run was
99.59%: source formatting during the run displaced wrapper line positions, and
native duplicate/unknown-time branches needed a real regression. The clean rerun
after adding that regression reached 100%; do not edit source during coverage.
Socket timeout in cloud transport is not an absolute whole-request deadline.
Native request usage is always an incomplete subset, not a global token total.
No raw transcript commands were executed. No DB migration or new runtime package
dependency was added. New optional key: `DEVRAR_CLOUD_API_KEY` (name only; never
save its value); `OPENCODE_DB` overrides discovery; `DEVRAR_BROWSER_TESTS=1`
enables browser checks. Numerical rating gates remain closed.

NEXT_STEP_TO_EXECUTE (only after owner resumes): in
`C:/Users/skyd3/antigarvity/DevRAR`, run
`gh pr checks codex/full-vision-recap` and inspect the first failing job, if any,
before beginning the native Markdown/evidence parity task above.

CHECKPOINT_VERIFIED_LOCALLY; FULL_VISION_PENDING; GOAL_PAUSED_BY_OWNER.

## Historical v0.1 delivery

Workspace: `C:/Users/skyd3/antigarvity/DevRAR`.
Repository: https://github.com/train-cell/DevRAR.
Branch: `codex/initial-mvp`. Agents must not merge it.
Pull request: https://github.com/train-cell/DevRAR/pull/1 (open, attached to the chat).
Initial implementation commit: `1f61f1b44f29e0f4d3369b7fa06e721012b32920`.
The subsequent [delivery audit](docs/audit.md) corrects defects missed by the
initial acceptance checks. Current source and checks are on PR #1.

Fresh verification on 27 October 2026 is recorded in
[docs/final-check.md](docs/final-check.md): full gates rerun, new installed CLI
and browser journeys, native-input partial coverage and successful actual
local-model inference. No product code changed in that validation. The complete
original vision is not claimed 100% delivered; v0.1 limits remain explicit.

The closure CI exposed a pending-pause clock race in the browser assertion.
The test awaits animation readiness and still requires paused/not-pending state
and exact clock equality. A temporary running-animation mutation is rejected;
runtime product code remains unchanged. See the CI finding in final-check.md.

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
- Audited code `7ab1d18` passed all five GitHub jobs, including ten browser tests:
  https://github.com/train-cell/DevRAR/actions/runs/40403248485.
  A second fresh public clone at that revision passed the README installation
  and demo; all eight artifacts, source import and Git ignore guard were checked,
  and Git status stayed clean. The documentation follow-up changes no product code.
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

## Historical v0.1 next step (superseded)

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
