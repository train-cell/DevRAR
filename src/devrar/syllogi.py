"""Τοπική συλλογή Claude, Codex και δηλωμένων Git repositories."""

from __future__ import annotations

import hashlib
import importlib
import json
import logging
import os
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import (
    BinaryIO,
    Literal,
    Mapping,
    Protocol,
    Sequence,
    TextIO,
    TypedDict,
    cast,
)
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from devrar.apantiseis import (
    KanalApantisis,
    SyllogistisCodexApantiseon,
)
from devrar.aporrita import katharise_aporrita
from devrar.xrisi import (
    ApotelesmaClaudeXrisis,
    SyllogistisClaudeXrisis,
    SyllogistisCodexXrisis,
)


class ZstandardApokodikopoiitis(Protocol):
    """Ελάχιστο interface του προαιρετικού decoder zstandard."""

    def stream_reader(self, source: BinaryIO) -> BinaryIO:
        """Δημιουργεί streaming reader για συμπιεσμένο περιεχόμενο."""


class ZstandardModule(Protocol):
    """Μέρος του API zstandard που χρησιμοποιεί ο collector."""

    ZstdError: type[Exception]

    def ZstdDecompressor(self) -> ZstandardApokodikopoiitis:
        """Δημιουργεί decompressor για ένα stream."""


try:
    # Dynamic import διατηρεί προαιρετικό το dependency χωρίς type-ignore για mypy.
    zstandard: ZstandardModule | None = cast(
        ZstandardModule, importlib.import_module("zstandard")
    )
except ImportError:  # pragma: no cover - εξαρτάται από προαιρετικό package
    zstandard = None
ZSTANDARD_DIATHESIMO = zstandard is not None
ZSTANDARD_SFALMA = zstandard.ZstdError if zstandard is not None else RuntimeError

logger = logging.getLogger(__name__)


class MetrikesAnaforas(TypedDict):
    """Εσωτερικές μετρικές με τύπους που διατηρούν το nullability του schema."""

    synedries: int
    rizikes: int
    ypopraktores: int
    minimata_xristi: int
    apantiseis: int
    kliseis_ergaleion: int
    tokens: int | None
    commits: int | None
    imeres: int


class MetrikesImeras(TypedDict):
    """Prompt και commit counts για μία ημερομηνία αναφοράς."""

    prompts: int
    commits: int | None


class Deigma(TypedDict):
    """Bounded transcript evidence row for local coaching analysis."""

    id: str
    pigi: str
    synedria: str
    rolos: Literal["user", "assistant", "tool"]
    eidos: Literal["prompt", "response", "tool_call", "tool_result"]
    keimeno: str
    locator: str
    imerominia: str | None


class KalypsiAnalysi(TypedDict):
    """Included and eligible evidence counts after bounded sampling."""

    epilegmena: int
    diathesima: int
    perikopi: bool


class KalypsiPigisTokens(TypedDict):
    """Per-source token evidence counts and collection status."""

    gnostes_aitiseis: int | None
    elleipeis_aitiseis: int | None
    agnosta_records: int | None
    methodos: str
    pliris: bool


class KalypsiTokens(TypedDict):
    """Coverage summary for token usage from all selected AI sources."""

    piges: dict[str, KalypsiPigisTokens]
    pliris: bool


class PeriodosDiathesimon(TypedDict):
    """Observed date bounds from recognized source events before filtering."""

    apo: str | None
    eos: str | None


@dataclass
class SygkrotitisPeriodou:
    """Κρατά μόνο min/max observed ημερομηνίες, όχι τη σειρά των events."""

    apo: date | None = None
    eos: date | None = None

    def prosthese(self, imerominia: date | None) -> None:
        """Επεκτείνει τα bounds μόνο με ημερομηνία που parse-αρίστηκε."""
        if imerominia is None:
            return
        self.apo = min(self.apo, imerominia) if self.apo else imerominia
        self.eos = max(self.eos, imerominia) if self.eos else imerominia

    def sto_schema(self) -> PeriodosDiathesimon:
        """Επιστρέφει νέα schema object με ISO date bounds."""
        return {
            "apo": self.apo.isoformat() if self.apo else None,
            "eos": self.eos.isoformat() if self.eos else None,
        }


PIGES = {"claude": "Claude Code", "codex": "Codex"}
ADAPTERS_PIGON = {"claude": "claude-jsonl-v1", "codex": "codex-jsonl-v1"}
GIT_ADAPTER = "git-head-v1"
PROTERAIOTITA_EIDON_DEIGMATON = {
    "prompt": 0,
    "response": 1,
    "tool_call": 2,
    "tool_result": 3,
}
CLAUDE_TYPOS_EGGRAFON = {
    "assistant",
    "bash_progress",
    "bridge-session",
    "bridge_session",
    "custom-title",
    "custom_title",
    "file-history-snapshot",
    "file_history_snapshot",
    "hook_progress",
    "last-prompt",
    "last_prompt",
    "mode",
    "permission-mode",
    "permission_mode",
    "progress",
    "queue-operation",
    "queue_operation",
    "session_meta",
    "summary",
    "system",
    "token_count",
    "tool_use_summary",
    "turn_context",
    "user",
}
CODEX_EVENT_TYPES = {
    "agent_message",
    "custom_tool_call",
    "custom_tool_call_output",
    "function_call",
    "function_call_output",
    "model_reasoning_summary_text",
    "reasoning",
    "task_complete",
    "token_count",
    "tool_call",
    "tool_call_output",
    "user_message",
    "web_search_call",
}
CODEX_RESPONSE_TYPES = {
    "code_interpreter_call",
    "compaction",
    "custom_tool_call",
    "custom_tool_call_output",
    "function_call",
    "function_call_output",
    "ghost_snapshot",
    "image_generation_call",
    "local_shell_call",
    "message",
    "reasoning",
    "token_count",
    "web_search_call",
}
CLAUDE_METADATA_KEYS = {
    "bridge-session",
    "bridge_session",
    "mode",
    "permission-mode",
    "permission_mode",
    "queue-operation",
    "queue_operation",
}
EIDI_MITRWTIKOU_CONTEXT = {
    "environments.environment_context",
    "additional_content.codex_apps_open_page",
}
CODEX_METADATA_TYPES = {"queue_operation", "token_count"}
PROEPILEGOMENA_PATHS = {
    "claude": Path.home() / ".claude" / "projects",
    "codex": Path.home() / ".codex" / "sessions",
}
ZSTD_SUFFIX = ".zst"
GIT_TIMEOUT_DEFTEROLEPTA = 30
MORFI_GIT_LOG = "%H%x1f%aN%x1f%aE%x1f%aI"
ORIA_DEIGMATON = 600
ORIA_MIKOUS_DEIGMATOS = 500
IMAGE_ONLY_PROMPT_NOTE = "Image-only human prompts are counted without text evidence."
PROELEFSIS_ANTHROPINIS = {
    "channel",
    "cli",
    "external",
    "human",
    "human_input",
    "interactive",
    "user",
    "user_input",
}


