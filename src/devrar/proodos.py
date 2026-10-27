"""Συγκρίνει αναφορές με ρητά compatibility και coverage όρια."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from datetime import date

logger = logging.getLogger(__name__)

EKDOSI_SYGKRISIS = "0.1"
METRIKA_SYNOLON = (
    "synedries",
    "rizikes",
    "ypopraktores",
    "minimata_xristi",
    "apantiseis",
    "kliseis_ergaleion",
    "tokens",
    "commits",
    "imeres",
)


def _xarti(timh: object) -> Mapping[str, object]:
    """Επιστρέφει mapping ή κενή mapping για ελλιπή report fields."""
    return timh if isinstance(timh, Mapping) else {}


def _lista_eggrafwn(timh: object) -> list[Mapping[str, object]]:
    """Κρατά μόνο mapping rows από sequence fields."""
    if not isinstance(timh, Sequence) or isinstance(timh, (str, bytes)):
        return []
    return [eggrafi for eggrafi in timh if isinstance(eggrafi, Mapping)]


def _imerominia(timh: object) -> date | None:
    """Αναλύει ISO date χωρίς να μαντεύει ελλιπές διάστημα."""
    if not isinstance(timh, str):
        return None
    try:
        return date.fromisoformat(timh)
    except ValueError:
        return None


def _katastasi_periodou(
    trexousa: Mapping[str, object], proigoumeni: Mapping[str, object]
) -> dict[str, str]:
    """Ελέγχει αν οι ημερομηνιακές περίοδοι επικαλύπτονται."""
    trexousa_apo = _imerominia(trexousa.get("apo"))
    trexousa_eos = _imerominia(trexousa.get("eos"))
    proigoumeni_apo = _imerominia(proigoumeni.get("apo"))
    proigoumeni_eos = _imerominia(proigoumeni.get("eos"))
    if (
        trexousa_apo is None
        or trexousa_eos is None
        or proigoumeni_apo is None
        or proigoumeni_eos is None
    ):
        return {
            "katastasi": "missing",
            "aitia": "One or both date periods are missing or invalid.",
        }
    if trexousa_apo <= proigoumeni_eos and proigoumeni_apo <= trexousa_eos:
        return {
            "katastasi": "overlapping",
            "aitia": (
                "The report periods overlap, so deltas could double-count activity."
            ),
        }
    return {
        "katastasi": "compatible",
        "aitia": "The report periods are valid and non-overlapping.",
    }


def _paragontas(katastasi: str, aitia: str) -> dict[str, str]:
    """Χτίζει εξηγημένο compatibility item."""
    return {"katastasi": katastasi, "aitia": aitia}


def _idia_timh(aristera: object, deksia: object, etiketa: str) -> dict[str, str]:
    """Συγκρίνει μία required compatibility τιμή."""
    if aristera is None or deksia is None:
        return _paragontas("missing", f"{etiketa} is missing from at least one report.")
    if aristera != deksia:
        return _paragontas("incompatible", f"{etiketa} differs between reports.")
    return _paragontas("compatible", f"{etiketa} matches.")


def _onomata_pigwn(anafora: Mapping[str, object]) -> frozenset[str] | None:
    """Εξάγει ονόματα πηγών μόνο όταν το source set έχει καταγραφεί."""
    if "piges" not in anafora:
        return None
    onomata = {
        onoma
        for eggrafi in _lista_eggrafwn(anafora.get("piges"))
        if isinstance((onoma := eggrafi.get("onoma")), str)
    }
    return frozenset(onomata)


def _kalypsi(anafora: Mapping[str, object]) -> str:
    """Συνοψίζει source coverage, Git deltas και bounded-analysis truncation."""
    piges = _lista_eggrafwn(anafora.get("piges"))
    analysi = _xarti(anafora.get("kalypsi_analysi"))
    epeisodia = _xarti(anafora.get("epeisodia_ergasias"))
    if any(eggrafi.get("katastasi") in {"partial", "missing"} for eggrafi in piges):
        return "partial"
    if "git_diafores" in anafora:
        git_diafores = _xarti(anafora.get("git_diafores"))
        if git_diafores.get("katastasi") != "ok":
            return "partial"
    if (
        analysi.get("perikopi") is True
        or _xarti(epeisodia.get("kalypsi")).get("perikopi") is True
    ):
        return "truncated"
    if "piges" not in anafora and "kalypsi_analysi" not in anafora:
        return "missing"
    return "complete"


def _epeisodia(anafora: Mapping[str, object]) -> list[Mapping[str, object]]:
    """Επιστρέφει analyzer summaries ή raw metrics episodes."""
    analysi = _xarti(anafora.get("epeisodia_ergasias"))
    if "paratiriseis" in analysi:
        return _lista_eggrafwn(analysi.get("paratiriseis"))
    metrika = _xarti(anafora.get("metrika_ergasias"))
    return _lista_eggrafwn(metrika.get("epeisodia"))


def _metrika_epeisodiwn(anafora: Mapping[str, object]) -> dict[str, int | None]:
    """Υπολογίζει μετρημένες εκβάσεις μόνο από episode-level recorded counters."""
    epeisodia = _epeisodia(anafora)
    if not epeisodia:
        return {
            "episodes_total": 0
            if "metrika_ergasias" in anafora or "epeisodia_ergasias" in anafora
            else None,
            "episodes_observed_success": 0,
            "episodes_observed_failure": 0,
            "tests_passed": None,
            "tests_failed": None,
            "tests_skipped": None,
            "workflow_cues": None,
        }
    katastaseis = [eggrafi.get("katastasi") for eggrafi in epeisodia]
    perasmena = apotyxhmena = paraleifthenta = 0
    dokimes_gnwstes = False
    for epeisodio in epeisodia:
        metrisi = _xarti(epeisodio.get("metrisi")) or epeisodio
        for kleidi, syssoreutis in (
            ("tests_passed", "passed"),
            ("tests_failed", "failed"),
            ("tests_skipped", "skipped"),
        ):
            timh = metrisi.get(kleidi)
            if isinstance(timh, int) and not isinstance(timh, bool) and timh >= 0:
                dokimes_gnwstes = True
                if syssoreutis == "passed":
                    perasmena += timh
                elif syssoreutis == "failed":
                    apotyxhmena += timh
                else:
                    paraleifthenta += timh
    paratiriseis = 0
    roes_gnwstes = False
    axiologisi = _xarti(anafora.get("axiologisi"))
    for diastasi in _lista_eggrafwn(axiologisi.get("diastaseis")):
        timh = diastasi.get("paratiriseis")
        if isinstance(timh, int) and not isinstance(timh, bool) and timh >= 0:
            roes_gnwstes = True
            paratiriseis += timh
    return {
        "episodes_total": len(epeisodia),
        "episodes_observed_success": sum(
            katastasi == "observed_success" for katastasi in katastaseis
        ),
        "episodes_observed_failure": sum(
            katastasi in {"observed_failure", "mixed"} for katastasi in katastaseis
        ),
        "tests_passed": perasmena if dokimes_gnwstes else None,
        "tests_failed": apotyxhmena if dokimes_gnwstes else None,
        "tests_skipped": paraleifthenta if dokimes_gnwstes else None,
        "workflow_cues": paratiriseis if roes_gnwstes else None,
    }


def _times_metrikwn(anafora: Mapping[str, object]) -> dict[str, int | float | None]:
    """Συνδυάζει report totals και evidence-aware episode metrics."""
    synola = _xarti(anafora.get("synola"))
    times: dict[str, int | float | None] = {}
    for kleidi in METRIKA_SYNOLON:
        timh = synola.get(kleidi)
        times[f"synola.{kleidi}"] = (
            timh
            if isinstance(timh, (int, float)) and not isinstance(timh, bool)
            else None
        )
    times.update(
        {
            f"episodia.{kleidi}": timh
            for kleidi, timh in _metrika_epeisodiwn(anafora).items()
        }
    )
    return times


def _sygkrisi_metrikou(
    trexousa: int | float | None,
    proigoumeni: int | float | None,
    geniki_katastasi: str,
    katastasi_kalypsis: str,
    trexousa_kalypsi: str,
    proigoumeni_kalypsi: str,
) -> dict[str, object]:
    """Δίνει nullable deltas με μηδενικό baseline ασφαλές ως undefined percent."""
    if geniki_katastasi != "compatible":
        return {
            "katastasi": geniki_katastasi,
            "kalypsi": {
                "trexousa": trexousa_kalypsi,
                "proigoumeni": proigoumeni_kalypsi,
            },
            "trexousa": trexousa,
            "proigoumeni": proigoumeni,
            "delta": None,
            "pososto": None,
            "aitia": "Global report compatibility does not permit a delta.",
        }
    if trexousa is None or proigoumeni is None:
        return {
            "katastasi": "missing",
            "kalypsi": {
                "trexousa": trexousa_kalypsi,
                "proigoumeni": proigoumeni_kalypsi,
            },
            "trexousa": trexousa,
            "proigoumeni": proigoumeni,
            "delta": None,
            "pososto": None,
            "aitia": "One or both metric values are unknown.",
        }
    diafora = trexousa - proigoumeni
    pososto = (diafora / proigoumeni * 100) if proigoumeni != 0 else None
    katastasi = (
        "partial" if katastasi_kalypsis in {"partial", "truncated"} else "compatible"
    )
    aitia = (
        "Coverage is partial; the delta describes recorded subsets only."
        if katastasi == "partial"
        else "Values are comparable for non-overlapping, compatible reports."
    )
    return {
        "katastasi": katastasi,
        "kalypsi": {"trexousa": trexousa_kalypsi, "proigoumeni": proigoumeni_kalypsi},
        "trexousa": trexousa,
        "proigoumeni": proigoumeni,
        "delta": diafora,
        "pososto": pososto,
        "aitia": aitia,
    }


def sygkrine_anafores(
    trexousa: Mapping[str, object], proigoumeni: Mapping[str, object]
) -> dict[str, object]:
    """Επιστρέφει comparison payload χωρίς baseline excerpts ή αιτιότητα."""
    trexousa_periodos = _xarti(trexousa.get("periodos"))
    proigoumeni_periodos = _xarti(proigoumeni.get("periodos"))
    trexousa_analysi = _xarti(trexousa.get("analysi"))
    proigoumeni_analysi = _xarti(proigoumeni.get("analysi"))
    trexousa_scope = _xarti(trexousa.get("scope_git"))
    proigoumeni_scope = _xarti(proigoumeni.get("scope_git"))
    trexouses_piges = _onomata_pigwn(trexousa)
    proigoumenes_piges = _onomata_pigwn(proigoumeni)
    paragontes = {
        "leitourgia": _idia_timh(
            trexousa.get("leitourgia"), proigoumeni.get("leitourgia"), "Demo/live mode"
        ),
        "ekdosi_sximatos": _idia_timh(
            trexousa.get("ekdosi_sximatos"),
            proigoumeni.get("ekdosi_sximatos"),
            "Schema version",
        ),
        "rubrika": _idia_timh(
            trexousa_analysi.get("rubrika"),
            proigoumeni_analysi.get("rubrika"),
            "Rubric version",
        ),
        "zoni": _idia_timh(
            trexousa_periodos.get("zoni"), proigoumeni_periodos.get("zoni"), "Timezone"
        ),
        "piges": _idia_timh(trexouses_piges, proigoumenes_piges, "Source set"),
        "scope_git_author": _idia_timh(
            [trexousa_scope["author"]] if "author" in trexousa_scope else None,
            [proigoumeni_scope["author"]] if "author" in proigoumeni_scope else None,
            "Git author scope",
        ),
        "repositories": _idia_timh(
            trexousa_scope.get("repositories"),
            proigoumeni_scope.get("repositories"),
            "Selected repository identities",
        ),
        "periodos": _katastasi_periodou(trexousa_periodos, proigoumeni_periodos),
    }
    trexousa_kalypsi = _kalypsi(trexousa)
    proigoumeni_kalypsi = _kalypsi(proigoumeni)
    paragontes["kalypsi"] = _paragontas(
        "truncated"
        if "truncated" in {trexousa_kalypsi, proigoumeni_kalypsi}
        else "partial"
        if "partial" in {trexousa_kalypsi, proigoumeni_kalypsi}
        else (
            "missing"
            if "missing" in {trexousa_kalypsi, proigoumeni_kalypsi}
            else "compatible"
        ),
        "Current coverage is "
        f"{trexousa_kalypsi}; baseline coverage is {proigoumeni_kalypsi}.",
    )
    blokarontes = [
        eggrafi["katastasi"]
        for kleidi, eggrafi in paragontes.items()
        if kleidi != "kalypsi" and eggrafi["katastasi"] != "compatible"
    ]
    geniki_katastasi = (
        "compatible"
        if not blokarontes
        else (
            "overlapping"
            if "overlapping" in blokarontes
            else "missing"
            if "missing" in blokarontes
            else "incompatible"
        )
    )
    katastasi_kalypsis = paragontes["kalypsi"]["katastasi"]
    trexouses_times = _times_metrikwn(trexousa)
    proigoumenes_times = _times_metrikwn(proigoumeni)
    sygkriseis = {
        kleidi: _sygkrisi_metrikou(
            timh,
            proigoumenes_times.get(kleidi),
            geniki_katastasi,
            katastasi_kalypsis,
            trexousa_kalypsi,
            proigoumeni_kalypsi,
        )
        for kleidi, timh in trexouses_times.items()
    }
    return {
        "ekdosi": EKDOSI_SYGKRISIS,
        "katastasi": geniki_katastasi,
        "symvatotita": paragontes,
        "metrika": sygkriseis,
        "periorismoi": [
            "Deltas describe activity and observed checks; volume does not "
            "establish skill, seniority, or progress causality.",
            "A zero baseline has no defined percent change.",
        ],
    }
