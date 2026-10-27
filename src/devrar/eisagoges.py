"""Local readers for explicitly recorded activity intervals and cost ledgers."""

from __future__ import annotations

import csv
import io
import json
import logging
import math
import re
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from typing import cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

logger = logging.getLogger(__name__)

ORIO_BYTE_EISAGOGIS = 20 * 1024 * 1024
ORIO_EGGRAFON = 100_000
TYPOS_AFK_WATCHER = "afkstatus"
KATASTASI_ENERGOS_AW = "not-afk"
KATASTASI_AFK_AW = "afk"
KATASTASI_ENERGOS_CSV = "active"
KATASTASI_AFK_CSV = "afk"
EIDI_KOSTOUS = frozenset({"billed", "estimated"})
MORFI_NOMISMATOS = re.compile(r"^[A-Z]{3}$")
MIDDEN = Decimal("0")
ORIO_PSIMION_POSOU = 128
ORIO_EKTHETI_POSOU = 128
AKRIVEIA_ATHROISMATOS = (
    ORIO_PSIMION_POSOU + 2 * ORIO_EKTHETI_POSOU + len(str(ORIO_EGGRAFON)) + 1
)


def _orismata_imerominion(
    apo: date | None, eos: date | None, zoni: str
) -> tuple[datetime | None, datetime | None, ZoneInfo]:
    """Validates dates and returns inclusive local-day bounds in UTC."""
    if apo is not None and eos is not None and apo > eos:
        raise ValueError("apo must not be after eos")
    if eos == date.max:
        raise ValueError("eos cannot exceed the maximum representable date")
    try:
        antikeimeno_zonis = ZoneInfo(zoni)
    except (ZoneInfoNotFoundError, ValueError) as sfalma:
        raise ValueError(f"Unknown timezone: {zoni}") from sfalma
    arxi = (
        datetime.combine(apo, time.min, antikeimeno_zonis).astimezone(timezone.utc)
        if apo is not None
        else None
    )
    telos = (
        datetime.combine(
            eos + timedelta(days=1), time.min, antikeimeno_zonis
        ).astimezone(timezone.utc)
        if eos is not None
        else None
    )
    return arxi, telos, antikeimeno_zonis


def _diavase_bytes(diadromi: Path) -> tuple[bytes | None, str | None]:
    """Reads one bounded local file without exposing its path in results."""
    try:
        megethos = diadromi.stat().st_size
    except OSError:
        return None, "missing"
    if megethos > ORIO_BYTE_EISAGOGIS:
        return None, "too_large"
    try:
        return diadromi.read_bytes(), None
    except OSError:
        return None, "missing"


def _antikeimeno_json(timi: object) -> dict[str, object] | None:
    """Narrows parsed JSON objects into a typed mapping."""
    if isinstance(timi, dict) and all(isinstance(kleidi, str) for kleidi in timi):
        return cast(dict[str, object], timi)
    return None


def _chronos_aware(timi: object) -> datetime | None:
    """Parses aware ISO timestamps only; naive values cannot establish a date."""
    if not isinstance(timi, str) or not timi:
        return None
    try:
        analyomeno = datetime.fromisoformat(timi.replace("Z", "+00:00"))
    except (ValueError, OverflowError):
        return None
    if analyomeno.tzinfo is None or analyomeno.utcoffset() is None:
        return None
    return analyomeno.astimezone(timezone.utc)


def _spase_diastima_ana_mera(
    arxi: datetime,
    telos: datetime,
    antikeimeno_zonis: ZoneInfo,
) -> list[tuple[str, datetime, datetime]]:
    """Clips an interval and splits it at local midnight, including DST changes."""
    apotelesma: list[tuple[str, datetime, datetime]] = []
    deiktis_xronou = arxi
    while deiktis_xronou < telos:
        topiki_imerominia = deiktis_xronou.astimezone(antikeimeno_zonis).date()
        epomena_mesanyxta = datetime.combine(
            topiki_imerominia + timedelta(days=1), time.min, antikeimeno_zonis
        ).astimezone(timezone.utc)
        telos_tmimatos = min(telos, epomena_mesanyxta)
        apotelesma.append(
            (topiki_imerominia.isoformat(), deiktis_xronou, telos_tmimatos)
        )
        deiktis_xronou = telos_tmimatos
    return apotelesma


