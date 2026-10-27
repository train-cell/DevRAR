"""Behavioral checks for explicit active-time and cost imports."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import cast

import pytest

from devrar import eisagoges
from devrar.eisagoges import (
    _egkyri_eggrafi_kostous,
    diavase_energo_xrono,
    diavase_kostos,
)


def test_kostos_akrivia_pano_apo_default_decimal_context(tmp_path: Path) -> None:
    """Διατηρεί μακρύ recorded decimal χωρίς rounding ή έκθεση σε huge exponents."""
    poso = "0." + "1" * 60
    grammi = {
        "timestamp": "2026-10-01T10:00:00Z",
        "provider": "synthetic",
        "model": "synthetic",
        "currency": "EUR",
        "kind": "billed",
        "amount": poso,
    }
    arxeio = tmp_path / "precision.json"
    grapse_json(arxeio, [grammi, grammi])
    assert diavase_kostos(arxeio)["totals"][0]["amount"] == "0." + "2" * 60
    for akyro in ("1e999999999", "1e-999999999", "1" * 129):
        assert _egkyri_eggrafi_kostous({**grammi, "amount": akyro}) is None


def grapse_json(path: Path, data: object) -> None:
    """Writes synthetic JSON input for a single import test."""
    path.write_text(json.dumps(data), encoding="utf-8")


def bucket_afk(bucket_id: str, *events: object) -> dict[str, object]:
    """Builds a complete synthetic ActivityWatch AFK bucket export entry."""
    return {
        "id": bucket_id,
        "name": "Synthetic AFK bucket",
        "type": "afkstatus",
        "client": "aw-watcher-afk",
        "hostname": "synthetic-host",
        "created": "2026-01-01T00:00:00Z",
        "events": list(events),
    }


def event_aw(start: str, seconds: float, status: str) -> dict[str, object]:
    """Builds an event in the documented ActivityWatch shape."""
    return {"timestamp": start, "duration": seconds, "data": {"status": status}}


def coverage_tou(result: dict[str, object]) -> dict[str, object]:
    """Narrows the report coverage map for assertions."""
    return cast(dict[str, object], result["coverage"])


def test_aw_enosi_kai_afairesi_afk(tmp_path: Path) -> None:
    """Overlapping active events union; AFK overlap is removed once."""
    path = tmp_path / "buckets.json"
    grapse_json(
        path,
        {
            "buckets": {
                "aw-watcher-afk_host-a": bucket_afk(
                    "aw-watcher-afk_host-a",
                    event_aw("2026-10-01T10:00:00Z", 1200, "not-afk"),
                    event_aw("2026-10-01T10:15:00Z", 600, "afk"),
                ),
                "aw-watcher-afk_host-b": bucket_afk(
                    "aw-watcher-afk_host-b",
                    event_aw("2026-10-01T10:10:00Z", 1200, "not-afk"),
                ),
            }
        },
    )

    result = diavase_energo_xrono(Path(path), zoni="UTC")

    assert result["status"] == "ok"
    assert result["active_seconds"] == 1200
    assert result["afk_seconds"] == 600
    assert result["method"] == "aw_afk_status_intervals_union"
    assert result["by_day"] == [
        {"date": "2026-10-01", "active_seconds": 1200, "afk_seconds": 600}
    ]


def test_aw_oria_imeras_dst_anixi(tmp_path: Path) -> None:
    """Inclusive local date bounds clip through the 23-hour Athens DST day."""
    path = tmp_path / "buckets.json"
    grapse_json(
        path,
        {
            "buckets": {
                "aw-watcher-afk_host": bucket_afk(
                    "aw-watcher-afk_host",
                    event_aw("2026-03-28T21:00:00Z", 24 * 3600, "not-afk"),
                )
            }
        },
    )

    result = diavase_energo_xrono(
        Path(path), apo=date(2026, 3, 29), eos=date(2026, 3, 29), zoni="Europe/Athens"
    )

    assert result["active_seconds"] == 23 * 3600
    assert result["by_day"] == [
        {"date": "2026-03-29", "active_seconds": 23 * 3600, "afk_seconds": 0}
    ]


def test_aw_orio_25oronis_imeras_dst(tmp_path: Path) -> None:
    """The Athens autumn DST day retains its full 25 local-clock hours."""
    path = tmp_path / "buckets.json"
    grapse_json(
        path,
        {
            "buckets": {
                "afk": bucket_afk(
                    "afk", event_aw("2026-10-24T20:00:00Z", 26 * 3600, "not-afk")
                )
            }
        },
    )

    result = diavase_energo_xrono(
        path, date(2026, 10, 25), date(2026, 10, 25), "Europe/Athens"
    )

    assert result["active_seconds"] == 25 * 3600
    assert result["by_day"] == [
        {"date": "2026-10-25", "active_seconds": 25 * 3600, "afk_seconds": 0}
    ]


def test_csv_enosi_energon_diastimaton_kai_agnoston_status(
    tmp_path: Path,
) -> None:
    """The documented fallback CSV supports explicit active/AFK intervals."""
    path = tmp_path / "activity.csv"
    Path(path).write_text(
        "start,end,status\n"
        "2026-10-01T10:00:00Z,2026-10-01T10:20:00Z,active\n"
        "2026-10-01T10:10:00Z,2026-10-01T10:30:00Z,active\n"
        "2026-10-01T10:15:00Z,2026-10-01T10:25:00Z,afk\n"
        "2026-10-01T10:30:00Z,2026-10-01T10:40:00Z,idle\n",
        encoding="utf-8",
    )

    result = diavase_energo_xrono(Path(path), zoni="UTC")

    assert result["status"] == "partial"
    assert result["active_seconds"] == 1200
    assert result["afk_seconds"] == 600
    assert coverage_tou(result)["events_ignored"] == 1
    assert result["source"] == "recorded CSV"


def test_agnostos_chronos_merikos_kai_filtrarisma(
    tmp_path: Path,
) -> None:
    """Unknown dates contribute to unfiltered measured totals, not filtered totals."""
    path = tmp_path / "costs.csv"
    Path(path).write_text(
        "timestamp,provider,model,amount,currency,kind\n"
        "2026-10-01T10:00:00Z,provider-a,model-x,1.25,usd,billed\n"
        ",provider-b,model-y,2.50,EUR,estimated\n",
        encoding="utf-8",
    )

    unfiltered = diavase_kostos(Path(path))
    filtered = diavase_kostos(Path(path), date(2026, 10, 1), date(2026, 10, 1))

    assert unfiltered["status"] == "partial"
    assert coverage_tou(unfiltered)["timestamps_unknown"] == 1
    assert unfiltered["totals"] == [
        {"currency": "EUR", "kind": "estimated", "amount": "2.50"},
        {"currency": "USD", "kind": "billed", "amount": "1.25"},
    ]
    assert filtered["totals"] == [
        {"currency": "USD", "kind": "billed", "amount": "1.25"}
    ]
    assert coverage_tou(filtered)["rows_ignored"] == 1


def test_kostos_xorizei_nomisma_kai_eidos(tmp_path: Path) -> None:
    """Each explicitly recorded kind and currency keeps an independent amount."""
    path = tmp_path / "ledger.json"
    grapse_json(
        Path(path),
        {
            "records": [
                {
                    "timestamp": "2026-10-01T10:00:00Z",
                    "provider": "p",
                    "model": "m",
                    "amount": "2.00",
                    "currency": "USD",
                    "kind": "billed",
                },
                {
                    "timestamp": "2026-10-01T11:00:00Z",
                    "provider": "p",
                    "model": "m",
                    "amount": "3.00",
                    "currency": "USD",
                    "kind": "estimated",
                },
                {
                    "timestamp": "2026-10-01T12:00:00Z",
                    "provider": "p",
                    "model": "m",
                    "amount": "4.00",
                    "currency": "EUR",
                    "kind": "billed",
                },
            ]
        },
    )

    result = diavase_kostos(Path(path))

    assert result["totals"] == [
        {"currency": "EUR", "kind": "billed", "amount": "4.00"},
        {"currency": "USD", "kind": "billed", "amount": "2.00"},
        {"currency": "USD", "kind": "estimated", "amount": "3.00"},
    ]


def test_eisagogi_readonly_kai_apokrypsi_diadromis(tmp_path: Path) -> None:
    """Read-only import preserves bytes and never reveals source path in result."""
    path = tmp_path / "ledger.csv"
    Path(path).write_text(
        "timestamp,provider,model,amount,currency,kind\n"
        "2026-10-01T10:00:00Z,p,m,1.00,USD,billed\n",
        encoding="utf-8",
    )
    before = hashlib.sha256(Path(path).read_bytes()).hexdigest()

    result = diavase_kostos(Path(path))

    after = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    assert before == after
    assert str(path) not in json.dumps(result)


def test_activitywatch_eisagogi_den_allazei_arxeio(tmp_path: Path) -> None:
    """ActivityWatch exports are read only and never rewritten during aggregation."""
    path = tmp_path / "buckets.json"
    grapse_json(
        path,
        {
            "buckets": {
                "afk": bucket_afk(
                    "afk", event_aw("2026-10-01T10:00:00Z", 60, "not-afk")
                )
            }
        },
    )
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    result = diavase_energo_xrono(path)

    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
    assert str(path) not in json.dumps(result)


def test_missing_kai_malformed_piges_agnostes(tmp_path: Path) -> None:
    """Missing or malformed exports report partial coverage and unavailable totals."""
    missing = tmp_path / "missing.json"
    malformed = tmp_path / "bad.json"
    malformed.write_text("{", encoding="utf-8")

    activity = diavase_energo_xrono(missing)
    costs = diavase_kostos(malformed)

    assert activity["status"] == "missing"
    assert activity["active_seconds"] is None
    assert costs["status"] == "partial"
    assert costs["totals"] is None


def test_elegxoi_pedion_kai_chronou_kostous(tmp_path: Path) -> None:
    """Malformed rows are skipped and valid zero remains a recorded zero."""
    path = tmp_path / "ledger.csv"
    Path(path).write_text(
        "timestamp,provider,model,amount,currency,kind\n"
        "2026-10-01T10:00:00Z,p,m,0,USD,billed\n"
        "2026-10-01T10:00:00Z,p,m,-1,USD,billed\n"
        "2026-10-01T10:00:00Z,p,m,1,US,billed\n"
        "2026-10-01T10:00:00Z,p,m,1,USD,unknown\n"
        "not-a-date,,,1,USD,billed\n",
        encoding="utf-8",
    )

    result = diavase_kostos(Path(path))

    assert result["status"] == "partial"
    assert result["totals"] == [{"currency": "USD", "kind": "billed", "amount": "0"}]
    assert result["totals"] == [{"currency": "USD", "kind": "billed", "amount": "0"}]
    assert coverage_tou(result)["rows_ignored"] == 4
    assert coverage_tou(result)["timestamps_unknown"] == 1


def test_aw_akyres_piges_katastaseis_kai_diarkeies(
    tmp_path: Path,
) -> None:
    """Bad or absent AW intervals stay partial/unknown rather than zero activity."""
    bad_json = tmp_path / "malformed.json"
    bad_json.write_text("not json", encoding="utf-8")
    unsupported = tmp_path / "window.json"
    grapse_json(unsupported, {"buckets": {"window": {"type": "currentwindow"}}})
    empty = tmp_path / "empty.csv"
    empty.write_text("start,end,status\n", encoding="utf-8")
    invalid_rows = tmp_path / "invalid-aw.json"
    grapse_json(
        invalid_rows,
        {
            "buckets": {
                "aw-watcher-afk_host": bucket_afk(
                    "aw-watcher-afk_host",
                    event_aw("not-a-date", 30, "not-afk"),
                    event_aw("2026-10-01T10:00:00Z", 0, "not-afk"),
                    event_aw("2026-10-01T10:00:00Z", True, "afk"),
                    event_aw("2026-10-01T10:00:00Z", 10, "hibernating"),
                )
            }
        },
    )

    assert diavase_energo_xrono(bad_json)["status"] == "partial"
    assert diavase_energo_xrono(unsupported)["status"] == "unsupported"
    empty_result = diavase_energo_xrono(empty)
    assert empty_result["status"] == "partial"
    assert empty_result["active_seconds"] is None
    invalid_result = diavase_energo_xrono(invalid_rows)
    assert invalid_result["status"] == "partial"
    assert invalid_result["active_seconds"] is None
    assert coverage_tou(invalid_result)["unknown_intervals"] == 4
    assert coverage_tou(invalid_result)["timestamps_unknown"] == 1


def test_decimal_akriveia_kai_aporripsi_nan(
    tmp_path: Path,
) -> None:
    """Numeric JSON amounts sum with Decimal and NaN/Infinity are rejected."""
    path = tmp_path / "decimal.json"
    path.write_text(
        '{"records":['
        '{"timestamp":"2026-10-01T10:00:00Z","provider":"p","model":"m",'
        '"amount":0.1,"currency":"USD","kind":"billed"},'
        '{"timestamp":"2026-10-01T11:00:00Z","provider":"p","model":"m",'
        '"amount":0.2,"currency":"USD","kind":"billed"},'
        '{"timestamp":"2026-10-01T12:00:00Z","provider":"p","model":"m",'
        '"amount":NaN,"currency":"USD","kind":"billed"}]}',
        encoding="utf-8",
    )

    result = diavase_kostos(path)

    assert result["totals"] == [{"currency": "USD", "kind": "billed", "amount": "0.3"}]
    assert result["status"] == "partial"
    assert coverage_tou(result)["rows_ignored"] == 1


def test_akyra_oria_zoni_kai_kostos_unsupported(
    tmp_path: Path,
) -> None:
    """Date bounds, timezone and unsupported ledger formats fail explicitly."""
    path = tmp_path / "ledger.csv"
    path.write_text("bad,headers\n", encoding="utf-8")
    unsupported_path = tmp_path / "ledger.txt"
    unsupported_path.write_text("irrelevant", encoding="utf-8")

    with pytest.raises(ValueError, match="apo"):
        diavase_energo_xrono(path, date(2026, 10, 2), date(2026, 10, 1))
    with pytest.raises(ValueError, match="timezone"):
        diavase_kostos(path, zoni="Mars/Olympus")
    with pytest.raises(ValueError, match="eos"):
        diavase_kostos(path, eos=date.max)
    assert diavase_kostos(path)["status"] == "unsupported"
    assert diavase_kostos(unsupported_path)["status"] == "unsupported"


def test_oria_eisagogis_kai_mi_anagnosimes_diadromes(
    tmp_path: Path, monkeypatch
) -> None:
    """Byte and row caps bound parsing; unreadable or oversized inputs stay partial."""
    oversized = tmp_path / "large.json"
    oversized.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(eisagoges, "ORIO_BYTE_EISAGOGIS", 1)
    assert diavase_energo_xrono(oversized)["status"] == "partial"
    assert diavase_kostos(oversized)["status"] == "partial"

    monkeypatch.setattr(eisagoges, "ORIO_BYTE_EISAGOGIS", 100_000)
    monkeypatch.setattr(eisagoges, "ORIO_EGGRAFON", 1)
    activity = tmp_path / "many.csv"
    activity.write_text(
        "start,end,status\n"
        "2026-10-01T10:00:00Z,2026-10-01T10:00:10Z,active\n"
        "2026-10-01T10:00:10Z,2026-10-01T10:00:20Z,active\n",
        encoding="utf-8",
    )
    costs = tmp_path / "many-costs.csv"
    costs.write_text(
        "timestamp,provider,model,amount,currency,kind\n"
        "2026-10-01T10:00:00Z,p,m,1,USD,billed\n"
        "2026-10-01T10:00:01Z,p,m,2,USD,billed\n",
        encoding="utf-8",
    )
    assert coverage_tou(diavase_energo_xrono(activity))["events_ignored"] == 1
    assert coverage_tou(diavase_kostos(costs))["rows_ignored"] == 1
    assert diavase_energo_xrono(tmp_path)["status"] == "missing"


def test_csv_akyri_kodikopoiisi_kai_stiles(
    tmp_path: Path,
) -> None:
    """Unreadable CSV bytes and missing required headers remain unavailable."""
    bad_encoding = tmp_path / "bad.csv"
    bad_encoding.write_bytes(b"start,end,status\n\xff")
    bad_headers = tmp_path / "headers.csv"
    bad_headers.write_text("start,end\n", encoding="utf-8")

    assert diavase_energo_xrono(bad_encoding)["status"] == "partial"
    assert diavase_energo_xrono(bad_headers)["status"] == "partial"


def test_filtrarisma_imeras_kai_agnostoi_xronoi(
    tmp_path: Path,
) -> None:
    """Inclusive date selection counts only aware timestamps inside local bounds."""
    path = tmp_path / "filtered.csv"
    path.write_text(
        "timestamp,provider,model,amount,currency,kind\n"
        "2026-09-30T23:59:59Z,p,m,1,USD,billed\n"
        "2026-10-01T12:00:00Z,p,m,2,USD,billed\n"
        "2026-10-02T00:00:00Z,p,m,3,USD,billed\n"
        "naive,p,m,4,USD,billed\n",
        encoding="utf-8",
    )

    result = diavase_kostos(path, date(2026, 10, 1), date(2026, 10, 1), "UTC")

    assert result["totals"] == [{"currency": "USD", "kind": "billed", "amount": "2"}]
    assert coverage_tou(result)["rows_ignored"] == 3
    assert coverage_tou(result)["timestamps_unknown"] == 1


def test_aw_akyra_bucket_kai_orio_grammon(tmp_path: Path, monkeypatch) -> None:
    """Malformed AFK buckets and event objects become explicit partial coverage."""
    path = tmp_path / "buckets.json"
    monkeypatch.setattr(eisagoges, "ORIO_EGGRAFON", 1)
    grapse_json(
        path,
        {
            "buckets": {
                "bad": {"type": "afkstatus", "events": "not-an-array"},
                "aw-watcher-afk_host": bucket_afk(
                    "aw-watcher-afk_host",
                    "not-an-object",
                    event_aw("2026-10-01T10:00:00Z", 5, "not-afk"),
                    event_aw("2026-10-01T10:00:05Z", 5, "not-afk"),
                ),
            }
        },
    )

    result = diavase_energo_xrono(path)

    assert result["status"] == "partial"
    assert coverage_tou(result)["events_total"] == 1
    assert coverage_tou(result)["events_used"] == 0
    assert coverage_tou(result)["events_ignored"] == 4


def test_csv_agnosta_diastimata_kai_oria(tmp_path: Path) -> None:
    """Invalid and out-of-range CSV intervals are excluded with coverage counts."""
    path = tmp_path / "activity.csv"
    path.write_text(
        "start,end,status\n"
        "naive,2026-10-01T10:00:10Z,active\n"
        "2026-09-30T23:00:00Z,2026-09-30T23:10:00Z,active\n"
        "2026-10-01T10:00:00Z,2026-10-01T10:00:10Z,active\n",
        encoding="utf-8",
    )

    result = diavase_energo_xrono(path, date(2026, 10, 1), date(2026, 10, 1), "UTC")

    assert result["active_seconds"] == 10
    assert coverage_tou(result)["events_total"] == 3
    assert coverage_tou(result)["events_used"] == 1
    assert coverage_tou(result)["events_ignored"] == 2
    assert coverage_tou(result)["timestamps_unknown"] == 1


def test_afk_epikalyptei_oli_tin_energi_drastiriotita(
    tmp_path: Path,
) -> None:
    """AFK overlap can remove all active seconds but remains separately recorded."""
    path = tmp_path / "activity.csv"
    path.write_text(
        "start,end,status\n"
        "2026-10-01T10:00:00Z,2026-10-01T10:10:00Z,active\n"
        "2026-10-01T09:55:00Z,2026-10-01T10:15:00Z,afk\n",
        encoding="utf-8",
    )

    result = diavase_energo_xrono(path, zoni="UTC")

    assert result["active_seconds"] == 0
    assert result["afk_seconds"] == 1200


def test_xorismena_energa_diastimata(tmp_path: Path) -> None:
    """Separated observed intervals sum independently and preserve their gap."""
    path = tmp_path / "activity.csv"
    path.write_text(
        "start,end,status\n"
        "2026-10-01T10:00:00Z,2026-10-01T10:00:10Z,active\n"
        "2026-10-01T10:00:30Z,2026-10-01T10:00:40Z,active\n",
        encoding="utf-8",
    )

    result = diavase_energo_xrono(path, zoni="UTC")

    assert result["active_seconds"] == 20


def test_aw_xoris_bucket_map_meros(tmp_path: Path) -> None:
    """An otherwise valid JSON object without canonical buckets stays partial."""
    path = tmp_path / "no-buckets.json"
    grapse_json(path, {"events": []})

    result = diavase_energo_xrono(path)

    assert result["status"] == "partial"
    assert result["active_seconds"] is None


def test_aw_agnostos_chronos_kai_diarkeies(
    tmp_path: Path,
) -> None:
    """Naive timestamps and unrepresentable duration values are never estimated."""
    path = tmp_path / "unknown-aw.json"
    grapse_json(
        path,
        {
            "buckets": {
                "afk": bucket_afk(
                    "afk",
                    event_aw("2026-10-01T10:00:00", 5, "not-afk"),
                    event_aw("2026-10-01T10:00:00Z", 1e308, "not-afk"),
                    {
                        "timestamp": "2026-10-01T10:00:00Z",
                        "duration": 10**400,
                        "data": {"status": "not-afk"},
                    },
                )
            }
        },
    )

    result = diavase_energo_xrono(path)

    assert result["status"] == "partial"
    assert result["active_seconds"] is None
    assert coverage_tou(result)["unknown_intervals"] == 3
    assert coverage_tou(result)["timestamps_unknown"] == 1


def test_aw_ektos_imerominion(tmp_path: Path) -> None:
    """Valid events wholly outside selected dates do not establish zero activity."""
    path = tmp_path / "out-of-range.json"
    grapse_json(
        path,
        {
            "buckets": {
                "afk": bucket_afk(
                    "afk", event_aw("2026-09-30T10:00:00Z", 60, "not-afk")
                )
            }
        },
    )

    result = diavase_energo_xrono(path, date(2026, 10, 1), date(2026, 10, 1), "UTC")

    assert result["status"] == "partial"
    assert result["active_seconds"] is None
    assert coverage_tou(result)["events_ignored"] == 1


def test_json_lista_kai_mi_antikeimena(tmp_path: Path) -> None:
    """Ledger JSON accepts arrays and counts malformed array rows as ignored."""
    path = tmp_path / "ledger.json"
    grapse_json(
        path,
        [
            "not-an-object",
            {
                "timestamp": "2026-10-01T10:00:00Z",
                "provider": "p",
                "model": "m",
                "amount": "1.20",
                "currency": "USD",
                "kind": "billed",
            },
        ],
    )

    result = diavase_kostos(path)

    assert result["status"] == "partial"
    assert result["totals"] == [{"currency": "USD", "kind": "billed", "amount": "1.20"}]
    assert coverage_tou(result)["rows_total"] == 2
    assert coverage_tou(result)["rows_ignored"] == 1


def test_json_kostos_apaitoun_lista_records(tmp_path: Path) -> None:
    """JSON ledger wrapper rejects a non-list records value as unsupported."""
    path = tmp_path / "bad-shape.json"
    grapse_json(path, {"records": {"timestamp": "2026-10-01T10:00:00Z"}})

    assert diavase_kostos(path)["status"] == "unsupported"


def test_oles_oi_eggrafes_kostos_akyres(tmp_path: Path) -> None:
    """No valid ledger entries means unavailable totals instead of zero spend."""
    path = tmp_path / "ledger.csv"
    path.write_text(
        "timestamp,provider,model,amount,currency,kind\n"
        "2026-10-01T10:00:00Z,p,m,-1,USD,billed\n",
        encoding="utf-8",
    )

    result = diavase_kostos(path)

    assert result["totals"] is None
    assert coverage_tou(result)["rows_used"] == 0


def test_mi_anagnosimos_fakelos_kai_kostos(tmp_path: Path) -> None:
    """Read failures and non-UTF8 ledger files do not escape or expose paths."""
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_bytes(b"timestamp,provider,model,amount,currency,kind\n\xff")

    assert diavase_kostos(bad_csv)["status"] == "partial"
    assert diavase_kostos(tmp_path)["status"] == "missing"


def test_kostos_aporriptei_akyrous_tupous_nan(tmp_path: Path) -> None:
    """Provider/model, amount, currency and kind must all be explicitly valid."""
    path = tmp_path / "invalid-ledger.json"
    grapse_json(
        path,
        {
            "records": [
                {
                    "provider": "",
                    "model": "m",
                    "amount": "1",
                    "currency": "USD",
                    "kind": "billed",
                },
                {
                    "provider": "p",
                    "model": [],
                    "amount": "1",
                    "currency": "USD",
                    "kind": "billed",
                },
                {
                    "provider": "p",
                    "model": "m",
                    "amount": True,
                    "currency": "USD",
                    "kind": "billed",
                },
                {
                    "provider": "p",
                    "model": "m",
                    "amount": "bad",
                    "currency": "USD",
                    "kind": "billed",
                },
                {
                    "provider": "p",
                    "model": "m",
                    "amount": "NaN",
                    "currency": "USD",
                    "kind": "billed",
                },
                {
                    "provider": "p",
                    "model": "m",
                    "amount": "Infinity",
                    "currency": 3,
                    "kind": "billed",
                },
                {
                    "provider": "p",
                    "model": "m",
                    "amount": "1",
                    "currency": "US",
                    "kind": 3,
                },
            ]
        },
    )

    result = diavase_kostos(path)

    assert result["status"] == "partial"
    assert result["totals"] is None
    assert coverage_tou(result)["rows_ignored"] == 7


def test_nomisma_katharizetai_kai_kanonikopoieitai() -> None:
    """Recorded currency text is normalized without changing amount semantics."""
    result = _egkyri_eggrafi_kostous(
        {
            "provider": "p",
            "model": "m",
            "amount": "1.25",
            "currency": " usd ",
            "kind": "billed",
        }
    )

    assert result is not None
    assert result[0] == "USD"
