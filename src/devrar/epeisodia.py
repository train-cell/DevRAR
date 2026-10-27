"""Παράγει συντηρητικές, τεκμηριωμένες παρατηρήσεις για work episodes."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence

from devrar.metrika import anagnorise_ekvaseis_tests

logger = logging.getLogger(__name__)

MAX_EPEISODIA = 100
MAX_TEKMIRIA = 3
MAX_PROTERAIOTITES = 3
EKDOSI_EPEISODION = "0.1"


def _lista_xartwn(timh: object) -> list[Mapping[str, object]]:
    """Επιστρέφει μόνο mapping rows από αδόμητη τιμή."""
    if not isinstance(timh, Sequence) or isinstance(timh, (str, bytes)):
        return []
    return [eggrafi for eggrafi in timh if isinstance(eggrafi, Mapping)]


def _plithos(timh: object) -> int | None:
    """Δέχεται μόνο μη αρνητικά ακέραια counters, όχι booleans."""
    if isinstance(timh, int) and not isinstance(timh, bool) and timh >= 0:
        return timh
    return None


def _tekmiria_egkyra(epeisodio: Mapping[str, object]) -> list[Mapping[str, object]]:
    """Κρατά exact citations από πραγματικά tool results ή recorded exits."""
    tekmiria = _lista_xartwn(epeisodio.get("tekmiria"))
    egkyra: list[Mapping[str, object]] = []
    for eggrafi in tekmiria:
        eidos = eggrafi.get("eidos")
        if eidos == "tool_result" and eggrafi.get("rolos") in (None, "tool"):
            egkyra.append(eggrafi)
    epilogi: list[Mapping[str, object]] = []
    epityxia = apotyxia = False
    for tekmirio in egkyra:
        perasmena, apotyximena = _metrisi_parapompon([tekmirio])
        if (perasmena and not epityxia) or (apotyximena and not apotyxia):
            epilogi.append(tekmirio)
            epityxia = epityxia or perasmena > 0
            apotyxia = apotyxia or apotyximena > 0
    epilogi.extend(tekmirio for tekmirio in egkyra if tekmirio not in epilogi)
    return epilogi[:MAX_TEKMIRIA]


def _parapompi(eggrafi: Mapping[str, object]) -> dict[str, str]:
    """Επιλέγει citation fields χωρίς να αλλοιώνει το source excerpt."""
    parapompi: dict[str, str] = {}
    for kleidi_pigis, kleidi_stoxos in (
        ("id", "id"),
        ("pigi", "pigi"),
        ("synedria", "synedria"),
        ("locator", "locator"),
        ("keimeno", "apospasma"),
    ):
        timh = eggrafi.get(kleidi_pigis)
        if kleidi_pigis == "keimeno" and not isinstance(timh, str):
            timh = eggrafi.get("apospasma")
        if isinstance(timh, str):
            parapompi[kleidi_stoxos] = timh
    kodikos = eggrafi.get("kodikos_exodou")
    if isinstance(kodikos, int) and not isinstance(kodikos, bool):
        parapompi["kodikos_exodou"] = str(kodikos)
    return parapompi


def _metrisi_parapompon(
    parapompes: Sequence[Mapping[str, object]],
) -> tuple[int, int]:
    """Μετρά μόνο τα checks που στηρίζονται στο ακριβές cited output/exit."""
    kodikoi_exodou = [
        eggrafi.get("kodikos_exodou")
        for eggrafi in parapompes
        if isinstance(eggrafi.get("kodikos_exodou"), int)
        and not isinstance(eggrafi.get("kodikos_exodou"), bool)
    ]
    exodoi_apotyxias = sum(kodikos != 0 for kodikos in kodikoi_exodou)
    exodoi_epityxias = sum(kodikos == 0 for kodikos in kodikoi_exodou)
    apotyxies, epityxies = exodoi_apotyxias, exodoi_epityxias
    for eggrafi in parapompes:
        keimeno = eggrafi.get("keimeno", eggrafi.get("apospasma"))
        synopsi = (
            anagnorise_ekvaseis_tests(keimeno) if isinstance(keimeno, str) else None
        )
        if synopsi is not None:
            epityxies += synopsi[0]
            apotyxies += synopsi[1]
    return epityxies, apotyxies


def _apotelesma_epeisodiou(parapompes: Sequence[Mapping[str, object]]) -> str:
    """Ταξινομεί μόνο outcomes που επαληθεύονται στις εμφανιζόμενες παραπομπές."""
    epityxies, apotyxies = _metrisi_parapompon(parapompes)
    if apotyxies and epityxies:
        return "mixed"
    if apotyxies:
        return "observed_failure"
    if epityxies:
        return "observed_success"
    return "unknown"


def _paratirisi_epeisodiou(
    epeisodio: Mapping[str, object], deiktis: int
) -> dict[str, object]:
    """Δημιουργεί bounded episode observation και conditional next step."""
    tekmiria = _tekmiria_egkyra(epeisodio)
    katastasi = _apotelesma_epeisodiou(tekmiria)
    parapompes_perikommenes = epeisodio.get("tekmiria_truncated") is True
    metrisi_tests = {
        kleidi: _plithos(epeisodio.get(kleidi))
        for kleidi in ("tests_passed", "tests_failed", "tests_skipped")
    }
    if katastasi == "observed_failure":
        dynata_simeia = []
        antitheta = (
            "The recorded failure does not establish its cause or overall task quality."
        )
        epomenes_energeies = [
            "If this check remains in scope, inspect the cited failure and "
            "record the rerun result."
        ]
        apotelesma = "Tool or test output records a failure."
    elif katastasi == "observed_success":
        dynata_simeia = ["Recorded tool or test output shows a successful check."]
        antitheta = (
            "A successful check does not establish full task completion "
            "or code quality."
        )
        epomenes_energeies = [
            "If completion matters, record the remaining acceptance checks "
            "and their results."
        ]
        apotelesma = "Tool or test output records a successful check."
    elif katastasi == "mixed":
        dynata_simeia = ["At least one recorded check succeeded."]
        antitheta = (
            "The failed check may be unrelated or outside the episode's "
            "acceptance scope."
        )
        epomenes_energeies = [
            "If the failed check is in scope, inspect its evidence and "
            "record a targeted rerun."
        ]
        apotelesma = "Recorded checks include both successful and failed results."
    else:
        dynata_simeia = []
        antitheta = "No eligible tool-result or exit evidence establishes an outcome."
        epomenes_energeies = [
            "If an outcome is needed, retain a tool result or exit record "
            "for the relevant check."
        ]
        apotelesma = "Outcome is unknown from the available tool and exit evidence."

    tautotita = epeisodio.get("id")
    return {
        "id": tautotita if isinstance(tautotita, str) else f"episode-{deiktis + 1}",
        "pigi": epeisodio.get("pigi") if isinstance(epeisodio.get("pigi"), str) else "",
        "synedria": epeisodio.get("synedria")
        if isinstance(epeisodio.get("synedria"), str)
        else "",
        "katastasi": katastasi,
        "apotelesma": apotelesma,
        "metrisi": {
            **metrisi_tests,
            "exit_success": _plithos(epeisodio.get("exit_success")),
            "exit_failure": _plithos(epeisodio.get("exit_failure")),
        },
        "dynata_simeia": dynata_simeia,
        "antitheta": antitheta,
        "epomenes_energeies": epomenes_energeies,
        "vevaiotita": "low" if tekmiria else "none",
        "tekmiria": [_parapompi(eggrafi) for eggrafi in tekmiria],
        "kalypsi_tekmirion": {
            "included": _plithos(epeisodio.get("tekmiria_included"))
            if _plithos(epeisodio.get("tekmiria_included")) is not None
            else len(tekmiria),
            "eligible": _plithos(epeisodio.get("tekmiria_eligible"))
            if _plithos(epeisodio.get("tekmiria_eligible")) is not None
            else len(tekmiria),
            "truncated": parapompes_perikommenes,
        },
        "periorismoi": (
            [
                "Evidence citations are truncated; aggregate counters alone "
                "do not verify an outcome."
            ]
            if parapompes_perikommenes
            else []
        ),
    }


def axiologise_epeisodia(dedomena: Mapping[str, object]) -> dict[str, object]:
    """Επιστρέφει report copy με bounded outcome observations, χωρίς βαθμολόγηση."""
    apotelesma = dict(dedomena)
    metrika = dedomena.get("metrika_ergasias")
    metrika_xarti = metrika if isinstance(metrika, Mapping) else {}
    grammes_epeisodiwn = _lista_xartwn(metrika_xarti.get("epeisodia"))
    egkyra_plithos = _plithos(metrika_xarti.get("episodes_eligible"))
    eisagomena_plithos = _plithos(metrika_xarti.get("episodes_included"))
    epeisodia_perikommena = metrika_xarti.get("episodes_truncated") is True
    paratiriseis = [
        _paratirisi_epeisodiou(eggrafi, deiktis)
        for deiktis, eggrafi in enumerate(grammes_epeisodiwn[:MAX_EPEISODIA])
    ]
    paratirimenes_apotyxies = sum(
        eggrafi["katastasi"] in {"observed_failure", "mixed"}
        for eggrafi in paratiriseis
    )
    agnwsta = sum(eggrafi["katastasi"] == "unknown" for eggrafi in paratiriseis)
    parapompes_apotyxias = [
        parapompi
        for eggrafi in paratiriseis
        if eggrafi["katastasi"] in {"observed_failure", "mixed"}
        for parapompi in _lista_xartwn(eggrafi.get("tekmiria"))
    ][:MAX_TEKMIRIA]
    parapompes_agnwstou = [
        parapompi
        for eggrafi in paratiriseis
        if eggrafi["katastasi"] == "unknown"
        for parapompi in _lista_xartwn(eggrafi.get("tekmiria"))
    ][:MAX_TEKMIRIA]
    proteraiotites: list[dict[str, object]] = []
    if paratirimenes_apotyxies:
        proteraiotites.append(
            {
                "titlos": "Review recorded failed checks",
                "aitia": (
                    f"{paratirimenes_apotyxies} episode(s) include tool or test "
                    "failure evidence."
                ),
                "protasi": (
                    "Where those checks are in scope, inspect the cited "
                    "output and record a targeted rerun."
                ),
                "tekmiria": parapompes_apotyxias,
                "katastasi": "conditional",
            }
        )
    if agnwsta:
        proteraiotites.append(
            {
                "titlos": "Improve outcome evidence where useful",
                "aitia": (
                    f"{agnwsta} episode(s) have no eligible tool-result "
                    "or exit evidence."
                ),
                "protasi": (
                    "When an outcome matters, retain the actual check "
                    "output or exit record."
                ),
                "tekmiria": parapompes_agnwstou,
                "katastasi": "conditional",
            }
        )
    apotelesma["epeisodia_ergasias"] = {
        "ekdosi": EKDOSI_EPEISODION,
        "katastasi": "partial"
        if epeisodia_perikommena or len(grammes_epeisodiwn) > MAX_EPEISODIA
        else "observed"
        if grammes_epeisodiwn
        else "unknown",
        "kalypsi": {
            "diathesima": egkyra_plithos
            if egkyra_plithos is not None
            else len(grammes_epeisodiwn),
            "analysimena": eisagomena_plithos
            if eisagomena_plithos is not None
            else len(paratiriseis),
            "perikopi": epeisodia_perikommena
            or len(grammes_epeisodiwn) > MAX_EPEISODIA,
        },
        "paratiriseis": paratiriseis,
        "dynata_simeia": ["Some recorded checks have successful tool or test results."]
        if any(
            eggrafi["katastasi"] in {"observed_success", "mixed"}
            for eggrafi in paratiriseis
        )
        else [],
        "proteraiotites": proteraiotites[:MAX_PROTERAIOTITES],
        "vathmologisi_energi": False,
        "periorismoi": (
            "Episode outcomes describe recorded checks only; they do not "
            "assign cause, blame, completion, or code quality."
        ),
    }
    native = dedomena.get("codex_native")
    if isinstance(native, Mapping):
        native_antigrafo = dict(native)
        native_analysi = axiologise_epeisodia({
            "metrika_ergasias": native.get("metrika_ergasias"),
        })
        native_antigrafo["epeisodia_ergasias"] = native_analysi["epeisodia_ergasias"]
        apotelesma["codex_native"] = native_antigrafo
    return apotelesma
