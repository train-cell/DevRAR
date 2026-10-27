"""Συμπεριφορικοί έλεγχοι για τα streaming work metrics."""

from typing import cast

from devrar.metrika import SyllogistisMetrikon, _exagage_tekmirio_tests
from devrar.symvanta import SymvanErgasias


def dimiourgia_event(
    *,
    event_id: str,
    source: str = "codex",
    session: str = "s1",
    timestamp: str | None = None,
    role: str = "user",
    kind: str = "prompt",
    text: str = "prompt text",
    tool: str | None = None,
    exit_code: int | None = None,
) -> SymvanErgasias:
    """Δημιουργεί πλήρες transient event σύμφωνα με το κοινό contract."""
    return {
        "id": event_id,
        "pigi": source,
        "synedria": session,
        "goneas": None,
        "chronos": timestamp,
        "rolos": role,  # type: ignore[typeddict-item]
        "eidos": kind,  # type: ignore[typeddict-item]
        "keimeno": text,
        "locator": f"{event_id}:1",
        "ergaleio": tool,
        "montelo": None,
        "kodikos_exodou": exit_code,
    }


def epeisodia_tou(result: dict[str, object]) -> list[dict[str, object]]:
    """Τυποποιεί τη λίστα episode του public report payload."""
    return cast(list[dict[str, object]], result["epeisodia"])


def tekmiria_tou(episode: dict[str, object]) -> list[dict[str, str]]:
    """Τυποποιεί τα bounded citations ενός episode."""
    return cast(list[dict[str, str]], episode["tekmiria"])


def synopsi_tests_tou(result: dict[str, object]) -> dict[str, object]:
    """Τυποποιεί το συνολικό test summary του report."""
    return cast(dict[str, object], result["test_summary"])


def test_kathysterimena_checks_den_xanontai_apo_citation_cap() -> None:
    """Μετά από πολλά prompts, επιτυχία και αποτυχία κρατούν exact citations."""
    metriko = SyllogistisMetrikon()
    for deiktis in range(20):
        metriko.prosthese(dimiourgia_event(event_id=f"p-{deiktis}"))
    for deiktis in range(7):
        metriko.prosthese(
            dimiourgia_event(
                event_id=f"r-{deiktis}",
                role="tool",
                kind="tool_result",
                text="=== 2 passed in 0.1s ===",
                exit_code=0,
            )
        )
    metriko.prosthese(
        dimiourgia_event(
            event_id="failure",
            role="tool",
            kind="tool_result",
            text="=== 1 failed in 0.1s ===",
            exit_code=1,
        )
    )
    for deiktis in range(6):
        metriko.prosthese(
            dimiourgia_event(
                event_id=f"f-{deiktis}",
                role="tool",
                kind="tool_result",
                text="=== 1 failed in 0.1s ===",
                exit_code=1,
            )
        )
    epeisodio = epeisodia_tou(metriko.apotelesma())[0]
    tekmiria = epeisodio["tekmiria"]
    assert len(tekmiria) == 5
    assert any(eggrafi.get("kodikos_exodou") == 1 for eggrafi in tekmiria)
    assert any(eggrafi.get("kodikos_exodou") == 0 for eggrafi in tekmiria)


def test_tap_description_xoris_dash_skip_kai_todo() -> None:
    """Το TAP δέχεται optional dash/number και κρατά TODO χωριστά από failures."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(
        dimiourgia_event(
            event_id="tap-directives",
            role="tool",
            kind="tool_result",
            text=(
                "TAP version 13\n1..5\nok 1 description\nok 2 # SKIP unavailable\n"
                "not ok 3 # TODO pending\nok 4 # todo bonus\nnot ok 5 broken"
            ),
        )
    )
    assert metriko.apotelesma()["test_summary"] == {
        "status": "observed",
        "passed": 1,
        "failed": 1,
        "skipped": 1,
        "todo": 2,
    }
    metriko = SyllogistisMetrikon()
    metriko.prosthese(
        dimiourgia_event(
            event_id="tap-unnumbered",
            role="tool",
            kind="tool_result",
            text="ok\nnot ok\nOK invalid-case\n  ok 1 nested-child",
        )
    )
    assert metriko.apotelesma()["test_summary"]["passed"] == 1
    assert metriko.apotelesma()["test_summary"]["failed"] == 1


def test_ora_athens_apo_utc_kai_dst() -> None:
    """Η τοπική ώρα μετατρέπει σωστά UTC και το DST της Αθήνας."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(
        dimiourgia_event(event_id="a", timestamp="2026-01-15T10:00:00+00:00")
    )
    metriko.prosthese(
        dimiourgia_event(event_id="b", timestamp="2026-07-15T10:00:00+00:00")
    )

    apotelesma = metriko.apotelesma()

    assert apotelesma["ora"] == [
        {"ora": ora, "prompts": 1 if ora in {12, 13} else 0} for ora in range(24)
    ]
    assert apotelesma["imeres"] == [
        {"imerominia": "2026-01-15", "prompts": 1},
        {"imerominia": "2026-07-15", "prompts": 1},
    ]


