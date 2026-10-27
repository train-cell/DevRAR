"""Ελέγχει ολοκληρωμένη συλλογή πολλών πηγών και full-stream work metrics."""

import json
from collections.abc import Callable, Iterator, Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import cast

import pytest

import devrar.syndesi as syndesi
from devrar.cli import kyria
from devrar.piges import ApotelesmaPigis
from devrar.symvanta import SymvanErgasias


def test_cli_sygkrisi_xoris_git_me_idio_source_scope(tmp_path: Path) -> None:
    """Η μηνιαία AI-only σύγκριση έχει ρητό κενό Git scope και έγκυρα deltas."""
    pigi = tmp_path / "synthetic.jsonl"
    eggrafes = [
        {
            "type": "user",
            "uuid": f"u-{imera}",
            "sessionId": f"s-{imera}",
            "timestamp": f"2026-10-{imera}T08:00:00Z",
            "message": {"role": "user", "content": "Run the check."},
        }
        for imera in ("26", "27")
    ]
    pigi.write_text("\n".join(json.dumps(eggrafi) for eggrafi in eggrafes), "utf-8")
    koino = ["wrap", "--claude-path", str(pigi), "--output", str(tmp_path / "out")]
    assert kyria(koino + ["--since", "2026-10-26", "--until", "2026-10-26"]) == 0
    baseline = next((tmp_path / "out").glob("run-*/apotelesmata.json"))
    assert (
        kyria(
            koino
            + [
                "--since",
                "2026-10-27",
                "--until",
                "2026-10-27",
                "--compare",
                str(baseline),
            ]
        )
        == 0
    )
    neo = next(
        arxeio
        for arxeio in (tmp_path / "out").glob("run-*/apotelesmata.json")
        if arxeio != baseline
    )
    dedomena = json.loads(neo.read_text(encoding="utf-8"))
    assert dedomena["scope_git"]["repositories"] == []
    assert dedomena["sygkrisi"]["katastasi"] == "compatible"
    assert dedomena["sygkrisi"]["metrika"]["synola.minimata_xristi"]["delta"] == 0


def test_missing_ai_den_paragei_midenika_hour_buckets(tmp_path: Path) -> None:
    """Αδιάβαστη επιλεγμένη πηγή δεν γίνεται 24 ώρες επινοημένων μηδενικών."""
    dedomena = syndesi.syllexe_pliri(["gemini"], {"gemini": tmp_path / "missing"}, [])
    assert dedomena["metrika_ergasias"]["ora"] == []


def test_tool_output_synopsi_meta_ta_20k_den_xanetai(tmp_path: Path) -> None:
    """Η περικοπή των displayed excerpts γίνεται μετά το full-output parsing."""
    arxeio = _grapse_pigi(
        tmp_path,
        [
            {
                "type": "tool",
                "id": "long-result",
                "sessionId": "s1",
                "timestamp": "2026-10-27T08:00:00Z",
                "content": "x" * 25000 + "\n=== 2 passed in 0.1s ===",
            }
        ],
    )
    dedomena = syndesi.syllexe_pliri(["gemini"], {"gemini": arxeio}, [])
    assert dedomena["metrika_ergasias"]["test_summary"]["passed"] == 2
    assert len(dedomena["deigmata"][0]["keimeno"]) == 500


def test_idle_minutes_apodidetai_kai_sta_native_command_spans(tmp_path: Path) -> None:
    """Το ίδιο explicit gap εφαρμόζεται στο χωριστό native command channel."""
    arxeio = tmp_path / "native.jsonl"
    eggrafes = [{
        "type": "event_msg", "timestamp": f"2026-10-27T08:{lepto}:00Z",
        "payload": {"type": "item_completed", "item": {
            "type": "CommandExecution", "id": f"c-{lepto}", "command": ["synthetic"],
            "status": "completed", "exit_code": 0,
        }},
    } for lepto in ("00", "20")]
    arxeio.write_text("\n".join(json.dumps(eggrafi) for eggrafi in eggrafes), "utf-8")
    dedomena = syndesi.syllexe_pliri(["codex"], {"codex": arxeio}, [], idle_minutes=30)
    native = dedomena["codex_native"]["metrika_ergasias"]
    assert native["interval_estimate_minutes"] == 20
    assert native["idle_minutes"] == 30
    assert dedomena["metrika_ergasias"]["idle_minutes"] == 30


