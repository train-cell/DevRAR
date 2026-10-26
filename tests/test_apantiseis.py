from __future__ import annotations

from devrar.apantiseis import KanalApantisis, SyllogistisCodexApantiseon


def prosthese_apantisi(
    syllogistis: SyllogistisCodexApantiseon,
    *,
    synedria: str = "s1",
    turn_id: str | None = "t1",
    kanal: KanalApantisis = "response_item",
    keimeno: str = "same reply",
    tautotita: str | None = None,
    chronos: str | None = None,
    modelo: str | None = "gpt-test",
    locator: str = "codex.jsonl:1",
) -> None:
    """Προσθέτει ένα synthetic candidate με metadata χαμηλής ευαισθησίας."""
    syllogistis.prosthese(
        synedria,
        turn_id,
        kanal,
        keimeno,
        tautotita,
        chronos,
        "2026-10-25",
        modelo,
        locator,
    )


def test_apantiseis_max_multiplicity_prefer_canonical_and_keep_turns() -> None:
    """Κρατά δύο canonical repeats, dedupes channels και χωρίζει turns."""
    syllogistis = SyllogistisCodexApantiseon()
    prosthese_apantisi(syllogistis, tautotita="canonical-a")
    prosthese_apantisi(syllogistis, tautotita="canonical-b")
    prosthese_apantisi(syllogistis, kanal="agent_message")
    prosthese_apantisi(syllogistis, kanal="task_complete")
    prosthese_apantisi(syllogistis, turn_id="t2")

    apotelesma = syllogistis.synopsi()

    assert apotelesma.plithos == 3
    assert apotelesma.amfigies == 0
    assert [apantisi.kanal for apantisi in apotelesma.candidates] == [
        "response_item",
        "response_item",
        "response_item",
    ]


def test_apantiseis_timestamp_fingerprint_kai_secret_redaction() -> None:
    """Timestamp dedupes same-channel copies and stores only redacted excerpt."""
    syllogistis = SyllogistisCodexApantiseon()
    prosthese_apantisi(
        syllogistis,
        tautotita=None,
        chronos="2026-10-25T10:00:00Z",
        keimeno="Bearer secret-token",
    )
    prosthese_apantisi(
        syllogistis,
        tautotita=None,
        chronos="2026-10-25T10:00:00Z",
        keimeno="Bearer secret-token",
    )

    apotelesma = syllogistis.synopsi()

    assert apotelesma.plithos == 1
    assert apotelesma.candidates[0].keimeno == "Bearer [REDACTED]"
    assert "secret-token" not in apotelesma.candidates[0].keimeno


def test_apantiseis_xoris_turn_id_dilonei_ambiguous_xoris_dedup() -> None:
    """Χωρίς turn linkage διατηρεί candidates και δηλώνει uncertainty."""
    syllogistis = SyllogistisCodexApantiseon()
    prosthese_apantisi(syllogistis, turn_id=None, tautotita="item-1")
    prosthese_apantisi(
        syllogistis, turn_id=None, kanal="agent_message", tautotita="event-1"
    )

    apotelesma = syllogistis.synopsi()

    assert apotelesma.plithos == 2
    assert apotelesma.amfigies == 1
    assert apotelesma.montela_amfiga == {"gpt-test"}


def test_apantiseis_different_sessions_den_sygxonevontai() -> None:
    """Ίδιο κείμενο και turn key σε άλλες sessions παραμένει ξεχωριστό."""
    syllogistis = SyllogistisCodexApantiseon()
    prosthese_apantisi(syllogistis, synedria="s1", tautotita="a1")
    prosthese_apantisi(syllogistis, synedria="s2", tautotita="a2")

    apotelesma = syllogistis.synopsi()

    assert apotelesma.plithos == 2
    assert apotelesma.amfigies == 0


def test_apantiseis_same_channel_without_identity_is_ambiguous() -> None:
    """Δεν εκτιμά multiplicity όταν το ίδιο channel στερείται ID και ώρας."""
    syllogistis = SyllogistisCodexApantiseon()
    prosthese_apantisi(syllogistis, tautotita=None, chronos=None)
    prosthese_apantisi(syllogistis, tautotita=None, chronos=None)

    apotelesma = syllogistis.synopsi()

    assert apotelesma.plithos == 2
    assert apotelesma.amfigies == 1
