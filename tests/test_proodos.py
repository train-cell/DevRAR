"""Synthetic report-comparison contract tests."""

import pytest

from devrar.proodos import sygkrine_anafores


def test_sygkrisi_me_rito_all_authors_scope() -> None:
    """Το ρητό null author σημαίνει all authors, ενώ απόν scope μένει unknown."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    trexousa = _anafora("2026-02-01", 2, 6)
    proigoumeni["scope_git"]["author"] = None
    trexousa["scope_git"]["author"] = None
    assert sygkrine_anafores(trexousa, proigoumeni)["katastasi"] == "compatible"
    trexousa["scope_git"] = {}
    assert sygkrine_anafores(trexousa, proigoumeni)["katastasi"] == "missing"


def _anafora(imerominia: str, synedries: int, prompts: int) -> dict[str, object]:
    """Δημιουργεί μικρή συνθετική αναφορά για ελεγχόμενη σύγκριση."""
    return {
        "ekdosi_sximatos": "1",
        "leitourgia": "live",
        "analysi": {"rubrika": "0.1"},
        "periodos": {
            "apo": imerominia,
            "eos": imerominia,
            "zoni": "Europe/Athens",
        },
        "scope_git": {"author": "synthetic-author", "repositories": []},
        "piges": [{"onoma": "Synthetic CLI", "katastasi": "ok"}],
        "kalypsi_analysi": {"perikopi": False},
        "synola": {"synedries": synedries, "minimata_xristi": prompts},
        "metrika_ergasias": {
            "epeisodia": [
                {
                    "id": f"ep-{index}",
                    "pigi": "Synthetic CLI",
                    "synedria": f"s-{index}",
                    "tests_passed": 2,
                    "tests_failed": 0,
                    "tests_skipped": 0,
                    "prompts": 3,
                    "tekmiria": [],
                }
                for index in range(synedries)
            ]
        },
        "axiologisi": {
            "diastaseis": [
                {
                    "id": "verification",
                    "paratiriseis": prompts,
                    "tekmiria": [],
                }
            ]
        },
    }


def test_sygkrisi_den_ypothetei_idio_repo_scope_i_mode() -> None:
    """Διαφορετικά repos/demo ή άγνωστο repository scope αποκλείουν progress delta."""
    prin = _anafora("2026-01-01", 1, 3)
    tora = _anafora("2026-02-01", 2, 6)
    tora["scope_git"]["repositories"] = ["synthetic-repo-id"]
    assert sygkrine_anafores(tora, prin)["katastasi"] == "incompatible"
    del tora["scope_git"]["repositories"]
    assert sygkrine_anafores(tora, prin)["katastasi"] == "missing"
    tora["scope_git"]["repositories"] = []
    tora["leitourgia"] = "demo"
    assert sygkrine_anafores(tora, prin)["katastasi"] == "incompatible"


def test_sygkrine_anafores_dinei_deltas_xoris_baseline_apospasmata() -> None:
    """Ελέγχει συμβατές περιόδους, deltas και απόκρυψη baseline excerpts."""
    proigoumeni = _anafora("2026-01-01", 2, 6)
    proigoumeni["idiotika"] = {"keimeno": "private baseline text"}
    trexousa = _anafora("2026-02-01", 3, 9)

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    synedries = sygkrisi["metrika"]["synola.synedries"]
    assert synedries["katastasi"] == "compatible"
    assert synedries["delta"] == 1
    assert synedries["pososto"] == 50.0
    assert "private baseline text" not in repr(sygkrisi)


def test_sygkrine_anafores_eksigei_asyvatotita_kai_miden_baseline() -> None:
    """Ελέγχει incompatibility, μηδενικό baseline και άγνωστο metric."""
    proigoumeni = _anafora("2026-01-01", 0, 6)
    proigoumeni["periodos"] = {
        "apo": "2026-01-01",
        "eos": "2026-01-01",
        "zoni": "UTC",
    }
    trexousa = _anafora("2026-02-01", 2, 9)

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    synedries = sygkrisi["metrika"]["synola.synedries"]
    assert synedries["katastasi"] == "incompatible"
    assert synedries["delta"] is None
    assert synedries["pososto"] is None
    assert sygkrisi["symvatotita"]["zoni"]["katastasi"] == "incompatible"


def test_sygkrine_anafores_null_percentage_for_zero_baseline() -> None:
    """Ελέγχει μηδενικό baseline σε αλλιώς συμβατή σύγκριση."""
    proigoumeni = _anafora("2026-01-01", 0, 0)
    trexousa = _anafora("2026-02-01", 2, 3)

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    synedries = sygkrisi["metrika"]["synola.synedries"]
    assert synedries["katastasi"] == "compatible"
    assert synedries["delta"] == 2
    assert synedries["pososto"] is None


def test_sygkrine_anafores_reports_overlapping_periods() -> None:
    """Ελέγχει ότι οι επικαλυπτόμενες ημερομηνίες αποκλείουν delta."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    proigoumeni["periodos"] = {
        "apo": "2026-01-01",
        "eos": "2026-02-01",
        "zoni": "Europe/Athens",
    }
    trexousa = _anafora("2026-02-01", 2, 6)

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    assert sygkrisi["katastasi"] == "overlapping"
    assert sygkrisi["metrika"]["synola.synedries"]["delta"] is None


