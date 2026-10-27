# DevRAR Assessment Rubric v0.1

## Status

This document defines an **experimental observation rubric**, not an active grade.
`axiologise_ergasia` reports bounded candidate signals from local evidence. Every
dimension score and the overall score remain `null` until both rubric calibration and
human-rater agreement have been validated. The scorecard exposes that gate and its
reason; activity volume never substitutes for evidence quality.

The five dimensions follow the Assessment section in `DevRAR.md`:

1. Scope and acceptance
2. Context and handoffs
3. Delegation and ownership
4. Debugging and evidence
5. Verification and completion

## Evidence eligibility

The rules inspect only rows in `deigmata` with `rolos="user"` and
`eidos="prompt"`. Assistant responses, tool calls, and tool results can neither
credit nor blame the human author. Records are de-duplicated by `(pigi, id)` and at
most 600 input rows are analyzed. `kalypsi_analysi` reports included rows, available
rows before the cap, and whether truncation occurred. The full metrics in `synola`
are copied unchanged and do not affect an assessment.

Each generated finding cites the exact `id`, `pigi`, `locator`, and `keimeno` excerpt
from its source row. A quote is a lead for review, not proof that a practice was
completed or effective. Findings identify their actor as `human_prompt`, state the
limited observed consequence separately from interpretation, retain an alternative
explanation, and use low confidence. Quoted, hypothetical, or illustrative markers
remain candidate signals.

## Candidate cue families

| Dimension | English cues | Greek cues |
|---|---|---|
| Scope and acceptance | acceptance criteria, success criteria, definition of done, expected behavior/result | κριτήρια αποδοχής, κριτήρια επιτυχίας, αναμενόμενη συμπεριφορά |
| Context and handoffs | context, handoff, current decisions, resume/continue from | πλαίσιο, παράδοση, τρέχουσες αποφάσεις, συνέχεια |
| Delegation and ownership | delegate, subagent, owner, ownership, integration, dependencies | ανάθεση, υποπράκτορας, ιδιοκτησία, ενσωμάτωση, εξαρτήσεις |
| Debugging and evidence | reproduce, traceback, stack trace, logs, observed output | αναπαραγωγή, ίχνος κλήσεων, καταγραφές |
| Verification and completion | pytest, test suite, run tests, verify, build result, CI | τρέξε τα tests, εκτέλεσε τις δοκιμές, επαλήθευσε, έλεγξε |

These phrases only detect that a human prompt mentions or requests the topic. The
rules do not infer completeness, skill, seniority, execution, task difficulty, or
success from a marker. Missing markers are not failures and do not create negative
findings.

Only an explicit, affirmative, unquoted request to skip tests or checks creates a
**growth candidate**. Anti-skip instructions (for example, "do not skip tests"),
questions, suggestions, and quoted examples do not create one. Even an affirmative
skip request is not a finding that tests were skipped or the change was unsafe. Its
recommendation is conditional: record the reason and nearest safe alternative when
tests are out of scope; otherwise run targeted tests and report the result.

## Recurrence and bounded findings

Three distinct `(pigi, synedria)` pairs are required before a prompt signal is called
recurring. Repeated rows from one session count as one session. Fewer than three
sessions are described as isolated or below the recurrence threshold. Unknown session
IDs cannot establish recurrence.

Each finding includes at most three representative evidence references. The scorecard
reports the number of matching observations and distinct sessions, plus zero
scoreable sessions while the calibration gate is closed. The rules create no more
than three candidate strengths and three candidate growth priorities. A lack of
candidate cues creates no improvement finding.

## Report fields

`axiologisi.diastaseis` contains all five dimensions. Each dimension has a null
`bathmos`, `katastasi="not_calibrated"`, `paratiriseis` for observed cue rows,
`episodia` for distinct sessions with a candidate signal, zero
`synedries_vathmologisimes`, `aitia`, and cited evidence IDs in `tekmiria`. The scorecard's
`gate_vathmologias` keeps rubric calibration, human agreement, and activation as
separate false gates.

Candidate findings use `katastasi="candidate_only"`, identify `drastis` as
`human_prompt`, and carry string fields for `eythyni`, `synepeia`, `ermineia`,
`enallaktiki`, `antitheta`, `vevaiotita`, and `aitiologia_vevaiotitas`. Their
`tekmiria` cite exact source IDs, locators, and excerpts. This keeps the observed cue,
the possible interpretation, responsibility, counterevidence, and uncertainty
separate in the report.

`analysi` records rules mode and version, evidence cap, valid evidence count, human
prompt count, and the inactive calibration flags. `kalypsi_analysi` preserves the
collector's `epilegmena`, `diathesima`, and `perikopi` meanings.

## Score calibration gate

The draft score anchors in `DevRAR.md` (unavailable, 0–4) are not yet calibrated
examples. Scoring stays disabled until the project has:

- A labeled, representative example set for all five dimensions, including ambiguous
  and counterevidence cases.
- Independent human ratings and a published agreement result against an agreed
  threshold.
- A reviewed adjudication protocol, rubric version, and approval to enable scoring.
- Tests showing that insufficient or truncated evidence never becomes a zero score.

After those gates are met, any numeric score must be calculated by deterministic code
from dimension ratings and include its evidence, counts, rubric version, period,
sources, and analyst metadata. No percentile or seniority claim follows from this
rubric.
