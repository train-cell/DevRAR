"""Κανονικοποίηση ανά Claude API message για τεκμηριωμένα token usage."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

COMPONENTS_XRISIS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)


@dataclass(frozen=True)
class ApotelesmaClaudeXrisis:
    """Συνοπτικά, deduplicated tokens και coverage της πηγής Claude."""

    tokens: int | None
    tokens_ana_modelo: dict[str, int]
    gnostes_aitiseis: int
    elleipeis_aitiseis: int
    agnosta_records: int
    pliris: bool


@dataclass
class KatastasiClaudeMinimatos:
    """Cumulative component maxima και συνέπεια metadata ανά message ID."""

    komponentes: dict[str, int] = field(default_factory=dict)
    montela: set[str] = field(default_factory=set)
    logoi_lixis: set[str] = field(default_factory=set)
    metadata_ellipi: bool = False
    komponenta_mi_egkyra: bool = False


class SyllogistisClaudeXrisis:
    """Συγχωνεύει μόνο ολοκληρωμένα, ταυτοποιημένα Claude message usage."""

    def __init__(self) -> None:
        """Αρχικοποιεί dedup state ανεξάρτητο από transcript event IDs."""
        self._minimata: dict[str, KatastasiClaudeMinimatos] = {}
        self._agnosta_records = 0

    def prosthese(self, eggrafi: dict[str, object]) -> None:
        """Προσθέτει ένα Claude API record, χωρίς να αθροίζει snapshots."""
        if eggrafi.get("type") != "assistant":
            return
        minima_obj = eggrafi.get("message")
        if not isinstance(minima_obj, dict) or minima_obj.get("role") != "assistant":
            self._agnosta_records += 1
            logger.debug("Claude assistant record lacks a valid API message shape")
            return
        minima: dict[str, object] = {
            kleidi: timi
            for kleidi, timi in minima_obj.items()
            if isinstance(kleidi, str)
        }
        tautotita = minima.get("id")
        if not isinstance(tautotita, str) or not tautotita.strip():
            self._agnosta_records += 1
            logger.debug("Claude usage record lacks a stable message ID")
            return
        katastasi = self._minimata.setdefault(tautotita, KatastasiClaudeMinimatos())
        self._prosthese_metadata(katastasi, minima)
        self._prosthese_komponentes(katastasi, minima.get("usage"))

    @staticmethod
    def _prosthese_metadata(
        katastasi: KatastasiClaudeMinimatos, minima: dict[str, object]
    ) -> None:
        """Ελέγχει ότι model και completed stop reason είναι συνεπή."""
        modelo = minima.get("model")
        stop_reason = minima.get("stop_reason")
        if isinstance(modelo, str) and modelo.strip():
            katastasi.montela.add(modelo.strip())
        else:
            katastasi.metadata_ellipi = True
        if isinstance(stop_reason, str) and stop_reason.strip():
            katastasi.logoi_lixis.add(stop_reason.strip())
        else:
            katastasi.metadata_ellipi = True

    @staticmethod
    def _prosthese_komponentes(
        katastasi: KatastasiClaudeMinimatos, xrisi_obj: object
    ) -> None:
        """Συγχωνεύει valid cumulative components με componentwise maxima."""
        if not isinstance(xrisi_obj, dict):
            katastasi.komponenta_mi_egkyra = True
            return
        for onoma in COMPONENTS_XRISIS:
            arithmos = xrisi_obj.get(onoma)
            if arithmos is None:
                continue
            if (
                not isinstance(arithmos, int)
                or isinstance(arithmos, bool)
                or arithmos < 0
            ):
                katastasi.komponenta_mi_egkyra = True
                continue
            katastasi.komponentes[onoma] = max(
                katastasi.komponentes.get(onoma, 0), arithmos
            )

    def synopsi(self, pigi_pliris: bool = True) -> ApotelesmaClaudeXrisis:
        """Επιστρέφει totals μόνο αν όλα τα observed Claude messages καλύπτονται."""
        gnwsta_ana_modelo: dict[str, int] = {}
        gnostes = 0
        for katastasi in self._minimata.values():
            if not self._einai_olokliromeni(katastasi):
                continue
            modelo = next(iter(katastasi.montela))
            synolo = sum(katastasi.komponentes[onoma] for onoma in COMPONENTS_XRISIS)
            gnwsta_ana_modelo[modelo] = gnwsta_ana_modelo.get(modelo, 0) + synolo
            gnostes += 1
        elleipeis = len(self._minimata) - gnostes
        pliris = (
            pigi_pliris
            and bool(self._minimata)
            and elleipeis == 0
            and self._agnosta_records == 0
        )
        tokens = sum(gnwsta_ana_modelo.values()) if pliris else None
        return ApotelesmaClaudeXrisis(
            tokens=tokens,
            tokens_ana_modelo=gnwsta_ana_modelo,
            gnostes_aitiseis=gnostes,
            elleipeis_aitiseis=elleipeis,
            agnosta_records=self._agnosta_records,
            pliris=pliris,
        )

    @staticmethod
    def _einai_olokliromeni(katastasi: KatastasiClaudeMinimatos) -> bool:
        """Ελέγχει τέσσερα counters, ένα model και completed stop reason."""
        return (
            not katastasi.metadata_ellipi
            and not katastasi.komponenta_mi_egkyra
            and len(katastasi.montela) == 1
            and len(katastasi.logoi_lixis) == 1
            and all(onoma in katastasi.komponentes for onoma in COMPONENTS_XRISIS)
        )


class SyllogistisCodexXrisis:
    """Μετρά Codex token_count snapshots χωρίς να τα εκλαμβάνει ως usage."""

    def __init__(self) -> None:
        """Αρχικοποιεί counter για observed cumulative snapshot records."""
        self._agnosta_records = 0

    def prosthese(self, eggrafi: dict[str, object]) -> None:
        """Καταγράφει token_count row αποκλειστικά ως μη αποδοτέο snapshot."""
        fortio_obj = eggrafi.get("payload")
        einai_snapshot = (
            eggrafi.get("type") == "token_count" and isinstance(fortio_obj, dict)
        ) or (
            eggrafi.get("type") == "event_msg"
            and isinstance(fortio_obj, dict)
            and fortio_obj.get("type") == "token_count"
        )
        if einai_snapshot:
            self._agnosta_records += 1

    def agnosta_records(self) -> int:
        """Επιστρέφει πόσα cumulative snapshots παρατηρήθηκαν."""
        return self._agnosta_records