def _kalypsi_tokens(
    piges_epilegmenes: Sequence[str],
    katastasi_ana_pigi: Mapping[str, str],
    syllogistis_claude: SyllogistisClaudeXrisis,
    syllogistis_codex: SyllogistisCodexXrisis,
) -> tuple[KalypsiTokens, ApotelesmaClaudeXrisis]:
    """Δηλώνει token coverage χωρίς να μετατρέπει άγνωστες πηγές σε μηδέν."""
    sygkekrimenes_piges = set(piges_epilegmenes).intersection(PIGES)
    piges: dict[str, KalypsiPigisTokens] = {}
    claude = syllogistis_claude.synopsi(
        pigi_pliris=katastasi_ana_pigi.get("claude") == "ok"
    )
    if "claude" in sygkekrimenes_piges:
        katastasi_claude = katastasi_ana_pigi.get("claude")
        if katastasi_claude is None or katastasi_claude == "missing":
            piges["claude"] = {
                "gnostes_aitiseis": None,
                "elleipeis_aitiseis": None,
                "agnosta_records": None,
                "methodos": "source_unavailable",
                "pliris": False,
            }
        else:
            piges["claude"] = {
                "gnostes_aitiseis": claude.gnostes_aitiseis,
                "elleipeis_aitiseis": claude.elleipeis_aitiseis,
                "agnosta_records": claude.agnosta_records,
                "methodos": "claude_api_message_usage",
                "pliris": claude.pliris,
            }
    if "codex" in sygkekrimenes_piges:
        katastasi_codex = katastasi_ana_pigi.get("codex")
        einai_diathesimo = katastasi_codex is not None and katastasi_codex != "missing"
        piges["codex"] = {
            "gnostes_aitiseis": None,
            "elleipeis_aitiseis": None,
            "agnosta_records": (
                syllogistis_codex.agnosta_records() if einai_diathesimo else None
            ),
            "methodos": (
                "unsupported_cumulative_snapshots"
                if einai_diathesimo
                else "source_unavailable"
            ),
            "pliris": False,
        }
    pliris = bool(piges) and all(pigi["pliris"] for pigi in piges.values())
    return {"piges": piges, "pliris": pliris}, claude


