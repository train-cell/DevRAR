from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import pytest

from devrar.axiologisi import axiologise_ergasia


def ftiaxe_deigma(
    kleidi: str,
    keimeno: str,
    synedria: str,
    rolos: str = "user",
    eidos: str = "prompt",
) -> dict[str, str]:
    """Δημιουργεί συνθετικό evidence row με ρητή απόδοση actor και session."""
    return {
        "id": kleidi,
        "pigi": "synthetic-fixture",
        "synedria": synedria,
        "rolos": rolos,
        "eidos": eidos,
        "keimeno": keimeno,
        "locator": f"{synedria}:{kleidi}",
        "imerominia": "2026-10-26T12:00:00Z",
    }


def pare_eyrimata(dedomena: Mapping[str, object]) -> list[dict[str, object]]:
    """Επιστρέφει με type guard τα ευρήματα του report."""
    eyrimata = dedomena["eyrimata"]
    assert isinstance(eyrimata, list)
    return [cast(dict[str, object], eyrima) for eyrima in eyrimata]


def pare_axiologisi(dedomena: Mapping[str, object]) -> dict[str, object]:
    """Επιστρέφει με type guard το scorecard του report."""
    axiologisi = dedomena["axiologisi"]
    assert isinstance(axiologisi, dict)
    return cast(dict[str, object], axiologisi)


def test_axiologisi_sparse_report_den_vathmologei() -> None:
    """Απουσία candidate evidence δεν γίνεται μηδενικός score ή αρνητικό finding."""
    arxika: dict[str, object] = {
        "leitourgia": "live",
        "synola": {"synedries": 900, "minimata_xristi": 9000},
        "deigmata": [],
    }

    apotelesma = axiologise_ergasia(arxika)
    axiologisi = pare_axiologisi(apotelesma)
    diastaseis = cast(list[dict[str, object]], axiologisi["diastaseis"])

    assert axiologisi["diathesimi"] is False
    assert axiologisi["synoliko"] is None
    assert len(diastaseis) == 5
    assert all(diastasi["bathmos"] is None for diastasi in diastaseis)
    assert all(diastasi["katastasi"] == "not_calibrated" for diastasi in diastaseis)
    assert pare_eyrimata(apotelesma) == []


def test_axiologisi_malformed_or_missing_rows_are_ignored_safely() -> None:
    """Αγνοεί μη mapping, ελλιπή, ή κενά source/id rows χωρίς να επινοεί findings."""
    arxika: dict[str, object] = {
        "deigmata": [
            None,
            {"id": "missing-source", "keimeno": "Run pytest."},
            ftiaxe_deigma("", "Run pytest.", "s-1"),
            ftiaxe_deigma("u-1", "Run pytest.", "s-1", rolos="assistant"),
        ]
    }

    apotelesma = axiologise_ergasia(arxika)

    assert pare_eyrimata(apotelesma) == []
    analysi = cast(dict[str, object], apotelesma["analysi"])
    assert analysi["egkyra_deigmata"] == 1


def test_axiologisi_non_list_deigmata_becomes_empty_bounded_input() -> None:
    """Μη λίστα `deigmata` αντιμετωπίζεται ως μη διαθέσιμα evidence rows."""
    apotelesma = axiologise_ergasia({"deigmata": None})

    assert apotelesma["deigmata"] == []
    assert apotelesma["kalypsi_analysi"] == {
        "epilegmena": 0,
        "diathesima": 0,
        "perikopi": False,
    }


