"""Ελέγχει τα synthetic event samples και τη μη βαθμολογημένη αξιολόγηση."""

from devrar.deigma import fortose_deigma


def test_synthetikes_diastaseis_menoun_xoris_vathmo() -> None:
    """Οι πέντε rubric dimensions παραμένουν χωρίς επινοημένο grade."""
    dedomena = fortose_deigma()
    axiologisi = dedomena["axiologisi"]

    assert axiologisi["diathesimi"] is False
    assert axiologisi["synoliko"] is None
    assert len(axiologisi["diastaseis"]) == 5
    assert {eggrafi["onoma"] for eggrafi in axiologisi["diastaseis"]} == {
        "Scope & acceptance",
        "Context & handoffs",
        "Delegation & ownership",
        "Debugging & evidence",
        "Verification & completion",
    }
    assert all(eggrafi["bathmos"] is None for eggrafi in axiologisi["diastaseis"])
    assert all(
        isinstance(eggrafi["episodia"], int) for eggrafi in axiologisi["diastaseis"]
    )
    assert all(
        isinstance(eggrafi["tekmiria"], list) for eggrafi in axiologisi["diastaseis"]
    )


def test_synthetika_deigmata_akolouthoun_symfonimeni_domi() -> None:
    """Τα bounded event rows έχουν κανονικοποιημένα IDs, roles και provenance."""
    dedomena = fortose_deigma()
    deigmata = dedomena["deigmata"]
    kleidia = {
        "id",
        "pigi",
        "synedria",
        "rolos",
        "eidos",
        "keimeno",
        "locator",
        "imerominia",
    }

    assert 3 <= len(deigmata) <= 12
    assert all(set(eggrafi) == kleidia for eggrafi in deigmata)
    assert len({eggrafi["synedria"] for eggrafi in deigmata}) >= 3
    assert {eggrafi["rolos"] for eggrafi in deigmata} <= {"user", "assistant", "tool"}
    assert {eggrafi["eidos"] for eggrafi in deigmata} == {
        "prompt",
        "response",
        "tool_call",
        "tool_result",
    }
    assert all(
        eggrafi["pigi"] and eggrafi["locator"] and eggrafi["keimeno"]
        for eggrafi in deigmata
    )
    assert all(eggrafi["imerominia"].startswith("2026-10-") for eggrafi in deigmata)
    piges = {eggrafi["onoma"] for eggrafi in dedomena["piges"]}
    assert {eggrafi["pigi"] for eggrafi in deigmata} <= piges


def test_synthetiki_kalypsi_analisis_exei_symfonimeni_domi() -> None:
    """Η κάλυψη δηλώνει επιλεγμένα/διαθέσιμα events και αν έγινε περικοπή."""
    dedomena = fortose_deigma()
    kalypsi = dedomena["kalypsi_analysi"]

    assert set(kalypsi) == {"epilegmena", "diathesima", "perikopi"}
    assert kalypsi["epilegmena"] == len(dedomena["deigmata"])
    assert kalypsi["diathesima"] == len(dedomena["deigmata"])
    assert kalypsi["perikopi"] is False
    assert "analysiscoverage" not in dedomena


def test_synthetika_eyrimata_exoun_context_kai_antitheta_stoixeia() -> None:
    """Τα findings διαχωρίζουν evidence, responsibility και limitations."""
    dedomena = fortose_deigma()
    for eyrima in dedomena["eyrimata"]:
        assert eyrima["eythyni"]
        assert eyrima["vevaiotita"] in {"high", "medium", "low"}
        assert eyrima["enallaktiki"]
        assert eyrima["antitheta"]