def syllexe_dedomena(
    piges: Sequence[str],
    fakeloi: Mapping[str, Path],
    apothitiria: Sequence[Path],
    apo: date | None = None,
    eos: date | None = None,
    zoni: str = "Europe/Athens",
    author: str | None = None,
) -> dict[str, object]:
    """Διαβάζει τοπικά AI JSONL και δηλωμένα Git repos και επιστρέφει report v1."""
    if apo is not None and eos is not None and apo > eos:
        raise ValueError("Η ημερομηνία apo πρέπει να προηγείται ή να ισούται με eos.")
    try:
        zonh_anaforas = ZoneInfo(zoni)
    except ZoneInfoNotFoundError as sfalma:
        raise ValueError(f"Άγνωστη IANA timezone: {zoni}") from sfalma

    metrikes: MetrikesAnaforas = {
        "synedries": 0,
        "rizikes": 0,
        "ypopraktores": 0,
        "minimata_xristi": 0,
        "apantiseis": 0,
        "kliseis_ergaleion": 0,
        "tokens": None,
        "commits": None,
        "imeres": 0,
    }
    piges_report: list[dict[str, object]] = []
    ergaleia: list[dict[str, object]] = []
    montela: list[dict[str, object]] = []
    drastiriotita: dict[str, MetrikesImeras] = {}
    deigmata: list[Deigma] = []
    kalypsi_analysi: KalypsiAnalysi = {
        "epilegmena": 0,
        "diathesima": 0,
        "perikopi": False,
    }
    simeioseis: list[str] = []
    synedries_ana_pigi: dict[str, set[str]] = defaultdict(set)
    piges_ai_me_arxeia: set[str] = set()
    montela_ana_pigi: dict[str, Counter[str]] = defaultdict(Counter)
    eggrafes_dedup: dict[str, set[str]] = defaultdict(set)
    katastasi_ana_pigi: dict[str, str] = {}
    syllogistis_claude_xrisis = SyllogistisClaudeXrisis()
    syllogistis_codex_xrisis = SyllogistisCodexXrisis()
    syllogistis_codex_apantiseon = SyllogistisCodexApantiseon()

    for pigi in dict.fromkeys(piges):
        if pigi not in PIGES:
            piges_report.append(_pigi_row(pigi, 0, 1, "Μη υποστηριζόμενη πηγή."))
            simeioseis.append(f"Μη υποστηριζόμενη πηγή: {pigi}.")
            continue
        riziko = fakeloi.get(pigi, PROEPILEGOMENA_PATHS[pigi])
        arxeia = _vrese_arxeia(riziko)
        if not arxeia:
            katastasi_ana_pigi[pigi] = "missing"
            piges_report.append(
                _pigi_row(
                    PIGES[pigi],
                    0,
                    0,
                    "Δεν βρέθηκαν αρχεία υποστηριζόμενου format.",
                    "missing",
                    adapter=ADAPTERS_PIGON[pigi],
                )
            )
            simeioseis.append(
                f"Δεν βρέθηκαν {PIGES[pigi]} JSONL αρχεία στην επιλεγμένη τοποθεσία."
            )
            continue
        sfalmata = 0
        agnostoi_chronoi = 0
        eixe_morfi_anagnorismeni = False
        periodos_pigis = SygkrotitisPeriodou()
        morfes_pigis = sorted({_morfi_arxeiou(arxeio) for arxeio in arxeia})
        prompts_proigoumena = metrikes["minimata_xristi"]
        synedries = synedries_ana_pigi[pigi]
        paidia: set[str] = set()
        apotypomata_prompt: dict[str, tuple[str, str]] = {}
        for arxeio in arxeia:
            try:
                with _anoikse_jsonl(arxeio) as roi:
                    (
                        diavase_esto,
                        sfalmata_arxeiou,
                        agnostoi_arxeiou,
                        eixe_arxeia_anagnorismena,
                    ) = _diavase_arxeio(
                        roi,
                        pigi,
                        arxeio,
                        synedries,
                        paidia,
                        eggrafes_dedup[pigi],
                        apotypomata_prompt,
                        montela_ana_pigi[pigi],
                        metrikes,
                        deigmata,
                        kalypsi_analysi,
                        simeioseis,
                        syllogistis_claude_xrisis,
                        syllogistis_codex_xrisis,
                        syllogistis_codex_apantiseon,
                        periodos_pigis,
                        drastiki=drastiriotita,
                        zoni=zonh_anaforas,
                        apo=apo,
                        eos=eos,
                    )
                if not diavase_esto:
                    sfalmata_arxeiou += 1
                sfalmata += sfalmata_arxeiou
                agnostoi_chronoi += agnostoi_arxeiou
                eixe_morfi_anagnorismeni = (
                    eixe_morfi_anagnorismeni or eixe_arxeia_anagnorismena
                )
            except (
                OSError,
                UnicodeError,
                ValueError,
                RuntimeError,
                ZSTANDARD_SFALMA,
            ) as sfalma:
                logger.warning(
                    "Αδυναμία ανάγνωσης %s (%s): %s", arxeio.name, pigi, sfalma
                )
                sfalmata += 1
        if eixe_morfi_anagnorismeni:
            piges_ai_me_arxeia.add(pigi)
        synedries_ana_pigi[pigi] = synedries
        metrikes["ypopraktores"] += len(paidia.intersection(synedries))
        sfalmata_kalypsis = sfalmata + agnostoi_chronoi
        katastasi = "ok" if sfalmata_kalypsis == 0 else "partial"
        katastasi_ana_pigi[pigi] = katastasi
        piges_report.append(
            _pigi_row(
                PIGES[pigi],
                len(arxeia),
                sfalmata_kalypsis,
                "",
                katastasi,
                adapter=ADAPTERS_PIGON[pigi],
                morfes=morfes_pigis,
                periodos_diathesimon=periodos_pigis.sto_schema(),
            )
        )
        if sfalmata:
            simeioseis.append(
                f"{PIGES[pigi]}: {sfalmata} records ήταν malformed, "
                "unrecognized ή χωρίς αξιοποιήσιμο timestamp."
            )
        if agnostoi_chronoi:
            simeioseis.append(
                f"{PIGES[pigi]}: {agnostoi_chronoi} events with unknown "
                "timestamps were excluded from "
                "filtered totals, so selected-period counts are partial."
            )
        ergaleia.append(
            {
                "onoma": PIGES[pigi],
                "synedries": len(synedries),
                "prompts": metrikes["minimata_xristi"] - prompts_proigoumena,
                "tokens": None,
            }
        )
    kalypsi_tokens, tokens_claude = _kalypsi_tokens(
        list(dict.fromkeys(piges)),
        katastasi_ana_pigi,
        syllogistis_claude_xrisis,
        syllogistis_codex_xrisis,
    )
    tokens_olokliromena = bool(kalypsi_tokens["piges"]) and bool(
        kalypsi_tokens["pliris"]
    )
    kalypsi_claude = kalypsi_tokens["piges"].get("claude")
    tokens_claude_pliri = bool(kalypsi_claude and kalypsi_claude["pliris"])
    metrikes["tokens"] = tokens_claude.tokens if tokens_olokliromena else None
    for ergaleio in ergaleia:
        ergaleio["tokens"] = (
            tokens_claude.tokens
            if ergaleio["onoma"] == PIGES["claude"] and tokens_claude_pliri
            else None
        )
    if kalypsi_claude is not None and not kalypsi_claude["pliris"]:
        simeioseis.append(
            "Claude token usage remains unavailable or partial unless every observed "
            "API message has a stable ID, consistent model/stop reason, and all four "
            "valid usage components. Copies are deduplicated by API message ID."
        )

    dedup_apantiseon = syllogistis_codex_apantiseon.synopsi()
    metrikes["apantiseis"] += dedup_apantiseon.plithos
    for candidate in dedup_apantiseon.candidates:
        if candidate.modelo:
            montela_ana_pigi["codex"][candidate.modelo] += 1
    for deigma_apantisis in dedup_apantiseon.candidates:
        tautotita_apantisis = deigma_apantisis.tautotita or (
            f"{deigma_apantisis.synedria}:{deigma_apantisis.turn_id or 'unknown'}:"
            f"{deigma_apantisis.fingerprint}:{deigma_apantisis.seira}"
        )
        _prosthese_deigma(
            "codex",
            tautotita_apantisis,
            deigma_apantisis.synedria,
            "assistant",
            "response",
            deigma_apantisis.keimeno,
            deigma_apantisis.locator,
            deigma_apantisis.imerominia,
            deigma_apantisis.seira,
            deigmata,
            kalypsi_analysi,
        )
    if dedup_apantiseon.amfigies:
        for pigi_row in piges_report:
            if pigi_row["onoma"] == PIGES["codex"]:
                pigi_row["katastasi"] = "partial"
                sfalmata_pigis = pigi_row["sfalmata"]
                pigi_row["sfalmata"] = (
                    sfalmata_pigis + dedup_apantiseon.amfigies
                    if isinstance(sfalmata_pigis, int)
                    else dedup_apantiseon.amfigies
                )
                pigi_row["simeiosi"] = (
                    f"{pigi_row['simeiosi']} "
                    "Codex assistant reply attribution is ambiguous without turn IDs."
                ).strip()
        simeioseis.append(
            "Codex assistant reply attribution is ambiguous without turn IDs."
        )

    for pigi in dict.fromkeys(piges):
        if pigi not in PIGES:
            continue
        for modelo, kliseis in sorted(montela_ana_pigi[pigi].items()):
            montela.append(
                {
                    "onoma": modelo,
                    "kliseis": (
                        None
                        if pigi == "codex" and modelo in dedup_apantiseon.montela_amfiga
                        else kliseis
                    ),
                    "tokens": (
                        tokens_claude.tokens_ana_modelo.get(modelo)
                        if pigi == "claude" and tokens_claude_pliri
                        else None
                    ),
                    "pigi": pigi,
                }
            )

    # Χωρίς AI sources, μηδενικοί counters σημαίνουν μηδενικά επιλεγμένα δεδομένα.
    commit_ids_synola: set[str] = set()
    erga: list[dict[str, object]] = []
    if apothitiria:
        sfalmata_git = 0
        agnostes_imerominies_git = 0
        apothikies_idomenes: set[str] = set()
        periodos_git = SygkrotitisPeriodou()
        filtro_grafea = author.casefold().strip() or None if author else None
        for apothikio in apothitiria:
            kleidi_apothikiou = os.path.normcase(str(apothikio.resolve()))
            if kleidi_apothikiou in apothikies_idomenes:
                continue
            apothikies_idomenes.add(kleidi_apothikiou)
            try:
                (
                    commit_ids,
                    plithos_arxeion,
                    periodos_apothikioy,
                    agnostes_imerominies,
                ) = _diavase_git_commits(
                    apothikio, zonh_anaforas, apo, eos, filtro_grafea
                )
            except (OSError, subprocess.SubprocessError, ValueError) as sfalma:
                logger.warning(
                    "Αδυναμία ανάγνωσης Git repository %s: %s", apothikio.name, sfalma
                )
                sfalmata_git += 1
                erga.append({"onoma": apothikio.name, "commits": None, "arxeia": None})
                continue
            agnostes_imerominies_git += agnostes_imerominies
            periodos_git.prosthese(periodos_apothikioy.apo)
            periodos_git.prosthese(periodos_apothikioy.eos)
            erga.append(
                {
                    "onoma": apothikio.name,
                    "commits": len(commit_ids),
                    "arxeia": plithos_arxeion,
                }
            )
            nea_commit_ids = commit_ids.keys() - commit_ids_synola
            commit_ids_synola.update(commit_ids)
            for commit_id in nea_commit_ids:
                commit = commit_ids[commit_id]
                imera_commit = commit["imerominia"]
                if imera_commit is not None:
                    metrikes_imeras = _vevaiwse_drastiriotita(
                        drastiriotita, imera_commit
                    )
                    metrikes_imeras["commits"] = (
                        int(metrikes_imeras["commits"] or 0) + 1
                    )
        metrikes["commits"] = None if sfalmata_git else len(commit_ids_synola)
        synolika_sfalmata_git = sfalmata_git + agnostes_imerominies_git
        katastasi_git = "ok" if synolika_sfalmata_git == 0 else "partial"
        simeiosi_git = ""
        if sfalmata_git:
            simeiosi_git = "Ορισμένα repositories δεν ήταν αναγνώσιμα."
        if agnostes_imerominies_git:
            simeiosi_git = (f"{simeiosi_git} " if simeiosi_git else "") + (
                f"{agnostes_imerominies_git} commits with unknown author dates "
                "were excluded from filtered totals."
            )
        if periodos_git.apo is None or periodos_git.eos is None:
            simeiosi_git = (
                f"{simeiosi_git} " if simeiosi_git else ""
            ) + "Δεν παρατηρήθηκαν έγκυρες ημερομηνίες σε HEAD history."
        piges_report.append(
            _pigi_row(
                "Git",
                len(apothikies_idomenes),
                synolika_sfalmata_git,
                simeiosi_git,
                katastasi_git,
                adapter=GIT_ADAPTER,
                morfes=["git"],
                periodos_diathesimon=periodos_git.sto_schema(),
            )
        )
        if sfalmata_git:
            simeioseis.append(f"Git: {sfalmata_git} repositories δεν ήταν αναγνώσιμα.")
        if agnostes_imerominies_git:
            simeioseis.append(
                f"Git: {agnostes_imerominies_git} commits with unknown timestamps "
                "were excluded from filtered totals, so selected-period counts "
                "are partial."
            )
    else:
        metrikes["commits"] = None

    metrikes["synedries"] = len(
        {
            (pigi, synedria)
            for pigi, times in synedries_ana_pigi.items()
            for synedria in times
        }
    )
    metrikes["rizikes"] = max(0, metrikes["synedries"] - metrikes["ypopraktores"])
    metrikes["imeres"] = len(drastiriotita)
    yparxei_ai_kalypsi = bool(piges_ai_me_arxeia)
    for ergaleio in ergaleia:
        pigi = next(
            (key for key, etiketa in PIGES.items() if etiketa == ergaleio["onoma"]), ""
        )
        ergaleio["synedries"] = len(synedries_ana_pigi[pigi])
    for imera_key, metrikes_imeras in sorted(drastiriotita.items()):
        if metrikes["commits"] is None:
            metrikes_imeras["commits"] = None
    # Unknown metrics remain unavailable; no engineering score is inferred by ingestion.
    seira_pigon = {
        PIGES[pigi]: seira
        for seira, pigi in enumerate(dict.fromkeys(piges))
        if pigi in PIGES
    }
    deigmata.sort(key=lambda deigma: _seira_deigmatos(deigma, seira_pigon))
    return {
        "ekdosi_sximatos": "1",
        "leitourgia": "live",
        "periodos": {
            "apo": apo.isoformat() if apo else None,
            "eos": eos.isoformat() if eos else None,
            "zoni": zoni,
        },
        "synola": {
            "synedries": metrikes["synedries"] if yparxei_ai_kalypsi else None,
            "rizikes": metrikes["rizikes"] if yparxei_ai_kalypsi else None,
            "ypopraktores": metrikes["ypopraktores"] if yparxei_ai_kalypsi else None,
            "minimata_xristi": (
                metrikes["minimata_xristi"] if yparxei_ai_kalypsi else None
            ),
            "apantiseis": (
                None
                if dedup_apantiseon.amfigies or not yparxei_ai_kalypsi
                else metrikes["apantiseis"]
            ),
            "kliseis_ergaleion": (
                metrikes["kliseis_ergaleion"] if yparxei_ai_kalypsi else None
            ),
            "tokens": metrikes["tokens"],
            "commits": metrikes["commits"],
            "imeres": metrikes["imeres"],
        },
        "ergaleia": ergaleia,
        "montela": montela,
        "drastiriotita": [
            {
                "imerominia": imera_key,
                "prompts": metrikes_imeras["prompts"],
                "commits": metrikes_imeras["commits"],
            }
            for imera_key, metrikes_imeras in sorted(drastiriotita.items())
        ],
        "projects": erga,
        "scope_git": {"rev": "HEAD", "author": filtro_grafea} if apothitiria else None,
        "deigmata": deigmata,
        "kalypsi_analysi": kalypsi_analysi,
        "kalypsi_tokens": kalypsi_tokens,
        "axiologisi": {
            "diathesimi": False,
            "synoliko": None,
            "aitia": "Not enough verified evidence to calculate an engineering score.",
            "diastaseis": [],
        },
        "eyrimata": [],
        "oroshma": [],
        "piges": piges_report,
        "simeioseis": simeioseis,
    }