def _enosi_diastimaton(
    diastimata: list[tuple[datetime, datetime]],
) -> list[tuple[datetime, datetime]]:
    """Merges overlapping or adjacent half-open intervals."""
    if not diastimata:
        return []
    taxinomimena = sorted(diastimata)
    enomena: list[list[datetime]] = [[taxinomimena[0][0], taxinomimena[0][1]]]
    for arxi, telos in taxinomimena[1:]:
        if arxi <= enomena[-1][1]:
            enomena[-1][1] = max(enomena[-1][1], telos)
        else:
            enomena.append([arxi, telos])
    return [(arxi, telos) for arxi, telos in enomena]


def _deuterolepta(diastimata: list[tuple[datetime, datetime]]) -> float:
    """Returns a total in observed wall-clock seconds for merged intervals."""
    return sum(
        (telos - arxi).total_seconds() for arxi, telos in _enosi_diastimaton(diastimata)
    )


def _epikalipsi_deuterolepton(
    aristera: list[tuple[datetime, datetime]], deksia: list[tuple[datetime, datetime]]
) -> float:
    """Returns the duration where two already unioned interval sets overlap."""
    aristeri_enosi = _enosi_diastimaton(aristera)
    deksia_enosi = _enosi_diastimaton(deksia)
    synolo = 0.0
    aristeros_deiktis = 0
    deksios_deiktis = 0
    while aristeros_deiktis < len(aristeri_enosi) and deksios_deiktis < len(
        deksia_enosi
    ):
        aristeri_arxi, aristero_telos = aristeri_enosi[aristeros_deiktis]
        deksia_arxi, deksi_telos = deksia_enosi[deksios_deiktis]
        synolo += max(
            0.0,
            (
                min(aristero_telos, deksi_telos) - max(aristeri_arxi, deksia_arxi)
            ).total_seconds(),
        )
        if aristero_telos <= deksi_telos:
            aristeros_deiktis += 1
        else:
            deksios_deiktis += 1
    return synolo


def _keno_xronou(
    katastasi: str, pigi: str, methodos: str, simeiosi: str
) -> dict[str, object]:
    """Builds an unavailable activity report without fabricating zeros."""
    return {
        "status": katastasi,
        "source": pigi,
        "method": methodos,
        "scope": "Supplied intervals only; not a complete PC-time record.",
        "note": simeiosi,
        "active_seconds": None,
        "afk_seconds": None,
        "coverage": {
            "events_total": 0,
            "events_used": 0,
            "events_ignored": 0,
            "timestamps_unknown": 0,
            "unknown_intervals": 0,
            "partial": katastasi != "ok",
        },
        "by_day": [],
    }