def test_axiologisi_human_prompts_paragoun_akribes_candidate_tekmiria() -> None:
    """Εξάγει υποψήφια στοιχεία από ανθρώπινα prompts και παραθέτει ακριβές quote."""
    apospasma = "Please include acceptance criteria, run pytest, and report the result."
    arxika: dict[str, object] = {
        "deigmata": [
            ftiaxe_deigma("u-1", apospasma, "s-1"),
            ftiaxe_deigma(
                "a-1",
                "Acceptance criteria and pytest passed",
                "s-1",
                "assistant",
                "response",
            ),
            ftiaxe_deigma(
                "t-1",
                "Acceptance criteria and pytest passed",
                "s-1",
                "tool",
                "tool_result",
            ),
        ],
        "synola": {"minimata_xristi": 1, "apantiseis": 1},
    }

    apotelesma = axiologise_ergasia(arxika)
    eyrimata = pare_eyrimata(apotelesma)

    assert {eyrima["diastasi"] for eyrima in eyrimata} == {
        "scope_acceptance",
        "verification",
    }
    assert all(eyrima["katastasi"] == "candidate_only" for eyrima in eyrimata)
    assert all(eyrima["drastis"] == "human_prompt" for eyrima in eyrimata)
    assert all(
        "does not establish completion" in str(eyrima["keimeno"]) for eyrima in eyrimata
    )
    assert all(eyrima["paratiriseis"] == 1 for eyrima in eyrimata)
    assert all(eyrima["enallaktiki"] and eyrima["ermineia"] for eyrima in eyrimata)
    assert all(eyrima["synepeia"] and eyrima["vevaiotita"] for eyrima in eyrimata)
    assert all(eyrima["vevaiotita"] == "low" for eyrima in eyrimata)
    assert all(eyrima["eythyni"] and eyrima["antitheta"] for eyrima in eyrimata)
    assert all(eyrima["tekmiria"][0]["id"] == "u-1" for eyrima in eyrimata)
    assert all(eyrima["tekmiria"][0]["apospasma"] == apospasma for eyrima in eyrimata)
    assert len(eyrimata) == 2


def test_axiologisi_tria_distinct_sessions_gia_epanalamvanomeno_sima() -> None:
    """Δύο sessions μένουν non-recurring και τρία μόνο candidate-recurring."""
    deigmata = [
        ftiaxe_deigma("u-1", "Add acceptance criteria to this change.", "s-1"),
        ftiaxe_deigma("u-2", "Add acceptance criteria to this change.", "s-1"),
        ftiaxe_deigma("u-3", "Add acceptance criteria to this change.", "s-2"),
        ftiaxe_deigma("u-4", "Add acceptance criteria to this change.", "s-3"),
    ]
    arxika: dict[str, object] = {"deigmata": deigmata}

    eyrimata_dyo_synedrion = pare_eyrimata(
        axiologise_ergasia({"deigmata": deigmata[:3]})
    )
    eyrima_dyo_synedrion = next(
        eyrima
        for eyrima in eyrimata_dyo_synedrion
        if eyrima["diastasi"] == "scope_acceptance"
    )
    assert eyrima_dyo_synedrion["paratirimenes_synedries"] == 2
    assert eyrima_dyo_synedrion["motivo"] != "recurring_candidate_signal"

    eyrimata = pare_eyrimata(axiologise_ergasia(arxika))
    eyrima = next(
        eyrima for eyrima in eyrimata if eyrima["diastasi"] == "scope_acceptance"
    )

    assert eyrima["paratirimenes_synedries"] == 3
    assert eyrima["motivo"] == "recurring_candidate_signal"
    assert eyrima["paratiriseis"] == 4
    assert len(eyrima["tekmiria"]) <= 3


def test_axiologisi_diplotipa_source_ids_metrontai_mia_fora() -> None:
    """Ίδιο source record id δεν αυξάνει observations ή cited evidence."""
    arxika: dict[str, object] = {
        "deigmata": [
            ftiaxe_deigma("u-1", "Run pytest and report the result.", "s-1"),
            ftiaxe_deigma("u-1", "Run pytest and report the result again.", "s-1"),
        ]
    }

    apotelesma = axiologise_ergasia(arxika)
    eyrima = pare_eyrimata(apotelesma)[0]

    assert eyrima["paratiriseis"] == 1
    assert [tekmirio["id"] for tekmirio in eyrima["tekmiria"]] == ["u-1"]


def test_axiologisi_agnosti_synedria_den_theoreitai_epanalamvanomeni() -> None:
    """Cue χωρίς session id παραμένει candidate χωρίς ισχυρισμό recurrence."""
    arxika: dict[str, object] = {
        "deigmata": [ftiaxe_deigma("u-1", "Define success criteria.", "")]
    }

    eyrima = pare_eyrimata(axiologise_ergasia(arxika))[0]

    assert eyrima["paratirimenes_synedries"] == 0
    assert eyrima["motivo"] == "isolated_candidate_signal"
    assert "session unknown" in str(eyrima["titlos"])
    assert "no session identifier" in str(eyrima["keimeno"])


