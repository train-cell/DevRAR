from __future__ import annotations

import contextlib
import io
import runpy
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType
from typing import Callable, Iterator, cast
from zoneinfo import ZoneInfoNotFoundError

import pytest

from devrar.cli import _anafora_einai_meriki, kyria


@dataclass
class KatastasiDokimis:
    """Κρατά τα calls των mocks για απομονωμένα CLI tests."""

    kliseis_demo: int = 0
    kliseis_syllogis: list[
        tuple[
            tuple[Sequence[str], Mapping[str, Path], Sequence[Path]],
            dict[str, object],
        ]
    ] = field(default_factory=list)
    kliseis_anaforas: list[tuple[Mapping[str, object], Path, bool, bool]] = field(
        default_factory=list
    )
    katastasi_pigis: str = "ok"
    piges_report: object | None = None
    sfalma_anaforas: KeyError | None = None
    kliseis_topikis: list[tuple[object, str, Path | None]] = field(default_factory=list)
    sfalma_topikis: RuntimeError | None = None


@pytest.fixture
def metatropes() -> Iterator[pytest.MonkeyPatch]:
    """Παρέχει monkeypatch context με αυτόματο teardown ανά test."""
    with pytest.MonkeyPatch.context() as metatropes:
        yield metatropes


@pytest.fixture
def prosorini_diathromi() -> Iterator[Path]:
    """Δημιουργεί και καθαρίζει προσωρινό χώρο για paths των tests."""
    with TemporaryDirectory() as prosorini:
        yield Path(prosorini)


@pytest.fixture
def katastasi(metatropes: pytest.MonkeyPatch) -> KatastasiDokimis:
    """Εγκαθιστά mocks των data modules χωρίς πραγματικά reads."""
    apotelesma = KatastasiDokimis()
    deigma = ModuleType("devrar.deigma")

    def fortose_deigma() -> dict[str, object]:
        """Επιστρέφει synthetic report και μετρά το demo dispatch."""
        apotelesma.kliseis_demo += 1
        return {"leitourgia": "demo", "piges": []}

    setattr(deigma, "fortose_deigma", fortose_deigma)
    syllogi = ModuleType("devrar.syllogi")

    def syllexe_dedomena(
        piges: Sequence[str],
        fakeloi: Mapping[str, Path],
        apothitiria: Sequence[Path],
        **epiloges: object,
    ) -> dict[str, object]:
        """Καταγράφει τις live επιλογές χωρίς filesystem access."""
        apotelesma.kliseis_syllogis.append(((piges, fakeloi, apothitiria), epiloges))
        piges_report = apotelesma.piges_report
        if piges_report is None:
            piges_report = [{"katastasi": apotelesma.katastasi_pigis}]
        return {
            "leitourgia": "live",
            "piges": piges_report,
        }

    setattr(syllogi, "syllexe_dedomena", syllexe_dedomena)
    anafora = ModuleType("devrar.anafora")

    def apothikefse_anafora(
        dedomena: Mapping[str, object],
        exodos: Path,
        anoigma: bool = False,
        roast: bool = False,
    ) -> Path:
        """Καταγράφει report call και επιστρέφει HTML path."""
        apotelesma.kliseis_anaforas.append((dedomena, exodos, anoigma, roast))
        if apotelesma.sfalma_anaforas is not None:
            raise apotelesma.sfalma_anaforas
        return exodos / "index.html"

    setattr(anafora, "apothikefse_anafora", apothikefse_anafora)

    topiko = ModuleType("devrar.topiko")
    sfalma_topikis = type("SfalmaTopikisAnalysis", (RuntimeError,), {})

    def analysi_topika(
        dedomena: object, modelo: str, ektelesimo: Path | None = None
    ) -> dict[str, object]:
        """Καταγράφει το local analysis request χωρίς daemon access."""
        apotelesma.kliseis_topikis.append((dedomena, modelo, ektelesimo))
        if apotelesma.sfalma_topikis is not None:
            raise apotelesma.sfalma_topikis
        assert isinstance(dedomena, dict)
        dedomena["analysi"] = {"methodos": "local", "katastasi": "ok"}
        return dedomena

    setattr(topiko, "analysi_topika", analysi_topika)
    setattr(topiko, "SfalmaTopikisAnalysis", sfalma_topikis)
    metatropes.setitem(sys.modules, "devrar.deigma", deigma)
    metatropes.setitem(sys.modules, "devrar.syllogi", syllogi)
    metatropes.setitem(sys.modules, "devrar.anafora", anafora)
    metatropes.setitem(sys.modules, "devrar.topiko", topiko)

    def psevdos_zoni_info(onoma_zonis: str) -> object:
        """Απομονώνει το IANA lookup από την εγκατάσταση tz database."""
        if onoma_zonis == "Mars/Olympus":
            raise ZoneInfoNotFoundError(onoma_zonis)
        return object()

    metatropes.setattr("devrar.cli.ZoneInfo", psevdos_zoni_info)
    return apotelesma