def diavase_energo_xrono(
    diadromi: Path,
    apo: date | None = None,
    eos: date | None = None,
    zoni: str = "Europe/Athens",
) -> dict[str, object]:
    """Reads explicit ActivityWatch AFK buckets or the documented interval CSV.

    ActivityWatch ``not-afk`` events are active; ``afk`` events subtract from
    the union of active intervals. Unsupported states and zero-length
    heartbeats stay unknown. Results describe only supplied watcher data.
    """
    orio_arxis, orio_telous, antikeimeno_zonis = _orismata_imerominion(apo, eos, zoni)
    einai_csv = diadromi.suffix.casefold() == ".csv"
    pigi = "recorded CSV" if einai_csv else "ActivityWatch"
    methodos = (
        "explicit_active_afk_interval_union"
        if einai_csv
        else "aw_afk_status_intervals_union"
    )
    dedomena, sfalma_anagnosis = _diavase_bytes(diadromi)
    if dedomena is None:
        katastasi = "partial" if sfalma_anagnosis == "too_large" else "missing"
        return _keno_xronou(
            katastasi, pigi, methodos, sfalma_anagnosis or "unavailable"
        )

    if einai_csv:
        diastimata, kalypsi, egkyri_pigi = _diavase_csv_xronou(
            dedomena, antikeimeno_zonis, orio_arxis, orio_telous
        )
    else:
        diastimata, kalypsi, egkyri_pigi = _diavase_activitywatch(
            dedomena, antikeimeno_zonis, orio_arxis, orio_telous
        )
    if not egkyri_pigi:
        katastasi = "partial" if kalypsi["partial"] else "unsupported"
        anafora = _keno_xronou(
            katastasi, pigi, methodos, "unsupported_or_malformed_source"
        )
        anafora["coverage"] = kalypsi
        return anafora

    grammes_imeron: list[dict[str, object]] = []
    times_imeron: dict[str, dict[str, list[tuple[datetime, datetime]]]] = {}
    for eidos, times in diastimata.items():
        for arxi, telos in times:
            for imera, arxi_tmimatos, telos_tmimatos in _spase_diastima_ana_mera(
                arxi, telos, antikeimeno_zonis
            ):
                times_imeron.setdefault(imera, {"active": [], "afk": []})[eidos].append(
                    (arxi_tmimatos, telos_tmimatos)
                )
    energo_synolo = 0.0
    anenergo_synolo = 0.0
    for imera in sorted(times_imeron):
        energa = times_imeron[imera]["active"]
        anenerga = times_imeron[imera]["afk"]
        anenerga_deuterolepta = _deuterolepta(anenerga)
        energa_deuterolepta = max(
            0.0, _deuterolepta(energa) - _epikalipsi_deuterolepton(energa, anenerga)
        )
        energo_synolo += energa_deuterolepta
        anenergo_synolo += anenerga_deuterolepta
        grammes_imeron.append(
            {
                "date": imera,
                "active_seconds": energa_deuterolepta,
                "afk_seconds": anenerga_deuterolepta,
            }
        )
    pliris = not bool(kalypsi["partial"])
    if not kalypsi["events_used"]:
        pliris = False
    kalypsi["partial"] = not pliris
    return {
        "status": "ok" if pliris else "partial",
        "source": pigi,
        "method": methodos,
        "scope": "Supplied intervals only; not a complete PC-time record.",
        "note": "Recorded watcher/CSV intervals; uncovered periods remain unknown.",
        "active_seconds": energo_synolo if kalypsi["events_used"] else None,
        "afk_seconds": anenergo_synolo if kalypsi["events_used"] else None,
        "coverage": kalypsi,
        "by_day": grammes_imeron,
    }


def _diavase_csv_xronou(
    dedomena: bytes,
    antikeimeno_zonis: ZoneInfo,
    orio_arxis: datetime | None,
    orio_telous: datetime | None,
) -> tuple[dict[str, list[tuple[datetime, datetime]]], dict[str, object], bool]:
    """Parses rows with ``start,end,status`` and explicit active/afk labels."""
    diastimata: dict[str, list[tuple[datetime, datetime]]] = {"active": [], "afk": []}
    kalypsi: dict[str, object] = _nea_kalypsi_xronou()
    try:
        periexomeno = dedomena.decode("utf-8-sig")
    except UnicodeDecodeError:
        kalypsi["partial"] = True
        return diastimata, kalypsi, False
    anagnostis = csv.DictReader(io.StringIO(periexomeno))
    if not anagnostis.fieldnames or not {"start", "end", "status"}.issubset(
        anagnostis.fieldnames
    ):
        kalypsi["partial"] = True
        return diastimata, kalypsi, False
    for deiktis, grammi in enumerate(anagnostis):
        if deiktis >= ORIO_EGGRAFON:
            _afxise_metriti(kalypsi, "events_ignored")
            kalypsi["partial"] = True
            continue
        _afxise_metriti(kalypsi, "events_total")
        arxi = _chronos_aware(grammi.get("start"))
        telos = _chronos_aware(grammi.get("end"))
        katastasi = (grammi.get("status") or "").strip().casefold()
        eidos = (
            "active"
            if katastasi == KATASTASI_ENERGOS_CSV
            else "afk"
            if katastasi == KATASTASI_AFK_CSV
            else None
        )
        if arxi is None or telos is None:
            _afxise_metriti(kalypsi, "timestamps_unknown")
        if eidos is None or arxi is None or telos is None or telos <= arxi:
            _agnoise_grammi_xronou(kalypsi, agnosto_diastima=True)
            continue
        perikommeni_arxi = max(arxi, orio_arxis) if orio_arxis else arxi
        perikommeno_telos = min(telos, orio_telous) if orio_telous else telos
        if perikommeno_telos <= perikommeni_arxi:
            _agnoise_grammi_xronou(kalypsi)
            continue
        diastimata[eidos].append((perikommeni_arxi, perikommeno_telos))
        _afxise_metriti(kalypsi, "events_used")
    return diastimata, kalypsi, True