@pytest.mark.parametrize(
    ("keimeno", "diastasi"),
    [
        ("Define success criteria and expected behavior.", "scope_acceptance"),
        ("Carry context and hand off the current decisions.", "context_handoffs"),
        ("Delegate this task; I will own integration.", "delegation_ownership"),
        ("Reproduce the bug from the traceback and logs.", "debugging_evidence"),
        ("Verify with pytest and report the build result.", "verification"),
        ("Ορίστε κριτήρια αποδοχής και αναμενόμενη συμπεριφορά.", "scope_acceptance"),
        ("Κράτησε το πλαίσιο, τις αποφάσεις και την παράδοση.", "context_handoffs"),
        ("Κάνε ανάθεση με σαφή ιδιοκτησία και ενσωμάτωση.", "delegation_ownership"),
        ("Αναπαρήγαγε το σφάλμα από logs και traceback.", "debugging_evidence"),
        ("Τρέξε τα tests και επαλήθευσε το build.", "verification"),
    ],
)
def test_axiologisi_anagnorizei_agglika_kai_ellinika_candidate_cues(
    keimeno: str, diastasi: str
) -> None:
    """Αναγνωρίζει ελεγμένα αγγλικά και ελληνικά cues ως candidate signals."""
    arxika: dict[str, object] = {"deigmata": [ftiaxe_deigma("u-1", keimeno, "s-1")]}

    eyrimata = pare_eyrimata(axiologise_ergasia(arxika))

    assert any(eyrima["diastasi"] == diastasi for eyrima in eyrimata)


def test_axiologisi_agent_failure_cannot_be_attributed_to_human() -> None:
    """Agent/tool statements alone do not credit or blame the human developer."""
    arxika: dict[str, object] = {
        "deigmata": [
            ftiaxe_deigma(
                "a-1",
                "I skipped tests and implementation failed.",
                "s-1",
                "assistant",
                "response",
            ),
            ftiaxe_deigma(
                "t-1", "pytest failed with AssertionError", "s-1", "tool", "tool_result"
            ),
        ]
    }

    apotelesma = axiologise_ergasia(arxika)

    assert pare_eyrimata(apotelesma) == []
    assert pare_axiologisi(apotelesma)["diathesimi"] is False


def test_axiologisi_unrecognized_actor_attribution_is_ignored() -> None:
    """Role user με attribution μη ανθρώπινο ή άγνωστο δεν μετρά ως human evidence."""
    deigma = ftiaxe_deigma("u-agent", "Run pytest and report the result.", "s-1")
    deigma["actor"] = "agent"
    arxika: dict[str, object] = {"deigmata": [deigma]}

    apotelesma = axiologise_ergasia(arxika)

    assert pare_eyrimata(apotelesma) == []
    analysi = cast(dict[str, object], apotelesma["analysi"])
    assert analysi["egkyra_deigmata"] == 0


def test_axiologisi_quoted_markers_menoun_candidate_signals() -> None:
    """Marker μέσα σε quoted prompt παραμένει candidate και δεν δηλώνει επιτυχία."""
    apospasma = 'The old note said "run tests"; please inspect this issue.'
    arxika: dict[str, object] = {"deigmata": [ftiaxe_deigma("u-q", apospasma, "s-q")]}

    eyrimata = pare_eyrimata(axiologise_ergasia(arxika))

    assert len(eyrimata) == 1
    assert eyrimata[0]["katastasi"] == "candidate_only"
    assert "does not establish completion" in str(eyrimata[0]["keimeno"])
    assert eyrimata[0]["tekmiria"][0]["apospasma"] == apospasma


def test_axiologisi_rhto_skip_elegxou_dinei_conditional_growth_candidate() -> None:
    """Ρητό αίτημα παράλειψης tests δίνει υπό όρους πρόταση, όχι ισχυρισμό εκτέλεσης."""
    apospasma = "Do not run tests for this patch."
    arxika: dict[str, object] = {
        "deigmata": [ftiaxe_deigma("u-skip", apospasma, "s-skip")]
    }

    eyrimata = pare_eyrimata(axiologise_ergasia(arxika))
    eyrimata_anaptyksis = [
        eyrima for eyrima in eyrimata if eyrima["epipedo"] == "growth"
    ]

    assert len(eyrimata_anaptyksis) == 1
    assert eyrimata_anaptyksis[0]["katastasi"] == "candidate_only"
    assert "does not prove tests were skipped" in str(eyrimata_anaptyksis[0]["keimeno"])
    assert "If tests are out of scope" in str(eyrimata_anaptyksis[0]["protasi"])
    assert eyrimata_anaptyksis[0]["drastis"] == "human_prompt"