def test_kyria_xoris_inputs_emfanizei_usage_xoris_syllogi(
    katastasi: KatastasiDokimis,
) -> None:
    """Χωρίς ρητή πηγή εμφανίζει οδηγίες και δεν σαρώνει ιστορικό."""
    eksodos = io.StringIO()
    with contextlib.redirect_stdout(eksodos):
        apotelesma = kyria([])

    assert apotelesma == 0
    assert "usage:" in eksodos.getvalue().lower()
    assert katastasi.kliseis_syllogis == []
    assert katastasi.kliseis_anaforas == []


def test_kyria_help_emfanizei_usage_xoris_syllogi(katastasi: KatastasiDokimis) -> None:
    """Η ρητή help επιλογή εμφανίζει usage χωρίς να φορτώνει πηγές."""
    eksodos = io.StringIO()
    with contextlib.redirect_stdout(eksodos):
        apotelesma = kyria(["--help"])

    assert apotelesma == 0
    assert "usage:" in eksodos.getvalue().lower()
    assert katastasi.kliseis_syllogis == []


def test_kyria_wrap_xoris_inputs_emfanizei_usage(katastasi: KatastasiDokimis) -> None:
    """Η εντολή wrap χωρίς πηγή εμφανίζει οδηγίες χωρίς dispatch."""
    eksodos = io.StringIO()
    with contextlib.redirect_stdout(eksodos):
        apotelesma = kyria(["wrap"])

    assert apotelesma == 0
    assert "usage:" in eksodos.getvalue().lower()
    assert katastasi.kliseis_syllogis == []
    assert katastasi.kliseis_anaforas == []