def _pigi_row(
    onoma: str,
    arxeia: int,
    sfalmata: int,
    simeiosi: str,
    katastasi: str | None = None,
    adapter: str | None = None,
    morfes: Sequence[str] | None = None,
    periodos_diathesimon: PeriodosDiathesimon | None = None,
) -> dict[str, object]:
    """Δημιουργεί coverage row συμβατό με το report schema."""
    katastasi_trexousa = katastasi or ("ok" if arxeia and not sfalmata else "partial")
    periodos = periodos_diathesimon or {"apo": None, "eos": None}
    return {
        "onoma": onoma,
        "katastasi": katastasi_trexousa,
        "arxeia": arxeia,
        "sfalmata": sfalmata,
        "simeiosi": simeiosi,
        "adapter": adapter,
        "morfes": list(morfes or []),
        "periodos_diathesimon": periodos,
    }


def _seira_deigmatos(
    deigma: Deigma, seira_pigon: Mapping[str, int]
) -> tuple[int, str, int, int]:
    """Ταξινομεί evidence με source/file/line και σειρά τύπου μέσα στη γραμμή."""
    onoma_arxeiou, diaxoristiko, grammi = deigma["locator"].rpartition(":")
    arithmos_grammis = int(grammi) if diaxoristiko and grammi.isdigit() else 0
    proteraiotita = PROTERAIOTITA_EIDON_DEIGMATON.get(deigma["eidos"], 4)
    return (
        seira_pigon.get(deigma["pigi"], len(seira_pigon)),
        onoma_arxeiou,
        arithmos_grammis,
        proteraiotita,
    )


def _vrese_arxeia(riziko: Path) -> list[Path]:
    """Επιστρέφει μόνο JSONL και προαιρετικά JSONL.zst αρχεία."""
    if riziko.is_file():
        ypopsifia_arxeia = [riziko]
    elif riziko.is_dir():
        ypopsifia_arxeia = sorted(
            diadromi for diadromi in riziko.rglob("*") if diadromi.is_file()
        )
    else:
        return []
    return [
        diadromi
        for diadromi in ypopsifia_arxeia
        if diadromi.name.casefold().endswith((".jsonl", ".jsonl.zst"))
    ]


def _morfi_arxeiou(arxeio: Path) -> str:
    """Επιστρέφει μόνο επιτρεπόμενο suffix χωρίς να αποκαλύπτει path."""
    return "jsonl.zst" if arxeio.name.casefold().endswith(".jsonl.zst") else "jsonl"


def _anoikse_jsonl(diadromi: Path) -> TextIO:
    """Ανοίγει JSONL σε UTF-8 και αποκωδικοποιεί zstd μόνο αν υπάρχει decoder."""
    if diadromi.name.casefold().endswith(ZSTD_SUFFIX):
        if not ZSTANDARD_DIATHESIMO or zstandard is None:
            raise RuntimeError(
                "Το προαιρετικό package zstandard δεν είναι εγκατεστημένο."
            )
        # Το TextIOWrapper κρατά streaming ανάγνωση για μεγάλα compressed transcripts.
        import io

        roi = zstandard.ZstdDecompressor().stream_reader(diadromi.open("rb"))
        return io.TextIOWrapper(roi, encoding="utf-8")
    return diadromi.open("r", encoding="utf-8")


def _einai_eggrafi_anagnorismeni(pigi: str, eggrafi: dict[str, object]) -> bool:
    """Ελέγχει schema type ή ασφαλή metadata record για Claude και Codex."""
    typos = _proto_keimeno(eggrafi.get("type"))
    payload_obj = eggrafi.get("payload")
    payload = payload_obj if isinstance(payload_obj, dict) else {}
    if pigi == "claude":
        if typos in CLAUDE_TYPOS_EGGRAFON:
            return True
        return any(
            kleidi in eggrafi or kleidi in payload for kleidi in CLAUDE_METADATA_KEYS
        )
    if typos in {"session_meta", "turn_context"}:
        return isinstance(payload_obj, dict)
    if typos in CODEX_METADATA_TYPES:
        return isinstance(payload_obj, dict) or (
            typos == "queue_operation" and isinstance(eggrafi.get("operation"), str)
        )
    if typos == "event_msg":
        return _proto_keimeno(payload.get("type")) in CODEX_EVENT_TYPES
    if typos == "response_item":
        return _proto_keimeno(payload.get("type")) in CODEX_RESPONSE_TYPES
    return False