def test_cli_syndeetai_me_pliri_metrika_kai_ora(tmp_path: Path) -> None:
    """A real selected JSONL stream reaches hour, tests and outcome summaries."""
    pigi = tmp_path / "synthetic.jsonl"
    eggrafes = [
        {
            "type": "user",
            "uuid": "u1",
            "sessionId": "s1",
            "timestamp": "2026-10-27T08:00:00Z",
            "message": {"role": "user", "content": "Run the check."},
        },
        {
            "type": "user",
            "uuid": "r1",
            "sessionId": "s1",
            "timestamp": "2026-10-27T08:02:00Z",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "c1",
                        "content": "=== 2 passed in 0.1s ===",
                    }
                ],
            },
        },
    ]
    pigi.write_text("\n".join(json.dumps(eggrafi) for eggrafi in eggrafes), "utf-8")
    assert (
        kyria(["wrap", "--claude-path", str(pigi), "--output", str(tmp_path / "out")])
        == 0
    )
    anafora = next((tmp_path / "out").glob("run-*/apotelesmata.json"))
    dedomena = json.loads(anafora.read_text(encoding="utf-8"))
    assert "metrika_ergasias" in dedomena
    assert dedomena["metrika_ergasias"]["ora"][10]["prompts"] == 1
    assert dedomena["metrika_ergasias"]["test_summary"]["passed"] == 2
    assert (
        dedomena["epeisodia_ergasias"]["paratiriseis"][0]["katastasi"]
        == "observed_success"
    )


def _diavase_legacy(
    piges: Sequence[str],
    fakeloi: Mapping[str, Path],
    apothitiria: Sequence[Path],
    apo: date | None,
    eos: date | None,
    zoni: str,
    author: str | None,
    paratiritis: Callable[[SymvanErgasias], None] | None,
    idle_minutes: int = 15,
) -> dict[str, object]:
    """Μιμείται legacy collector με null όταν δεν υπάρχουν αναγνώσιμες πηγές."""
    del fakeloi, apothitiria, apo, eos, zoni, author, idle_minutes
    einai_epilegmeni = "claude" in piges
    if einai_epilegmeni and paratiritis is not None:
        for symvan in _legacy_events():
            paratiritis(symvan)
    return {
        "synola": {
            "synedries": 1 if einai_epilegmeni else None,
            "rizikes": 1 if einai_epilegmeni else None,
            "ypopraktores": 0 if einai_epilegmeni else None,
            "minimata_xristi": 1 if einai_epilegmeni else None,
            "apantiseis": 1 if einai_epilegmeni else None,
            "kliseis_ergaleion": 0 if einai_epilegmeni else None,
            "tokens": 120 if einai_epilegmeni else None,
            "commits": None,
            "imeres": 1 if einai_epilegmeni else 0,
        },
        "piges": (
            [{"onoma": "Claude Code", "katastasi": "ok", "arxeia": 1}]
            if einai_epilegmeni
            else []
        ),
        "ergaleia": (
            [{"onoma": "Claude Code", "synedries": 1, "prompts": 1, "tokens": 120}]
            if einai_epilegmeni
            else []
        ),
        "montela": [],
        "drastiriotita": [],
        "simeioseis": [],
        "deigmata": [],
        "kalypsi_tokens": {
            "piges": (
                {
                    "claude": {
                        "gnostes_aitiseis": 1,
                        "elleipeis_aitiseis": 0,
                        "agnosta_records": 0,
                        "methodos": "claude_api_message_usage",
                        "pliris": True,
                    }
                }
                if einai_epilegmeni
                else {}
            ),
            "pliris": einai_epilegmeni,
        },
    }


def _legacy_events() -> list[SymvanErgasias]:
    """Δημιουργεί ένα ασφαλές synthetic legacy user event."""
    return [
        {
            "id": "legacy-1",
            "pigi": "Claude Code",
            "synedria": "legacy-session",
            "goneas": None,
            "chronos": "2026-10-27T08:00:00+00:00",
            "rolos": "user",
            "eidos": "prompt",
            "keimeno": "Please verify this change.",
            "locator": "legacy.jsonl:1",
            "ergaleio": None,
            "montelo": None,
            "kodikos_exodou": None,
        }
    ]