def test_sygkrine_anafores_keeps_tests_unknown_without_episodes() -> None:
    """Ελέγχει ότι μη καταχωρημένα test outcomes δεν μετατρέπονται σε μηδέν."""
    proigoumeni = _anafora("2026-01-01", 0, 0)
    proigoumeni["metrika_ergasias"]["epeisodia"] = []
    trexousa = _anafora("2026-02-01", 0, 0)
    trexousa["metrika_ergasias"]["epeisodia"] = []

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    tests = sygkrisi["metrika"]["episodia.tests_failed"]
    assert tests["katastasi"] == "missing"
    assert tests["trexousa"] is None
    assert tests["proigoumeni"] is None


def test_sygkrine_anafores_marks_partial_and_truncated_coverage() -> None:
    """Ελέγχει per-metric coverage για partial και truncated reports."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    trexousa = _anafora("2026-02-01", 2, 6)
    trexousa["piges"] = [{"onoma": "Synthetic CLI", "katastasi": "partial"}]

    partial = sygkrine_anafores(trexousa, proigoumeni)
    assert partial["symvatotita"]["kalypsi"]["katastasi"] == "partial"
    assert partial["metrika"]["synola.synedries"]["katastasi"] == "partial"
    assert partial["metrika"]["synola.synedries"]["delta"] == 1

    trexousa["piges"] = [{"onoma": "Synthetic CLI", "katastasi": "ok"}]
    trexousa["kalypsi_analysi"] = {"perikopi": True}
    truncated = sygkrine_anafores(trexousa, proigoumeni)
    assert truncated["symvatotita"]["kalypsi"]["katastasi"] == "truncated"
    assert (
        truncated["metrika"]["synola.synedries"]["kalypsi"]["trexousa"] == "truncated"
    )


@pytest.mark.parametrize("katastasi_git", ["partial", "missing", "unsupported"])
def test_sygkrine_anafores_includes_git_delta_coverage(
    katastasi_git: str,
) -> None:
    """Git delta coverage limits also appear in comparison coverage."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    trexousa = _anafora("2026-02-01", 2, 6)
    trexousa["git_diafores"] = {"katastasi": katastasi_git}

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    assert sygkrisi["symvatotita"]["kalypsi"]["katastasi"] == "partial"
    assert sygkrisi["metrika"]["synola.synedries"]["kalypsi"]["trexousa"] == "partial"


@pytest.mark.parametrize("git_delta", [None, "malformed"])
def test_sygkrine_anafores_marks_malformed_present_git_delta_partial(
    git_delta: object,
) -> None:
    """Present Git delta without a valid status is unknown coverage."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    trexousa = _anafora("2026-02-01", 2, 6)
    trexousa["git_diafores"] = git_delta

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    assert sygkrisi["symvatotita"]["kalypsi"]["katastasi"] == "partial"


def test_sygkrine_anafores_allows_ai_only_report_without_git_delta() -> None:
    """Missing optional Git section does not degrade AI-only coverage."""
    trexousa = _anafora("2026-02-01", 2, 6)
    proigoumeni = _anafora("2026-01-01", 1, 3)

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    assert sygkrisi["symvatotita"]["kalypsi"]["katastasi"] == "compatible"


def test_sygkrine_anafores_reports_mismatched_scope_schema_rubric_sources() -> None:
    """Ελέγχει ότι mismatch scope/schema/rubric/source set ακυρώνει deltas."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    trexousa = _anafora("2026-02-01", 2, 6)
    trexousa["ekdosi_sximatos"] = "2"
    trexousa["analysi"] = {"rubrika": "0.2"}
    trexousa["scope_git"] = {"author": "another-author"}
    trexousa["piges"] = [{"onoma": "Other source", "katastasi": "ok"}]

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    for key in ("ekdosi_sximatos", "rubrika", "piges", "scope_git_author"):
        assert sygkrisi["symvatotita"][key]["katastasi"] == "incompatible"
    assert sygkrisi["metrika"]["synola.synedries"]["delta"] is None


