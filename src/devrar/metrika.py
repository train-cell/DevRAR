"""Streaming aggregates for observable, in-scope coding work events."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from devrar.symvanta import SymvanErgasias

logger = logging.getLogger(__name__)

ORA_BUCKETS = 24
MAX_EPEISODIA = 500
MAX_TEKMIRIA_ANA_EPEISODIO = 5
MAX_APOSPASMA_CHARS = 500
MIN_IDLE_MINUTES = 1
MAX_IDLE_MINUTES = 24 * 60
PROTERAIOTITA_LOIPOU = 0
PROTERAIOTITA_TOOL_RESULT = 1
PROTERAIOTITA_EPITYXIAS = 2
PROTERAIOTITA_APOTYXIAS = 3
PROTERAIOTITA_MIKTOU = 4

_PYTEST_SUMMARY = re.compile(
    r"^\s*={2,}\s*(?P<summary>.*?)\s*={2,}\s*$"
    r"|^\s*(?P<plain>\d+\s+(?:passed|failed|skipped)"
    r"(?:,\s*\d+\s+(?:passed|failed|skipped))*\s+in\s+\S+)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_PYTEST_COUNT = re.compile(r"(\d+)\s+(passed|failed|skipped)\b", re.IGNORECASE)
_UNITTEST_RAN = re.compile(r"^Ran\s+(\d+)\s+tests?\s+in\s+\S+", re.MULTILINE)
_UNITTEST_FAILED = re.compile(r"^FAILED\s*\(([^)]*)\)", re.MULTILINE)
_UNITTEST_COUNT = re.compile(r"(failures|errors|skipped)=(\d+)")
_TAP_RESULT = re.compile(r"^(not[ \t]+)?ok(?:[ \t]+[^\n]*)?[ \t\r]*$", re.MULTILINE)
_TAP_ODIGIA = re.compile(r"#\s*(TODO|SKIP)\b", re.IGNORECASE)


@dataclass
class _SynopsiTests:
    """Κρατάει τα μετρημένα αποτελέσματα ενός ρητού test summary."""

    perasmena: int = 0
    apotyximena: int = 0
    paraleifthenta: int = 0
    anamenomena: int = 0
    paratirimeno: bool = False

    def prosthese(self, alli: _SynopsiTests) -> None:
        """Προσθέτει μόνο counts που προήλθαν από αναγνωρισμένο format."""
        if alli.paratirimeno:
            self.perasmena += alli.perasmena
            self.apotyximena += alli.apotyximena
            self.paraleifthenta += alli.paraleifthenta
            self.anamenomena += alli.anamenomena
            self.paratirimeno = True


@dataclass
class _Epeisodio:
    """Συνοψίζει ένα επιλεγμένο source/session χωρίς raw event objects."""

    pigi: str
    synedria: str
    erotimata: int = 0
    kliseis_ergaleion: int = 0
    apotelesmata_ergaleion: int = 0
    exodoi_epityxias: int = 0
    exodoi_apotyxias: int = 0
    dokimes: _SynopsiTests = field(default_factory=_SynopsiTests)
    tekmiria: list[dict[str, object]] = field(default_factory=list)
    proteraiotites: list[int] = field(default_factory=list)
    diathesima_tekmiria: int = 0


@dataclass
class _MetrisiPigis:
    """Συγκεντρώνει πλήρη counters ανά πηγή."""

    symvanta: int = 0
    erotimata: int = 0
    kliseis_ergaleion: int = 0
    apotelesmata_ergaleion: int = 0
    dokimes: _SynopsiTests = field(default_factory=_SynopsiTests)


def _analuse_xrono(timi: str | None) -> datetime | None:
    """Επιστρέφει μόνο έγκυρο aware ISO timestamp σε UTC."""
    if timi is None:
        return None
    try:
        analyomeno = datetime.fromisoformat(timi.replace("Z", "+00:00"))
    except (ValueError, OverflowError):
        return None
    if analyomeno.tzinfo is None or analyomeno.utcoffset() is None:
        return None
    return analyomeno.astimezone(timezone.utc)


def _analuse_synopsi_tests(keimeno: str) -> _SynopsiTests:
    """Αναγνωρίζει μόνο ρητές pytest, unittest και TAP συνοψίσεις."""
    apotelesma = _SynopsiTests()
    synopseis_pytest: set[str] = set()
    for taftisi in _PYTEST_SUMMARY.finditer(keimeno):
        synopsi = taftisi.group("summary") or taftisi.group("plain") or ""
        tautotita = " ".join(synopsi.casefold().split())
        if not tautotita or tautotita in synopseis_pytest:
            continue
        times: dict[str, int] = {}
        for plithos, ekvasi in _PYTEST_COUNT.findall(synopsi):
            kanonikopoiimeno = ekvasi.casefold()
            times[kanonikopoiimeno] = times.get(kanonikopoiimeno, 0) + int(plithos)
        if times:
            synopseis_pytest.add(tautotita)
            apotelesma.perasmena += times.get("passed", 0)
            apotelesma.apotyximena += times.get("failed", 0)
            apotelesma.paraleifthenta += times.get("skipped", 0)
    if synopseis_pytest:
        apotelesma.paratirimeno = True
        return apotelesma

    synopseis_unittest: set[str] = set()
    ekteleseis = list(_UNITTEST_RAN.finditer(keimeno))
    for deiktis, ektelesi in enumerate(ekteleseis):
        telos_tmimatos = (
            ekteleseis[deiktis + 1].start()
            if deiktis + 1 < len(ekteleseis)
            else len(keimeno)
        )
        tmima = keimeno[ektelesi.start() : telos_tmimatos]
        tautotita = " ".join(tmima.casefold().split())
        if tautotita in synopseis_unittest:
            continue
        synolo = int(ektelesi.group(1))
        taftisi_apotyxias = _UNITTEST_FAILED.search(tmima)
        if taftisi_apotyxias is None and re.search(r"^OK(?:\s|$)", tmima, re.MULTILINE):
            paraleifthenta = re.search(r"skipped=(\d+)", tmima)
            plithos_paraleipseon = int(paraleifthenta.group(1)) if paraleifthenta else 0
            apotelesma.paraleifthenta += plithos_paraleipseon
            apotelesma.perasmena += max(0, synolo - plithos_paraleipseon)
            synopseis_unittest.add(tautotita)
        elif taftisi_apotyxias is not None:
            metriseis = {
                onoma: int(timi)
                for onoma, timi in _UNITTEST_COUNT.findall(taftisi_apotyxias.group(1))
            }
            plithos_apotyxion = metriseis.get("failures", 0) + metriseis.get(
                "errors", 0
            )
            plithos_paraleipseon = metriseis.get("skipped", 0)
            apotelesma.apotyximena += plithos_apotyxion
            apotelesma.paraleifthenta += plithos_paraleipseon
            apotelesma.perasmena += max(
                0, synolo - plithos_apotyxion - plithos_paraleipseon
            )
            synopseis_unittest.add(tautotita)
    if synopseis_unittest:
        apotelesma.paratirimeno = True
        return apotelesma

    tap = list(_TAP_RESULT.finditer(keimeno))
    if tap:
        for taftisi in tap:
            odigia = _TAP_ODIGIA.search(taftisi.group(0))
            if odigia and odigia.group(1).casefold() == "todo":
                apotelesma.anamenomena += 1
            elif odigia:
                apotelesma.paraleifthenta += 1
            elif taftisi.group(1):
                apotelesma.apotyximena += 1
            else:
                apotelesma.perasmena += 1
        apotelesma.paratirimeno = True
    return apotelesma


class SyllogistisMetrikon:
    """Υπολογίζει streaming activity, bounded episodes και observed test outcomes."""

    def __init__(self, zoni: str = "Europe/Athens", idle_minutes: int = 15) -> None:
        """Ρυθμίζει ζώνη ώρας και ανώτατο κενό για observed-event intervals."""
        if not MIN_IDLE_MINUTES <= idle_minutes <= MAX_IDLE_MINUTES:
            raise ValueError("idle_minutes εκτός επιτρεπτού εύρους")
        try:
            self._zoni = ZoneInfo(zoni)
        except (ZoneInfoNotFoundError, ValueError) as sfalma:
            raise ValueError(f"Άγνωστη ζώνη ώρας: {zoni}") from sfalma
        self._onoma_zonis = zoni
        self._lepta_adraneias = idle_minutes
        self._orio_adraneias = timedelta(minutes=idle_minutes)
        self._idomena: set[tuple[str, str]] = set()
        self._symvanta = 0
        self._agnostoi_xronoi = 0
        self._ores = [0] * ORA_BUCKETS
        self._imeres: dict[str, int] = {}
        self._piges: dict[str, _MetrisiPigis] = {}
        self._epeisodia: dict[tuple[str, str], _Epeisodio] = {}
        self._idomena_epeisodia: set[tuple[str, str]] = set()
        self._diathesima_epeisodia = 0
        self._xronoi: dict[tuple[str, str], set[datetime]] = {}
        self._oles_dokimes = _SynopsiTests()

    def prosthese(self, symvan: SymvanErgasias) -> None:
        """Ενσωματώνει ένα accepted event μία φορά, χωρίς να κρατά το raw event."""
        kleidi_symvantos = (symvan["pigi"], symvan["id"])
        if kleidi_symvantos in self._idomena:
            return
        self._idomena.add(kleidi_symvantos)
        self._symvanta += 1
        pigi = symvan["pigi"]
        metrisi_pigis = self._piges.setdefault(pigi, _MetrisiPigis())
        metrisi_pigis.symvanta += 1

        chronos = _analuse_xrono(symvan["chronos"])
        if chronos is None:
            self._agnostoi_xronoi += 1
        else:
            topikos = chronos.astimezone(self._zoni)
            if symvan["rolos"] == "user" and symvan["eidos"] == "prompt":
                self._ores[topikos.hour] += 1
                imera = topikos.date().isoformat()
                self._imeres[imera] = self._imeres.get(imera, 0) + 1
            kleidi = (pigi, symvan["synedria"])
            self._xronoi.setdefault(kleidi, set()).add(chronos)

        erotima = symvan["rolos"] == "user" and symvan["eidos"] == "prompt"
        klisi_ergaleiou = symvan["eidos"] == "tool_call"
        apotelesma_ergaleiou = symvan["eidos"] == "tool_result"
        metrisi_pigis.erotimata += int(erotima)
        metrisi_pigis.kliseis_ergaleion += int(klisi_ergaleiou)
        metrisi_pigis.apotelesmata_ergaleion += int(apotelesma_ergaleiou)

        kleidi = (pigi, symvan["synedria"])
        epeisodio = self._epeisodia.get(kleidi)
        if kleidi not in self._idomena_epeisodia:
            self._idomena_epeisodia.add(kleidi)
            self._diathesima_epeisodia += 1
            if len(self._epeisodia) < MAX_EPEISODIA:
                epeisodio = _Epeisodio(pigi, symvan["synedria"])
                self._epeisodia[kleidi] = epeisodio
        if epeisodio is not None:
            epeisodio.erotimata += int(erotima)
            epeisodio.kliseis_ergaleion += int(klisi_ergaleiou)
            epeisodio.apotelesmata_ergaleion += int(apotelesma_ergaleiou)

        if (
            apotelesma_ergaleiou
            and symvan["rolos"] == "tool"
            and symvan["kodikos_exodou"] is not None
        ):
            if symvan["kodikos_exodou"] == 0:
                if epeisodio is not None:
                    epeisodio.exodoi_epityxias += 1
            elif epeisodio is not None:
                epeisodio.exodoi_apotyxias += 1

        dokimes = (
            _analuse_synopsi_tests(symvan["keimeno"])
            if symvan["rolos"] == "tool" and apotelesma_ergaleiou
            else _SynopsiTests()
        )
        metrisi_pigis.dokimes.prosthese(dokimes)
        self._oles_dokimes.prosthese(dokimes)
        if epeisodio is not None:
            epeisodio.dokimes.prosthese(dokimes)
        if epeisodio is not None:
            epeisodio.diathesima_tekmiria += 1
        if epeisodio is not None:
            apospasma = symvan["keimeno"][:MAX_APOSPASMA_CHARS]
            if (
                dokimes.paratirimeno
                and symvan["rolos"] == "tool"
                and apotelesma_ergaleiou
            ):
                apospasma = _exagage_tekmirio_tests(symvan["keimeno"]) or ""
            kodikos = (
                symvan["kodikos_exodou"]
                if symvan["rolos"] == "tool" and apotelesma_ergaleiou
                else None
            )
            epityxia = dokimes.perasmena > 0 or kodikos == 0
            apotyxia = dokimes.apotyximena > 0 or (kodikos is not None and kodikos != 0)
            proteraiotita = (
                PROTERAIOTITA_MIKTOU
                if epityxia and apotyxia
                else PROTERAIOTITA_APOTYXIAS
                if apotyxia
                else PROTERAIOTITA_EPITYXIAS
                if epityxia
                else PROTERAIOTITA_TOOL_RESULT
                if apotelesma_ergaleiou
                else PROTERAIOTITA_LOIPOU
            )
            _krata_tekmirio(
                epeisodio,
                {
                    "id": symvan["id"],
                    "pigi": pigi,
                    "synedria": symvan["synedria"],
                    "locator": symvan["locator"],
                    "rolos": symvan["rolos"],
                    "eidos": symvan["eidos"],
                    "apospasma": apospasma,
                    "kodikos_exodou": kodikos,
                },
                proteraiotita,
            )

    def apotelesma(self) -> dict[str, object]:
        """Επιστρέφει report fragment με bounded citations και full-stream counts."""
        diastimata: list[tuple[datetime, datetime]] = []
        for simeia in self._xronoi.values():
            taxinomimena = sorted(simeia)
            for arxi, telos in zip(taxinomimena, taxinomimena[1:]):
                if telos - arxi <= self._orio_adraneias:
                    diastimata.append((arxi, telos))
        lepta_diastimaton: int | None
        if diastimata:
            diastimata.sort()
            enomena: list[list[datetime]] = []
            for arxi, telos in diastimata:
                if enomena and arxi <= enomena[-1][1]:
                    enomena[-1][1] = max(enomena[-1][1], telos)
                else:
                    enomena.append([arxi, telos])
            lepta_diastimaton = sum(
                int((telos - arxi).total_seconds() // 60) for arxi, telos in enomena
            )
        else:
            lepta_diastimaton = None

        synopsi_tests: dict[str, object] = {
            "status": "observed"
            if self._oles_dokimes.paratirimeno
            else "no_observed_tests",
            "passed": self._oles_dokimes.perasmena
            if self._oles_dokimes.paratirimeno
            else None,
            "failed": self._oles_dokimes.apotyximena
            if self._oles_dokimes.paratirimeno
            else None,
            "skipped": self._oles_dokimes.paraleifthenta
            if self._oles_dokimes.paratirimeno
            else None,
        }
        if self._oles_dokimes.anamenomena:
            synopsi_tests["todo"] = self._oles_dokimes.anamenomena
        metrika: dict[str, object] = {
            "zoni": self._onoma_zonis,
            "idle_minutes": self._lepta_adraneias,
            "ora": [
                {"ora": ora, "prompts": plithos}
                for ora, plithos in enumerate(self._ores)
            ],
            "imeres": [
                {"imerominia": imera, "prompts": self._imeres[imera]}
                for imera in sorted(self._imeres)
            ],
            "timestamps_unknown": self._agnostoi_xronoi,
            "events": self._symvanta,
            "interval_estimate_minutes": lepta_diastimaton,
            "interval_estimate_status": (
                "observed_pairs_only"
                if diastimata
                else "no_bounded_pairs"
                if self._xronoi
                else "no_timestamps"
            ),
            "sources": [
                {
                    "pigi": pigi,
                    "events": metrisi.symvanta,
                    "prompts": metrisi.erotimata,
                    "tool_calls": metrisi.kliseis_ergaleion,
                    "tool_results": metrisi.apotelesmata_ergaleion,
                    "tests_passed": metrisi.dokimes.perasmena
                    if metrisi.dokimes.paratirimeno
                    else None,
                    "tests_failed": metrisi.dokimes.apotyximena
                    if metrisi.dokimes.paratirimeno
                    else None,
                    "tests_skipped": (
                        metrisi.dokimes.paraleifthenta
                        if metrisi.dokimes.paratirimeno
                        else None
                    ),
                }
                for pigi, metrisi in sorted(self._piges.items())
            ],
            "test_summary": synopsi_tests,
        }
        epeisodia: list[dict[str, object]] = []
        for deiktis, ((pigi, synedria), epeisodio) in enumerate(
            self._epeisodia.items(), start=1
        ):
            paratirimeno = epeisodio.dokimes.paratirimeno
            epeisodia.append(
                {
                    "id": f"W{deiktis:04d}",
                    "pigi": pigi,
                    "synedria": synedria,
                    "prompts": epeisodio.erotimata,
                    "tool_calls": epeisodio.kliseis_ergaleion,
                    "tool_results": epeisodio.apotelesmata_ergaleion,
                    "tests_passed": epeisodio.dokimes.perasmena
                    if paratirimeno
                    else None,
                    "tests_failed": epeisodio.dokimes.apotyximena
                    if paratirimeno
                    else None,
                    "tests_skipped": epeisodio.dokimes.paraleifthenta
                    if paratirimeno
                    else None,
                    "tests_status": "observed" if paratirimeno else "no_observed_tests",
                    "exit_success": epeisodio.exodoi_epityxias,
                    "exit_failure": epeisodio.exodoi_apotyxias,
                    "tekmiria": list(epeisodio.tekmiria),
                    "tekmiria_included": len(epeisodio.tekmiria),
                    "tekmiria_eligible": epeisodio.diathesima_tekmiria,
                    "tekmiria_truncated": (
                        epeisodio.diathesima_tekmiria > len(epeisodio.tekmiria)
                    ),
                }
            )
        return {
            **metrika,
            "epeisodia": epeisodia,
            "episodes_included": len(epeisodia),
            "episodes_eligible": self._diathesima_epeisodia,
            "episodes_truncated": self._diathesima_epeisodia > len(epeisodia),
        }


def _krata_tekmirio(
    epeisodio: _Epeisodio, tekmirio: dict[str, object], proteraiotita: int
) -> None:
    """Προτιμά actual outcomes στο cap και διατηρεί διαφορετικά outcome είδη."""
    if len(epeisodio.tekmiria) < MAX_TEKMIRIA_ANA_EPEISODIO:
        epeisodio.tekmiria.append(tekmirio)
        epeisodio.proteraiotites.append(proteraiotita)
        return
    ypopsifies = [
        thesi
        for thesi, vathmos in enumerate(epeisodio.proteraiotites)
        if vathmos < PROTERAIOTITA_EPITYXIAS
        or epeisodio.proteraiotites.count(vathmos) > 1
    ]
    thesi = min(ypopsifies, key=lambda deiktis: epeisodio.proteraiotites[deiktis])
    elaxisto = epeisodio.proteraiotites[thesi]
    ananeosi = proteraiotita > elaxisto
    diaforetiko_outcome = (
        proteraiotita >= PROTERAIOTITA_EPITYXIAS
        and proteraiotita not in epeisodio.proteraiotites
    )
    if ananeosi or diaforetiko_outcome:
        epeisodio.tekmiria[thesi] = tekmirio
        epeisodio.proteraiotites[thesi] = proteraiotita


def anagnorise_ekvaseis_tests(keimeno: str) -> tuple[int, int, int] | None:
    """Επιστρέφει observed counts από actual output, ποτέ από episode aggregates."""
    synopsi = _analuse_synopsi_tests(keimeno)
    return (
        (synopsi.perasmena, synopsi.apotyximena, synopsi.paraleifthenta)
        if synopsi.paratirimeno
        else None
    )


def _exagage_tekmirio_tests(keimeno: str) -> str | None:
    """Επιστρέφει μόνο το ακριβές, bounded summary που στήριξε τα test counts."""
    taftiseis_pytest = list(_PYTEST_SUMMARY.finditer(keimeno))
    if taftiseis_pytest:
        synopseis: list[str] = []
        tautotites: set[str] = set()
        for taftisi in taftiseis_pytest:
            synopsi = taftisi.group(0).strip()
            tautotita = " ".join(synopsi.casefold().split())
            if tautotita not in tautotites:
                synopseis.append(synopsi)
                tautotites.add(tautotita)
        return "\n".join(synopseis)[:MAX_APOSPASMA_CHARS]

    synopseis_unittest: list[str] = []
    ekteleseis = list(_UNITTEST_RAN.finditer(keimeno))
    for deiktis, taftisi in enumerate(ekteleseis):
        telos_tmimatos = (
            ekteleseis[deiktis + 1].start()
            if deiktis + 1 < len(ekteleseis)
            else len(keimeno)
        )
        tmima = keimeno[taftisi.start() : telos_tmimatos]
        teliki_taftisi = _UNITTEST_FAILED.search(tmima)
        if teliki_taftisi is not None:
            synopseis_unittest.append(tmima[: teliki_taftisi.end()].strip())
            continue
        ok = re.search(r"^OK(?:\s*\([^\n]*\))?", tmima, re.MULTILINE)
        if ok is not None:
            synopseis_unittest.append(tmima[: ok.end()].strip())
    if synopseis_unittest:
        return "\n".join(synopseis_unittest)[:MAX_APOSPASMA_CHARS]

    tap_summaries = [
        apotelesma.group(0) for apotelesma in _TAP_RESULT.finditer(keimeno)
    ]
    if tap_summaries:
        return "\n".join(tap_summaries)[:MAX_APOSPASMA_CHARS]
    return None