def _grapse_pigi(
    tmp_path: Path, rows: list[dict[str, object]], suffix: str = ".json"
) -> Path:
    """Γράφει αποκλειστικά synthetic source fixture σε προσωρινό φάκελο."""
    path = tmp_path / f"synthetic{suffix}"
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path


def test_syllexe_pliri_unknown_new_source_makes_token_coverage_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Νέα πηγή χωρίς reported usage ακυρώνει inherited πλήρη token coverage."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    path = _grapse_pigi(
        tmp_path,
        [
            {
                "type": "user",
                "id": "g1",
                "sessionId": "s1",
                "timestamp": "2026-10-27T08:00:00Z",
                "content": "Check.",
            }
        ],
    )

    dedomena = syndesi.syllexe_pliri(["claude", "gemini"], {"gemini": path}, [])

    kalypsi = cast(dict[str, object], dedomena["kalypsi_tokens"])
    piges_kalypsis = cast(dict[str, Mapping[str, object]], kalypsi["piges"])
    synola = cast(Mapping[str, object], dedomena["synola"])
    assert synola["tokens"] is None
    assert kalypsi["pliris"] is False
    assert piges_kalypsis["gemini"]["pliris"] is False
    assert piges_kalypsis["claude"]["pliris"] is True


def test_syllexe_pliri_keeps_unknown_timestamp_counts_null(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Όλα τα events με άγνωστες ώρες δεν γίνονται μηδενική δραστηριότητα με φίλτρο."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    path = _grapse_pigi(
        tmp_path,
        [
            {
                "type": "user",
                "id": "g1",
                "sessionId": "s1",
                "timestamp": "2026-10-27T08:00:00",
                "content": "Unknown local time.",
            }
        ],
    )

    dedomena = syndesi.syllexe_pliri(
        ["gemini"], {"gemini": path}, [], apo=date(2026, 10, 27), eos=date(2026, 10, 27)
    )

    synola = cast(dict[str, object], dedomena["synola"])
    pigi = cast(list[Mapping[str, object]], dedomena["piges"])[0]
    assert synola["minimata_xristi"] is None
    assert pigi["katastasi"] == "partial"
    assert pigi["sfalmata"] == 1
    assert cast(Mapping[str, object], pigi["periodos_diathesimon"])["apo"] is None


def test_syllexe_pliri_missing_new_source_does_not_assert_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Επιλεγμένη αλλά απούσα πηγή κρατά unknown counters ως null."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)

    dedomena = syndesi.syllexe_pliri(
        ["gemini"], {"gemini": tmp_path / "missing.json"}, []
    )

    synola = cast(dict[str, object], dedomena["synola"])
    assert synola["synedries"] is None
    assert synola["minimata_xristi"] is None
    assert (
        cast(list[Mapping[str, object]], dedomena["piges"])[0]["katastasi"] == "missing"
    )


def test_syllexe_pliri_combines_legacy_and_new_metrics_but_nulls_tokens(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Legacy/new counters combine once while cross-source tokens stay unknown."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    path = _grapse_pigi(
        tmp_path,
        [
            {
                "type": "user",
                "id": "g1",
                "sessionId": "s2",
                "timestamp": "2026-10-27T08:00:00Z",
                "content": "Check.",
            }
        ],
    )

    dedomena = syndesi.syllexe_pliri(["claude", "gemini"], {"gemini": path}, [])

    synola = cast(Mapping[str, object], dedomena["synola"])
    kalypsi = cast(Mapping[str, object], dedomena["kalypsi_tokens"])
    assert synola["synedries"] == 2
    assert synola["minimata_xristi"] == 2
    assert synola["tokens"] is None
    assert kalypsi["pliris"] is False


def test_syllexe_pliri_keeps_legacy_counts_when_new_source_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing new adapter does not erase already readable legacy counts."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)

    dedomena = syndesi.syllexe_pliri(
        ["claude", "gemini"], {"gemini": tmp_path / "missing.json"}, []
    )

    synola = cast(Mapping[str, object], dedomena["synola"])
    assert synola["synedries"] == 1
    assert synola["minimata_xristi"] == 1
    new_pigi = next(
        row
        for row in cast(list[Mapping[str, object]], dedomena["piges"])
        if row["onoma"] == "Gemini CLI"
    )
    assert new_pigi["katastasi"] == "missing"