def _diavase_activitywatch(
    dedomena: bytes,
    antikeimeno_zonis: ZoneInfo,
    orio_arxis: datetime | None,
    orio_telous: datetime | None,
) -> tuple[dict[str, list[tuple[datetime, datetime]]], dict[str, object], bool]:
    """Reads exported ``afkstatus`` buckets, not unrelated app/window buckets."""
    diastimata: dict[str, list[tuple[datetime, datetime]]] = {"active": [], "afk": []}
    kalypsi: dict[str, object] = _nea_kalypsi_xronou()
    try:
        fortio = _antikeimeno_json(json.loads(dedomena))
    except (json.JSONDecodeError, UnicodeDecodeError):
        kalypsi["partial"] = True
        return diastimata, kalypsi, False
    kadoi = fortio.get("buckets") if fortio is not None else None
    xartis_kadon = _antikeimeno_json(kadoi) if kadoi is not None else None
    if xartis_kadon is None:
        kalypsi["partial"] = True
        return diastimata, kalypsi, False
    vrethike_kados_afk = False
    grammes_pou_eidame = 0
    for kados in xartis_kadon.values():
        dedomena_kadou = _antikeimeno_json(kados)
        if dedomena_kadou is None or dedomena_kadou.get("type") != TYPOS_AFK_WATCHER:
            continue
        vrethike_kados_afk = True
        symvanta = dedomena_kadou.get("events")
        if not isinstance(symvanta, list):
            kalypsi["partial"] = True
            _afxise_metriti(kalypsi, "events_ignored")
            continue
        for symvan in symvanta:
            grammes_pou_eidame += 1
            if grammes_pou_eidame > ORIO_EGGRAFON:
                _afxise_metriti(kalypsi, "events_ignored")
                kalypsi["partial"] = True
                continue
            _afxise_metriti(kalypsi, "events_total")
            dedomena_symvantos = _antikeimeno_json(symvan)
            if dedomena_symvantos is None:
                _agnoise_grammi_xronou(kalypsi)
                continue
            arxi = _chronos_aware(dedomena_symvantos.get("timestamp"))
            timi_diarkeias = dedomena_symvantos.get("duration")
            dedomena_katastasis = _antikeimeno_json(dedomena_symvantos.get("data"))
            katastasi = (
                dedomena_katastasis.get("status")
                if dedomena_katastasis is not None
                else None
            )
            eidos = (
                "active"
                if katastasi == KATASTASI_ENERGOS_AW
                else "afk"
                if katastasi == KATASTASI_AFK_AW
                else None
            )
            if arxi is None:
                _afxise_metriti(kalypsi, "timestamps_unknown")
            diarkeia = _thetiki_diarkeia(timi_diarkeias)
            if eidos is None or arxi is None or diarkeia is None:
                _agnoise_grammi_xronou(kalypsi, agnosto_diastima=True)
                continue
            try:
                telos = arxi + timedelta(seconds=diarkeia)
            except OverflowError:
                _agnoise_grammi_xronou(kalypsi, agnosto_diastima=True)
                continue
            perikommeni_arxi = max(arxi, orio_arxis) if orio_arxis else arxi
            perikommeno_telos = min(telos, orio_telous) if orio_telous else telos
            if perikommeno_telos <= perikommeni_arxi:
                _agnoise_grammi_xronou(kalypsi)
                continue
            diastimata[eidos].append((perikommeni_arxi, perikommeno_telos))
            _afxise_metriti(kalypsi, "events_used")
    return diastimata, kalypsi, vrethike_kados_afk


