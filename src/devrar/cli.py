"""Παρέχει το τοπικό command-line interface του DevRAR."""

from __future__ import annotations

import argparse
import io
import json
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
YPOSYRIZES_PIGES = ("claude", "codex", "opencode", "gemini", "antigravity")
TROPOI_ANALYSI = ("rules", "local", "cloud")
PROEPILEGMENO_CLOUD_KEY_ENV = "DEVRAR_CLOUD_API_KEY"
ORIO_COMPARE_BYTES = 10 * 1024 * 1024
ELAXISTA_IDLE_MINUTES = 1
MEGISTA_IDLE_MINUTES = 1440
PROEPILEGMENES_IDLE_MINUTES = 15
EPITYXIA = 0
APOTYXIA = 1
MERIKH_KALYPSI = 3
CLOUD_FAILURE_REASON = (
    "The cloud request failed or its response did not pass validation; "
    "collected metrics and rules observations are retained."
)


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
    tyligma.add_argument("--opencode-path", dest="diadromi_opencode", type=Path)
    tyligma.add_argument("--gemini-path", dest="diadromi_gemini", type=Path)
    tyligma.add_argument("--antigravity-path", dest="diadromi_antigravity", type=Path)
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
        help=(
            "rules, local model, or cloud; cloud sends bounded redacted excerpts "
            "to the chosen provider"
        ),
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
    tyligma.add_argument(
        "--cloud-endpoint",
        dest="cloud_endpoint",
        help="explicit HTTPS chat-completions URL; bounded redacted excerpts are sent",
    )
    tyligma.add_argument("--cloud-model", dest="cloud_model")
    tyligma.add_argument(
        "--cloud-key-env",
        dest="cloud_key_env",
        default=None,
        help=(
            "environment variable containing the API key "
            f"(default: {PROEPILEGMENO_CLOUD_KEY_ENV})"
        ),
    )
    tyligma.add_argument(
        "--allow-cloud-evidence",
        dest="allow_cloud_evidence",
        action="store_true",
        help="consent to send bounded redacted excerpts to the chosen provider",
    )
    tyligma.add_argument(
        "--idle-minutes",
        dest="lepta_adraneias",
        type=int,
        default=PROEPILEGMENES_IDLE_MINUTES,
        help="session split gap in minutes (1-1440)",
    )
    tyligma.add_argument("--compare", dest="diadromi_sygkrisis", type=Path)
    tyligma.add_argument(
        "--activitywatch-path", dest="diadromi_drastiriotitas", type=Path
    )
    tyligma.add_argument("--cost-path", dest="diadromi_kostous", type=Path)
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
    for kleidi in ("energos_xronos", "kostos"):
        eisagogi = dedomena.get(kleidi)
        if isinstance(eisagogi, Mapping) and eisagogi.get("status") != "ok":
            return True
    piges = dedomena.get("piges")
    if not isinstance(piges, list):
        return True
    for pigi in piges:
        if isinstance(pigi, Mapping) and pigi.get("katastasi") != "ok":
            return True
    if "git_diafores" in dedomena:
        git_diafores = dedomena.get("git_diafores")
        if (
            not isinstance(git_diafores, Mapping)
            or git_diafores.get("katastasi") != "ok"
        ):
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
        ("opencode", orismata.diadromi_opencode),
        ("gemini", orismata.diadromi_gemini),
        ("antigravity", orismata.diadromi_antigravity),
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
        or orismata.diadromi_drastiriotitas is not None
        or orismata.diadromi_kostous is not None
        or orismata.lepta_adraneias != PROEPILEGMENES_IDLE_MINUTES
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
    cloud_orismata_rita = (
        orismata.cloud_endpoint is not None
        or orismata.cloud_model is not None
        or orismata.cloud_key_env is not None
        or orismata.allow_cloud_evidence
    )
    if orismata.analysi == "cloud":
        if not isinstance(orismata.cloud_endpoint, str) or not orismata.cloud_endpoint:
            analytis.error("--analysis cloud requires --cloud-endpoint")
        if (
            not isinstance(orismata.cloud_model, str)
            or not orismata.cloud_model.strip()
        ):
            analytis.error("--analysis cloud requires --cloud-model")
        if not orismata.allow_cloud_evidence:
            analytis.error("--analysis cloud requires --allow-cloud-evidence consent")
        if orismata.topiko_modelo is not None or orismata.diadromi_ollama is not None:
            analytis.error("--local-model and --ollama-path cannot be used with cloud")
    elif cloud_orismata_rita:
        analytis.error("Cloud options are only with --analysis cloud")
    if not ELAXISTA_IDLE_MINUTES <= orismata.lepta_adraneias <= MEGISTA_IDLE_MINUTES:
        analytis.error("--idle-minutes must be between 1 and 1440")
    return piges, fakeloi, apo, eos


