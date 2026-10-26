# v0.1 acceptance evidence

This is a traceability record, not a substitute for the checks themselves.
Commands are documented in CONTRIBUTING.md; final release state is in handoff.md
and the pull request checks.

| Requirement | Implementation and authoritative evidence |
|---|---|
| Installable local CLI | Final wheel/sdist, outside-source clean-environment demo and byte equality of all 14 package files; fresh public clone followed README installation, generated all eight artifacts and retained a clean Git working tree |
| Claude/Codex/Git ingestion | Synthetic JSONL/ZST and temporary Git fixtures; native Codex spot-checks matched independent human/assistant counts without changing sources |
| Trustworthy metrics | Date/timezone bounds, unique IDs, explicit child metadata, cross-channel turn reconciliation, author/HEAD scope, file inventory and source provenance regressions |
| Token usage without invented costs | Claude API-message maxima/dedup; source/model coverage; cumulative Codex usage stays unavailable; docs/usage.md defines the arithmetic |
| Evidence-linked assessment | Five workflow dimensions, exact cited excerpts, role-aware attribution, alternatives/counterevidence, recurrence threshold and bounded priorities; test_axiologisi.py |
| Optional local coaching | Owned cloud-disabled Ollama process, manifest check, bounded excerpts, strict JSON/quotes, code-derived authorship and deadline/cleanup tests; actual full demo succeeded with installed phi4-mini |
| Fair numerical score gates | Numeric grades remain null while calibration/human agreement are unvalidated; neither volume nor model prose can activate them |
| Personal Wrapped | Nine distinct Story chapters, Explore categories, charts, details, source-chart filter, three bounded recognition badges and opt-in original narrator copy |
| Actual interaction | Chromium keyboard, autoplay/pause, replay, scene/detail focus restoration, source filter and full nine-chapter traversal; screenshots and recordings under ignored artifacts/ |
| Mobile and reduced motion | Touch-enabled small viewport, reduced-motion navigation, readable content and no horizontal overflow |
| Motion smoke | Separate headless Chromium 151 traversal of nine chapters: p95 frame interval 16.8 ms, max 33.4 ms, no unexpected layout shift; one 111 ms long task. Local observation only, no physical-device performance claim |
| Print | Print CSS exercised in Chromium; generated three-page synthetic PDF inspected for readable content and hidden navigation |
| Private artifacts and safe sharing | HTML/Markdown/JSON/JSONL/run metadata, common credential redaction, script escaping and exact CSP hash; browser/static SVG allowlist tests exclude private names, quotes and dates |
| Offline operation | Generated report has embedded assets, no remote fonts/scripts/analytics, and browser tests observe no external HTTP requests |
| Open-source delivery | MIT, contribution guide, documented source/asset provenance, feature branch and attached PR; merge remains the owner's action |

[PR #1](https://github.com/train-cell/DevRAR/pull/1) contains the implementation.
[Implementation CI](https://github.com/train-cell/DevRAR/actions/runs/40398383268)
passed Linux/Windows on Python 3.11/3.12 and the separate Chromium job. See the
pull request for checks of the current documentation follow-up.

Numerical rubric calibration, human agreement, cohort percentiles, additional
vendor adapters and actual PC-time imports remain outside the enabled v0.1
capability. No claim is made that activity counts establish code quality,
seniority, task success, hours worked or subscription charges. Pilot feedback on
usefulness is still a human question; it is not inferred from clicks or test counts.