def _nea_kalypsi_xronou() -> dict[str, object]:
    """Creates explicit interval coverage counters."""
    return {
        "events_total": 0,
        "events_used": 0,
        "events_ignored": 0,
        "timestamps_unknown": 0,
        "unknown_intervals": 0,
        "partial": False,
    }


def _afxise_metriti(kalypsi: dict[str, object], kleidi: str, poso: int = 1) -> None:
    """Increments a named coverage count in a generic result map."""
    timi = kalypsi.get(kleidi)
    trexon = timi if isinstance(timi, int) and not isinstance(timi, bool) else 0
    kalypsi[kleidi] = trexon + poso


def _agnoise_grammi_xronou(
    kalypsi: dict[str, object], agnosto_diastima: bool = False
) -> None:
    """Marks a source row as excluded without converting it into zero activity."""
    _afxise_metriti(kalypsi, "events_ignored")
    _afxise_metriti(kalypsi, "unknown_intervals", int(agnosto_diastima))
    kalypsi["partial"] = True


def _thetiki_diarkeia(timi: object) -> float | None:
    """Validates finite, positive event durations; zero heartbeats stay unknown."""
    if isinstance(timi, bool) or not isinstance(timi, (int, float)):
        return None
    try:
        diarkeia = float(timi)
    except OverflowError:
        return None
    return diarkeia if math.isfinite(diarkeia) and diarkeia > 0 else None


def diavase_kostos(
    diadromi: Path,
    apo: date | None = None,
    eos: date | None = None,
    zoni: str = "Europe/Athens",
) -> dict[str, object]:
    """Reads only user-supplied billed/estimated ledger values from CSV or JSON.

    Amounts are summed with ``Decimal`` and returned as decimal strings so JSON
    serialization does not lose ledger precision. No price lookup is performed.
    """
    orio_arxis, orio_telous, antikeimeno_zonis = _orismata_imerominion(apo, eos, zoni)
    dedomena, sfalma_anagnosis = _diavase_bytes(diadromi)
    if dedomena is None:
        return _keno_kostos(
            "missing" if sfalma_anagnosis != "too_large" else "partial",
            sfalma_anagnosis or "unavailable",
        )
    grammes, katastasi_analysis = _diavase_eggrafes_kostous(
        dedomena, diadromi.suffix.casefold()
    )
    if grammes is None:
        return _keno_kostos(katastasi_analysis, "malformed_or_unsupported_source")
    athroismata: dict[tuple[str, str], Decimal] = {}
    kalypsi: dict[str, object] = {
        "rows_total": len(grammes),
        "rows_used": 0,
        "rows_ignored": max(0, len(grammes) - ORIO_EGGRAFON),
        "timestamps_unknown": 0,
        "partial": len(grammes) > ORIO_EGGRAFON,
    }
    for grammi in grammes[:ORIO_EGGRAFON]:
        timi_xronou = grammi.get("timestamp")
        xronos = _chronos_aware(timi_xronou)
        if xronos is None:
            _afxise_metriti(kalypsi, "timestamps_unknown")
            kalypsi["partial"] = True
            if orio_arxis is not None or orio_telous is not None:
                _afxise_metriti(kalypsi, "rows_ignored")
                continue
        elif (orio_arxis is not None and xronos < orio_arxis) or (
            orio_telous is not None and xronos >= orio_telous
        ):
            _afxise_metriti(kalypsi, "rows_ignored")
            continue
        eggrafi = _egkyri_eggrafi_kostous(grammi)
        if eggrafi is None:
            _afxise_metriti(kalypsi, "rows_ignored")
            kalypsi["partial"] = True
            continue
        nomisma, eidos, poso = eggrafi
        with localcontext() as plaisio:
            plaisio.prec = AKRIVEIA_ATHROISMATOS
            athroismata[(nomisma, eidos)] = (
                athroismata.get((nomisma, eidos), MIDDEN) + poso
            )
        _afxise_metriti(kalypsi, "rows_used")
    pliris = not bool(kalypsi["partial"])
    if not grammes or not kalypsi["rows_used"]:
        return {
            "status": "partial",
            "source": "recorded ledger",
            "coverage": kalypsi,
            "totals": None,
        }
    return {
        "status": "ok" if pliris else "partial",
        "source": "recorded ledger",
        "coverage": kalypsi,
        "totals": [
            {"currency": nomisma, "kind": eidos, "amount": _keimeno_decimal(poso)}
            for (nomisma, eidos), poso in sorted(athroismata.items())
        ],
    }


