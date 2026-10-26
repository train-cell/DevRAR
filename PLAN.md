# DevRAR Initial MVP Implementation Plan

> For agentic workers: use the agreed parallel ownership below. The human owner explicitly requested execution with multiple GPT-6 Luna agents on 26/10/2026.

**Goal:** λειτουργικό, τοπικό CLI που παράγει διαδραστικό Developer Wrapped από συνθετικά demo δεδομένα ή υποστηριζόμενα Claude/Codex/Git δεδομένα.

**Architecture:** κοινή JSON σύνοψη με provenance, απομονωμένοι readers, renderer που ενσωματώνει CSS/JS/data σε offline HTML. Story και Explore μοιράζονται τις ίδιες μετρήσεις. Η αρχική αξιολόγηση είναι rules-based, με εμφανές score unavailable όταν δεν υπάρχει τεκμηριωμένο rubric evaluation.

**Tech stack:** Python 3.11+, standard library, tzdata, προαιρετικό zstandard, pytest, vanilla HTML/CSS/JS και πραγματικός browser έλεγχος.

**Spec:** DevRAR.md και DESIGN-BRIEF.md.

## Global constraints

- Greeklish implementation identifiers, docstrings, strict types, named constants.
- No telemetry, remote report resources or execution of imported instructions.
- Synthetic demo always labelled; live missing data never replaced by demo.
- Implemented functions and output schema below are shared integration contracts.
- Scope: initial working release with optional verified local inference. Experimental numerical grades remain unavailable until calibration and human agreement gates pass.

## Review focus

- Duplicate / malformed records and copied fork histories do not inflate counts.
- UTC/date conversion excludes unknown timestamps from date-filtered totals and reports partial coverage.
- Untrusted imported strings cannot execute HTML/JS or leak private paths in share cards.
- Missing input creates honest partial / missing coverage rather than invented statistics.
- Keyboard, mobile, reduced motion, Story/Explore/detail return and offline execution work in a browser.

## Ownership and interfaces

### A — Data and metrics worker

Owns src/devrar/syllogi.py, related reader modules if needed and tests/test_syllogi.py.

Produces:

~~~python
def syllexe_dedomena(
    piges: Sequence[str],
    fakeloi: Mapping[str, Path],
    apothitiria: Sequence[Path],
    apo: date | None = None,
    eos: date | None = None,
    zoni: str = "Europe/Athens",
    author: str | None = None,
) -> dict[str, object]:
    ...
~~~

Input sources: claude and codex; explicit root paths or documented default app directories. Git metadata only from declared repositories. Return docs/report-schema.md.

- [x] RED: synthetic JSONL, duplicate IDs, tool-result role, malformed records, period filters and temporary Git repository tests.
- [x] GREEN: read-only readers and trustworthy counts.
- [x] Verify targeted tests and document format limitations.

### B — Frontend worker

Owns src/devrar/assets/report.html, wrapped.css and wrapped.js.

Consumes the report schema. Template placeholders: __DEVRAR_CSS__, __DEVRAR_DATA__, __DEVRAR_JS__, __DEVRAR_CSP__.

Required: strongly designed multi-colour Story scenes, sidebar Explore, actual data cards/charts, next/previous/play/pause/replay, detail dialog with focus restoration, source filter, mobile and reduced motion. All display text from data uses safe DOM APIs.

- [x] Define interaction acceptance against the schema.
- [x] Implement self-contained static assets.
- [x] Verify JS syntax and assist orchestrator's rendered browser checks.

### C — CLI worker

Owns src/devrar/cli.py, __main__.py and tests/test_cli.py.

Produces kyria(orismata: Sequence[str] | None = None) -> int.

Consumes:

~~~python
from devrar.deigma import fortose_deigma
from devrar.syllogi import syllexe_dedomena
from devrar.anafora import apothikefse_anafora

# fortose_deigma() -> dict[str, object]
# apothikefse_anafora(dedomena: Mapping[str, object], exodos: Path,
#                   anoigma: bool = False, roast: bool = False) -> Path
# returned Path is the generated index.html
~~~

Command: devrar wrap. Flags --demo, repeated --source/--repo, --claude-path, --codex-path, --since/--until, --timezone, --author, --output, --open, --roast and --analysis rules.

An unsupported analysis mode returns an actionable error, with no fallback to invented coaching. Errors return the specified 1/2/3 codes. Demo plus real sources must be rejected to avoid data contamination.

- [x] RED: CLI help, demo/live dispatch, invalid dates/timezone, partial coverage and conflicting inputs.
- [x] GREEN: argparse and safe dispatch.
- [x] Verify targeted tests.

### Orchestrator — shared integration and release

Owns packaging, schema, synthetic demo, renderer, rules-based recognition/coaching, README, LICENSE, project CI and browser test scripts.

- [x] Write renderer/output/security tests and observe RED.
- [x] Implement renderer and clearly synthetic demo, preserving the frozen schema.
- [x] Integrate workers; run full pytest, package installation/build and browser interaction checks.
- [x] Inspect desktop/mobile screenshots, verify no external requests and save proof locally.
- [x] Independent Luna review and necessary fixes.
- [x] Create public GitHub repository and feature-branch PR once authenticated; do not merge.
- [x] Save handoff with actual coverage, validation results and remaining work.

## Definition of this delivery

A user can install the project, run devrar wrap --demo --open, get a distinctive working HTML experience, and run supported local inputs with visible provenance. No overall programmer grade or production readiness claim is invented. Public installation and all five CI jobs passed; [PR #1](https://github.com/train-cell/DevRAR/pull/1) remains open for owner review.

## Goal continuation — 26 October 2026

The owner explicitly requested `/goal` until a usable end product. The working
integration baseline passed 68 Python tests with 100% line coverage and three
Chromium tests before this extension. These results are a baseline, not final
verification of subsequent changes.

1. Data worker: bounded, redacted normalized evidence with sampling coverage;
   correct Git attribution and duplicate activity; full streaming metric counts.
2. Assessment worker: transparent workflow observations over human evidence,
   alternatives and attribution, five dimension profiles and explicit calibration
   gates. Missing markers do not establish bad practice.
3. UI worker: expanded personal narrative, useful recognition and next actions,
   honest empty/partial states, evidence details and readable scorecard states.
4. Orchestrator: integrate assessment, enrich private metadata/Markdown, verify
   packaging and fresh installation, browser journeys, accessibility and CI;
   independent review; publish the feature branch and PR without merging.

The product's v0.1 scope stays Claude Code, Codex and Git. OpenCode/Gemini/
Antigravity adapters, actual PC time, cloud inference and calibrated seniority
ratings are outside this release. Optional deeper local analysis uses an owned
cloud-disabled process, installed models only, bounded excerpts and validated
citations; it does not bypass evidence or numerical calibration gates.

Completion audit additions: implement and verify the optional local analyzer,
print layout, visible opt-in roast, bounded recognition badges and supported
Claude message usage aggregation before final publication. These are acceptance
items from the original brief, not a redefinition of a smaller release.
