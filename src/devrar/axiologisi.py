"""Παράγει συντηρητικές, evidence-linked παρατηρήσεις για human–AI practices."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from re import Pattern
from typing import cast

MAX_DEIGMATA_ANALYSIS = 600
MAX_TEKMIRIA_ANA_EYRIMA = 3
MAX_EYRIMATA_ANA_KATIGORIA = 3
ELAXISTES_SYNEDRIES_MOTIVOU = 3
EKDOSI_RUBRIKAS = "0.1"
EKDOSI_ANALYSI = "0.1"
IDENTITITA_GENERATORA = "rules-0.1"
ANTHROPINA_APODOSI = frozenset({"human", "human_prompt", "root_user", "user"})
AITIA_MH_VATHMOLOGISIS = (
    "Scores are withheld until the rubric is calibrated and human-rater "
    "agreement is validated."
)


@dataclass(frozen=True)
class Kanonas:
    """Μία dimension και τα επιτρεπόμενα human-prompt candidate cues."""

    id: str
    onoma: str
    thematiki: str
    protasi: str
    merkes: tuple[Pattern[str], ...]


def _merkes(*ekfraseis: str) -> tuple[Pattern[str], ...]:
    """Μετατρέπει σταθερά rubric expressions σε case-insensitive patterns."""
    return tuple(re.compile(ekfrasi, re.IGNORECASE) for ekfrasi in ekfraseis)


KANONES = (
    Kanonas(
        "scope_acceptance",
        "Scope & acceptance",
        "scope or acceptance criteria",
        "Keep acceptance criteria beside the change and record how each was checked.",
        _merkes(
            r"\bacceptance criteria\b",
            r"\bsuccess criteria\b",
            r"\bdefinition of done\b",
            r"\bdone when\b",
            r"\bexpected (?:behavior|result|outcome)\b",
            r"κριτήρια αποδοχής",
            r"κριτήρια επιτυχίας",
            r"αναμενόμενη συμπεριφορά",
            r"ορισμός ολοκλήρωσης",
        ),
    ),
    Kanonas(
        "context_handoffs",
        "Context & handoffs",
        "context, decisions, or handoff",
        "Keep a short handoff with current state, decisions, and the next owner.",
        _merkes(
            r"\bcontext\b",
            r"\bhandoff\b",
            r"\bhand-off\b",
            r"\bcurrent decisions\b",
            r"\bresume from\b",
            r"\bcontinue from\b",
            r"πλαίσιο",
            r"παράδοση",
            r"τρέχουσες αποφάσεις",
            r"συνέχεια",
        ),
    ),
    Kanonas(
        "delegation_ownership",
        "Delegation & ownership",
        "delegation, ownership, or integration",
        "State the owner, dependencies, and integration check when work is delegated.",
        _merkes(
            r"\bdelegate\b",
            r"\bdelegation\b",
            r"\bsubagent\b",
            r"\bownership\b",
            r"\bowner\b",
            r"\bi will integrate\b",
            r"\bintegration owner\b",
            r"\bdependencies\b",
            r"ανάθεση",
            r"υποπράκτορα",
            r"ιδιοκτησία",
            r"ενσωμάτωση",
            r"εξαρτήσεις",
        ),
    ),
    Kanonas(
        "debugging_evidence",
        "Debugging & evidence",
        "reproduction, logs, or a traceback",
        "Keep the minimal reproduction and observed error output with the fix.",
        _merkes(
            r"\breproduce\b",
            r"\breproduction\b",
            r"\btraceback\b",
            r"\bstack trace\b",
            r"\blogs\b",
            r"\bobserved output\b",
            r"αναπαραγωγή",
            r"ίχνος κλήσεων",
            r"καταγραφές",
            r"logs",
        ),
    ),
    Kanonas(
        "verification",
        "Verification & completion",
        "tests, verification, or build results",
        "Record the exact verification command and its observed result.",
        _merkes(
            r"\bpytest\b",
            r"\btest suite\b",
            r"\brun (?:the )?tests?\b",
            r"\bverify\b",
            r"\bverification\b",
            r"\bcheck that\b",
            r"\bbuild result\b",
            r"\bci\b",
            r"τρέξε τα tests",
            r"εκτέλεσε τις δοκιμές",
            r"επαλήθευσε",
            r"έλεγξε",
            r"αποτέλεσμα build",
        ),
    ),
)

MERKES_RITIS_PARALIPSIS = _merkes(
    r"\bdo not (?:run|execute) (?:the )?(?:tests?|pytest|checks?)\b",
    r"\bdon't (?:run|execute) (?:the )?(?:tests?|pytest|checks?)\b",
    r"\bskip(?:ping)? (?:the )?(?:tests?|pytest|checks?)\b",
    r"\bno need to (?:run|execute) (?:the )?(?:tests?|pytest|checks?)\b",
    r"\bwithout (?:running )?(?:the )?(?:tests?|pytest|checks?)\b",
    r"μην (?:τρέξεις|εκτελέσεις) (?:τα )?(?:tests|δοκιμές|ελέγχους)",
    r"χωρίς (?:να )?(?:τρέξεις|εκτελέσεις) (?:τα )?(?:tests|δοκιμές|ελέγχους)",
    r"παράλειψε (?:τα )?(?:tests|δοκιμές|ελέγχους)",
)
MERKES_ANTI_PARALIPSIS = _merkes(
    r"\b(?:do not|don't|never|should not|shouldn't|must not|mustn't) skip\b"
    r"[^.!?;]{0,80}\b(?:the )?(?:tests?|pytest|checks?)\b",
    r"\bnot skip\b[^.!?;]{0,60}\b(?:the )?(?:tests?|pytest|checks?)\b",
    r"μην παραλείψ(?:εις|ετε|ουμε|ουν)\b[^.!?;]{0,60}\b(?:τα )?"
    r"(?:tests|δοκιμές|ελέγχους)\b",
    r"μην παραλείπ(?:εις|ετε|ουμε|ουν)\b[^.!?;]{0,60}\b(?:τα )?"
    r"(?:tests|δοκιμές|ελέγχους)\b",
)
MERKES_YPO_TROPOU_PARALIPSIS = _merkes(
    r"\b(?:should|could|would|might|may|maybe|consider|whether)\b"
    r"[^.!?;\n]{0,60}\bskip(?:ping)?\b[^.!?;\n]{0,40}\b(?:tests?|pytest|checks?)\b",
)
MERKES_PARAGRAFON = _merkes(
    r"\"[^\"\n]*\"",
    r"'[^'\n]*'",
    r"“[^”\n]*”",
    r"‘[^’\n]*’",
    r"«[^»\n]*»",
)


@dataclass(frozen=True)
class Sima:
    """Ένα human prompt και τα σταθερά πεδία provenance του."""

    id: str
    pigi: str
    synedria: str
    rolos: str
    eidos: str
    keimeno: str
    locator: str


def _diavase_deigma(eggrafi: object) -> Sima | None:
    """Επικυρώνει τα πεδία identity, role, type και excerpt ενός row."""
    if not isinstance(eggrafi, Mapping):
        return None
    for kleidi in ("actor", "attribution", "apodosi", "drastis"):
        if kleidi in eggrafi:
            attribution = eggrafi.get(kleidi)
            if (
                not isinstance(attribution, str)
                or attribution.casefold() not in ANTHROPINA_APODOSI
            ):
                return None
    apaitoumena = ("id", "pigi", "synedria", "rolos", "eidos", "keimeno", "locator")
    pedia = [eggrafi.get(kleidi) for kleidi in apaitoumena]
    if not all(isinstance(pedio, str) for pedio in pedia):
        return None
    return Sima(
        id=cast(str, eggrafi["id"]),
        pigi=cast(str, eggrafi["pigi"]),
        synedria=cast(str, eggrafi["synedria"]),
        rolos=cast(str, eggrafi["rolos"]),
        eidos=cast(str, eggrafi["eidos"]),
        keimeno=cast(str, eggrafi["keimeno"]),
        locator=cast(str, eggrafi["locator"]),
    )


def _xwrise_deigmata(dedomena: Mapping[str, object]) -> tuple[list[object], list[Sima]]:
    """Περιορίζει rows στο όριο και επιστρέφει έγκυρα, deduplicated signals."""
    deigmata_raw = dedomena.get("deigmata")
    if not isinstance(deigmata_raw, list):
        return [], []
    periorismena = deigmata_raw[:MAX_DEIGMATA_ANALYSIS]
    egkyra: list[Sima] = []
    seen: set[tuple[str, str]] = set()
    for eggrafi in periorismena:
        sima = _diavase_deigma(eggrafi)
        if sima is None or not sima.id or not sima.pigi:
            continue
        kleidi = (sima.pigi, sima.id)
        if kleidi in seen:
            continue
        seen.add(kleidi)
        egkyra.append(sima)
    return periorismena, egkyra


def _elegxos_anthropinou_prompt(sima: Sima) -> bool:
    """Επιλέγει μόνο human user prompts και αποκλείει agent/tool output."""
    return sima.rolos == "user" and sima.eidos == "prompt"


def _antistoixiseis(keimeno: str, kanonas: Kanonas) -> bool:
    """Ελέγχει αν excerpt περιέχει ένα από τα δημοσιευμένα candidate cues."""
    return any(merki.search(keimeno) for merki in kanonas.merkes)


def _einai_se_paragrafika(keimeno: str, thesi: int) -> bool:
    """Ελέγχει αν ένα skip cue βρίσκεται μέσα σε εισαγωγικά."""
    for merki in MERKES_PARAGRAFON:
        for paragrafiko in merki.finditer(keimeno):
            if paragrafiko.start() <= thesi < paragrafiko.end():
                return True
    return False


def _einai_rhto_skip_elegxou(keimeno: str) -> bool:
    """Αναγνωρίζει μόνο unquoted, affirmative skip instructions, όχι anti-skip."""
    if any(merki.search(keimeno) for merki in MERKES_ANTI_PARALIPSIS):
        return False
    if any(merki.search(keimeno) for merki in MERKES_YPO_TROPOU_PARALIPSIS):
        return False
    for merki in MERKES_RITIS_PARALIPSIS:
        for parousia in merki.finditer(keimeno):
            if not _einai_se_paragrafika(keimeno, parousia.start()):
                return True
    return False


def _tekmirio(sima: Sima) -> dict[str, str]:
    """Δημιουργεί citation με exact matching excerpt και source identity."""
    return {
        "id": sima.id,
        "pigi": sima.pigi,
        "locator": sima.locator,
        "apospasma": sima.keimeno,
    }


def _synedries(simata: Sequence[Sima]) -> set[tuple[str, str]]:
    """Μετρά distinct source/session pairs, ποτέ rows ως sessions."""
    return {(sima.pigi, sima.synedria) for sima in simata if sima.synedria}


def _titlos_eyrimatos(kanonas: Kanonas, epanalamvanomeno: bool, synedries: int) -> str:
    """Δημιουργεί τίτλο που διακρίνει recurring signals από isolated cues."""
    if epanalamvanomeno:
        return f"Recurring prompt signal: {kanonas.thematiki}"
    if synedries == 0:
        return f"Candidate prompt signal: {kanonas.thematiki}; session unknown"
    return f"Candidate prompt signal: {kanonas.thematiki}; not recurring"


def _keimeno_eyrimatos(kanonas: Kanonas, synedries: int) -> str:
    """Περιγράφει prompt intent χωρίς να ισχυρίζεται εκτέλεση ή αποτέλεσμα."""
    if synedries >= ELAXISTES_SYNEDRIES_MOTIVOU:
        perigraphi = (
            f"The cue appears in {synedries} distinct sessions. "
            "It remains a prompt signal, "
            "not proof that the practice was completed or effective."
        )
    elif synedries:
        perigraphi = (
            f"The cue appears in {synedries} distinct session(s), "
            "below the three-session "
            "recurrence threshold. It does not establish completion or quality."
        )
    else:
        perigraphi = (
            "A prompt cue was found, but no session identifier was available; "
            "recurrence "
            "cannot be assessed. It does not establish completion or quality."
        )
    return f"The human prompt explicitly references {kanonas.thematiki}. {perigraphi}"


def _aitia_vevaiotitas() -> str:
    """Εξηγεί τη χαμηλή confidence που επιβάλλει prompt-only evidence."""
    return "Prompt text shows stated intent, not execution, outcome, or task context."


def _ftiaxe_eyrima(
    kanonas: Kanonas,
    simata: Sequence[Sima],
    id_eyrimatos: str,
) -> dict[str, object]:
    """Δημιουργεί candidate observation με περιορισμένα exact citations."""
    synedries = len(_synedries(simata))
    return {
        "id": id_eyrimatos,
        "paragogos": IDENTITITA_GENERATORA,
        "titlos": _titlos_eyrimatos(
            kanonas, synedries >= ELAXISTES_SYNEDRIES_MOTIVOU, synedries
        ),
        "epipedo": "strength",
        "keimeno": _keimeno_eyrimatos(kanonas, synedries),
        "protasi": kanonas.protasi,
        "diastasi": kanonas.id,
        "katastasi": "candidate_only",
        "drastis": "human_prompt",
        "motivo": "recurring_candidate_signal"
        if synedries >= ELAXISTES_SYNEDRIES_MOTIVOU
        else "isolated_candidate_signal",
        "paratirimenes_synedries": synedries,
        "paratiriseis": len(simata),
        "synepeia": "No execution outcome can be established from prompt text alone.",
        "ermineia": (
            "This signal describes prompt wording, not underlying behavior or ability."
        ),
        "eythyni": "Human prompt only; responsibility for execution is unknown.",
        "enallaktiki": (
            "The cue may be quoted, illustrative, or requested without follow-through; "
            "this report observes prompt text only."
        ),
        "antitheta": (
            "No execution or test-result rows were used to confirm the request."
        ),
        "simeiosi_drasti": (
            "Attribution is limited to the human-authored prompt, "
            "not the developer's execution."
        ),
        "vevaiotita": "low",
        "aitiologia_vevaiotitas": _aitia_vevaiotitas(),
        "tekmiria": [_tekmirio(sima) for sima in simata[:MAX_TEKMIRIA_ANA_EYRIMA]],
    }


def _ftiaxe_eyrima_paralipsis(
    simata: Sequence[Sima],
    id_eyrimatos: str,
) -> dict[str, object]:
    """Δημιουργεί conditional growth candidate για ρητό skip verification cue."""
    synedries = len(_synedries(simata))
    return {
        "id": id_eyrimatos,
        "paragogos": IDENTITITA_GENERATORA,
        "titlos": "Candidate prompt signal: verification explicitly deferred",
        "epipedo": "growth",
        "keimeno": (
            "A human prompt explicitly asks not to run tests. "
            "This is an intent signal; "
            "it does not prove tests were skipped or that the work was unsafe."
        ),
        "protasi": (
            "If tests are out of scope, record the reason and nearest safe "
            "verification "
            "alternative; otherwise run targeted tests and report the result."
        ),
        "diastasi": "verification",
        "katastasi": "candidate_only",
        "drastis": "human_prompt",
        "motivo": "recurring_candidate_signal"
        if synedries >= ELAXISTES_SYNEDRIES_MOTIVOU
        else "isolated_candidate_signal",
        "paratirimenes_synedries": synedries,
        "paratiriseis": len(simata),
        "synepeia": "The prompt documents a requested scope, not what was executed.",
        "ermineia": (
            "This signal describes requested scope, not underlying behavior or ability."
        ),
        "eythyni": "Human prompt only; responsibility for execution is unknown.",
        "enallaktiki": (
            "Verification may have been performed elsewhere, or an exception may have "
            "been appropriate for the task scope."
        ),
        "antitheta": (
            "No execution or test-result rows were used to confirm the request."
        ),
        "simeiosi_drasti": (
            "Attribution is limited to the human-authored prompt, not execution."
        ),
        "vevaiotita": "low",
        "aitiologia_vevaiotitas": _aitia_vevaiotitas(),
        "tekmiria": [_tekmirio(sima) for sima in simata[:MAX_TEKMIRIA_ANA_EYRIMA]],
    }


def _tekmiria_ana_diastasi(simata: Sequence[Sima]) -> dict[str, list[Sima]]:
    """Συσχετίζει human prompts με candidate dimension cues."""
    simata_ana_diastasi: dict[str, list[Sima]] = {kanonas.id: [] for kanonas in KANONES}
    for sima in simata:
        if not _elegxos_anthropinou_prompt(sima):
            continue
        paralipsi_elegxou = _einai_rhto_skip_elegxou(sima.keimeno)
        for kanonas in KANONES:
            if kanonas.id == "verification" and paralipsi_elegxou:
                continue
            if _antistoixiseis(sima.keimeno, kanonas):
                simata_ana_diastasi[kanonas.id].append(sima)
    return simata_ana_diastasi


def _paralipseis_elegxou(simata: Sequence[Sima]) -> list[Sima]:
    """Επιστρέφει ανθρώπινα prompts που ρητά ζητούν skip verification."""
    return [
        sima
        for sima in simata
        if _elegxos_anthropinou_prompt(sima) and _einai_rhto_skip_elegxou(sima.keimeno)
    ]


def _diastaseis(
    simata_ana_diastasi: Mapping[str, Sequence[Sima]],
) -> list[dict[str, object]]:
    """Δημιουργεί πενταδιάστατο scorecard χωρίς ενεργούς αριθμητικούς βαθμούς."""
    apotelesmata: list[dict[str, object]] = []
    for kanonas in KANONES:
        simata = simata_ana_diastasi[kanonas.id]
        apotelesmata.append(
            {
                "id": kanonas.id,
                "onoma": kanonas.onoma,
                "bathmos": None,
                "katastasi": "not_calibrated",
                "katastasi_simatos": "candidate_observed"
                if simata
                else "no_candidate_observed",
                "paratiriseis": len(simata),
                "episodia": len(_synedries(simata)),
                "synedries_vathmologisimes": 0,
                "tekmiria": [sima.id for sima in simata[:MAX_TEKMIRIA_ANA_EYRIMA]],
                "aitia": AITIA_MH_VATHMOLOGISIS,
            }
        )
    return apotelesmata


def _vathmologisi(diastaseis: Sequence[Mapping[str, object]]) -> dict[str, object]:
    """Δηλώνει calibration and inter-rater gates και κρατά score unavailable."""
    return {
        "diathesimi": False,
        "synoliko": None,
        "aitia": AITIA_MH_VATHMOLOGISIS,
        "rubrika": EKDOSI_RUBRIKAS,
        "diastaseis": [dict(diastasi) for diastasi in diastaseis],
        "gate_vathmologias": {
            "energo": False,
            "rubrika_vathmologimeni": False,
            "symfonia_anthropinon_aksiologiton": False,
            "aitia": AITIA_MH_VATHMOLOGISIS,
        },
    }


def _kalypsi_analysi(
    dedomena: Mapping[str, object],
    deigmata_periorismena: Sequence[object],
) -> dict[str, object]:
    """Διατηρεί collector coverage semantics και εφαρμόζει όριο 600 rows."""
    kalypsi_raw = dedomena.get("kalypsi_analysi")
    kalypsi = kalypsi_raw if isinstance(kalypsi_raw, Mapping) else {}
    plithos_eisodou = len(deigmata_periorismena)
    diathesima_raw = kalypsi.get("diathesima")
    diathesima = (
        diathesima_raw
        if isinstance(diathesima_raw, int) and not isinstance(diathesima_raw, bool)
        else plithos_eisodou
    )
    diathesima = max(diathesima, plithos_eisodou)
    epilegmena = min(plithos_eisodou, MAX_DEIGMATA_ANALYSIS)
    return {
        "epilegmena": epilegmena,
        "diathesima": diathesima,
        "perikopi": kalypsi.get("perikopi") is True
        or diathesima > epilegmena
        or plithos_eisodou > MAX_DEIGMATA_ANALYSIS,
    }


def _neo_id_eyrimatos(yparxonta_eyrimata: Sequence[object], arithmos: int) -> str:
    """Επιλέγει νέο A-prefixed finding ID χωρίς collision με υπάρχοντα rows."""
    yparxonta = {
        cast(str, eyrima.get("id"))
        for eyrima in yparxonta_eyrimata
        if isinstance(eyrima, Mapping) and isinstance(eyrima.get("id"), str)
    }
    neo_id = f"A{arithmos:03d}"
    while neo_id in yparxonta:
        arithmos += 1
        neo_id = f"A{arithmos:03d}"
    return neo_id


def _periorismena_yparxonta(eyrimata_raw: object) -> list[object]:
    """Κρατά υπάρχοντα findings, αφαιρεί προηγούμενα rule outputs και εφαρμόζει caps."""
    if not isinstance(eyrimata_raw, list):
        return []
    yparxonta: list[object] = []
    plithos_ana_epipedo = {"strength": 0, "growth": 0}
    for eyrima in eyrimata_raw:
        if (
            isinstance(eyrima, Mapping)
            and eyrima.get("paragogos") == IDENTITITA_GENERATORA
        ):
            continue
        if isinstance(eyrima, Mapping):
            epipedo = eyrima.get("epipedo")
            if isinstance(epipedo, str) and epipedo in plithos_ana_epipedo:
                if plithos_ana_epipedo[epipedo] >= MAX_EYRIMATA_ANA_KATIGORIA:
                    continue
                plithos_ana_epipedo[epipedo] += 1
        yparxonta.append(eyrima)
    return yparxonta


def _eyrimata(
    dedomena: Mapping[str, object],
    simata_ana_diastasi: Mapping[str, Sequence[Sima]],
    simata_paralipsis: Sequence[Sima],
) -> list[object]:
    """Συντηρεί υπάρχοντα findings και προσθέτει έως τρία ανά polarity."""
    yparxonta = _periorismena_yparxonta(dedomena.get("eyrimata"))
    neo: list[dict[str, object]] = []
    isxyonta_eyrimata = sum(
        isinstance(eyrima, Mapping) and eyrima.get("epipedo") == "strength"
        for eyrima in yparxonta
    )
    anaptyksi_eyrimata = sum(
        isinstance(eyrima, Mapping) and eyrima.get("epipedo") == "growth"
        for eyrima in yparxonta
    )
    eyrimata_isxyos = [
        (kanonas, simata)
        for kanonas in KANONES
        if (simata := simata_ana_diastasi[kanonas.id])
    ]
    eyrimata_isxyos.sort(
        key=lambda eggrafi: (len(_synedries(eggrafi[1])), len(eggrafi[1])),
        reverse=True,
    )
    diathesimes_isxyes = max(0, MAX_EYRIMATA_ANA_KATIGORIA - isxyonta_eyrimata)
    for kanonas, simata in eyrimata_isxyos[:diathesimes_isxyes]:
        neo.append(
            _ftiaxe_eyrima(
                kanonas, simata, _neo_id_eyrimatos(yparxonta + neo, len(neo) + 1)
            )
        )
    if simata_paralipsis and anaptyksi_eyrimata < MAX_EYRIMATA_ANA_KATIGORIA:
        neo.append(
            _ftiaxe_eyrima_paralipsis(
                simata_paralipsis,
                _neo_id_eyrimatos(yparxonta + neo, len(neo) + 1),
            )
        )
    return [*yparxonta, *neo]


def axiologise_ergasia(dedomena: Mapping[str, object]) -> dict[str, object]:
    """Επιστρέφει report copy με bounded, evidence-linked candidate observations."""
    apotelesma = dict(dedomena)
    deigmata_periorismena, egkyra = _xwrise_deigmata(dedomena)
    anthropina = [sima for sima in egkyra if _elegxos_anthropinou_prompt(sima)]
    simata_ana_diastasi = _tekmiria_ana_diastasi(egkyra)
    simata_paralipsis = _paralipseis_elegxou(egkyra)
    diastaseis = _diastaseis(simata_ana_diastasi)

    apotelesma["deigmata"] = list(deigmata_periorismena)
    apotelesma["kalypsi_analysi"] = _kalypsi_analysi(dedomena, deigmata_periorismena)
    apotelesma["axiologisi"] = _vathmologisi(diastaseis)
    apotelesma["eyrimata"] = _eyrimata(
        dedomena,
        simata_ana_diastasi,
        simata_paralipsis,
    )
    apotelesma["analysi"] = {
        "methodos": "rules",
        "ekdosi": EKDOSI_ANALYSI,
        "rubrika": EKDOSI_RUBRIKAS,
        "max_deigmata": MAX_DEIGMATA_ANALYSIS,
        "egkyra_deigmata": len(egkyra),
        "anthropina_minimata": len(anthropina),
        "vathmoi_vathmologimenoi": False,
        "symfonia_anthropinon_aksiologiton": False,
    }
    return apotelesma