def test_syllexe_pliri_filters_aware_timestamps_in_report_timezone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Aware timestamps use the selected local date, inclusive at both ends."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    path = _grapse_pigi(
        tmp_path,
        [
            {
                "type": "user",
                "id": "before",
                "sessionId": "s1",
                "timestamp": "2026-10-26T22:30:00Z",
                "content": "Local Oct 27.",
            },
            {
                "type": "user",
                "id": "in",
                "sessionId": "s1",
                "timestamp": "2026-10-27T21:30:00Z",
                "content": "Local Oct 28.",
            },
            {
                "type": "user",
                "id": "after",
                "sessionId": "s1",
                "timestamp": "2026-10-28T22:30:00Z",
                "content": "Local Oct 29.",
            },
        ],
    )

    dedomena = syndesi.syllexe_pliri(
        ["gemini"],
        {"gemini": path},
        [],
        date(2026, 10, 27),
        date(2026, 10, 28),
        "Europe/Athens",
    )

    synola = cast(Mapping[str, object], dedomena["synola"])
    pigi = next(
        row
        for row in cast(list[Mapping[str, object]], dedomena["piges"])
        if row["onoma"] == "Gemini CLI"
    )
    periodos = cast(Mapping[str, object], pigi["periodos_diathesimon"])
    assert synola["minimata_xristi"] == 2
    assert periodos == {"apo": "2026-10-27", "eos": "2026-10-29"}
    assert pigi["katastasi"] == "ok"


def test_syllexe_pliri_balances_deterministic_evidence_sample(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Full counts survive truncation while the sample retains multiple kinds."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    eggrafes: list[dict[str, object]] = [
        {
            "type": "user",
            "id": f"p{deiktis}",
            "sessionId": "s1",
            "timestamp": "2026-10-27T08:00:00Z",
            "content": "User prompt.",
        }
        for deiktis in range(601)
    ]
    eggrafes.extend(
        {
            "type": "assistant",
            "id": f"r{deiktis}",
            "sessionId": "s1",
            "timestamp": "2026-10-27T08:01:00Z",
            "content": "Assistant response.",
        }
        for deiktis in range(5)
    )
    path = _grapse_pigi(tmp_path, eggrafes)

    dedomena = syndesi.syllexe_pliri(["gemini"], {"gemini": path}, [])
    dedomena_deuteri = syndesi.syllexe_pliri(["gemini"], {"gemini": path}, [])

    synola = cast(Mapping[str, object], dedomena["synola"])
    deigmata = cast(list[Mapping[str, object]], dedomena["deigmata"])
    assert synola["minimata_xristi"] == 601
    assert len(deigmata) == 600
    assert sum(row["eidos"] == "response" for row in deigmata) == 5
    assert dedomena["deigmata"] == dedomena_deuteri["deigmata"]
    assert cast(Mapping[str, object], dedomena["kalypsi_analysi"]) == {
        "epilegmena": 600,
        "diathesima": 606,
        "perikopi": True,
    }


def test_syllexe_pliri_copies_reader_event_before_source_normalization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Source reader event stays unchanged when report label is normalized."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    path = _grapse_pigi(
        tmp_path,
        [
            {
                "type": "user",
                "id": "g1",
                "sessionId": "s1",
                "timestamp": "2026-10-27T08:00:00Z",
                "content": "Check.",
            }
        ],
    )
    symvanta: list[SymvanErgasias] = []
    original = cast(
        Callable[[str, Path], ApotelesmaPigis], getattr(syndesi, "diavase_pigi")
    )

    def krata_reader_event(pigi: str, diadromi: Path) -> object:
        """Επιστρέφει controlled stream και κρατά αναφορά στο αρχικό event."""
        apotelesma_pigis = original(pigi, diadromi)

        def event_stream() -> Iterator[SymvanErgasias]:
            """Κρατά τα ίδια event objects πριν το normalization copy."""
            for symvan in apotelesma_pigis.gegonota:
                symvanta.append(symvan)
                yield symvan

        return ApotelesmaPigis(event_stream(), apotelesma_pigis.kalypsi)

    monkeypatch.setattr(syndesi, "diavase_pigi", krata_reader_event)
    dedomena = syndesi.syllexe_pliri(["gemini"], {"gemini": path}, [])

    assert (
        cast(list[Mapping[str, object]], dedomena["deigmata"])[0]["pigi"]
        == "Gemini CLI"
    )
    assert symvanta[0]["pigi"] == "gemini"