def _diavase_arxeio(
    roi: TextIO,
    pigi: str,
    arxeio: Path,
    synedries: set[str],
    paidia: set[str],
    ids_diplotypwn: set[str],
    apotypomata_prompt: dict[str, tuple[str, str]],
    montela: Counter[str],
    metrikes: MetrikesAnaforas,
    deigmata: list[Deigma],
    kalypsi_analysi: KalypsiAnalysi,
    simeioseis: list[str],
    syllogistis_claude_xrisis: SyllogistisClaudeXrisis,
    syllogistis_codex_xrisis: SyllogistisCodexXrisis,
    syllogistis_codex_apantiseon: SyllogistisCodexApantiseon,
    periodos_diathesimon: SygkrotitisPeriodou,
    drastiki: dict[str, MetrikesImeras],
    zoni: ZoneInfo,
    apo: date | None,
    eos: date | None,
) -> tuple[bool, int, int, bool]:
    """Διαβάζει JSONL γραμμή-γραμμή, κρατώντας έγκυρα records μετά από σφάλματα."""
    diavase_esto = False
    eixe_morfi_anagnorismeni = False
    sfalmata = 0
    agnostoi_chronoi = 0
    efedriki_synedria = arxeio.stem.removesuffix(".jsonl")
    energi_synedria = efedriki_synedria
    energo_modelo: str | None = None
    energo_goneas: str | None = None
    energo_turn_id: str | None = None
    for arithmos_grammis, grammi in enumerate(roi, 1):
        if not grammi.strip():
            continue
        try:
            eggrafi = json.loads(grammi)
        except json.JSONDecodeError:
            logger.warning(
                "Malformed JSONL record at %s:%d", arxeio.name, arithmos_grammis
            )
            sfalmata += 1
            continue
        if not isinstance(eggrafi, dict):
            sfalmata += 1
            continue
        diavase_esto = True
        if not _einai_eggrafi_anagnorismeni(pigi, eggrafi):
            sfalmata += 1
            continue
        eixe_morfi_anagnorismeni = True
        payload_obj = eggrafi.get("payload")
        payload = payload_obj if isinstance(payload_obj, dict) else {}
        minima_obj = eggrafi.get("message") or payload.get("message")
        minima = minima_obj if isinstance(minima_obj, dict) else {}
        chronos_pigis = _proto_keimeno(
            eggrafi.get("timestamp"), payload.get("timestamp"), minima.get("timestamp")
        )
        periodos_diathesimon.prosthese(_imerominia_zonis(chronos_pigis, zoni))
        fortio = eggrafi.get("payload")
        if eggrafi.get("type") == "session_meta" and isinstance(fortio, dict):
            energi_synedria = (
                _proto_keimeno(fortio.get("id"), fortio.get("session_id"))
                or energi_synedria
            )
        if eggrafi.get("type") == "turn_context" and isinstance(fortio, dict):
            energo_modelo = _proto_keimeno(fortio.get("model"))
            energo_turn_id = _proto_keimeno(
                fortio.get("turn_id"), fortio.get("root_turn_id")
            )
        if eggrafi.get("type") == "session_meta" and isinstance(fortio, dict):
            energo_goneas = (
                _proto_keimeno(
                    fortio.get("parentSessionId"), fortio.get("parent_session_id")
                )
                or energo_goneas
            )
        agnostos_chronos = _kanonikopoihse_eggrafi(
            eggrafi,
            pigi,
            energi_synedria,
            synedries,
            paidia,
            ids_diplotypwn,
            apotypomata_prompt,
            montela,
            metrikes,
            drastiki,
            zoni,
            apo,
            eos,
            energo_modelo,
            energo_goneas,
            f"{arxeio.name}:{arithmos_grammis}",
            deigmata,
            kalypsi_analysi,
            simeioseis,
            syllogistis_claude_xrisis,
            syllogistis_codex_xrisis,
            syllogistis_codex_apantiseon,
            energo_turn_id,
        )
        if agnostos_chronos:
            agnostoi_chronoi += 1
    return diavase_esto, sfalmata, agnostoi_chronoi, eixe_morfi_anagnorismeni