def _diavase_sygkrisi(
    diadromi: Path, analytis: argparse.ArgumentParser
) -> Mapping[str, object]:
    """Διαβάζει περιορισμένο JSON baseline ως αυστηρό report object."""
    try:
        with diadromi.open("rb") as arxeio:
            periexomeno = arxeio.read(ORIO_COMPARE_BYTES + 1)
    except OSError as sfalma:
        analytis.error(f"cannot read comparison report: {sfalma}")
    if len(periexomeno) > ORIO_COMPARE_BYTES:
        analytis.error("comparison report exceeds the 10 MB limit")
    try:
        dedomena = json.loads(periexomeno)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError):
        analytis.error("comparison report must be valid UTF-8 JSON")
    if not isinstance(dedomena, dict) or not all(
        isinstance(kleidi, str) for kleidi in dedomena
    ):
        analytis.error("comparison report must be a JSON object")
    return cast(Mapping[str, object], dedomena)


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
    if (
        not epiloges.synthetika
        and not piges
        and not epiloges.apothitiria
        and epiloges.diadromi_drastiriotitas is None
        and epiloges.diadromi_kostous is None
    ):
        analytis.print_help()
        return EPITYXIA
    sygkrisi_baseline: Mapping[str, object] | None = None
    if epiloges.diadromi_sygkrisis is not None:
        try:
            sygkrisi_baseline = _diavase_sygkrisi(epiloges.diadromi_sygkrisis, analytis)
        except SystemExit as sfalma:
            return int(sfalma.code or EPITYXIA)
        baseline_leitourgia = sygkrisi_baseline.get("leitourgia")
        if baseline_leitourgia not in {"demo", "live"}:
            try:
                analytis.error("comparison baseline must declare demo or live mode")
            except SystemExit as sfalma:
                return int(sfalma.code or EPITYXIA)
        baseline_demo = baseline_leitourgia == "demo"
        if baseline_demo != bool(epiloges.synthetika):
            try:
                analytis.error("comparison baseline must use the same demo/live mode")
            except SystemExit as sfalma:
                return int(sfalma.code or EPITYXIA)
    local_sfalma: str | None = None
    cloud_sfalma = False
    try:
        if epiloges.synthetika:
            print("Loading the synthetic demo...")
            from devrar.deigma import fortose_deigma

            dedomena = fortose_deigma()
        else:
            print("Reading the selected local history...")
            from devrar.syndesi import syllexe_pliri

            dedomena = syllexe_pliri(
                piges,
                fakeloi,
                epiloges.apothitiria,
                apo,
                eos,
                epiloges.zoni or PROEPILEGMENI_ZONI,
                author=epiloges.syggrafeas,
                idle_minutes=epiloges.lepta_adraneias,
            )

        from devrar.axiologisi import axiologise_ergasia
        from devrar.epeisodia import axiologise_epeisodia

        print("Reviewing workflow evidence...")
        dedomena = axiologise_ergasia(dedomena)
        dedomena = axiologise_epeisodia(dedomena)
        if (
            epiloges.diadromi_drastiriotitas is not None
            or epiloges.diadromi_kostous is not None
        ):
            from devrar.eisagoges import diavase_energo_xrono, diavase_kostos

            zoni_eisagogis = epiloges.zoni or PROEPILEGMENI_ZONI
            if epiloges.diadromi_drastiriotitas is not None:
                dedomena["energos_xronos"] = diavase_energo_xrono(
                    epiloges.diadromi_drastiriotitas, apo, eos, zoni_eisagogis
                )
            if epiloges.diadromi_kostous is not None:
                dedomena["kostos"] = diavase_kostos(
                    epiloges.diadromi_kostous, apo, eos, zoni_eisagogis
                )
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
        elif epiloges.analysi == "cloud":
            print("Starting explicitly approved cloud analysis...")
            try:
                cloud = import_module("devrar.cloud")
                analysi_cloud = cast(
                    Callable[
                        [Mapping[str, object], str, str, bool, str], dict[str, object]
                    ],
                    getattr(cloud, "analysi_cloud"),
                )
                assert isinstance(epiloges.cloud_model, str)
                assert isinstance(epiloges.cloud_endpoint, str)
                dedomena = analysi_cloud(
                    dedomena,
                    epiloges.cloud_model,
                    epiloges.cloud_endpoint,
                    True,
                    epiloges.cloud_key_env or PROEPILEGMENO_CLOUD_KEY_ENV,
                )
            except (
                AttributeError,
                ImportError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
                KeyError,
            ):
                KATAGRAFI.warning("DevRAR cloud analysis failed")
                cloud_sfalma = True
                proigoumeni_analysi = dedomena.get("analysi")
                analysi_fail = (
                    dict(proigoumeni_analysi)
                    if isinstance(proigoumeni_analysi, Mapping)
                    else {}
                )
                analysi_fail.update(
                    {
                        "methodos": "cloud",
                        "katastasi": "failed",
                        "aitia": CLOUD_FAILURE_REASON,
                        "provider": "openai_compatible",
                        "model_id": epiloges.cloud_model,
                        "cloud_opt_in": True,
                        "efarmostike": "rules",
                        "vathmoi_vathmologimenoi": False,
                        "symfonia_anthropinon_aksiologiton": False,
                    }
                )
                dedomena["analysi"] = analysi_fail
        if sygkrisi_baseline is not None:
            from devrar.proodos import sygkrine_anafores

            dedomena["sygkrisi"] = sygkrine_anafores(dedomena, sygkrisi_baseline)

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
    if cloud_sfalma:
        print(
            "Cloud analysis failed; the report keeps collected metrics and rules "
            "observations. Check the endpoint, model, and API key configuration.",
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