def test_kyria_xoris_command_epistrefei_invalid_usage(
    katastasi: KatastasiDokimis,
) -> None:
    """Απουσία subcommand απορρίπτεται με exit code 2."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["--"])

    assert apotelesma == 2
    assert "error:" in sfalmata.getvalue()
    assert katastasi.kliseis_syllogis == []


def test_kyria_xoris_orismata_diavazei_sys_argv(
    katastasi: KatastasiDokimis, metatropes: pytest.MonkeyPatch
) -> None:
    """Η console entrypoint χρησιμοποιεί τα πραγματικά arguments διεργασίας."""
    metatropes.setattr(sys, "argv", ["devrar", "wrap", "--demo"])

    apotelesma = kyria(None)

    assert apotelesma == 0
    assert katastasi.kliseis_demo == 1
    assert len(katastasi.kliseis_anaforas) == 1


def test_main_ekkinisi_proothei_ta_arguments(
    katastasi: KatastasiDokimis, metatropes: pytest.MonkeyPatch
) -> None:
    """Η συνάρτηση ekkinisi περνά τα process arguments στην kyria."""
    metatropes.setattr(sys, "argv", ["devrar", "wrap", "--demo"])
    diadromi_main = (
        Path(__file__).resolve().parents[1] / "src" / "devrar" / "__main__.py"
    )
    xoros = runpy.run_path(str(diadromi_main), run_name="devrar.__main__")
    ekkinisi = cast(Callable[[], int], xoros["ekkinisi"])

    assert ekkinisi() == 0
    assert katastasi.kliseis_demo == 1


def test_main_module_guard_exits_with_cli_status(
    katastasi: KatastasiDokimis, metatropes: pytest.MonkeyPatch
) -> None:
    """Η εκτέλεση __main__ καλεί το CLI και μεταφέρει exit code."""
    metatropes.setattr(sys, "argv", ["devrar", "wrap", "--demo"])
    diadromi_main = (
        Path(__file__).resolve().parents[1] / "src" / "devrar" / "__main__.py"
    )

    with pytest.raises(SystemExit) as sfalma:
        runpy.run_path(str(diadromi_main), run_name="__main__")

    assert sfalma.value.code == 0
    assert katastasi.kliseis_demo == 1


def test_kyria_demo_fortonei_synthetic_report(katastasi: KatastasiDokimis) -> None:
    """Το demo dispatch χρησιμοποιεί αποκλειστικά συνθετικά δεδομένα."""
    apotelesma = kyria(["wrap", "--demo", "--output", "demo-out", "--roast"])

    assert apotelesma == 0
    assert katastasi.kliseis_demo == 1
    assert katastasi.kliseis_syllogis == []
    assert len(katastasi.kliseis_anaforas) == 1
    dedomena, exodos, anoigma, psisimo = katastasi.kliseis_anaforas[0]
    assert dedomena["leitourgia"] == "demo"
    assert dedomena["piges"] == []
    assert _pare_analysi(dedomena)["methodos"] == "rules"
    axiologisi = dedomena["axiologisi"]
    assert isinstance(axiologisi, Mapping)
    assert axiologisi["synoliko"] is None
    assert (exodos, anoigma, psisimo) == (Path("demo-out"), False, True)


@pytest.mark.parametrize(
    "filtra",
    [
        ["--since", "2026-01-01"],
        ["--until", "2026-12-31"],
        ["--author", "Dev"],
        ["--timezone", "Europe/Athens"],
    ],
)
def test_kyria_demo_aporriptei_live_filters(
    katastasi: KatastasiDokimis, filtra: list[str]
) -> None:
    """Demo απορρίπτει live filters που δεν εφαρμόζονται στα synthetic δεδομένα."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--demo", *filtra])

    assert apotelesma == 2
    assert "--demo cannot be combined" in sfalmata.getvalue()
    assert katastasi.kliseis_demo == 0
    assert katastasi.kliseis_anaforas == []