def _diavase_eggrafes_kostous(
    dedomena: bytes, kataliksi: str
) -> tuple[list[dict[str, object]] | None, str]:
    """Reads CSV rows or documented JSON array/records objects."""
    if kataliksi == ".csv":
        try:
            periexomeno = dedomena.decode("utf-8-sig")
        except UnicodeDecodeError:
            return None, "partial"
        anagnostis = csv.DictReader(io.StringIO(periexomeno))
        apaitoumena = {"timestamp", "provider", "model", "amount", "currency", "kind"}
        if not anagnostis.fieldnames or not apaitoumena.issubset(anagnostis.fieldnames):
            return None, "unsupported"
        grammes_csv = [cast(dict[str, object], grammi) for grammi in anagnostis]
        return grammes_csv, "ok"
    if kataliksi != ".json":
        return None, "unsupported"
    try:
        fortio = json.loads(dedomena, parse_float=Decimal)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, "partial"
    arxikes_grammes: object
    if isinstance(fortio, list):
        arxikes_grammes = fortio
    else:
        antikeimeno = _antikeimeno_json(fortio)
        arxikes_grammes = (
            antikeimeno.get("records") if antikeimeno is not None else None
        )
    if not isinstance(arxikes_grammes, list):
        return None, "unsupported"
    grammes: list[dict[str, object]] = []
    for arxiki_grammi in arxikes_grammes:
        xartografimeno = _antikeimeno_json(arxiki_grammi)
        grammes.append(xartografimeno if xartografimeno is not None else {})
    return grammes, "ok"


def _egkyri_eggrafi_kostous(
    grammi: dict[str, object],
) -> tuple[str, str, Decimal] | None:
    """Validates required recorded-ledger fields without live price inference."""
    paroxos = grammi.get("provider")
    montelo = grammi.get("model")
    arxiko_poso = grammi.get("amount")
    arxiko_nomisma = grammi.get("currency")
    arxiko_eidos = grammi.get("kind")
    if not isinstance(paroxos, str) or not paroxos.strip():
        return None
    if not isinstance(montelo, str) or not montelo.strip():
        return None
    if isinstance(arxiko_poso, bool) or not isinstance(
        arxiko_poso, (str, int, float, Decimal)
    ):
        return None
    try:
        poso = Decimal(str(arxiko_poso))
    except InvalidOperation:
        return None
    if not poso.is_finite() or poso < MIDDEN:
        return None
    psifia = poso.as_tuple()
    if len(psifia.digits) > ORIO_PSIMION_POSOU or (
        isinstance(psifia.exponent, int) and abs(psifia.exponent) > ORIO_EKTHETI_POSOU
    ):
        return None
    if not isinstance(arxiko_nomisma, str) or not MORFI_NOMISMATOS.fullmatch(
        arxiko_nomisma.strip().upper()
    ):
        return None
    if not isinstance(arxiko_eidos, str) or arxiko_eidos not in EIDI_KOSTOUS:
        return None
    return arxiko_nomisma.strip().upper(), arxiko_eidos, poso


def _keimeno_decimal(poso: Decimal) -> str:
    """Serializes a finite total without scientific notation or float loss."""
    return format(poso, "f")


def _keno_kostos(katastasi: str, simeiosi: str) -> dict[str, object]:
    """Builds an unavailable cost report without inferring zero spend."""
    return {
        "status": katastasi,
        "source": "recorded ledger",
        "note": simeiosi,
        "coverage": {
            "rows_total": 0,
            "rows_used": 0,
            "rows_ignored": 0,
            "timestamps_unknown": 0,
            "partial": katastasi != "ok",
        },
        "totals": None,
    }