def _kanonikopoihse_eggrafi(
    eggrafi: dict[str, object],
    pigi: str,
    efedriki_synedria: str,
    synedries: set[str],
    paidia: set[str],
    ids_diplotypwn: set[str],
    apotypomata_prompt: dict[str, tuple[str, str]],
    montela: Counter[str],
    metrikes: MetrikesAnaforas,
    drastiki: dict[str, MetrikesImeras],
    zoni: ZoneInfo,
    apo: date | None,
    eos: date | None,
    energo_modelo: str | None,
    energo_goneas: str | None,
    locator: str,
    deigmata: list[Deigma],
    kalypsi_analysi: KalypsiAnalysi,
    simeioseis: list[str],
    syllogistis_claude_xrisis: SyllogistisClaudeXrisis,
    syllogistis_codex_xrisis: SyllogistisCodexXrisis,
    syllogistis_codex_apantiseon: SyllogistisCodexApantiseon,
    energo_turn_id: str | None,
) -> bool:
    """Κανονικοποιεί record Claude ή Codex χωρίς να εκτελεί imported content."""
    fortio_obj = eggrafi.get("payload")
    fortio = fortio_obj if isinstance(fortio_obj, dict) else {}
    minima_obj = eggrafi.get("message") or fortio.get("message")
    minima = minima_obj if isinstance(minima_obj, dict) else {}
    meta = fortio if eggrafi.get("type") == "session_meta" else {}
    agent_tautotita = _proto_keimeno(eggrafi.get("agentId"), meta.get("agentId"))
    synedria_id = _proto_keimeno(
        agent_tautotita,
        eggrafi.get("sessionId"),
        eggrafi.get("session_id"),
        meta.get("id"),
        meta.get("session_id"),
        efedriki_synedria,
    )
    goneas = _proto_keimeno(
        eggrafi.get("parentSessionId"),
        eggrafi.get("parent_session_id"),
        meta.get("parentSessionId"),
        meta.get("parent_session_id"),
        energo_goneas,
    )
    turn_id = _proto_keimeno(
        eggrafi.get("turn_id"),
        eggrafi.get("root_turn_id"),
        fortio.get("turn_id"),
        fortio.get("root_turn_id"),
        energo_turn_id,
    )

    chronos = _proto_keimeno(
        eggrafi.get("timestamp"), fortio.get("timestamp"), minima.get("timestamp")
    )
    imera = _imerominia_zonis(chronos, zoni)
    if chronos and imera is None:
        # Μη έγκυρες ημερομηνίες μένουν άγνωστες ως προς το ημερολογιακό φίλτρο.
        pass
    elif (apo is not None and imera is not None and imera < apo) or (
        eos is not None and imera is not None and imera > eos
    ):
        return False

    typos_eggrafis = _proto_keimeno(eggrafi.get("type"), fortio.get("type"))
    rolos = _proto_keimeno(eggrafi.get("role"), minima.get("role"), fortio.get("role"))
    einai_record_assistant_claude = pigi == "claude" and typos_eggrafis == "assistant"
    einai_codex_snapshot = pigi == "codex" and (
        (typos_eggrafis == "event_msg" and fortio.get("type") == "token_count")
        or (
            typos_eggrafis == "token_count" and isinstance(eggrafi.get("payload"), dict)
        )
    )
    einai_prompt = False
    einai_apantisi = False
    einai_reply_codex = False
    kanal_apantisis: KanalApantisis | None = None
    keimeno_apantisis: str | None = None
    kliseis = 0
    keimeno_prompt: str | None = None
    periexomeno_apodeixis: object = None
    periexomeno_filtrarismeno = False
    einai_prompt_mono_eikona = False
    modelo = _proto_keimeno(
        minima.get("model"), fortio.get("model"), eggrafi.get("model"), energo_modelo
    )
    if pigi == "claude":
        rolos = rolos or _proto_keimeno(eggrafi.get("type"))
        periexomeno = minima.get("content", eggrafi.get("content"))
        periexomeno_apodeixis = periexomeno
        if rolos == "user":
            proelefsi_pigis = eggrafi.get("origin")
            typos_origin = (
                proelefsi_pigis.get("kind")
                if isinstance(proelefsi_pigis, dict)
                else None
            )
            einai_synthetic_meta = (
                eggrafi.get("isMeta") is True and typos_origin != "channel"
            )
            if not einai_synthetic_meta:
                (
                    keimeno_prompt,
                    eikona_xristi,
                    periexomeno_apodeixis,
                ) = _analuse_periexomeno_xristi(eggrafi, periexomeno)
                periexomeno_filtrarismeno = True
                einai_prompt_mono_eikona = eikona_xristi and not keimeno_prompt
                einai_prompt = bool(keimeno_prompt) or eikona_xristi
        elif rolos == "assistant":
            einai_apantisi = _exei_anthropino_keimeno(periexomeno)
            kliseis = _metrise_kliseis_ergaleion(periexomeno)
    else:
        if typos_eggrafis == "event_msg":
            if fortio.get("type") == "user_message":
                (
                    keimeno_prompt,
                    eikona_xristi,
                    periexomeno_apodeixis,
                ) = _analuse_periexomeno_xristi(eggrafi, fortio.get("message"))
                periexomeno_filtrarismeno = True
                einai_prompt_mono_eikona = eikona_xristi and not keimeno_prompt
                einai_prompt = bool(keimeno_prompt) or eikona_xristi
            elif fortio.get("type") in {"agent_message", "task_complete"}:
                periexomeno_apantisis = fortio.get("message") or fortio.get(
                    "last_agent_message"
                )
                keimeno_apantisis = _keimeno_keimenou(
                    periexomeno_apantisis, {"text", "output_text"}
                )
                kanal_apantisis = (
                    "agent_message"
                    if fortio.get("type") == "agent_message"
                    else "task_complete"
                )
                einai_reply_codex = bool(keimeno_apantisis)
                einai_apantisi = einai_reply_codex
            elif fortio.get("type") in {
                "tool_call",
                "function_call",
                "custom_tool_call",
            }:
                kliseis = 1
        elif typos_eggrafis == "response_item":
            typos_antikeimenou = _proto_keimeno(fortio.get("type"))
            if typos_antikeimenou == "message":
                if rolos == "user":
                    (
                        keimeno_prompt,
                        eikona_xristi,
                        periexomeno_apodeixis,
                    ) = _analuse_periexomeno_xristi(
                        eggrafi, minima.get("content", fortio.get("content"))
                    )
                    periexomeno_filtrarismeno = True
                    einai_prompt_mono_eikona = eikona_xristi and not keimeno_prompt
                    einai_prompt = bool(keimeno_prompt) or eikona_xristi
                elif rolos == "assistant":
                    keimeno_apantisis = _keimeno_keimenou(
                        minima.get("content", fortio.get("content")),
                        {"text", "output_text"},
                    )
                    kanal_apantisis = "response_item"
                    einai_reply_codex = bool(keimeno_apantisis)
                    einai_apantisi = einai_reply_codex
            elif typos_antikeimenou in {"function_call", "custom_tool_call"}:
                kliseis = 1
    einai_prompt_anthropino = (
        einai_prompt
        and not goneas
        and not agent_tautotita
        and _einai_proelefsi_anthropini(eggrafi)
    )
    if (
        (apo is not None or eos is not None)
        and (
            einai_prompt
            or einai_apantisi
            or einai_reply_codex
            or kliseis
            or einai_record_assistant_claude
            or einai_codex_snapshot
        )
        and imera is None
    ):
        return True
    if einai_record_assistant_claude:
        syllogistis_claude_xrisis.prosthese(eggrafi)
    if einai_codex_snapshot:
        syllogistis_codex_xrisis.prosthese(eggrafi)
    tautotita = _tautotita_eggrafis(eggrafi, fortio, pigi)
    einai_diplotypi_tautotita = bool(tautotita and tautotita in ids_diplotypwn)
    if einai_diplotypi_tautotita:
        return False
    if tautotita:
        ids_diplotypwn.add(tautotita)
    if (
        pigi == "codex"
        and einai_reply_codex
        and kanal_apantisis is not None
        and keimeno_apantisis is not None
    ):
        syllogistis_codex_apantiseon.prosthese(
            synedria_id or efedriki_synedria,
            turn_id,
            kanal_apantisis,
            keimeno_apantisis,
            tautotita,
            chronos,
            imera.isoformat() if imera else None,
            modelo,
            locator,
        )
        einai_apantisi = False
    if (
        pigi == "codex"
        and einai_prompt
        and chronos
        and keimeno_prompt
        and not tautotita
    ):
        apotypoma_prompt = hashlib.sha256(
            f"{chronos}\0{keimeno_prompt}".encode("utf-8")
        ).hexdigest()
        tautotita_prompt = (synedria_id or "", typos_eggrafis or "")
        proigoumeni_tautotita = apotypomata_prompt.get(apotypoma_prompt)
        if (
            proigoumeni_tautotita is not None
            and proigoumeni_tautotita != tautotita_prompt
        ):
            return False
        if proigoumeni_tautotita is None:
            apotypomata_prompt[apotypoma_prompt] = tautotita_prompt
    if pigi != "claude" and not periexomeno_filtrarismeno:
        periexomeno_apodeixis = (
            fortio.get("message") or fortio.get("last_agent_message")
            if typos_eggrafis == "event_msg"
            and fortio.get("type") in {"agent_message", "task_complete"}
            else minima.get("content", fortio.get("content"))
        )
    if (
        einai_prompt_mono_eikona
        and einai_prompt_anthropino
        and IMAGE_ONLY_PROMPT_NOTE not in simeioseis
    ):
        simeioseis.append(IMAGE_ONLY_PROMPT_NOTE)
    _prosthese_apodeixeis(
        pigi,
        eggrafi,
        fortio,
        typos_eggrafis,
        rolos,
        periexomeno_apodeixis,
        keimeno_prompt,
        einai_prompt,
        einai_apantisi,
        synedria_id or efedriki_synedria,
        goneas,
        agent_tautotita,
        tautotita,
        locator,
        imera,
        deigmata,
        kalypsi_analysi,
    )
    yparxei_drastiriotita = (
        einai_prompt or einai_apantisi or einai_reply_codex or bool(kliseis)
    )
    if synedria_id and yparxei_drastiriotita:
        synedries.add(synedria_id)
    if (
        synedria_id
        and yparxei_drastiriotita
        and (
            goneas
            or eggrafi.get("isSidechain") is True
            or eggrafi.get("is_subagent") is True
            or eggrafi.get("agentId")
            or meta.get("is_subagent") is True
            or meta.get("agentId")
        )
    ):
        paidia.add(synedria_id)
    if modelo and (einai_apantisi or kliseis):
        montela[modelo] += 1
    if einai_prompt_anthropino:
        metrikes["minimata_xristi"] += 1
        if imera is not None:
            _vevaiwse_drastiriotita(drastiki, imera)["prompts"] += 1
    if einai_apantisi:
        metrikes["apantiseis"] += 1
    if kliseis:
        metrikes["kliseis_ergaleion"] += kliseis
    if imera is not None and (
        einai_prompt or einai_apantisi or einai_reply_codex or kliseis
    ):
        _vevaiwse_drastiriotita(drastiki, imera)
    return False