def test_kyria_live_proothonei_filters_sources_kai_repo(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Προωθεί sources, repositories, dates, timezone και author στη συλλογή."""
    apothitiri = prosorini_diathromi / "repo"
    diadromi_pigis = prosorini_diathromi / "claude"
    apotelesma = kyria(
        [
            "wrap",
            "--source",
            "claude",
            "--source",
            "codex",
            "--claude-path",
            str(diadromi_pigis),
            "--repo",
            str(apothitiri),
            "--since",
            "2026-01-02",
            "--until",
            "2026-02-03",
            "--timezone",
            "Europe/Athens",
            "--author",
            "Dev",
            "--output",
            str(prosorini_diathromi / "report"),
            "--open",
            "--roast",
        ]
    )

    assert apotelesma == 0
    orismata_syllogis, epiloges_syllogis = katastasi.kliseis_syllogis[0]
    assert tuple(orismata_syllogis[0]) == ("claude", "codex")
    assert orismata_syllogis[1] == {"claude": diadromi_pigis}
    assert tuple(orismata_syllogis[2]) == (apothitiri,)
    assert epiloges_syllogis == {
        "apo": date(2026, 1, 2),
        "eos": date(2026, 2, 3),
        "zoni": "Europe/Athens",
        "author": "Dev",
    }
    assert katastasi.kliseis_anaforas[0][1:] == (
        prosorini_diathromi / "report",
        True,
        True,
    )


def test_kyria_path_only_epilegei_antistoixi_pigi(katastasi: KatastasiDokimis) -> None:
    """Ένα ρητό source path αρκεί για να επιλεγεί η αντίστοιχη πηγή."""
    apotelesma = kyria(["wrap", "--codex-path", "codex-data"])

    assert apotelesma == 0
    orismata_syllogis, _ = katastasi.kliseis_syllogis[0]
    assert tuple(orismata_syllogis[0]) == ("codex",)
    assert orismata_syllogis[1] == {"codex": Path("codex-data")}
    assert katastasi.kliseis_syllogis[0][1]["zoni"] == "Europe/Athens"


def test_kyria_malformed_source_coverage_epistrefei_partial(
    katastasi: KatastasiDokimis,
) -> None:
    """Malformed source coverage παραμένει partial αντί να εμφανίζεται ως επιτυχία."""
    katastasi.piges_report = False

    apotelesma = kyria(["wrap", "--source", "claude"])

    assert apotelesma == 3
    assert len(katastasi.kliseis_anaforas) == 1


def test_kyria_invalid_iso_presentation_epistrefei_invalid_usage(
    katastasi: KatastasiDokimis,
) -> None:
    """Απορρίπτει ISO date που δεν ακολουθεί το δημόσιο YYYY-MM-DD format."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--since", "20260102", "--demo"])

    assert apotelesma == 2
    assert "YYYY-MM-DD" in sfalmata.getvalue()


def test_kyria_generation_key_error_epistrefei_failure(
    katastasi: KatastasiDokimis,
) -> None:
    """Σφάλμα schema από τον renderer γίνεται ελεγχόμενη αποτυχία CLI."""
    katastasi.sfalma_anaforas = KeyError("missing report field")
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--demo"])

    assert apotelesma == 1
    assert "could not create the report" in sfalmata.getvalue()


@pytest.mark.parametrize(
    "orismata",
    [
        ["wrap", "--demo", "--source", "claude"],
        ["wrap", "--since", "2026-02-02", "--until", "2026-02-01", "--demo"],
        ["wrap", "--since", "not-a-date", "--demo"],
        ["wrap", "--timezone", "Mars/Olympus", "--demo"],
        ["wrap", "--analysis", "unknown", "--demo"],
    ],
)
def test_kyria_invalid_usage_epistrefei_2_kai_den_paragei(
    katastasi: KatastasiDokimis, orismata: list[str]
) -> None:
    """Μη έγκυρες επιλογές απορρίπτονται πριν από συλλογή ή παραγωγή."""
    eksodos = io.StringIO()
    sfalmata = io.StringIO()
    with contextlib.redirect_stdout(eksodos), contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(orismata)

    assert apotelesma == 2
    assert katastasi.kliseis_syllogis == []
    assert katastasi.kliseis_anaforas == []
    assert sfalmata.getvalue()


def test_kyria_local_apaitiei_modelo_prin_apo_syllogi(
    katastasi: KatastasiDokimis,
) -> None:
    """Χωρίς explicit local model επιστρέφει usage error πριν από reads."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--source", "claude", "--analysis", "local"])

    assert apotelesma == 2
    assert "--local-model" in sfalmata.getvalue()
    assert katastasi.kliseis_syllogis == []
    assert katastasi.kliseis_topikis == []


@pytest.mark.parametrize("topiko_orisma", ["--local-model", "--ollama-path"])
def test_kyria_rules_aporriptei_local_orismata(
    katastasi: KatastasiDokimis, topiko_orisma: str
) -> None:
    """Rules mode απορρίπτει local options αντί να τα αγνοεί."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--demo", topiko_orisma, "model-or-path"])

    assert apotelesma == 2
    assert "only with --analysis local" in sfalmata.getvalue()
    assert katastasi.kliseis_demo == 0