def test_sygkrine_anafores_reports_missing_and_invalid_metadata() -> None:
    """Ελέγχει missing source/scope and invalid date metadata without guessing."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    trexousa = _anafora("invalid-date", 2, 6)
    del trexousa["piges"]
    del trexousa["scope_git"]
    del trexousa["ekdosi_sximatos"]
    del trexousa["analysi"]

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    assert sygkrisi["katastasi"] == "missing"
    assert sygkrisi["symvatotita"]["periodos"]["katastasi"] == "missing"
    assert sygkrisi["symvatotita"]["piges"]["katastasi"] == "missing"
    assert sygkrisi["symvatotita"]["rubrika"]["katastasi"] == "missing"
    assert sygkrisi["symvatotita"]["scope_git_author"]["katastasi"] == "missing"


def test_sygkrine_anafores_uses_analyzed_episode_cues_and_missing_coverage() -> None:
    """Ελέγχει analyzer episode shape και missing analysis coverage status."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    trexousa = _anafora("2026-02-01", 2, 6)
    del trexousa["piges"]
    del trexousa["kalypsi_analysi"]
    trexousa["epeisodia_ergasias"] = {
        "paratiriseis": [
            {
                "katastasi": "observed_success",
                "metrisi": {"tests_passed": 2, "tests_failed": 0, "tests_skipped": 1},
            }
        ]
    }
    trexousa["axiologisi"] = {"diastaseis": [{"id": "scope", "paratiriseis": 4}]}

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    assert sygkrisi["symvatotita"]["kalypsi"]["katastasi"] == "missing"
    assert sygkrisi["metrika"]["episodia.episodes_observed_success"]["trexousa"] == 1
    assert sygkrisi["metrika"]["episodia.tests_passed"]["trexousa"] == 2
    assert sygkrisi["metrika"]["episodia.workflow_cues"]["trexousa"] == 4


def test_sygkrine_anafores_filters_malformed_report_fields() -> None:
    """Ελέγχει malformed sequence/mapping fields ως missing και nullable."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    trexousa = _anafora("2026-02-01", 2, 6)
    trexousa["piges"] = "invalid"
    trexousa["scope_git"] = "invalid"
    trexousa["synola"] = "invalid"
    trexousa["metrika_ergasias"] = {"epeisodia": "invalid"}
    trexousa["periodos"] = "invalid"
    trexousa["analysi"] = "invalid"

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    assert sygkrisi["katastasi"] == "missing"
    assert sygkrisi["metrika"]["synola.synedries"]["katastasi"] == "missing"
    assert sygkrisi["metrika"]["episodia.tests_passed"]["trexousa"] is None


def test_sygkrine_anafores_marks_missing_null_metric_values() -> None:
    """Ελέγχει known report but unavailable token count as missing metric."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    trexousa = _anafora("2026-02-01", 2, 6)
    trexousa["synola"]["tokens"] = None

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    tokens = sygkrisi["metrika"]["synola.tokens"]
    assert tokens["katastasi"] == "missing"
    assert tokens["trexousa"] is None
    assert tokens["delta"] is None


def test_sygkrine_anafores_uses_source_partial_coverage_status() -> None:
    """Ελέγχει partial source status και retains subset-only delta wording."""
    proigoumeni = _anafora("2026-01-01", 1, 3)
    trexousa = _anafora("2026-02-01", 2, 6)
    trexousa["piges"] = [{"onoma": "Synthetic CLI", "katastasi": "missing"}]

    sygkrisi = sygkrine_anafores(trexousa, proigoumeni)

    synedries = sygkrisi["metrika"]["synola.synedries"]
    assert synedries["katastasi"] == "partial"
    assert "recorded subsets" in synedries["aitia"]