def test_interval_estimate_is_union_of_bounded_pairs_across_sessions() -> None:
    """Παράλληλα session spans μετριούνται ως union χωρίς synthetic tail."""
    metriko = SyllogistisMetrikon(idle_minutes=15)
    metriko.prosthese(
        dimiourgia_event(event_id="a", timestamp="2026-01-01T10:00:00+00:00")
    )
    metriko.prosthese(
        dimiourgia_event(
            event_id="b", session="s2", timestamp="2026-01-01T10:05:00+00:00"
        )
    )
    metriko.prosthese(
        dimiourgia_event(event_id="c", timestamp="2026-01-01T10:10:00+00:00")
    )
    metriko.prosthese(
        dimiourgia_event(
            event_id="d",
            timestamp="2026-01-01T11:00:00+00:00",
            role="assistant",
            kind="response",
        )
    )

    assert metriko.apotelesma()["interval_estimate_minutes"] == 10


def test_out_of_order_overlapping_session_intervals_are_unioned() -> None:
    """Out-of-order events και overlapping streams δεν διπλομετρούν spans."""
    metriko = SyllogistisMetrikon(idle_minutes=15)
    for event_id, session, minute in (
        ("a2", "s1", 10),
        ("b2", "s2", 15),
        ("a1", "s1", 0),
        ("b1", "s2", 5),
    ):
        metriko.prosthese(
            dimiourgia_event(
                event_id=event_id,
                session=session,
                timestamp=f"2026-01-01T10:{minute:02d}:00+00:00",
            )
        )

    assert metriko.apotelesma()["interval_estimate_minutes"] == 15


def test_mixed_roles_count_only_human_prompts_and_retain_bounded_citations() -> None:
    """Οι activity counts χωρίζουν prompts/tool events και excerpt cap είναι 500."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(dimiourgia_event(event_id="p"))
    metriko.prosthese(
        dimiourgia_event(
            event_id="c", role="assistant", kind="tool_call", tool="pytest"
        )
    )
    metriko.prosthese(
        dimiourgia_event(
            event_id="r",
            role="tool",
            kind="tool_result",
            text="x" * 700,
            exit_code=0,
        )
    )

    apotelesma = metriko.apotelesma()
    epeisodio = epeisodia_tou(apotelesma)[0]

    assert epeisodio["prompts"] == 1
    assert epeisodio["tool_calls"] == 1
    assert epeisodio["tool_results"] == 1
    citations = tekmiria_tou(epeisodio)
    assert len(citations[-1]["apospasma"]) == 500
    assert citations[-1]["locator"] == "r:1"


def test_explicit_pytest_result_counts_and_event_id_deduplication() -> None:
    """Explicit pytest summary contributes once even if its event is repeated."""
    metriko = SyllogistisMetrikon()
    event = dimiourgia_event(
        event_id="result",
        role="tool",
        kind="tool_result",
        text="================ 3 passed, 1 failed, 2 skipped in 1.2s ================",
        exit_code=1,
    )
    metriko.prosthese(event)
    metriko.prosthese(event)

    apotelesma = metriko.apotelesma()

    assert apotelesma["test_summary"] == {
        "status": "observed",
        "passed": 3,
        "failed": 1,
        "skipped": 2,
    }
    assert epeisodia_tou(apotelesma)[0]["exit_failure"] == 1


def test_repeated_test_summary_in_one_event_counts_once_but_distinct_runs_count() -> (
    None
):
    """Identical summaries in one output collapse; different reruns add counts."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(
        dimiourgia_event(
            event_id="runs",
            role="tool",
            kind="tool_result",
            text=(
                "==== 2 passed in 0.1s ====\n"
                "==== 2 passed in 0.1s ====\n"
                "==== 3 passed in 0.2s ====\n"
                "1..2\nok 1 - first\nok 2 - second"
            ),
            exit_code=0,
        )
    )

    result = metriko.apotelesma()

    assert result["test_summary"] == {
        "status": "observed",
        "passed": 5,
        "failed": 0,
        "skipped": 0,
    }


