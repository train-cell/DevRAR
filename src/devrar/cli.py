"""Παρέχει το τοπικό command-line interface του DevRAR."""

from __future__ import annotations

import argparse
import io
import logging
import sys
from collections.abc import Mapping, Sequence
from datetime import date
from importlib import import_module
from pathlib import Path
from typing import Callable, cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

KATAGRAFI = logging.getLogger(__name__)
PROEPILEGMENOS_FAKELOS = Path("devrar-reports")
PROEPILEGMENI_ZONI = "Europe/Athens"
YPOSYRIZES_PIGES = ("claude", "codex")
TROPOI_ANALYSI = ("rules", "local")
EPITYXIA = 0
APOTYXIA = 1
MERIKH_KALYPSI = 3


def _ftiaxe_analytis() -> argparse.ArgumentParser:
    """Δημιουργεί τον parser για την εντολή wrap."""
    analytis = argparse.ArgumentParser(
        prog="devrar",
        description="Create a local developer recap from selected sources.",
    )
    entoles = analytis.add_subparsers(dest="entoli")
    tyligma = entoles.add_parser("wrap", help="create a Developer Wrapped report")
    tyligma.add_argument(
        "--demo", dest="synthetika", action="store_true", help="use synthetic demo data"
    )
    tyligma.add_argument(
        "--source",
        dest="piges",
        action="append",
        choices=YPOSYRIZES_PIGES,
        default=[],
        help="read a supported local source (repeatable)",
    )
    tyligma.add_argument(
        "--repo",
        dest="apothitiria",
        action="append",
        type=Path,
        default=[],
        help="Git repository (repeatable)",
    )
    tyligma.add_argument(
        "--claude-path", dest="diadromi_claude", type=Path, help="Claude Code data root"
    )
    tyligma.add_argument(
        "--codex-path", dest="diadromi_codex", type=Path, help="Codex data root"
    )
    tyligma.add_argument(
        "--since", dest="apo", help="inclusive start date (YYYY-MM-DD)"
    )
    tyligma.add_argument("--until", dest="eos", help="inclusive end date (YYYY-MM-DD)")
    tyligma.add_argument("--timezone", dest="zoni", default=None, help="IANA timezone")
    tyligma.add_argument(
        "--author", dest="syggrafeas", help="Git author name or email filter"
    )
    tyligma.add_argument(
        "--output",
        dest="exodos",
        type=Path,
        default=PROEPILEGMENOS_FAKELOS,
        help="parent folder for report runs",
    )
    tyligma.add_argument(
        "--open", dest="anoigma", action="store_true", help="open the generated report"
    )
    tyligma.add_argument(
        "--roast",
        dest="psisimo",
        action="store_true",
        help="enable optional humorous commentary",
    )
    tyligma.add_argument(
        "--analysis",
        dest="analysi",
        choices=TROPOI_ANALYSI,
        default="rules",
        help="analysis mode",
    )
    tyligma.add_argument(
        "--local-model",
        dest="topiko_modelo",
        help="explicit local model name for local analysis",
    )
    tyligma.add_argument(
        "--ollama-path",
        dest="diadromi_ollama",
        type=Path,
        help="optional path to the local Ollama executable",
    )
    return analytis


def _diavase_imerominia(
    keimeno: str | None,
    onoma_orismatos: str,
    analytis: argparse.ArgumentParser,
) -> date | None:
    """Επικυρώνει προαιρετική ημερομηνία ISO και επιστρέφει date."""
    if keimeno is None:
        return None
    try:
        imerominia = date.fromisoformat(keimeno)
    except ValueError:
        analytis.error(f"{onoma_orismatos} must be a valid ISO date (YYYY-MM-DD)")
    if imerominia.isoformat() != keimeno:
        analytis.error(f"{onoma_orismatos} must use YYYY-MM-DD format")
    return imerominia


def _anafora_einai_meriki(dedomena: Mapping[str, object]) -> bool:
    """Ελέγχει αν κάποια επιλεγμένη πηγή έχει μη πλήρη κάλυψη."""
    analysi = dedomena.get("analysi")
    if isinstance(analysi, Mapping) and analysi.get("katastasi") == "failed":
        return True
    piges = dedomena.get("piges")
    if not isinstance(piges, list):
        return True
    for pigi in piges:
        if isinstance(pigi, Mapping) and pigi.get("katastasi") != "ok":
            return True
    return False


