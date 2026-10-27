"""Χτίζει αναγνώριση της καταγεγραμμένης δραστηριότητας χωρίς skill inference."""

from collections.abc import Mapping

MEGISTA_HIGHLIGHTS = 4
ELAXISTES_PIGES_EXPLORER = 2


def _xartis(timi: object) -> Mapping[str, object]:
    """Αναγνωρίζει mapping χωρίς υπόθεση για optional fields."""
    return timi if isinstance(timi, Mapping) else {}


def _grammes(timi: object) -> list[Mapping[str, object]]:
    """Φιλτράρει malformed list rows χωρίς να μετατρέπει missing σε μηδέν."""
    return (
        [grammi for grammi in timi if isinstance(grammi, Mapping)]
        if isinstance(timi, list)
        else []
    )


def _thetiko(timi: object) -> int:
    """Δέχεται μόνο θετικά recorded integer counts."""
    return (
        timi if isinstance(timi, int) and not isinstance(timi, bool) and timi > 0 else 0
    )


def ftiaxe_anagnorisi(dedomena: Mapping[str, object]) -> dict[str, object]:
    """Δημιουργεί playful report label και μετρημένα highlights με definitions."""
    synola = _xartis(dedomena.get("synola"))
    piges = [
        pigi
        for pigi in _grammes(dedomena.get("ergaleia"))
        if _thetiko(pigi.get("prompts"))
    ]
    ypopraktores = _thetiko(synola.get("ypopraktores"))
    prompts = _thetiko(synola.get("minimata_xristi"))
    commits = _thetiko(synola.get("commits"))
    if ypopraktores:
        titlos = (
            "Multi-tool conductor"
            if len(piges) >= ELAXISTES_PIGES_EXPLORER
            else "Agent conductor"
        )
        aitia = f"{ypopraktores} explicit child sessions recorded in this report."
    elif len(piges) >= ELAXISTES_PIGES_EXPLORER:
        titlos = "Toolbox explorer"
        aitia = f"Human prompts recorded across {len(piges)} supported tool sources."
    elif prompts:
        titlos = "Focused builder"
        aitia = f"{prompts} human prompts recorded in the selected history."
    elif commits:
        titlos = "Repository replay"
        aitia = (
            f"{commits} commits in selected repositories; the Git author scope applies."
        )
    else:
        titlos = "An unwritten chapter"
        aitia = "The selected inputs do not yet establish an activity profile."
    highlights: list[dict[str, str]] = []
    imeres = _thetiko(synola.get("imeres"))
    if imeres:
        highlights.append(
            {
                "titlos": f"{imeres} days in the record",
                "keimeno": "Distinct recorded dates, not elapsed work time.",
            }
        )
    if piges:
        korifi = max(piges, key=lambda pigi: _thetiko(pigi.get("prompts")))
        highlights.append(
            {
                "titlos": f"{korifi.get('onoma', 'Recorded tool')}: "
                f"{korifi['prompts']} prompts",
                "keimeno": "Highest prompt count among supported source rows; "
                "ties may exist.",
            }
        )
    drastiriotita = [
        imera
        for imera in _grammes(dedomena.get("drastiriotita"))
        if _thetiko(imera.get("prompts"))
    ]
    if drastiriotita:
        megisto = max(_thetiko(imera.get("prompts")) for imera in drastiriotita)
        korifes = ", ".join(
            str(imera.get("imerominia", "Unknown date"))
            for imera in drastiriotita
            if imera.get("prompts") == megisto
        )
        highlights.append(
            {
                "titlos": f"{megisto} prompts on your peak recorded day",
                "keimeno": f"Date(s): {korifes}. Volume does not imply quality.",
            }
        )
    tests = _xartis(_xartis(dedomena.get("metrika_ergasias")).get("test_summary"))
    if _thetiko(tests.get("passed")) or _thetiko(tests.get("failed")):
        perasmena = tests.get("passed")
        apotyximena = tests.get("failed")
        perasmena_keimeno = str(perasmena) if perasmena is not None else "Not recorded"
        apotyximena_keimeno = (
            str(apotyximena) if apotyximena is not None else "Not recorded"
        )
        highlights.append(
            {
                "titlos": "Your checks left receipts",
                "keimeno": f"{perasmena_keimeno} passed / {apotyximena_keimeno} failed "
                "test executions recorded. Includes reruns; not unique tests.",
            }
        )
    return {
        "ekdosi": "1",
        "profile": {"titlos": titlos, "aitia": aitia},
        "highlights": highlights[:MEGISTA_HIGHLIGHTS],
        "periorismos": "A playful label for this report's activity, not a personality, "
        "skill, seniority, or code-quality assessment.",
    }