def test_exit_code_tracks_command_failure_without_inventing_test_failures() -> None:
    """Recorded nonzero exit is command failure; absent test summary stays null."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(
        dimiourgia_event(
            event_id="failed-command",
            role="tool",
            kind="tool_result",
            text="command returned nonzero",
            exit_code=1,
        )
    )

    result = metriko.apotelesma()
    episode = epeisodia_tou(result)[0]

    assert synopsi_tests_tou(result)["passed"] is None
    assert synopsi_tests_tou(result)["failed"] is None
    assert episode["exit_failure"] == 1
    assert episode["tests_status"] == "no_observed_tests"


def test_unittest_and_tap_results_are_recognized_as_explicit_formats() -> None:
    """Οι γνωστές unittest και TAP σύνοψεις καταγράφονται συντηρητικά."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(
        dimiourgia_event(
            event_id="u",
            role="tool",
            kind="tool_result",
            text="Ran 4 tests in 0.10s\n\nOK (skipped=1)",
            exit_code=0,
        )
    )
    metriko.prosthese(
        dimiourgia_event(
            event_id="t",
            role="tool",
            kind="tool_result",
            text="1..3\nok 1 - one\nnot ok 2 - two\nok 3 - three # SKIP later",
            exit_code=1,
        )
    )

    synopsi = metriko.apotelesma()["test_summary"]
    assert synopsi == {"status": "observed", "passed": 4, "failed": 1, "skipped": 2}


def test_unittest_failed_summary_counts_failures_errors_and_skips() -> None:
    """FAILED unittest summary separates passed, failed and skipped executions."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(
        dimiourgia_event(
            event_id="unittest-failed",
            role="tool",
            kind="tool_result",
            text=("Ran 4 tests in 0.10s\n\nFAILED (failures=1, errors=1, skipped=1)"),
            exit_code=1,
        )
    )

    result = metriko.apotelesma()
    episode = epeisodia_tou(result)[0]

    assert result["test_summary"] == {
        "status": "observed",
        "passed": 1,
        "failed": 2,
        "skipped": 1,
    }
    citations = tekmiria_tou(episode)
    assert "FAILED (failures=1, errors=1, skipped=1)" in citations[0]["apospasma"]


def test_repeated_identical_unittest_summary_in_one_event_counts_once() -> None:
    """Ίδια unittest summary που επαναλαμβάνεται στο output μετρά μία φορά."""
    metriko = SyllogistisMetrikon()
    repeated = "Ran 2 tests in 0.1s\nOK"
    metriko.prosthese(
        dimiourgia_event(
            event_id="duplicate-unittest",
            role="tool",
            kind="tool_result",
            text=f"{repeated}\n\n{repeated}",
            exit_code=0,
        )
    )

    assert synopsi_tests_tou(metriko.apotelesma())["passed"] == 2


def test_unknown_timestamps_and_malformed_test_output_stay_null() -> None:
    """Άγνωστα timestamps και αόριστα output δεν μετατρέπονται σε μηδενικά."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(dimiourgia_event(event_id="a", timestamp=None))
    metriko.prosthese(dimiourgia_event(event_id="b", timestamp="2026-01-01T10:00:00"))
    metriko.prosthese(
        dimiourgia_event(
            event_id="r", role="tool", kind="tool_result", text="tests probably passed"
        )
    )

    apotelesma = metriko.apotelesma()

    assert apotelesma["timestamps_unknown"] == 3
    assert apotelesma["interval_estimate_minutes"] is None
    assert apotelesma["test_summary"] == {
        "status": "no_observed_tests",
        "passed": None,
        "failed": None,
        "skipped": None,
    }


def test_unrecognized_output_has_no_test_summary_citation() -> None:
    """Μη αναγνωρισμένο output δεν αποδίδεται ως test-summary evidence."""
    assert _exagage_tekmirio_tests("tests probably passed") is None


