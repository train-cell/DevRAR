"""Παράγει συνεπή, ρητά συνθετική ροή για τις νέες δυνατότητες του demo."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from typing import Literal

from devrar.epeisodia import axiologise_epeisodia
from devrar.metrika import SyllogistisMetrikon
from devrar.proodos import sygkrine_anafores
from devrar.symvanta import SymvanErgasias

CLAUDE_PROMPTS = 720
CLAUDE_RIZES = 30
CLAUDE_SYNOLO = 42
CODEX_RIZES = 14
SYNEDRIES_SYNOLO = 60
APANTISEIS_SYNOLO = 1038
KLISEIS_SYNOLO = 1362
SYNTHETIKO_TEST_KATHE = 100
SYNTHETIKI_APOTYXIA_KATHE = 250
PROMPTS_PROIGOUMENA = 860
COMMITS_PROIGOUMENA = 18


def _symvan(
    tautotita: str,
    deiktis: int,
    chronos: datetime,
    rolos: Literal["user", "assistant", "tool"],
    eidos: Literal["prompt", "response", "tool_call", "tool_result"],
    keimeno: str,
    kodikos: int | None = None,
) -> SymvanErgasias:
    """Δημιουργεί ένα καθαρά συνθετικό event με σταθερή provenance."""
    thesi = deiktis % SYNEDRIES_SYNOLO
    claude = thesi < CLAUDE_SYNOLO
    topiki_thesi = thesi if claude else thesi - CLAUDE_SYNOLO
    orio_rizon = CLAUDE_RIZES if claude else CODEX_RIZES
    pigi = "Claude Code" if claude else "Codex CLI"
    return {
        "id": tautotita,
        "pigi": pigi,
        "synedria": f"demo-{pigi}-{topiki_thesi}",
        "goneas": f"demo-{pigi}-0" if topiki_thesi >= orio_rizon else None,
        "chronos": chronos.isoformat(),
        "rolos": rolos,
        "eidos": eidos,
        "keimeno": keimeno,
        "locator": f"synthetic-stream#{tautotita}",
        "ergaleio": "synthetic-check"
        if eidos in {"tool_call", "tool_result"}
        else None,
        "montelo": None,
        "kodikos_exodou": kodikos,
    }


def prosthese_deigma_ergasias(
    dedomena: dict[str, object],
    imerominies: Sequence[str],
    prompts_ana_imera: Sequence[int],
) -> dict[str, object]:
    """Εμπλουτίζει το synthetic report χωρίς ανάγνωση προσωπικών πηγών."""
    syllogistis = SyllogistisMetrikon()
    deiktis = 0
    for imera, plithos in zip(imerominies, prompts_ana_imera, strict=True):
        arxi = datetime.fromisoformat(f"{imera}T08:00:00+00:00")
        for lepto in range(plithos):
            thesi = (
                deiktis % CLAUDE_RIZES
                if deiktis < CLAUDE_PROMPTS
                else (CLAUDE_SYNOLO + (deiktis - CLAUDE_PROMPTS) % CODEX_RIZES)
            )
            syllogistis.prosthese(
                _symvan(
                    f"human-{deiktis}",
                    thesi,
                    arxi + timedelta(minutes=lepto),
                    "user",
                    "prompt",
                    "Synthetic human prompt: inspect the recorded result.",
                )
            )
            deiktis += 1
    arxi = datetime.fromisoformat(imerominies[0]).replace(hour=8, tzinfo=timezone.utc)
    for deiktis in range(APANTISEIS_SYNOLO):
        syllogistis.prosthese(
            _symvan(
                f"reply-{deiktis}",
                deiktis,
                arxi + timedelta(seconds=deiktis),
                "assistant",
                "response",
                "Synthetic assistant response.",
            )
        )
    for deiktis in range(KLISEIS_SYNOLO):
        chronos = arxi + timedelta(seconds=deiktis)
        syllogistis.prosthese(
            _symvan(
                f"call-{deiktis}",
                deiktis,
                chronos,
                "assistant",
                "tool_call",
                "synthetic-check",
            )
        )
        apotyxia = deiktis % SYNTHETIKI_APOTYXIA_KATHE == 0
        apotelesma = (
            "=== 1 failed in 0.1s ==="
            if apotyxia
            else (
                "=== 5 passed in 0.2s ==="
                if deiktis % SYNTHETIKO_TEST_KATHE == 0
                else "Synthetic operation finished."
            )
        )
        syllogistis.prosthese(
            _symvan(
                f"result-{deiktis}",
                deiktis,
                chronos + timedelta(milliseconds=1),
                "tool",
                "tool_result",
                apotelesma,
                1 if apotyxia else 0,
            )
        )
    dedomena["metrika_ergasias"] = syllogistis.apotelesma()
    apotelesma_report = axiologise_epeisodia(dedomena)
    synola = dedomena.get("synola")
    synola_proigoumena = dict(synola) if isinstance(synola, dict) else {}
    synola_proigoumena.update(
        minimata_xristi=PROMPTS_PROIGOUMENA, commits=COMMITS_PROIGOUMENA
    )
    baseline = {
        "ekdosi_sximatos": dedomena["ekdosi_sximatos"],
        "leitourgia": "demo",
        "periodos": {"apo": "2026-09-12", "eos": "2026-09-23", "zoni": "Europe/Athens"},
        "synola": synola_proigoumena,
        "piges": dedomena["piges"],
        "scope_git": dedomena.get("scope_git"),
        "analysi": dedomena.get("analysi"),
        "axiologisi": dedomena.get("axiologisi"),
    }
    apotelesma_report["sygkrisi"] = sygkrine_anafores(apotelesma_report, baseline)
    return apotelesma_report
