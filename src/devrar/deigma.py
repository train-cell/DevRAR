"""Παρέχει σταθερά, συνθετικά δεδομένα για το offline demo."""

from __future__ import annotations

from copy import deepcopy
from typing import TypeAlias

from devrar.axiologisi import axiologise_ergasia

AnaforaDedom: TypeAlias = dict[str, object]

IMEROMINIES = (
    "2026-10-12",
    "2026-10-13",
    "2026-10-14",
    "2026-10-15",
    "2026-10-16",
    "2026-10-17",
    "2026-10-18",
    "2026-10-19",
    "2026-10-20",
    "2026-10-21",
    "2026-10-22",
    "2026-10-23",
)
PROMPTS_ANA_IMERA = (38, 72, 115, 96, 44, 128, 85, 68, 107, 53, 92, 176)
COMMITS_ANA_IMERA = (1, 2, 1, 3, 0, 4, 2, 1, 3, 1, 2, 4)


def fortose_deigma() -> AnaforaDedom:
    """Επιστρέφει ανεξάρτητο αντίγραφο του συνεπούς synthetic report."""
    dedomena: AnaforaDedom = {
        "ekdosi_sximatos": "1",
        "leitourgia": "demo",
        "scope_git": {
            "rev": "HEAD",
            "author": None,
            "repositories": [
                "demo-orbit-notes",
                "demo-little-compiler",
                "demo-garden-api",
            ],
        },
        "periodos": {
            "apo": IMEROMINIES[0],
            "eos": IMEROMINIES[-1],
            "zoni": "Europe/Athens",
        },
        "synola": {
            "synedries": 60,
            "rizikes": 44,
            "ypopraktores": 16,
            "minimata_xristi": 1074,
            "apantiseis": 1038,
            "kliseis_ergaleion": 1362,
            "tokens": 894200,
            "commits": 24,
            "imeres": 12,
        },
        "ergaleia": [
            {"onoma": "Claude Code", "synedries": 42, "prompts": 720, "tokens": 628000},
            {"onoma": "Codex CLI", "synedries": 18, "prompts": 354, "tokens": 266200},
        ],
        "montela": [
            {"onoma": "claude-sonnet", "kliseis": 720, "tokens": 628000},
            {"onoma": "gpt-codex", "kliseis": 354, "tokens": 266200},
        ],
        "drastiriotita": [
            {"imerominia": imerominia, "prompts": prompts, "commits": commits}
            for imerominia, prompts, commits in zip(
                IMEROMINIES, PROMPTS_ANA_IMERA, COMMITS_ANA_IMERA, strict=True
            )
        ],
        "projects": [
            {"onoma": "orbit-notes", "commits": 10, "arxeia": 34},
            {"onoma": "little-compiler", "commits": 8, "arxeia": 27},
            {"onoma": "garden-api", "commits": 6, "arxeia": 19},
        ],
        "kalypsi_analysi": {
            "epilegmena": 10,
            "diathesima": 10,
            "perikopi": False,
        },
        "deigmata": [
            {
                "id": "S001",
                "pigi": "Claude Code",
                "synedria": "demo-session-alpha",
                "rolos": "user",
                "eidos": "prompt",
                "keimeno": (
                    "Define acceptance criteria for the report filter; unknown totals "
                    "must stay unknown."
                ),
                "locator": "demo-session-alpha#1",
                "imerominia": "2026-10-12",
            },
            {
                "id": "S002",
                "pigi": "Claude Code",
                "synedria": "demo-session-alpha",
                "rolos": "assistant",
                "eidos": "response",
                "keimeno": "The criteria separate recorded zero from unavailable data.",
                "locator": "demo-session-alpha#2",
                "imerominia": "2026-10-12",
            },
            {
                "id": "S003",
                "pigi": "Claude Code",
                "synedria": "demo-session-beta",
                "rolos": "tool",
                "eidos": "tool_result",
                "keimeno": (
                    "Synthetic log: parsed 3 records; one malformed row was skipped."
                ),
                "locator": "demo-session-beta#tool-1",
                "imerominia": "2026-10-14",
            },
            {
                "id": "S004",
                "pigi": "Codex CLI",
                "synedria": "demo-session-gamma",
                "rolos": "user",
                "eidos": "prompt",
                "keimeno": (
                    "Reproduce the issue from logs, run pytest, and report the result."
                ),
                "locator": "demo-session-gamma#1",
                "imerominia": "2026-10-18",
            },
            {
                "id": "S005",
                "pigi": "Codex CLI",
                "synedria": "demo-session-gamma",
                "rolos": "tool",
                "eidos": "tool_result",
                "keimeno": "Synthetic test log: 5 focused tests passed.",
                "locator": "demo-session-gamma#tool-1",
                "imerominia": "2026-10-18",
            },
            {
                "id": "S010",
                "pigi": "Codex CLI",
                "synedria": "demo-session-gamma",
                "rolos": "assistant",
                "eidos": "tool_call",
                "keimeno": "Invoke the focused test suite for missing source records.",
                "locator": "demo-session-gamma#call-1",
                "imerominia": "2026-10-18",
            },
            {
                "id": "S006",
                "pigi": "Codex CLI",
                "synedria": "demo-session-delta",
                "rolos": "user",
                "eidos": "prompt",
                "keimeno": (
                    "Handoff: keep the engineering score unavailable until the "
                    "rubric is calibrated."
                ),
                "locator": "demo-session-delta#1",
                "imerominia": "2026-10-22",
            },
            {
                "id": "S007",
                "pigi": "Codex CLI",
                "synedria": "demo-session-delta",
                "rolos": "assistant",
                "eidos": "response",
                "keimeno": (
                    "The report will preserve unknown grades and show evidence limits."
                ),
                "locator": "demo-session-delta#2",
                "imerominia": "2026-10-22",
            },
            {
                "id": "S008",
                "pigi": "Codex CLI",
                "synedria": "demo-session-delta",
                "rolos": "tool",
                "eidos": "tool_result",
                "keimeno": (
                    "Synthetic run log: report artifacts written to a new local folder."
                ),
                "locator": "demo-session-delta#tool-1",
                "imerominia": "2026-10-22",
            },
            {
                "id": "S009",
                "pigi": "Synthetic collector",
                "synedria": "demo-analysis-session",
                "rolos": "tool",
                "eidos": "tool_result",
                "keimeno": (
                    "Synthetic activity summary: records span 12 distinct dates."
                ),
                "locator": "demo-analysis-session#tool-1",
                "imerominia": "2026-10-23",
            },
        ],
        "eyrimata": [
            {
                "id": "D001",
                "titlos": "A dozen days on the board",
                "epipedo": "strength",
                "keimeno": (
                    "The synthetic activity log contains work on 12 distinct dates."
                ),
                "protasi": (
                    "Pick one moment from the period and add a short note about "
                    "what you are proud of."
                ),
                "eythyni": "Aggregate evidence describes activity volume only.",
                "vevaiotita": "high",
                "enallaktiki": (
                    "Recorded days do not show what was completed on each day."
                ),
                "antitheta": (
                    "Activity dates alone do not establish which changes "
                    "were completed."
                ),
                "tekmiria": [
                    {
                        "pigi": "Synthetic collector",
                        "locator": "S009",
                        "apospasma": (
                            "Synthetic activity summary: records span "
                            "12 distinct dates."
                        ),
                    }
                ],
            },
            {
                "id": "D002",
                "titlos": "Make the next recap more specific",
                "epipedo": "growth",
                "keimeno": (
                    "This demo records activity totals, but it cannot establish "
                    "code quality or outcomes."
                ),
                "protasi": (
                    "Keep a brief project note beside an important change so future "
                    "evidence has useful context."
                ),
                "eythyni": "No individual behavior is inferred from absent records.",
                "vevaiotita": "high",
                "enallaktiki": (
                    "This is a schema limitation, not evidence of a weakness."
                ),
                "antitheta": (
                    "One synthetic test result does not establish overall "
                    "project quality."
                ),
                "tekmiria": [
                    {
                        "pigi": "Codex CLI",
                        "locator": "S006",
                        "apospasma": (
                            "Handoff: keep the engineering score unavailable until "
                            "the rubric is calibrated."
                        ),
                    }
                ],
            },
        ],
        "oroshma": [],
        "piges": [
            {
                "onoma": "Claude Code",
                "katastasi": "ok",
                "arxeia": 18,
                "sfalmata": 0,
                "simeiosi": "Synthetic demo data.",
            },
            {
                "onoma": "Codex CLI",
                "katastasi": "ok",
                "arxeia": 12,
                "sfalmata": 0,
                "simeiosi": "Synthetic demo data.",
            },
            {
                "onoma": "Git repositories",
                "katastasi": "ok",
                "arxeia": 3,
                "sfalmata": 0,
                "simeiosi": "Synthetic project aggregates.",
            },
            {
                "onoma": "Synthetic collector",
                "katastasi": "ok",
                "arxeia": 1,
                "sfalmata": 0,
                "simeiosi": "Synthetic activity summary.",
            },
        ],
        "simeioseis": [
            (
                "All activity, repository names, and counts in this report are "
                "synthetic demo data."
            )
        ],
    }
    from devrar.deigma_ergasias import prosthese_deigma_ergasias

    return prosthese_deigma_ergasias(
        axiologise_ergasia(deepcopy(dedomena)), IMEROMINIES, PROMPTS_ANA_IMERA
    )