def test_invalid_timezone_and_idle_bounds_are_rejected() -> None:
    """Μη έγκυρες IANA ζώνες και thresholds απορρίπτονται ρητά."""
    import pytest

    with pytest.raises(ValueError, match="idle_minutes"):
        SyllogistisMetrikon(idle_minutes=0)
    with pytest.raises(ValueError, match="ζώνη ώρας"):
        SyllogistisMetrikon(zoni="Mars/Olympus")


def test_malformed_and_naive_timestamps_are_unknown() -> None:
    """Μη parseable και timezone-naive timestamps δεν γίνονται ακριβής ώρα."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(dimiourgia_event(event_id="malformed", timestamp="not-a-date"))
    metriko.prosthese(
        dimiourgia_event(event_id="naive", timestamp="2026-01-01T10:00:00")
    )

    result = metriko.apotelesma()

    assert result["timestamps_unknown"] == 2
    assert result["interval_estimate_minutes"] is None


def test_exit_codes_are_recorded_without_inventing_test_counts() -> None:
    """Exit codes are evidence of command outcome without test-result text."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(
        dimiourgia_event(
            event_id="ok", role="tool", kind="tool_result", text="", exit_code=0
        )
    )
    metriko.prosthese(
        dimiourgia_event(
            event_id="err",
            role="tool",
            kind="tool_result",
            text="error",
            exit_code=2,
        )
    )

    epeisodio = epeisodia_tou(metriko.apotelesma())[0]
    assert (epeisodio["exit_success"], epeisodio["exit_failure"]) == (1, 1)
    assert (epeisodio["tests_passed"], epeisodio["tests_failed"]) == (None, None)


def test_assistant_claim_is_not_test_result_evidence() -> None:
    """Assistant text claiming tests passed cannot establish executed outcomes."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(
        dimiourgia_event(
            event_id="claim",
            role="assistant",
            kind="response",
            text="All tests passed: 20 passed.",
        )
    )

    result = metriko.apotelesma()
    episode = epeisodia_tou(result)[0]

    assert result["test_summary"] == {
        "status": "no_observed_tests",
        "passed": None,
        "failed": None,
        "skipped": None,
    }
    assert episode["tests_status"] == "no_observed_tests"
    assert episode["exit_success"] == 0


def test_exit_code_on_non_tool_event_is_not_command_outcome() -> None:
    """Exit metadata outside tool_result δεν αποδίδεται σε command outcome."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(
        dimiourgia_event(
            event_id="assistant-code",
            role="assistant",
            kind="response",
            exit_code=0,
        )
    )

    episode = epeisodia_tou(metriko.apotelesma())[0]
    assert episode["exit_success"] == 0
    assert episode["exit_failure"] == 0


def test_episode_and_citation_caps_preserve_full_activity_counts() -> None:
    """Η περικοπή περιορίζει evidence ενώ οι πλήρεις event μετρήσεις συνεχίζουν."""
    metriko = SyllogistisMetrikon()
    for index in range(7):
        metriko.prosthese(dimiourgia_event(event_id=str(index), text=f"prompt {index}"))

    result = metriko.apotelesma()
    episode = epeisodia_tou(result)[0]

    assert result["events"] == 7
    assert episode["prompts"] == 7
    assert episode["tekmiria_included"] == 5
    assert episode["tekmiria_eligible"] == 7
    assert episode["tekmiria_truncated"] is True


def test_duplicate_event_ids_from_distinct_sources_remain_distinct() -> None:
    """Σταθερά IDs είναι scoped ανά πηγή και δεν καταργούν άλλο source event."""
    metriko = SyllogistisMetrikon()
    metriko.prosthese(dimiourgia_event(event_id="same", source="codex"))
    metriko.prosthese(dimiourgia_event(event_id="same", source="claude"))

    result = metriko.apotelesma()

    assert result["events"] == 2
    sources = cast(list[dict[str, object]], result["sources"])
    assert [item["pigi"] for item in sources] == ["claude", "codex"]


def test_episode_output_cap_reports_truncation_without_dropping_global_events() -> None:
    """Μετά το όριο episodes, το payload παραμένει bounded και counters συνεχίζουν."""
    metriko = SyllogistisMetrikon()
    for index in range(501):
        metriko.prosthese(dimiourgia_event(event_id=str(index), session=f"s{index}"))

    result = metriko.apotelesma()

    assert result["events"] == 501
    assert result["episodes_included"] == 500
    assert result["episodes_eligible"] == 501
    assert result["episodes_truncated"] is True