def _prosthese_apodeixeis(
    pigi: str,
    eggrafi: dict[str, object],
    fortio: dict[str, object],
    typos_eggrafis: str | None,
    rolos: str | None,
    periexomeno: object,
    keimeno_prompt: str | None,
    einai_prompt: bool,
    einai_apantisi: bool,
    synedria: str,
    goneas: str | None,
    agent_tautotita: str | None,
    tautotita: str | None,
    locator: str,
    imera: date | None,
    deigmata: list[Deigma],
    kalypsi_analysi: KalypsiAnalysi,
) -> None:
    """Εξάγει μόνο αναγνωρισμένο, deduped evidence με provenance περιορισμένο."""
    prompt_asfales = (
        einai_prompt
        and (
            rolos == "user"
            or (
                pigi == "codex"
                and typos_eggrafis == "event_msg"
                and fortio.get("type") == "user_message"
            )
        )
        and not goneas
        and not agent_tautotita
        and eggrafi.get("isSidechain") is not True
        and eggrafi.get("is_subagent") is not True
        and _einai_proelefsi_anthropini(eggrafi)
    )
    imerominia = imera.isoformat() if imera else None
    arithmos = 0
    if prompt_asfales and keimeno_prompt:
        _prosthese_deigma(
            pigi,
            tautotita,
            synedria,
            "user",
            "prompt",
            keimeno_prompt,
            locator,
            imerominia,
            arithmos,
            deigmata,
            kalypsi_analysi,
        )
        arithmos += 1
    if einai_apantisi:
        keimeno_apantisis = _keimeno_keimenou(periexomeno, {"text", "output_text"})
        if keimeno_apantisis:
            _prosthese_deigma(
                pigi,
                tautotita,
                synedria,
                "assistant",
                "response",
                keimeno_apantisis,
                locator,
                imerominia,
                arithmos,
                deigmata,
                kalypsi_analysi,
            )
            arithmos += 1

    periexomeno_blocks = periexomeno if isinstance(periexomeno, list) else []
    if pigi == "claude":
        for block in periexomeno_blocks:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                onoma_ergaleiou = _proto_keimeno(block.get("name"))
                if onoma_ergaleiou:
                    _prosthese_deigma(
                        pigi,
                        tautotita or _proto_keimeno(block.get("id")),
                        synedria,
                        "tool",
                        "tool_call",
                        onoma_ergaleiou,
                        locator,
                        imerominia,
                        arithmos,
                        deigmata,
                        kalypsi_analysi,
                    )
                    arithmos += 1
            elif rolos == "user" and block.get("type") == "tool_result":
                apotelesma = _keimeno_keimenou(
                    block.get("content"), {"text", "output_text"}
                )
                if apotelesma:
                    _prosthese_deigma(
                        pigi,
                        tautotita or _proto_keimeno(block.get("tool_use_id")),
                        synedria,
                        "tool",
                        "tool_result",
                        apotelesma,
                        locator,
                        imerominia,
                        arithmos,
                        deigmata,
                        kalypsi_analysi,
                    )
                    arithmos += 1
    elif pigi == "codex":
        eidos_codex = _proto_keimeno(fortio.get("type"))
        if eidos_codex in {"tool_call", "function_call", "custom_tool_call"} or (
            typos_eggrafis == "response_item"
            and eidos_codex in {"function_call", "custom_tool_call"}
        ):
            onoma_ergaleiou = _proto_keimeno(
                fortio.get("name"), fortio.get("tool_name"), fortio.get("tool")
            )
            if onoma_ergaleiou:
                _prosthese_deigma(
                    pigi,
                    tautotita,
                    synedria,
                    "tool",
                    "tool_call",
                    onoma_ergaleiou,
                    locator,
                    imerominia,
                    arithmos,
                    deigmata,
                    kalypsi_analysi,
                )
                arithmos += 1
        if eidos_codex in {
            "tool_call_output",
            "custom_tool_call_output",
            "function_call_output",
            "tool_result",
        }:
            apotelesma = _proto_keimeno(
                fortio.get("output"), fortio.get("content"), fortio.get("result")
            )
            if apotelesma:
                _prosthese_deigma(
                    pigi,
                    tautotita or _proto_keimeno(fortio.get("call_id")),
                    synedria,
                    "tool",
                    "tool_result",
                    apotelesma,
                    locator,
                    imerominia,
                    arithmos,
                    deigmata,
                    kalypsi_analysi,
                )


def _tautotita_eggrafis(
    eggrafi: dict[str, object], fortio: dict[str, object], pigi: str
) -> str | None:
    """Επιστρέφει record ID χωρίς να συγχέει Codex tool call με result ID."""
    typos = _proto_keimeno(fortio.get("type"))
    klisi_id = _proto_keimeno(fortio.get("call_id"), fortio.get("callId"))
    if pigi == "codex" and typos and klisi_id:
        if typos in {
            "tool_call_output",
            "custom_tool_call_output",
            "function_call_output",
            "tool_result",
        }:
            return f"tool-result:{klisi_id}"
        if typos in {"tool_call", "function_call", "custom_tool_call"}:
            return f"tool-call:{klisi_id}"
    tautotita = _proto_keimeno(eggrafi.get("uuid"), eggrafi.get("id"), fortio.get("id"))
    if tautotita:
        return tautotita
    if pigi != "codex":
        return klisi_id
    return _proto_keimeno(fortio.get("call_id"), fortio.get("callId"))


def _einai_proelefsi_anthropini(eggrafi: dict[str, object]) -> bool:
    """Δέχεται prompts μόνο όταν τα ρητά source markers είναι ανθρώπινα."""
    markers: list[object] = []
    payload_obj = eggrafi.get("payload")
    payload = payload_obj if isinstance(payload_obj, dict) else {}
    for context in (eggrafi, payload):
        if (
            context.get("isSidechain") is True
            or context.get("is_subagent") is True
            or context.get("agentId")
        ):
            return False
        if "origin" in context:
            origin = context["origin"]
            if not isinstance(origin, dict):
                return False
            markers.append(origin.get("kind"))
        markers.extend(
            context[key]
            for key in ("promptSource", "turnOrigin", "userType")
            if key in context
        )
    for marker in markers:
        if not isinstance(marker, str):
            return False
        marker_norm = marker.strip().casefold().replace("-", "_")
        if marker_norm not in PROELEFSIS_ANTHROPINIS:
            return False
    return True


def _prosthese_deigma(
    pigi: str,
    tautotita: str | None,
    synedria: str,
    rolos: Literal["user", "assistant", "tool"],
    eidos: Literal["prompt", "response", "tool_call", "tool_result"],
    keimeno: str,
    locator: str,
    imerominia: str | None,
    arithmos: int,
    deigmata: list[Deigma],
    kalypsi_analysi: KalypsiAnalysi,
) -> None:
    """Redacts, truncates and appends one eligible evidence row within the cap."""
    kalypsi_analysi["diathesima"] += 1
    if len(deigmata) >= ORIA_DEIGMATON:
        kalypsi_analysi["perikopi"] = True
        return
    katharo = katharise_aporrita(keimeno)[:ORIA_MIKOUS_DEIGMATOS]
    tautotita_kleidiou = tautotita or locator
    row_id = hashlib.sha256(
        f"{pigi}\0{tautotita_kleidiou}\0{eidos}\0{arithmos}".encode("utf-8")
    ).hexdigest()[:16]
    deigmata.append(
        {
            "id": row_id,
            "pigi": PIGES[pigi],
            "synedria": synedria,
            "rolos": rolos,
            "eidos": eidos,
            "keimeno": katharo,
            "locator": locator,
            "imerominia": imerominia,
        }
    )
    kalypsi_analysi["epilegmena"] += 1


def _keimeno_keimenou(periexomeno: object, typos: set[str]) -> str | None:
    """Συνενώνει μόνο ρητά αναγνωρισμένα text blocks ή scalar strings."""
    if isinstance(periexomeno, str):
        return periexomeno.strip() or None
    if not isinstance(periexomeno, list):
        return None
    kommata: list[str] = []
    for block in periexomeno:
        if not isinstance(block, dict) or block.get("type") not in typos:
            continue
        keimeno = block.get("text")
        if isinstance(keimeno, str) and keimeno.strip():
            kommata.append(keimeno.strip())
    return "\n".join(kommata) or None


def _exei_anthropino_keimeno(periexomeno: object) -> bool:
    """Ελέγχει αν content περιέχει ορατό text block και όχι tool result."""
    if isinstance(periexomeno, str):
        return bool(periexomeno.strip())
    if not isinstance(periexomeno, list):
        return False
    for block_periexomenou in periexomeno:
        if isinstance(block_periexomenou, str) and block_periexomenou.strip():
            return True
        if not isinstance(block_periexomenou, dict):
            continue
        typos_block = block_periexomenou.get("type")
        if typos_block in {"text", "input_text", "output_text"}:
            timi = block_periexomenou.get("text")
            if isinstance(timi, str) and timi.strip():
                return True
    return False