def _epikyrone_epiloges(
    orismata: argparse.Namespace,
    analytis: argparse.ArgumentParser,
) -> tuple[list[str], dict[str, Path], date | None, date | None]:
    """Επικυρώνει το εύρος συλλογής και επιστρέφει κανονικοποιημένα inputs."""
    apo = _diavase_imerominia(orismata.apo, "--since", analytis)
    eos = _diavase_imerominia(orismata.eos, "--until", analytis)
    if apo is not None and eos is not None and apo > eos:
        analytis.error("--since must be earlier than or equal to --until")

    zoni = orismata.zoni or PROEPILEGMENI_ZONI
    try:
        ZoneInfo(zoni)
    except (ZoneInfoNotFoundError, ValueError):
        analytis.error(f"unknown IANA timezone: {zoni}")

    piges = list(dict.fromkeys(orismata.piges))
    fakeloi: dict[str, Path] = {}
    for onoma_pigis, diadromi in (
        ("claude", orismata.diadromi_claude),
        ("codex", orismata.diadromi_codex),
    ):
        if diadromi is not None:
            fakeloi[onoma_pigis] = diadromi
            if onoma_pigis not in piges:
                piges.append(onoma_pigis)

    if orismata.synthetika and (
        piges
        or orismata.apothitiria
        or apo is not None
        or eos is not None
        or orismata.syggrafeas is not None
        or orismata.zoni is not None
    ):
        analytis.error(
            "--demo cannot be combined with live sources, repositories, or filters"
        )
    if orismata.analysi == "local" and not (
        isinstance(orismata.topiko_modelo, str) and orismata.topiko_modelo.strip()
    ):
        analytis.error("--analysis local requires an explicit --local-model")
    if orismata.analysi == "rules" and (
        orismata.topiko_modelo is not None or orismata.diadromi_ollama is not None
    ):
        analytis.error("--local-model and --ollama-path are only with --analysis local")
    return piges, fakeloi, apo, eos


def kyria(orismata: Sequence[str] | None = None) -> int:
    """Επικυρώνει τα ορίσματα και δημιουργεί demo ή live report."""
    for rohi in (sys.stdout, sys.stderr):
        if isinstance(rohi, io.TextIOWrapper):
            rohi.reconfigure(errors="backslashreplace")
    analytis = _ftiaxe_analytis()
    energes_epiloges = list(orismata) if orismata is not None else sys.argv[1:]
    if not energes_epiloges:
        analytis.print_help()
        return EPITYXIA

    try:
        epiloges = analytis.parse_args(energes_epiloges)
    except SystemExit as sfalma:
        return int(sfalma.code or EPITYXIA)

    try:
        piges, fakeloi, apo, eos = _epikyrone_epiloges(epiloges, analytis)
    except SystemExit as sfalma:
        return int(sfalma.code or EPITYXIA)
    if not epiloges.synthetika and not piges and not epiloges.apothitiria:
        analytis.print_help()
        return EPITYXIA
    local_sfalma: str | None = None
    try:
        if epiloges.synthetika:
            print("Loading the synthetic demo...")
            from devrar.deigma import fortose_deigma

            dedomena = fortose_deigma()
        else:
            print("Reading the selected local history...")
            from devrar.syllogi import syllexe_dedomena

            dedomena = syllexe_dedomena(
                piges,
                fakeloi,
                epiloges.apothitiria,
                apo=apo,
                eos=eos,
                zoni=epiloges.zoni or PROEPILEGMENI_ZONI,
                author=epiloges.syggrafeas,
            )

        from devrar.axiologisi import axiologise_ergasia

        print("Reviewing workflow evidence...")
        dedomena = axiologise_ergasia(dedomena)
        if epiloges.analysi == "local":
            assert epiloges.topiko_modelo is not None
            print(f"Starting local analysis with {epiloges.topiko_modelo}...")
            try:
                topiko = import_module("devrar.topiko")
                analysi_topika = cast(
                    Callable[
                        [Mapping[str, object], str, Path | None], dict[str, object]
                    ],
                    getattr(topiko, "analysi_topika"),
                )

                dedomena = analysi_topika(
                    dedomena,
                    epiloges.topiko_modelo,
                    epiloges.diadromi_ollama,
                )
            except (
                AttributeError,
                ImportError,
                OSError,
                RuntimeError,
                ValueError,
            ) as sfalma:
                KATAGRAFI.exception("DevRAR local analysis failed")
                local_sfalma = str(sfalma).strip() or "Local analysis failed."
                dedomena["analysi"] = {
                    "methodos": "local",
                    "katastasi": "failed",
                    "aitia": local_sfalma,
                    "modelo": epiloges.topiko_modelo,
                    "efarmostike": "rules",
                }

        from devrar.anafora import apothikefse_anafora

        print("Writing the offline report...")
        apotelesma = apothikefse_anafora(
            dedomena,
            epiloges.exodos,
            anoigma=epiloges.anoigma,
            roast=epiloges.psisimo,
        )
    except (
        ImportError,
        OSError,
        ValueError,
        RuntimeError,
        TypeError,
        KeyError,
    ) as sfalma:
        KATAGRAFI.exception("DevRAR report generation failed")
        print(f"DevRAR could not create the report: {sfalma}", file=sys.stderr)
        return APOTYXIA

    print(f"Report created: {apotelesma}")
    if epiloges.synthetika:
        print("Demo report uses synthetic data.")
    if local_sfalma is not None:
        print(
            f"Local analysis failed: {local_sfalma.rstrip('.')}. "
            "The report keeps the original metrics and rules observations. "
            "Check the Ollama/model error above, or use --analysis rules.",
            file=sys.stderr,
        )
        return MERIKH_KALYPSI
    if not epiloges.synthetika and _anafora_einai_meriki(dedomena):
        print(
            "Some selected sources are missing or only partially readable.",
            file=sys.stderr,
        )
        return MERIKH_KALYPSI
    return EPITYXIA