@pytest.mark.parametrize(
    ("keimeno", "anamenetai_growth"),
    [
        ("Do not skip the tests; run pytest and report the result.", False),
        ("Please don't skip tests.", False),
        ("Consider skipping tests.", False),
        ('The old note says "skip tests"; please inspect.', False),
        ("Μην παραλείψεις τα tests, τρέξε pytest.", False),
        ("Η παλιά οδηγία ήταν «παράλειψε τα tests».", False),
        ("Should we skip tests?", False),
        ("Μην τρέξεις τα tests για αυτό το patch.", True),
        ("Παράλειψε τα tests για αυτό το patch.", True),
    ],
)
def test_axiologisi_skip_growth_requires_clear_affirmative_instruction(
    keimeno: str, anamenetai_growth: bool
) -> None:
    """Μόνο ρητό, μη quoted affirmative skip cue δίνει growth candidate."""
    arxika: dict[str, object] = {"deigmata": [ftiaxe_deigma("u-s", keimeno, "s-s")]}

    eyrimata = pare_eyrimata(axiologise_ergasia(arxika))
    eyrimata_anaptyksis = [
        eyrima for eyrima in eyrimata if eyrima["epipedo"] == "growth"
    ]

    assert bool(eyrimata_anaptyksis) is anamenetai_growth


def test_axiologisi_einai_idempotent_se_epanalipsi() -> None:
    """Δεύτερη ανάλυση του ίδιου report δεν προσθέτει διπλό candidate finding."""
    arxika: dict[str, object] = {
        "deigmata": [ftiaxe_deigma("u-1", "Run pytest.", "s-1")]
    }

    proti_analysi = axiologise_ergasia(arxika)
    deuteri_analysi = axiologise_ergasia(proti_analysi)

    assert pare_eyrimata(proti_analysi) == pare_eyrimata(deuteri_analysi)
    assert cast(dict[str, object], deuteri_analysi["analysi"])["methodos"] == "rules"


def test_axiologisi_den_ypervainei_tria_growth_me_proyparxonta() -> None:
    """Τα rule growth actions συμμορφώνονται με το συνολικό όριο μαζί με εισερχόμενα."""
    arxika: dict[str, object] = {
        "deigmata": [ftiaxe_deigma("u-skip", "Do not run tests.", "s-skip")],
        "eyrimata": [
            {"id": "G1", "epipedo": "growth"},
            {"id": "G2", "epipedo": "growth"},
            {"id": "G3", "epipedo": "growth"},
            {"id": "G4", "epipedo": "growth"},
            {"id": "S1", "epipedo": "strength"},
            {"id": "S2", "epipedo": "strength"},
            {"id": "S3", "epipedo": "strength"},
            {"id": "S4", "epipedo": "strength"},
        ],
    }

    eyrimata = pare_eyrimata(axiologise_ergasia(arxika))
    eyrimata_anaptyksis = [
        eyrima for eyrima in eyrimata if eyrima["epipedo"] == "growth"
    ]
    eyrimata_isxyos = [eyrima for eyrima in eyrimata if eyrima["epipedo"] == "strength"]

    assert len(eyrimata_anaptyksis) == 3
    assert len(eyrimata_isxyos) == 3


def test_axiologisi_periorizei_evidence_kai_den_dinei_fake_score() -> None:
    """Περιορίζει τα evidence rows στα 600 και διατηρεί source coverage counts."""
    deigmata = [
        ftiaxe_deigma(
            f"u-{arithmos}", "Run pytest and report the result.", f"s-{arithmos}"
        )
        for arithmos in range(605)
    ]
    arxika: dict[str, object] = {
        "deigmata": deigmata,
        "kalypsi_analysi": {"epilegmena": 600, "diathesima": 605, "perikopi": True},
        "synola": {"minimata_xristi": 605},
    }

    apotelesma = axiologise_ergasia(arxika)
    kalypsi = cast(dict[str, object], apotelesma["kalypsi_analysi"])
    deigmata_apotelesmatos = cast(list[object], apotelesma["deigmata"])

    assert len(deigmata_apotelesmatos) == 600
    assert kalypsi == {"epilegmena": 600, "diathesima": 605, "perikopi": True}
    assert pare_axiologisi(apotelesma)["synoliko"] is None
    assert len(deigmata) == 605