def test_syllexe_pliri_adds_git_delta_report_only_for_selected_repositories(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Selected repos get a separate first-parent delta fragment."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    kliseis: list[tuple[object, ...]] = []

    def pare_git(*orismata: object) -> dict[str, object]:
        """Returns explicit synthetic first-parent stats."""
        kliseis.append(orismata)
        return {"adapter": "git-numstat-first-parent-v1", "katastasi": "ok"}

    monkeypatch.setattr(syndesi, "syllexe_git_diafores", pare_git)

    xoris_repo = syndesi.syllexe_pliri([], {}, [])
    me_repo = syndesi.syllexe_pliri(
        [], {}, [Path("repo")], date(2026, 1, 1), None, "Europe/Athens", "Dev"
    )

    assert "git_diafores" not in xoris_repo
    assert me_repo["git_diafores"] == {
        "adapter": "git-numstat-first-parent-v1",
        "katastasi": "ok",
    }
    assert kliseis == [([Path("repo")], date(2026, 1, 1), None, "Europe/Athens", "Dev")]


def test_syllexe_pliri_git_delta_error_is_explicit_partial(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected Git delta failure produces a partial null-count fragment."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)

    def sfalma_git(*orismata: object) -> dict[str, object]:
        """Raises a controlled failure from the delta adapter."""
        raise RuntimeError("git process unavailable")

    monkeypatch.setattr(syndesi, "syllexe_git_diafores", sfalma_git)

    dedomena = syndesi.syllexe_pliri([], {}, [Path("repo")])

    git = cast(Mapping[str, object], dedomena["git_diafores"])
    assert git["katastasi"] == "partial"
    assert cast(Mapping[str, object], git["synola"])["unique_commits"] is None
    assert (
        "git process unavailable"
        in cast(list[str], cast(Mapping[str, object], git["kalypsi"])["simeioseis"])[0]
    )


def test_proepilegmenes_diadromes_kai_treis_antigravity_rizikes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """OpenCode env override and bounded Antigravity roots are deterministic."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("OPENCODE_DB", str(tmp_path / "override.db"))
    (tmp_path / ".gemini" / "antigravity-ide" / "brain").mkdir(parents=True)

    assert syndesi.proepilegmenes_diadromes("opencode") == (tmp_path / "override.db",)
    assert syndesi.proepilegmenes_diadromes("gemini") == (tmp_path / ".gemini" / "tmp",)
    assert syndesi.proepilegmenes_diadromes("antigravity") == (
        tmp_path / ".gemini" / "antigravity-ide" / "brain",
    )
    with pytest.raises(ValueError, match="Unsupported source"):
        syndesi.proepilegmenes_diadromes("claude")


@pytest.mark.parametrize("timestamp", ["not-a-date", "2026-10-27T08:00:00"])
def test_syllexe_pliri_invalid_or_naive_time_is_partial_under_filter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, timestamp: str
) -> None:
    """Malformed και naive timestamps δεν ορίζουν ημερομηνία φίλτρου."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    path = _grapse_pigi(
        tmp_path,
        [
            {
                "type": "user",
                "id": "g1",
                "sessionId": "s1",
                "timestamp": timestamp,
                "content": "Unknown date.",
            }
        ],
    )

    dedomena = syndesi.syllexe_pliri(
        ["gemini"], {"gemini": path}, [], date(2026, 10, 27), date(2026, 10, 27)
    )

    synola = cast(Mapping[str, object], dedomena["synola"])
    assert synola["minimata_xristi"] is None
    pigi = cast(list[Mapping[str, object]], dedomena["piges"])[0]
    assert pigi["katastasi"] == "partial"
    assert pigi["sfalmata"] == 1


def test_syllexe_pliri_unsupported_source_and_file_stay_explicit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown source key errors; unsupported selected file is partial and null."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    unsupported = tmp_path / "unsupported.bin"
    unsupported.write_bytes(b"synthetic")

    with pytest.raises(ValueError, match="Unsupported source"):
        syndesi.syllexe_pliri(["other"], {}, [])
    dedomena = syndesi.syllexe_pliri(["gemini"], {"gemini": unsupported}, [])

    synola = cast(Mapping[str, object], dedomena["synola"])
    pigi = next(
        row
        for row in cast(list[Mapping[str, object]], dedomena["piges"])
        if row["onoma"] == "Gemini CLI"
    )
    assert synola["synedries"] is None
    assert pigi["katastasi"] == "partial"
    assert pigi["arxeia"] == 1
    assert "bin" in cast(list[str], pigi["morfes"])


def test_syllexe_pliri_counts_parent_tool_and_model_events(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Parent sessions, recorded tool calls and model IDs feed separate counters."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    path = _grapse_pigi(
        tmp_path,
        [
            {
                "type": "user",
                "id": "u1",
                "sessionId": "root",
                "timestamp": "2026-10-27T08:00:00Z",
                "content": "Check.",
            },
            {
                "type": "assistant",
                "kind": "tool_call",
                "id": "c1",
                "sessionId": "child",
                "parentSessionId": "root",
                "model": "recorded-model",
                "timestamp": "2026-10-27T08:01:00Z",
                "content": "run tests",
            },
            {
                "type": "assistant",
                "id": "r1",
                "sessionId": "child",
                "parentSessionId": "root",
                "model": "recorded-model",
                "timestamp": "2026-10-27T08:02:00Z",
                "content": "Done.",
            },
        ],
    )

    dedomena = syndesi.syllexe_pliri(["gemini"], {"gemini": path}, [])

    synola = cast(Mapping[str, object], dedomena["synola"])
    assert synola["synedries"] == 2
    assert synola["rizikes"] == 1
    assert synola["ypopraktores"] == 1
    assert synola["kliseis_ergaleion"] == 1
    assert (
        cast(list[Mapping[str, object]], dedomena["montela"])[0]["onoma"]
        == "recorded-model"
    )


def test_idia_vendor_ids_se_diaforetikes_synedries_den_xanontai(tmp_path: Path) -> None:
    """Το event ID ενός export μπορεί να είναι τοπικό στη συνομιλία του."""
    pigi = _grapse_pigi(
        tmp_path,
        [
            {
                "type": "user",
                "id": "local-1",
                "sessionId": synedria,
                "timestamp": "2026-10-27T08:00:00Z",
                "content": "Synthetic prompt",
            }
            for synedria in ("s1", "s2")
        ],
    )
    dedomena = syndesi.syllexe_pliri(["gemini"], {"gemini": pigi}, [])
    assert dedomena["synola"]["minimata_xristi"] == 2
    assert dedomena["metrika_ergasias"]["events"] == 2


def test_syllexe_pliri_duplicate_ids_are_deduplicated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Repeated source event IDs count once in full metrics and evidence."""
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    path = _grapse_pigi(
        tmp_path,
        [
            {
                "type": "user",
                "id": "copied",
                "sessionId": "s1",
                "timestamp": "2026-10-27T08:00:00Z",
                "content": "Original.",
            },
            {
                "type": "assistant",
                "id": "copied",
                "sessionId": "s1",
                "timestamp": "2026-10-27T08:01:00Z",
                "content": "Duplicate ID.",
            },
        ],
    )

    dedomena = syndesi.syllexe_pliri(["gemini"], {"gemini": path}, [])

    synola = cast(Mapping[str, object], dedomena["synola"])
    assert synola["minimata_xristi"] == 1
    assert synola["apantiseis"] == 0
    assert len(cast(list[object], dedomena["deigmata"])) == 1


def test_syllexe_pliri_rejects_invalid_legacy_timestamp_without_fabricating_date(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed legacy timestamp remains undated but transcript counters survive."""
    original_events = _legacy_events()
    invalid_event = original_events[0].copy()
    invalid_event["chronos"] = "not-an-iso-date"
    monkeypatch.setattr(syndesi, "syllexe_dedomena", _diavase_legacy)
    monkeypatch.setattr(__import__(__name__), "_legacy_events", lambda: [invalid_event])

    dedomena = syndesi.syllexe_pliri(["claude"], {}, [])

    synola = cast(Mapping[str, object], dedomena["synola"])
    deigma = cast(list[Mapping[str, object]], dedomena["deigmata"])[0]
    assert synola["minimata_xristi"] == 1
    assert deigma["imerominia"] is None