def _keimeno_prompt(periexomeno: object) -> str | None:
    """Εξάγει αποκλειστικά αναγνωρισμένα user text blocks για deduplication."""
    if isinstance(periexomeno, str):
        return periexomeno.strip() or None
    if not isinstance(periexomeno, list):
        return None
    kommata: list[str] = []
    for block_periexomenou in periexomeno:
        if not isinstance(block_periexomenou, dict):
            continue
        if block_periexomenou.get("type") not in {"text", "input_text"}:
            continue
        timi = block_periexomenou.get("text")
        if isinstance(timi, str) and timi.strip():
            kommata.append(timi.strip())
    return "\n".join(kommata) or None


def _analuse_periexomeno_xristi(
    eggrafi: dict[str, object], periexomeno: object
) -> tuple[str | None, bool, object]:
    """Ξεχωρίζει ρητό ανθρώπινο κείμενο από εισαγόμενο Claude context."""
    fortio_obj = eggrafi.get("payload")
    fortio = fortio_obj if isinstance(fortio_obj, dict) else {}
    minima_obj = eggrafi.get("message") or fortio.get("message")
    minima = minima_obj if isinstance(minima_obj, dict) else {}
    metadomena_obj = next(
        (
            plaisio["internal_chat_message_metadata_passthrough"]
            for plaisio in (eggrafi, fortio, minima)
            if "internal_chat_message_metadata_passthrough" in plaisio
        ),
        None,
    )
    if metadomena_obj is None:
        return (
            _keimeno_prompt(periexomeno),
            False,
            periexomeno,
        )
    if isinstance(metadomena_obj, str):
        try:
            metadomena_obj = json.loads(metadomena_obj)
        except json.JSONDecodeError:
            return None, False, None
    if not isinstance(metadomena_obj, dict):
        return None, False, None
    eidi_obj = metadomena_obj.get("content_item_kinds")
    if not isinstance(eidi_obj, list) or not eidi_obj:
        return (
            _keimeno_prompt(periexomeno),
            False,
            periexomeno,
        )
    if not all(isinstance(eidos, str) for eidos in eidi_obj):
        return None, False, None
    eidi = [eidos for eidos in eidi_obj if isinstance(eidos, str)]
    theseis_xristi = [
        deiktis for deiktis, eidos in enumerate(eidi) if eidos.startswith("user.")
    ]
    if not theseis_xristi:
        if any(eidos in EIDI_MITRWTIKOU_CONTEXT for eidos in eidi):
            return None, False, None
        return (
            _keimeno_prompt(periexomeno),
            False,
            periexomeno,
        )
    if not isinstance(periexomeno, list):
        if all(eidos.startswith("user.") for eidos in eidi):
            return (
                _keimeno_prompt(periexomeno),
                any(eidos == "user.image" for eidos in eidi),
                periexomeno,
            )
        return None, False, None
    if len(periexomeno) != len(eidi) and any(
        eidos in EIDI_MITRWTIKOU_CONTEXT for eidos in eidi
    ):
        return None, False, None
    if len(periexomeno) != len(eidi):
        return (
            _keimeno_prompt(periexomeno),
            False,
            periexomeno,
        )
    periexomeno_filtrarismeno = [periexomeno[deiktis] for deiktis in theseis_xristi]
    yparxei_eikona_xristi = any(
        eidi[deiktis] == "user.image" for deiktis in theseis_xristi
    )
    return (
        _keimeno_prompt(periexomeno_filtrarismeno),
        yparxei_eikona_xristi,
        periexomeno_filtrarismeno,
    )


def _metrise_kliseis_ergaleion(periexomeno: object) -> int:
    """Μετρά distinct tool-use IDs μέσα στο Claude assistant message."""
    if not isinstance(periexomeno, list):
        return 0
    tautotites: set[str] = set()
    synolo = 0
    for block_periexomenou in periexomeno:
        if (
            isinstance(block_periexomenou, dict)
            and block_periexomenou.get("type") == "tool_use"
        ):
            klisi_id = _proto_keimeno(block_periexomenou.get("id"))
            if klisi_id:
                if klisi_id not in tautotites:
                    tautotites.add(klisi_id)
                    synolo += 1
            else:
                synolo += 1
    return synolo


def _imerominia_zonis(timi: str | None, zoni: ZoneInfo) -> date | None:
    """Μετατρέπει RFC3339/ISO timestamp σε ημερομηνία αναφοράς, αν έχει timezone."""
    if not timi:
        return None
    try:
        xronos_parsed = datetime.fromisoformat(timi.replace("Z", "+00:00"))
    except ValueError:
        return None
    if xronos_parsed.tzinfo is None:
        return None
    try:
        return xronos_parsed.astimezone(zoni).date()
    except (OverflowError, ValueError):
        return None


def _vevaiwse_drastiriotita(
    drastiki: dict[str, MetrikesImeras],
    imera: date,
) -> MetrikesImeras:
    """Δημιουργεί bucket δραστηριότητας για ημερομηνία με γνωστό timestamp."""
    return drastiki.setdefault(imera.isoformat(), {"prompts": 0, "commits": 0})


def _diavase_git_commits(
    apothikio: Path,
    zoni: ZoneInfo,
    apo: date | None,
    eos: date | None,
    grafeas: str | None,
) -> tuple[dict[str, dict[str, date | None]], int, SygkrotitisPeriodou, int]:
    """Διαβάζει commits και το tracked inventory του HEAD χωρίς αλλαγές."""
    entoli = [
        "git",
        "-C",
        str(apothikio),
        "log",
        "HEAD",
        "--format=" + MORFI_GIT_LOG,
    ]
    apotelesma_git = subprocess.run(
        entoli,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=GIT_TIMEOUT_DEFTEROLEPTA,
    )
    commit_ids: dict[str, dict[str, date | None]] = {}
    trexon_id: str | None = None
    trexousa_imerominia: date | None = None
    trexon_dimioyrgos: str = ""
    periodos = SygkrotitisPeriodou()
    agnostes_imerominies = 0
    grammes = apotelesma_git.stdout.splitlines()
    for grammi in grammes + ["\x00"]:
        if "\x1f" in grammi or grammi == "\x00":
            if trexon_id:
                egkyr_dimioyrgos = grafeas is None or grafeas in trexon_dimioyrgos
                xreiazetai_imerominia = apo is not None or eos is not None
                if (
                    egkyr_dimioyrgos
                    and trexousa_imerominia is None
                    and xreiazetai_imerominia
                ):
                    agnostes_imerominies += 1
                    trexon_id = None
                    if grammi == "\x00":
                        break
                else:
                    entos_periodou = trexousa_imerominia is None or (
                        (apo is None or trexousa_imerominia >= apo)
                        and (eos is None or trexousa_imerominia <= eos)
                    )
                    if egkyr_dimioyrgos and entos_periodou:
                        commit_ids[trexon_id] = {"imerominia": trexousa_imerominia}
                trexon_id = None
            if grammi == "\x00":
                break
            tmimata = grammi.split("\x1f")
            if len(tmimata) < 4:
                trexon_id = None
                continue
            trexon_id, onoma_grafea, email_grafea, chronos_commit = tmimata[:4]
            trexon_dimioyrgos = f"{onoma_grafea} {email_grafea}".casefold()
            trexousa_imerominia = _imerominia_zonis(chronos_commit, zoni)
            periodos.prosthese(trexousa_imerominia)
            continue
    apotelesma_tree = subprocess.run(
        ["git", "-C", str(apothikio), "ls-tree", "-r", "-z", "--name-only", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=GIT_TIMEOUT_DEFTEROLEPTA,
    )
    tracked_head = [
        diadromi for diadromi in apotelesma_tree.stdout.split("\0") if diadromi
    ]
    return commit_ids, len(tracked_head), periodos, agnostes_imerominies


def _proto_keimeno(*times: object) -> str | None:
    """Επιστρέφει πρώτη μη κενή scalar string τιμή."""
    for timi in times:
        if isinstance(timi, str) and timi.strip():
            return timi.strip()
    return None
