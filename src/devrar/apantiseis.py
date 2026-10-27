"""Ασφαλής deduplication Codex assistant replies μεταξύ export channels."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Literal

from devrar.aporrita import katharise_aporrita

KanalApantisis = Literal["response_item", "agent_message", "task_complete"]
PROTERAIOTITA_KANALION: dict[KanalApantisis, int] = {
    "response_item": 0,
    "agent_message": 1,
    "task_complete": 2,
}
ORIA_APOSPASTOS = 500


@dataclass(frozen=True)
class ApantisiCodex:
    """Safe normalized representative of one candidate assistant reply."""

    synedria: str
    turn_id: str | None
    fingerprint: str
    kanal: KanalApantisis
    tautotita: str | None
    modelo: str | None
    chronos: str | None
    imerominia: str | None
    locator: str
    keimeno: str
    seira: int


@dataclass
class OmadaApantiseon:
    """Replies with equal normalized text within a session and turn scope."""

    candidates: dict[KanalApantisis, list[ApantisiCodex]] = field(default_factory=dict)
    tautotites: dict[KanalApantisis, set[str]] = field(default_factory=dict)
    amfigies: bool = False


@dataclass(frozen=True)
class ApotelesmaApantiseon:
    """Deduplicated reply candidates plus explicit attribution ambiguity."""

    candidates: list[ApantisiCodex]
    plithos: int
    amfigies: int
    montela_amfiga: set[str]


class SyllogistisCodexApantiseon:
    """Deduplicates exact assistant text only with reliable session/turn linkage."""

    def __init__(self) -> None:
        """Initializes bounded-to-metadata grouping state for the source scan."""
        self._omades: dict[tuple[str, str | None, str], OmadaApantiseon] = {}
        self._seira = 0

    def prosthese(
        self,
        synedria: str,
        turn_id: str | None,
        kanal: KanalApantisis,
        keimeno_plires: str,
        tautotita: str | None,
        chronos: str | None,
        imerominia: str | None,
        modelo: str | None,
        locator: str,
    ) -> None:
        """Adds a text fingerprint and redacted excerpt without retaining raw text."""
        fingerprint = hashlib.sha256(keimeno_plires.encode("utf-8")).hexdigest()
        scope_turn_id = turn_id.strip() if turn_id and turn_id.strip() else None
        kleidi = (synedria, scope_turn_id, fingerprint)
        omada = self._omades.setdefault(kleidi, OmadaApantiseon())
        candidates = omada.candidates.setdefault(kanal, [])
        tautotites = omada.tautotites.setdefault(kanal, set())
        if tautotita:
            identita_record = f"id:{tautotita}"
        elif chronos:
            identita_record = f"timestamp:{chronos}"
        else:
            identita_record = ""
        if identita_record and identita_record in tautotites:
            return
        if not identita_record and candidates:
            omada.amfigies = True
        if identita_record:
            tautotites.add(identita_record)
        self._seira += 1
        excerpt = katharise_aporrita(keimeno_plires)[:ORIA_APOSPASTOS]
        candidates.append(
            ApantisiCodex(
                synedria=synedria,
                turn_id=scope_turn_id,
                fingerprint=fingerprint,
                kanal=kanal,
                tautotita=tautotita,
                modelo=modelo,
                chronos=chronos,
                imerominia=imerominia,
                locator=locator,
                keimeno=excerpt,
                seira=self._seira,
            )
        )

    def synopsi(self) -> ApotelesmaApantiseon:
        """Picks maximum channel multiplicity, preferring response_item on ties."""
        epilegmenes: list[ApantisiCodex] = []
        montela_amfiga: set[str] = set()
        amfigies = 0
        for (synedria, turn_id, _fingerprint), omada in self._omades.items():
            if turn_id is None and len(omada.candidates) > 1:
                omada.amfigies = True
            if omada.amfigies:
                amfigies += 1
                montela_amfiga.update(
                    candidate.modelo
                    for candidates in omada.candidates.values()
                    for candidate in candidates
                    if candidate.modelo is not None
                )
                epilegmenes.extend(
                    candidate
                    for candidates in omada.candidates.values()
                    for candidate in candidates
                )
                continue
            kanal = min(
                omada.candidates,
                key=lambda typos: (
                    -len(omada.candidates[typos]),
                    PROTERAIOTITA_KANALION[typos],
                ),
            )
            epilegmenes.extend(omada.candidates[kanal])
        epilegmenes.sort(key=lambda candidate: candidate.seira)
        return ApotelesmaApantiseon(
            candidates=epilegmenes,
            plithos=len(epilegmenes),
            amfigies=amfigies,
            montela_amfiga=montela_amfiga,
        )
