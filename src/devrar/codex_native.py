"""Κανονικοποιεί αποδεδειγμένα Codex native rows χωρίς κρυφό περιεχόμενο."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypeAlias, TypeGuard

KatigoriaNative = Literal[
    "assistant",
    "command",
    "file_change",
    "collaboration",
    "inter_agent",
    "usage",
    "metadata",
]
TypoiKatigorias: TypeAlias = frozenset[str]

EIDOS_KEIMENOU_AGENT = "text"
KATIGORIES_KATASKEVIS: TypoiKatigorias = frozenset(
    {"in_progress", "completed", "failed", "declined"}
)
KATIGORIES_SYNERGASIAS: TypoiKatigorias = frozenset(
    {"started", "interacted", "interrupted", "completed"}
)
TYPOI_XRISIMON_XRISIS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)


@dataclass(frozen=True, slots=True)
class ProvoliAsistant:
    """Περιγράφει assistant message projection με το native item identity."""

    tautotita: str
    keimeno: str
    fasi: str | None


@dataclass(frozen=True, slots=True)
class XrisiAnaApantisi:
    """Κρατά per-response counters και IDs· cached/reasoning είναι subsets."""

    apantisi_id: str
    synedria_id: str
    nima_id: str
    strofi_id: str
    riziki_strofi_id: str
    eisagomena_tokens: int
    apothikevmena_eisagomena_tokens: int
    grammena_cache_tokens: int
    paragomena_tokens: int
    reasoning_paragomena_tokens: int
    recorded_synolika_tokens: int


@dataclass(frozen=True, slots=True)
class ApotelesmaCodexNative:
    """Επιστρέφει safe fields ενός υποστηριζόμενου Codex native row."""

    katigoria: KatigoriaNative
    tautotita: str
    chronos: str | None
    synedria_id: str | None
    nima_id: str | None
    strofi_id: str | None
    riziki_strofi_id: str | None
    rolos: Literal["assistant"] | None
    fasi: str | None
    provoli_assistant: ProvoliAsistant | None
    entoli: tuple[str, ...] | None
    exodos_entolis: str | None
    kodikos_exodou: int | None
    synopsi: Mapping[str, str | int | bool]
    xrisi: XrisiAnaApantisi | None


def anagnorise_native(
    eggrafi: Mapping[str, object],
) -> ApotelesmaCodexNative | None:
    """Αναγνωρίζει μόνο supported native envelope/schema pairs."""
    typos = eggrafi.get("type")
    fortio = eggrafi.get("payload")
    if not isinstance(fortio, Mapping):
        return None
    chronos = _chronos_aware(eggrafi.get("timestamp"))

    if typos == "event_msg":
        if fortio.get("type") != "item_completed":
            return None
        stoixeio = fortio.get("item")
        if not isinstance(stoixeio, Mapping):
            return None
        typos_stoixeiou = stoixeio.get("type")
        if typos_stoixeiou == "AgentMessage":
            return _anagnorise_apantisi(stoixeio, chronos)
        if typos_stoixeiou == "CommandExecution":
            return _anagnorise_entoli(stoixeio, chronos)
        if typos_stoixeiou == "FileChange":
            return _anagnorise_allagi_arxeiou(stoixeio, chronos)
        if typos_stoixeiou == "SubAgentActivity":
            return _anagnorise_synergasia(stoixeio, chronos)
        if typos_stoixeiou in {"Reasoning", "ContextCompaction"}:
            return _anagnorise_metadata(stoixeio, chronos)
        return None

    if typos == "response_item" and fortio.get("type") == "agent_message":
        return _anagnorise_inter_agent(fortio, chronos)
    if typos == "token_usage_record":
        return _anagnorise_xrisi(fortio, chronos)
    return None


def _anagnorise_apantisi(
    stoixeio: Mapping[str, object], chronos: str | None
) -> ApotelesmaCodexNative | None:
    """Χαρτογραφεί AgentMessage text και stable legacy projection."""
    tautotita = _nonempty_string(stoixeio.get("id"))
    periexomeno = stoixeio.get("content")
    fasi = stoixeio.get("phase")
    if tautotita is None or not isinstance(periexomeno, Sequence) or isinstance(
        periexomeno, (str, bytes)
    ):
        return None
    if fasi is not None and not isinstance(fasi, str):
        return None
    keimeno_parts: list[str] = []
    for kommataki in periexomeno:
        if (
            not isinstance(kommataki, Mapping)
            or kommataki.get("type") != EIDOS_KEIMENOU_AGENT
        ):
            return None
        keimeno_tmima = kommataki.get("text")
        if not isinstance(keimeno_tmima, str):
            return None
        keimeno_parts.append(keimeno_tmima)
    keimeno = "".join(keimeno_parts)
    projection = ProvoliAsistant(tautotita, keimeno, fasi)
    return _apotelesma(
        "assistant",
        tautotita,
        chronos,
        rolos="assistant",
        fasi=fasi,
        provoli_assistant=projection,
    )


def _anagnorise_entoli(
    stoixeio: Mapping[str, object], chronos: str | None
) -> ApotelesmaCodexNative | None:
    """Χαρτογραφεί observed command completion χωρίς legacy call join."""
    tautotita = _nonempty_string(stoixeio.get("id"))
    entoli = stoixeio.get("command")
    katastasi = stoixeio.get("status")
    exodos = stoixeio.get("aggregated_output")
    kodikos_exodou = stoixeio.get("exit_code")
    if (
        tautotita is None
        or not isinstance(entoli, list)
        or not all(isinstance(tmima, str) for tmima in entoli)
        or not isinstance(katastasi, str)
        or katastasi not in KATIGORIES_KATASKEVIS
        or (exodos is not None and not isinstance(exodos, str))
        or (kodikos_exodou is not None and not _einai_akeraios(kodikos_exodou))
    ):
        return None
    return _apotelesma(
        "command",
        tautotita,
        chronos,
        entoli=tuple(entoli),
        exodos_entolis=exodos if isinstance(exodos, str) else None,
        kodikos_exodou=kodikos_exodou if _einai_akeraios(kodikos_exodou) else None,
        synopsi={
            "status": katastasi,
            "command_count": len(entoli),
            "exit_code_recorded": _einai_akeraios(kodikos_exodou),
        },
    )


def _anagnorise_allagi_arxeiou(
    stoixeio: Mapping[str, object], chronos: str | None
) -> ApotelesmaCodexNative | None:
    """Χαρτογραφεί file-change count/status χωρίς paths ή patch bodies."""
    tautotita = _nonempty_string(stoixeio.get("id"))
    allages = stoixeio.get("changes")
    katastasi = stoixeio.get("status")
    if (
        tautotita is None
        or not isinstance(allages, Mapping)
        or not all(
            isinstance(diadromi, str) and isinstance(allagi, Mapping)
            for diadromi, allagi in allages.items()
        )
        or (katastasi is not None and not isinstance(katastasi, str))
    ):
        return None
    synopsi: dict[str, str | int | bool] = {"change_count": len(allages)}
    if isinstance(katastasi, str):
        synopsi["status"] = katastasi
    return _apotelesma("file_change", tautotita, chronos, synopsi=synopsi)


def _anagnorise_synergasia(
    stoixeio: Mapping[str, object], chronos: str | None
) -> ApotelesmaCodexNative | None:
    """Χαρτογραφεί collaboration activity και δηλώνει child ID χωριστά."""
    tautotita = _nonempty_string(stoixeio.get("id"))
    eidos = stoixeio.get("kind")
    paidi_id = _nonempty_string(stoixeio.get("agent_thread_id"))
    diadromi_agent = _nonempty_string(stoixeio.get("agent_path"))
    if (
        tautotita is None
        or not isinstance(eidos, str)
        or eidos not in KATIGORIES_SYNERGASIAS
        or paidi_id is None
        or diadromi_agent is None
    ):
        return None
    return _apotelesma(
        "collaboration",
        tautotita,
        chronos,
        synopsi={"kind": eidos, "agent_thread_id": paidi_id},
    )


def _anagnorise_inter_agent(
    fortio: Mapping[str, object], chronos: str | None
) -> ApotelesmaCodexNative | None:
    """Κρατά agent attribution και απορρίπτει body/ciphertext ολόκληρα."""
    tautotita = _nonempty_string(fortio.get("id"))
    syggrafeas = _nonempty_string(fortio.get("author"))
    apodektis = _nonempty_string(fortio.get("recipient"))
    periexomeno = fortio.get("content")
    if (
        tautotita is None
        or syggrafeas is None
        or apodektis is None
        or not isinstance(periexomeno, list)
    ):
        return None
    return _apotelesma(
        "inter_agent",
        tautotita,
        chronos,
        synopsi={"author": syggrafeas, "recipient": apodektis},
    )


def _anagnorise_xrisi(
    fortio: Mapping[str, object], chronos: str | None
) -> ApotelesmaCodexNative | None:
    """Κρατά valid per-response counters, ποτέ cumulative snapshots."""
    apantisi_id = _nonempty_string(fortio.get("response_id"))
    synedria_id = _nonempty_string(fortio.get("session_id"))
    nima_id = _nonempty_string(fortio.get("thread_id"))
    strofi_id = _nonempty_string(fortio.get("turn_id"))
    riziki_strofi_id = _nonempty_string(fortio.get("root_turn_id"))
    metriseis = fortio.get("usage")
    if (
        apantisi_id is None
        or synedria_id is None
        or nima_id is None
        or strofi_id is None
        or riziki_strofi_id is None
        or not isinstance(metriseis, Mapping)
    ):
        return None
    apokodikopoiimena: dict[str, int] = {}
    for pedio in TYPOI_XRISIMON_XRISIS:
        timi = metriseis.get(pedio)
        if not _einai_akeraios(timi) or timi < 0:
            return None
        apokodikopoiimena[pedio] = timi
    xrisi = XrisiAnaApantisi(
        apantisi_id=apantisi_id,
        synedria_id=synedria_id,
        nima_id=nima_id,
        strofi_id=strofi_id,
        riziki_strofi_id=riziki_strofi_id,
        eisagomena_tokens=apokodikopoiimena["input_tokens"],
        apothikevmena_eisagomena_tokens=apokodikopoiimena["cached_input_tokens"],
        grammena_cache_tokens=apokodikopoiimena["cache_write_input_tokens"],
        paragomena_tokens=apokodikopoiimena["output_tokens"],
        reasoning_paragomena_tokens=apokodikopoiimena["reasoning_output_tokens"],
        recorded_synolika_tokens=apokodikopoiimena["total_tokens"],
    )
    return _apotelesma(
        "usage",
        apantisi_id,
        chronos,
        synedria_id=synedria_id,
        nima_id=nima_id,
        strofi_id=strofi_id,
        riziki_strofi_id=riziki_strofi_id,
        xrisi=xrisi,
    )


def _anagnorise_metadata(
    stoixeio: Mapping[str, object], chronos: str | None
) -> ApotelesmaCodexNative | None:
    """Αναγνωρίζει terminal metadata χωρίς επιστροφή private fields."""
    tautotita = _nonempty_string(stoixeio.get("id"))
    typos_stoixeiou = stoixeio.get("type")
    if tautotita is None or typos_stoixeiou not in {"Reasoning", "ContextCompaction"}:
        return None
    return _apotelesma(
        "metadata", tautotita, chronos, synopsi={"item_type": typos_stoixeiou}
    )


def _apotelesma(
    katigoria: KatigoriaNative,
    tautotita: str,
    chronos: str | None,
    *,
    synedria_id: str | None = None,
    nima_id: str | None = None,
    strofi_id: str | None = None,
    riziki_strofi_id: str | None = None,
    rolos: Literal["assistant"] | None = None,
    fasi: str | None = None,
    provoli_assistant: ProvoliAsistant | None = None,
    entoli: tuple[str, ...] | None = None,
    exodos_entolis: str | None = None,
    kodikos_exodou: int | None = None,
    synopsi: Mapping[str, str | int | bool] | None = None,
    xrisi: XrisiAnaApantisi | None = None,
) -> ApotelesmaCodexNative:
    """Χτίζει σταθερό result με κενή structural summary ως default."""
    return ApotelesmaCodexNative(
        katigoria=katigoria,
        tautotita=tautotita,
        chronos=chronos,
        synedria_id=synedria_id,
        nima_id=nima_id,
        strofi_id=strofi_id,
        riziki_strofi_id=riziki_strofi_id,
        rolos=rolos,
        fasi=fasi,
        provoli_assistant=provoli_assistant,
        entoli=entoli,
        exodos_entolis=exodos_entolis,
        kodikos_exodou=kodikos_exodou,
        synopsi=synopsi if synopsi is not None else {},
        xrisi=xrisi,
    )


def _nonempty_string(timi: object) -> str | None:
    """Επιστρέφει non-empty string IDs/labels χωρίς coercion."""
    return timi if isinstance(timi, str) and timi else None


def _einai_akeraios(timi: object) -> TypeGuard[int]:
    """Ελέγχει ακέραιο χωρίς να δέχεται bool ως integer."""
    return isinstance(timi, int) and not isinstance(timi, bool)


def _chronos_aware(timi: object) -> str | None:
    """Διατηρεί μόνο parseable timestamps που έχουν ρητό UTC offset."""
    if not isinstance(timi, str):
        return None
    try:
        chronos = datetime.fromisoformat(timi.replace("Z", "+00:00"))
    except ValueError:
        return None
    if chronos.tzinfo is None or chronos.utcoffset() is None:
        return None
    return timi