def test_kyria_local_fortonei_report_me_model_kai_path(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Local analysis λαμβάνει explicit model/path και τροφοδοτεί το report."""
    diadromi_ollama = prosorini_diathromi / "ollama.exe"
    eksodos = io.StringIO()
    with contextlib.redirect_stdout(eksodos):
        apotelesma = kyria(
            [
                "wrap",
                "--demo",
                "--analysis",
                "local",
                "--local-model",
                "qwen-local",
                "--ollama-path",
                str(diadromi_ollama),
            ]
        )

    assert apotelesma == 0
    assert katastasi.kliseis_demo == 1
    assert len(katastasi.kliseis_topikis) == 1
    _, modelo, ektelesimo = katastasi.kliseis_topikis[0]
    assert (modelo, ektelesimo) == ("qwen-local", diadromi_ollama)
    dedomena, _, _, _ = katastasi.kliseis_anaforas[0]
    assert _pare_analysi(dedomena) == {"methodos": "local", "katastasi": "ok"}
    assert "synthetic" in eksodos.getvalue().lower()


def test_kyria_local_failure_krata_report_kai_epistrefei_partial(
    katastasi: KatastasiDokimis,
) -> None:
    """Αποτυχία local model κρατά το report και δηλώνει ανάλυση failed."""
    katastasi.sfalma_topikis = RuntimeError("local daemon unavailable")
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(
            [
                "wrap",
                "--demo",
                "--analysis",
                "local",
                "--local-model",
                "qwen-local",
            ]
        )

    assert apotelesma == 3
    assert "local daemon unavailable" in sfalmata.getvalue()
    assert "original metrics and rules observations" in sfalmata.getvalue().lower()
    assert "--analysis rules" in sfalmata.getvalue()
    assert len(katastasi.kliseis_anaforas) == 1
    dedomena, _, _, _ = katastasi.kliseis_anaforas[0]
    analysi = _pare_analysi(dedomena)
    assert analysi["methodos"] == "local"
    assert analysi["katastasi"] == "failed"
    assert "unavailable" in str(analysi["aitia"])


def test_kyria_local_backend_failure_krata_report(
    katastasi: KatastasiDokimis, metatropes: pytest.MonkeyPatch
) -> None:
    """Missing local backend γίνεται partial report αντί για early exit."""

    def apetyxe_eisagogi(onoma: str) -> ModuleType:
        """Προσομοιώνει backend που δεν είναι εγκατεστημένο."""
        raise ImportError(f"{onoma} is not installed")

    metatropes.setattr("devrar.cli.import_module", apetyxe_eisagogi)
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(
            ["wrap", "--demo", "--analysis", "local", "--local-model", "model"]
        )

    assert apotelesma == 3
    assert "Local analysis failed" in sfalmata.getvalue()
    assert len(katastasi.kliseis_anaforas) == 1
    dedomena, _, _, _ = katastasi.kliseis_anaforas[0]
    assert _pare_analysi(dedomena)["katastasi"] == "failed"


def test_anafora_einai_meriki_an_analysi_apetyxei() -> None:
    """Το report χαρακτηρίζεται partial όταν έχει αποτύχει το local analysis."""
    assert _anafora_einai_meriki(
        {"piges": [], "analysi": {"methodos": "local", "katastasi": "failed"}}
    )


def _pare_analysi(dedomena: Mapping[str, object]) -> Mapping[str, object]:
    """Επιστρέφει το section ανάλυσης με type narrowing για assertions."""
    analysi = dedomena.get("analysi")
    assert isinstance(analysi, Mapping)
    return analysi


@pytest.mark.parametrize("katastasi_pigis", ["partial", "missing"])
def test_kyria_live_partial_coverage_paragei_report_kai_epistrefei_3(
    katastasi: KatastasiDokimis, katastasi_pigis: str
) -> None:
    """Κρατά report και δηλώνει πηγή partial ή missing με exit code 3."""
    katastasi.katastasi_pigis = katastasi_pigis

    apotelesma = kyria(["wrap", "--source", "claude"])

    assert apotelesma == 3
    assert len(katastasi.kliseis_anaforas) == 1