def test_axiologisi_preserves_input_and_does_not_rewrite_full_metrics() -> None:
    """Επιστρέφει νέο mapping και αφήνει metrics και source rows ανέπαφα."""
    deigma = ftiaxe_deigma("u-1", "Run pytest and share the exact output.", "s-1")
    synola = {"synedries": 999, "minimata_xristi": 10000}
    arxika: dict[str, object] = {"deigmata": [deigma], "synola": synola}

    apotelesma = axiologise_ergasia(arxika)

    assert apotelesma is not arxika
    assert arxika == {"deigmata": [deigma], "synola": synola}
    assert apotelesma["synola"] is synola
    assert apotelesma["deigmata"] == [deigma]


def test_axiologisi_scorecard_exposes_calibration_gate_and_session_counts() -> None:
    """Score dimensions expose signal counts and explicit human-calibration gate."""
    arxika: dict[str, object] = {
        "deigmata": [
            ftiaxe_deigma("u-1", "Run pytest.", "s-1"),
            ftiaxe_deigma("u-2", "Run pytest.", "s-2"),
        ]
    }

    axiologisi = pare_axiologisi(axiologise_ergasia(arxika))
    gate = cast(dict[str, object], axiologisi["gate_vathmologias"])
    diastaseis = cast(list[dict[str, object]], axiologisi["diastaseis"])
    diastasi_epalitheusis = next(
        diastasi for diastasi in diastaseis if diastasi["id"] == "verification"
    )

    assert gate["energo"] is False
    assert gate["symfonia_anthropinon_aksiologiton"] is False
    assert axiologisi["diathesimi"] is False
    assert diastasi_epalitheusis["bathmos"] is None
    assert diastasi_epalitheusis["episodia"] == 2
    assert diastasi_epalitheusis["synedries_vathmologisimes"] == 0
    assert "calibrat" in str(diastasi_epalitheusis["aitia"]).lower()


def test_axiologisi_caps_findings_per_type_and_keeps_exact_reference_ids() -> None:
    """Περιορίζει findings και συνδέει κάθε citation με υπαρκτό row."""
    deigmata = [
        ftiaxe_deigma("u-scope", "Define acceptance criteria.", "s-1"),
        ftiaxe_deigma("u-context", "Carry the handoff context.", "s-2"),
        ftiaxe_deigma("u-delegate", "Delegate ownership; I will integrate.", "s-3"),
        ftiaxe_deigma("u-debug", "Reproduce with traceback and logs.", "s-4"),
        ftiaxe_deigma("u-verify", "Run pytest.", "s-5"),
        ftiaxe_deigma("u-skip", "Do not run tests.", "s-6"),
    ]
    arxika: dict[str, object] = {"deigmata": deigmata}

    eyrimata = pare_eyrimata(axiologise_ergasia(arxika))
    eyrimata_me_isxy = [
        eyrima for eyrima in eyrimata if eyrima["epipedo"] == "strength"
    ]
    eyrimata_anaptyksis = [
        eyrima for eyrima in eyrimata if eyrima["epipedo"] == "growth"
    ]
    id_deigmaton = {deigma["id"] for deigma in deigmata}

    assert len(eyrimata_me_isxy) <= 3
    assert len(eyrimata_anaptyksis) <= 3
    assert all(
        tekmirio["id"] in id_deigmaton
        for eyrima in eyrimata
        for tekmirio in eyrima["tekmiria"]
    )


def test_axiologisi_avoids_id_collision_with_existing_findings() -> None:
    """Το νέο assessment ID δεν επαναχρησιμοποιεί υπάρχον A001."""
    arxika: dict[str, object] = {
        "deigmata": [ftiaxe_deigma("u-1", "Run pytest.", "s-1")],
        "eyrimata": [{"id": "A001", "epipedo": "strength"}],
    }

    eyrimata = pare_eyrimata(axiologise_ergasia(arxika))

    assert eyrimata[0]["id"] == "A001"
    assert eyrimata[1]["id"] == "A002"
