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
    git_diafores_report: object | None = None
    dedomena_syllogis_extra: dict[str, object] = field(default_factory=dict)
    sfalma_anaforas: KeyError | None = None
    kliseis_topikis: list[tuple[object, str, Path | None]] = field(default_factory=list)
    sfalma_topikis: RuntimeError | None = None
    kliseis_cloud: list[tuple[Mapping[str, object], str, str, bool, str]] = field(
        default_factory=list
    )
    sfalma_cloud: RuntimeError | None = None
    apotelesma_cloud: dict[str, object] | None = None
    seira_analisis: list[str] = field(default_factory=list)
    apotelesma_xronou: dict[str, object] = field(
        default_factory=lambda: {"status": "ok"}
    )
    apotelesma_kostous: dict[str, object] = field(
        default_factory=lambda: {"status": "ok"}
    )
    kliseis_xronou: list[tuple[object, ...]] = field(default_factory=list)
    kliseis_kostous: list[tuple[object, ...]] = field(default_factory=list)
    sygkrisi: Mapping[str, object] | None = None


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
    syllogi = ModuleType("devrar.syndesi")

    def syllexe_pliri(
        piges: Sequence[str],
        fakeloi: Mapping[str, Path],
        apothitiria: Sequence[Path],
        apo: date | None = None,
        eos: date | None = None,
        zoni: str = "Europe/Athens",
        author: str | None = None,
        idle_minutes: int = 15,
    ) -> dict[str, object]:
        """Καταγράφει τις live επιλογές χωρίς filesystem access."""
        epiloges: dict[str, object] = {
            "apo": apo,
            "eos": eos,
            "zoni": zoni,
            "author": author,
            "idle_minutes": idle_minutes,
        }
        apotelesma.kliseis_syllogis.append(((piges, fakeloi, apothitiria), epiloges))
        piges_report = apotelesma.piges_report
        if piges_report is None:
            piges_report = [{"katastasi": apotelesma.katastasi_pigis}]
        anafora: dict[str, object] = {
            "leitourgia": "live",
            "piges": piges_report,
        }
        if apotelesma.git_diafores_report is not None:
            anafora["git_diafores"] = apotelesma.git_diafores_report
        anafora.update(apotelesma.dedomena_syllogis_extra)
        return anafora

    setattr(syllogi, "syllexe_pliri", syllexe_pliri)
    axiologisi = ModuleType("devrar.axiologisi")

    def axiologise_ergasia(dedomena: Mapping[str, object]) -> dict[str, object]:
        """Καταγράφει την πρώτη φάση αξιολόγησης."""
        apotelesma.seira_analisis.append("ergasia")
        apotelesma_dedomenon = dict(dedomena)
        apotelesma_dedomenon.setdefault("analysi", {"methodos": "rules"})
        apotelesma_dedomenon.setdefault("axiologisi", {"synoliko": None})
        return apotelesma_dedomenon

    setattr(axiologisi, "axiologise_ergasia", axiologise_ergasia)
    epeisodia = ModuleType("devrar.epeisodia")

    def axiologise_epeisodia(dedomena: Mapping[str, object]) -> dict[str, object]:
        """Καταγράφει την αξιολόγηση επεισοδίων."""
        apotelesma.seira_analisis.append("epeisodia")
        return dict(dedomena)

    setattr(epeisodia, "axiologise_epeisodia", axiologise_epeisodia)
    eisagoges = ModuleType("devrar.eisagoges")

    def diavase_energo_xrono(*orismata: object) -> dict[str, object]:
        """Επιστρέφει controlled active-time import."""
        apotelesma.kliseis_xronou.append(orismata)
        return apotelesma.apotelesma_xronou

    def diavase_kostos(*orismata: object) -> dict[str, object]:
        """Επιστρέφει controlled cost import."""
        apotelesma.kliseis_kostous.append(orismata)
        return apotelesma.apotelesma_kostous

    setattr(eisagoges, "diavase_energo_xrono", diavase_energo_xrono)
    setattr(eisagoges, "diavase_kostos", diavase_kostos)
    proodos = ModuleType("devrar.proodos")

    def sygkrine_anafores(
        trexousa: Mapping[str, object], proigoumeni: Mapping[str, object]
    ) -> dict[str, object]:
        """Καταγράφει baseline comparison με safe aggregate result."""
        apotelesma.seira_analisis.append("sygkrisi")
        return dict(apotelesma.sygkrisi or {"aggregate": "compatible"})

    setattr(proodos, "sygkrine_anafores", sygkrine_anafores)
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
        apotelesma.seira_analisis.append("topiko")
        apotelesma.kliseis_topikis.append((dedomena, modelo, ektelesimo))
        if apotelesma.sfalma_topikis is not None:
            raise apotelesma.sfalma_topikis
        assert isinstance(dedomena, dict)
        dedomena["analysi"] = {"methodos": "local", "katastasi": "ok"}
        return dedomena

    setattr(topiko, "analysi_topika", analysi_topika)
    setattr(topiko, "SfalmaTopikisAnalysis", sfalma_topikis)
    cloud = ModuleType("devrar.cloud")

    def analysi_cloud(
        dedomena: Mapping[str, object],
        modelo: str,
        endpoint: str,
        epitrepetai: bool = False,
        onoma_env_key: str = "DEVRAR_CLOUD_API_KEY",
    ) -> dict[str, object]:
        """Captures explicit cloud dispatch without environment or network use."""
        apotelesma.seira_analisis.append("cloud")
        apotelesma.kliseis_cloud.append(
            (dedomena, modelo, endpoint, epitrepetai, onoma_env_key)
        )
        if apotelesma.sfalma_cloud is not None:
            raise apotelesma.sfalma_cloud
        anafora_cloud = dict(dedomena)
        if apotelesma.apotelesma_cloud is not None:
            anafora_cloud.update(apotelesma.apotelesma_cloud)
        else:
            anafora_cloud["analysi"] = {
                "methodos": "cloud",
                "katastasi": "ok",
                "provider": "openai_compatible",
            }
        return anafora_cloud

    setattr(cloud, "analysi_cloud", analysi_cloud)
    metatropes.setitem(sys.modules, "devrar.deigma", deigma)
    metatropes.setitem(sys.modules, "devrar.syndesi", syllogi)
    metatropes.setitem(sys.modules, "devrar.axiologisi", axiologisi)
    metatropes.setitem(sys.modules, "devrar.epeisodia", epeisodia)
    metatropes.setitem(sys.modules, "devrar.eisagoges", eisagoges)
    metatropes.setitem(sys.modules, "devrar.proodos", proodos)
    metatropes.setitem(sys.modules, "devrar.anafora", anafora)
    metatropes.setitem(sys.modules, "devrar.topiko", topiko)
    metatropes.setitem(sys.modules, "devrar.cloud", cloud)

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
        "idle_minutes": 15,
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


@pytest.mark.parametrize(
    ("extra", "minima"),
    [
        (["--analysis", "cloud", "--cloud-model", "model"], "--cloud-endpoint"),
        (
            [
                "--analysis",
                "cloud",
                "--cloud-endpoint",
                "https://api.invalid/v1/chat/completions",
            ],
            "--cloud-model",
        ),
        (
            [
                "--analysis",
                "cloud",
                "--cloud-endpoint",
                "https://api.invalid/v1/chat/completions",
                "--cloud-model",
                "model",
            ],
            "--allow-cloud-evidence",
        ),
    ],
)
def test_kyria_cloud_requires_endpoint_model_and_opt_in_before_collection(
    katastasi: KatastasiDokimis, extra: list[str], minima: str
) -> None:
    """Cloud mode requires endpoint, model and consent before any reads."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--source", "claude", *extra])

    assert apotelesma == 2
    assert minima in sfalmata.getvalue()
    assert katastasi.kliseis_syllogis == []
    assert katastasi.kliseis_cloud == []


@pytest.mark.parametrize(
    ("mode", "cloud_orisma"),
    [
        (mode, cloud_orisma)
        for mode in ("rules", "local")
        for cloud_orisma in (
            ["--cloud-endpoint", "https://api.invalid/v1/chat/completions"],
            ["--cloud-model", "model"],
            ["--cloud-key-env", "ALT_KEY"],
            ["--allow-cloud-evidence"],
        )
    ],
)
def test_kyria_non_cloud_modes_aporriptoun_cloud_flags(
    katastasi: KatastasiDokimis, mode: str, cloud_orisma: list[str]
) -> None:
    """Rules/local modes do not silently ignore any explicit cloud option."""
    sfalmata = io.StringIO()
    local_orismata = (
        ["--analysis", "local", "--local-model", "local"] if mode == "local" else []
    )
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--demo", *local_orismata, *cloud_orisma])

    assert apotelesma == 2
    assert "only with --analysis cloud" in sfalmata.getvalue()
    assert katastasi.kliseis_demo == 0


@pytest.mark.parametrize(
    "local_orisma", [["--local-model", "local"], ["--ollama-path", "ollama.exe"]]
)
def test_kyria_cloud_aporriptei_local_flags_prin_collection(
    katastasi: KatastasiDokimis, local_orisma: list[str]
) -> None:
    """Cloud analysis cannot combine with local-only model or executable flags."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(
            [
                "wrap",
                "--source",
                "claude",
                "--analysis",
                "cloud",
                "--cloud-endpoint",
                "https://api.invalid/v1/chat/completions",
                "--cloud-model",
                "model",
                "--allow-cloud-evidence",
                *local_orisma,
            ]
        )

    assert apotelesma == 2
    assert katastasi.kliseis_syllogis == []
    assert katastasi.kliseis_cloud == []


def test_kyria_cloud_help_warns_about_evidence_transfer(
    katastasi: KatastasiDokimis,
) -> None:
    """Help explains bounded redacted evidence leaves the local machine."""
    eksodos = io.StringIO()
    with contextlib.redirect_stdout(eksodos):
        apotelesma = kyria(["wrap", "--help"])

    assert apotelesma == 0
    assert "bounded redacted excerpts" in eksodos.getvalue()
    assert "chosen provider" in eksodos.getvalue()
    assert "DEVRAR_CLOUD_API_KEY" in eksodos.getvalue()
    assert katastasi.kliseis_syllogis == []


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
    assert katastasi.seira_analisis == ["ergasia", "epeisodia", "topiko"]
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


def test_kyria_cloud_success_forwards_consent_and_compares_after_analysis(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Cloud mode receives explicit values and comparison follows cloud analysis."""
    baseline = prosorini_diathromi / "baseline.json"
    baseline.write_text('{"leitourgia":"demo"}', encoding="utf-8")

    apotelesma = kyria(
        [
            "wrap",
            "--demo",
            "--analysis",
            "cloud",
            "--cloud-endpoint",
            "https://api.synthetic.invalid/v1/chat/completions",
            "--cloud-model",
            "synthetic-model",
            "--cloud-key-env",
            "ALT_SYNTHETIC_KEY",
            "--allow-cloud-evidence",
            "--compare",
            str(baseline),
        ]
    )

    assert apotelesma == 0
    assert katastasi.seira_analisis == ["ergasia", "epeisodia", "cloud", "sygkrisi"]
    assert len(katastasi.kliseis_cloud) == 1
    dedomena, modelo, endpoint, consent, env_name = katastasi.kliseis_cloud[0]
    assert dedomena["leitourgia"] == "demo"
    assert (modelo, endpoint, consent, env_name) == (
        "synthetic-model",
        "https://api.synthetic.invalid/v1/chat/completions",
        True,
        "ALT_SYNTHETIC_KEY",
    )
    assert katastasi.kliseis_demo == 1
    assert katastasi.kliseis_anaforas[0][0]["analysi"]["methodos"] == "cloud"
    assert "synthetic key" not in str(katastasi.kliseis_anaforas[0][0]).casefold()


def test_kyria_cloud_uses_default_key_environment_name(
    katastasi: KatastasiDokimis,
) -> None:
    """Cloud mode uses the documented key environment name by default."""
    apotelesma = kyria(
        [
            "wrap",
            "--demo",
            "--analysis",
            "cloud",
            "--cloud-endpoint",
            "https://api.synthetic.invalid/v1/chat/completions",
            "--cloud-model",
            "synthetic-model",
            "--allow-cloud-evidence",
        ]
    )

    assert apotelesma == 0
    assert katastasi.kliseis_cloud[0][4] == "DEVRAR_CLOUD_API_KEY"


def test_kyria_cloud_failure_keeps_rules_metrics_and_nested_evidence(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Cloud errors produce a safe partial artifact with prior analysis intact."""
    baseline = prosorini_diathromi / "baseline.json"
    baseline.write_text('{"leitourgia":"live"}', encoding="utf-8")
    katastasi.sfalma_cloud = RuntimeError(
        "synthetic key private-secret https://api.invalid/private/path"
    )
    katastasi.katastasi_pigis = "partial"
    katastasi.dedomena_syllogis_extra = {
        "synola": {"synedries": 17, "tokens": None},
        "metrika_ergasias": {"epeisodia": [{"synedria": "private-session"}]},
        "epeisodia_ergasias": {"paratiriseis": [{"id": "nested"}]},
        "eyrimata": [{"id": "rules-finding", "paragogos": "rules"}],
    }
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(
            [
                "wrap",
                "--source",
                "claude",
                "--analysis",
                "cloud",
                "--cloud-endpoint",
                "https://api.synthetic.invalid/v1/chat/completions",
                "--cloud-model",
                "synthetic-model",
                "--allow-cloud-evidence",
                "--compare",
                str(baseline),
            ]
        )

    assert apotelesma == 3
    assert len(katastasi.kliseis_anaforas) == 1
    report = katastasi.kliseis_anaforas[0][0]
    assert report["synola"] == {"synedries": 17, "tokens": None}
    assert report["metrika_ergasias"] == {
        "epeisodia": [{"synedria": "private-session"}]
    }
    assert report["epeisodia_ergasias"] == {"paratiriseis": [{"id": "nested"}]}
    assert report["eyrimata"] == [{"id": "rules-finding", "paragogos": "rules"}]
    analysi = _pare_analysi(report)
    assert analysi["methodos"] == "cloud"
    assert analysi["katastasi"] == "failed"
    assert analysi["efarmostike"] == "rules"
    assert analysi["provider"] == "openai_compatible"
    assert analysi["model_id"] == "synthetic-model"
    assert analysi["cloud_opt_in"] is True
    assert "cloud request failed" in str(analysi["aitia"]).casefold()
    assert "private-secret" not in str(report)
    assert "/private/path" not in str(report)
    assert "private-secret" not in sfalmata.getvalue()
    assert "/private/path" not in sfalmata.getvalue()
    assert katastasi.seira_analisis == ["ergasia", "epeisodia", "cloud", "sygkrisi"]


def test_kyria_cloud_success_keeps_exit_three_for_partial_source(
    katastasi: KatastasiDokimis,
) -> None:
    """Cloud success does not hide partial selected source coverage."""
    katastasi.katastasi_pigis = "partial"

    apotelesma = kyria(
        [
            "wrap",
            "--source",
            "claude",
            "--analysis",
            "cloud",
            "--cloud-endpoint",
            "https://api.synthetic.invalid/v1/chat/completions",
            "--cloud-model",
            "synthetic-model",
            "--allow-cloud-evidence",
        ]
    )

    assert apotelesma == 3
    assert _pare_analysi(katastasi.kliseis_anaforas[0][0])["katastasi"] == "ok"
    dedomena, _, _, _ = katastasi.kliseis_anaforas[0]
    assert _pare_analysi(dedomena)["katastasi"] == "ok"


def test_anafora_einai_meriki_an_analysi_apetyxei() -> None:
    """Το report χαρακτηρίζεται partial όταν έχει αποτύχει το local analysis."""
    assert _anafora_einai_meriki(
        {"piges": [], "analysi": {"methodos": "local", "katastasi": "failed"}}
    )


@pytest.mark.parametrize("katastasi_git", ["partial", "missing", "unsupported"])
def test_anafora_einai_meriki_an_git_delta_den_einai_ok(katastasi_git: str) -> None:
    """Git delta with a non-complete status marks the report partial."""
    assert _anafora_einai_meriki(
        {"piges": [{"katastasi": "ok"}], "git_diafores": {"katastasi": katastasi_git}}
    )


@pytest.mark.parametrize("git_delta", [None, "malformed"])
def test_anafora_einai_meriki_an_git_delta_einai_malformed(git_delta: object) -> None:
    """Malformed present Git delta status marks the report partial."""
    assert _anafora_einai_meriki(
        {"piges": [{"katastasi": "ok"}], "git_diafores": git_delta}
    )


def test_anafora_einai_meriki_den_apaitiei_git_delta_gia_ai_only() -> None:
    """AI-only reports do not require optional repository metrics."""
    assert not _anafora_einai_meriki({"piges": [{"katastasi": "ok"}]})


@pytest.mark.parametrize("katastasi_git", ["partial", "missing", "unsupported"])
def test_kyria_git_delta_partial_krata_report_kai_epistrefei_3(
    katastasi: KatastasiDokimis, katastasi_git: str
) -> None:
    """Partial repository delta saves the report and returns exit code three."""
    katastasi.git_diafores_report = {"katastasi": katastasi_git}

    apotelesma = kyria(["wrap", "--repo", "repo"])

    assert apotelesma == 3
    assert len(katastasi.kliseis_anaforas) == 1
    assert katastasi.kliseis_anaforas[0][0]["git_diafores"] == {
        "katastasi": katastasi_git
    }


def test_kyria_malformed_git_delta_krata_report_kai_epistrefei_3(
    katastasi: KatastasiDokimis,
) -> None:
    """Malformed present Git section keeps the artifact and returns partial."""
    katastasi.git_diafores_report = "malformed"

    apotelesma = kyria(["wrap", "--repo", "repo"])

    assert apotelesma == 3
    assert len(katastasi.kliseis_anaforas) == 1
    assert katastasi.kliseis_anaforas[0][0]["git_diafores"] == "malformed"


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


def test_kyria_demo_aporriptei_activitywatch_flag(
    katastasi: KatastasiDokimis,
) -> None:
    """Το demo απορρίπτει ρητή εισαγωγή πραγματικού χρόνου δραστηριότητας."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--demo", "--activitywatch-path", "aw.json"])

    assert apotelesma == 2
    assert "--demo cannot be combined" in sfalmata.getvalue()
    assert katastasi.kliseis_demo == 0


def test_kyria_anagnorizei_nees_piges(katastasi: KatastasiDokimis) -> None:
    """Η νέα CLI δέχεται τις τρεις πρόσθετες πηγές transcript."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--source", "opencode"])

    assert apotelesma == 0
    assert not sfalmata.getvalue()
    assert katastasi.kliseis_syllogis


@pytest.mark.parametrize(
    ("pigi", "orisma_diadromis"),
    [
        ("opencode", "--opencode-path"),
        ("gemini", "--gemini-path"),
        ("antigravity", "--antigravity-path"),
    ],
)
def test_kyria_nees_diadromes_epilegoun_pigi(
    katastasi: KatastasiDokimis, pigi: str, orisma_diadromis: str
) -> None:
    """Τα νέα path options επιλέγουν τη σωστή πηγή χωρίς ξεχωριστό --source."""
    apotelesma = kyria(["wrap", orisma_diadromis, "private-data"])

    assert apotelesma == 0
    orismata_syllogis, _ = katastasi.kliseis_syllogis[0]
    assert tuple(orismata_syllogis[0]) == (pigi,)
    assert orismata_syllogis[1] == {pigi: Path("private-data")}


def test_kyria_live_perna_idle_minutes_sti_syllogi(
    katastasi: KatastasiDokimis,
) -> None:
    """Το idle gap περνάει αυτούσιο στον streaming collector."""
    apotelesma = kyria(["wrap", "--source", "claude", "--idle-minutes", "37"])

    assert apotelesma == 0
    assert katastasi.kliseis_syllogis[0][1]["idle_minutes"] == 37


@pytest.mark.parametrize("lepta", ["0", "1441", "bad"])
def test_kyria_idle_minutes_mi_egkyro_epistrefei_usage_error(
    katastasi: KatastasiDokimis, lepta: str
) -> None:
    """Idle minutes εκτός ορίων ή μη αριθμητικά απορρίπτονται πριν από συλλογή."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--source", "claude", "--idle-minutes", lepta])

    assert apotelesma == 2
    assert katastasi.kliseis_syllogis == []


def test_kyria_imports_xrono_kai_kostos_me_filtra(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Οι explicit imports λαμβάνουν date bounds και επισυνάπτονται στο report."""
    apotelesma = kyria(
        [
            "wrap",
            "--repo",
            "repo",
            "--activitywatch-path",
            "watch.json",
            "--cost-path",
            "ledger.csv",
            "--since",
            "2026-01-01",
            "--until",
            "2026-01-31",
            "--timezone",
            "Europe/Athens",
        ]
    )

    assert apotelesma == 0
    dedomena = katastasi.kliseis_anaforas[0][0]
    assert dedomena["energos_xronos"] == {"status": "ok"}
    assert dedomena["kostos"] == {"status": "ok"}
    assert katastasi.kliseis_xronou[0][1:] == (
        date(2026, 1, 1),
        date(2026, 1, 31),
        "Europe/Athens",
    )
    assert katastasi.kliseis_kostous[0][1:] == (
        date(2026, 1, 1),
        date(2026, 1, 31),
        "Europe/Athens",
    )
    assert katastasi.seira_analisis == ["ergasia", "epeisodia"]


def test_kyria_partial_import_keeps_report_and_returns_three(
    katastasi: KatastasiDokimis,
) -> None:
    """Μη πλήρης supplied import κρατά artifact και επιστρέφει partial code."""
    katastasi.apotelesma_xronou = {"status": "unsupported"}

    apotelesma = kyria(["wrap", "--repo", "repo", "--activitywatch-path", "watch.json"])

    assert apotelesma == 3
    assert len(katastasi.kliseis_anaforas) == 1
    assert _anafora_einai_meriki(katastasi.kliseis_anaforas[0][0])


def test_kyria_compare_attaches_aggregate_after_assessments(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Το comparison εκτελείται μετά τα δύο assessments και αποθηκεύεται στο report."""
    baseline = prosorini_diathromi / "baseline.json"
    baseline.write_text('{"leitourgia":"live","synola":{}}', encoding="utf-8")
    katastasi.sygkrisi = {"deltas": [{"metric": "sessions", "delta": 1}]}

    apotelesma = kyria(["wrap", "--repo", "repo", "--compare", str(baseline)])

    assert apotelesma == 0
    assert katastasi.seira_analisis == ["ergasia", "epeisodia", "sygkrisi"]
    assert katastasi.kliseis_anaforas[0][0]["sygkrisi"] == katastasi.sygkrisi


@pytest.mark.parametrize("periexomeno", ["[]", "null", "{broken"])
def test_kyria_compare_malformed_baseline_aporriptei_prin_syllogi(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path, periexomeno: str
) -> None:
    """Malformed/non-object baseline δεν ξεκινάει source collection."""
    baseline = prosorini_diathromi / "baseline.json"
    baseline.write_text(periexomeno, encoding="utf-8")
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--repo", "repo", "--compare", str(baseline)])

    assert apotelesma == 2
    assert katastasi.kliseis_syllogis == []


def test_kyria_compare_rejects_demo_live_mismatch(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Demo report δεν συγκρίνεται με baseline live δεδομένων."""
    baseline = prosorini_diathromi / "baseline.json"
    baseline.write_text('{"leitourgia":"live"}', encoding="utf-8")
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--demo", "--compare", str(baseline)])

    assert apotelesma == 2
    assert katastasi.kliseis_demo == 0


def test_kyria_demo_compare_accepts_demo_baseline(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Demo comparison επιτρέπεται μόνο με ρητά synthetic baseline."""
    baseline = prosorini_diathromi / "baseline.json"
    baseline.write_text('{"leitourgia":"demo"}', encoding="utf-8")

    apotelesma = kyria(["wrap", "--demo", "--compare", str(baseline)])

    assert apotelesma == 0
    assert katastasi.seira_analisis == ["ergasia", "epeisodia", "sygkrisi"]


def test_kyria_demo_rejects_import_paths(katastasi: KatastasiDokimis) -> None:
    """Το demo δεν ενσωματώνει πραγματικό ActivityWatch ή cost input."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--demo", "--cost-path", "ledger.json"])

    assert apotelesma == 2
    assert katastasi.kliseis_demo == 0


def test_kyria_compare_requires_known_baseline_mode(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Baseline χωρίς mode δεν τεκμηριώνει συμβατή live σύγκριση."""
    baseline = prosorini_diathromi / "baseline.json"
    baseline.write_text('{"synola":{}}', encoding="utf-8")
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--repo", "repo", "--compare", str(baseline)])

    assert apotelesma == 2
    assert katastasi.kliseis_syllogis == []


def test_kyria_compare_rejects_oversized_baseline(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Baseline πάνω από το όριο αναγνώζεται ως invalid usage χωρίς συλλογή."""
    baseline = prosorini_diathromi / "baseline.json"
    baseline.write_bytes(b" " * (10 * 1024 * 1024 + 1))
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--repo", "repo", "--compare", str(baseline)])

    assert apotelesma == 2
    assert "10 MB" in sfalmata.getvalue()
    assert katastasi.kliseis_syllogis == []


def test_kyria_compare_missing_file_returns_invalid_usage(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Απόν baseline επιστρέφει σαφές CLI usage error πριν από source reads."""
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(
            [
                "wrap",
                "--repo",
                "repo",
                "--compare",
                str(prosorini_diathromi / "missing.json"),
            ]
        )

    assert apotelesma == 2
    assert "cannot read comparison report" in sfalmata.getvalue()
    assert katastasi.kliseis_syllogis == []


def test_kyria_compare_bounded_json_depth_aporriptei_baseline(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Υπερβολικά nested JSON απορρίπτεται με usage error, χωρίς traceback."""
    baseline = prosorini_diathromi / "baseline.json"
    baseline.write_text("[" * 1500 + "]" * 1500, encoding="utf-8")
    sfalmata = io.StringIO()
    with contextlib.redirect_stderr(sfalmata):
        apotelesma = kyria(["wrap", "--repo", "repo", "--compare", str(baseline)])

    assert apotelesma == 2
    assert "valid UTF-8 JSON" in sfalmata.getvalue()
    assert katastasi.kliseis_syllogis == []


def test_kyria_import_path_monon_paragei_report(
    katastasi: KatastasiDokimis,
) -> None:
    """Ρητό data import μόνο του αρκεί ως live input και παράγει report."""
    apotelesma = kyria(["wrap", "--activitywatch-path", "watch.json"])

    assert apotelesma == 0
    assert len(katastasi.kliseis_anaforas) == 1
    assert katastasi.kliseis_anaforas[0][0]["energos_xronos"] == {"status": "ok"}


def test_kyria_compare_runs_after_local_analysis(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Η σύγκριση λαμβάνει report μετά rules, episodes και local analysis."""
    baseline = prosorini_diathromi / "baseline.json"
    baseline.write_text('{"leitourgia":"demo"}', encoding="utf-8")

    apotelesma = kyria(
        [
            "wrap",
            "--demo",
            "--analysis",
            "local",
            "--local-model",
            "model",
            "--compare",
            str(baseline),
        ]
    )

    assert apotelesma == 0
    assert katastasi.seira_analisis == ["ergasia", "epeisodia", "topiko", "sygkrisi"]


def test_kyria_compare_solo_emfanizei_help_xoris_baseline_read(
    katastasi: KatastasiDokimis, prosorini_diathromi: Path
) -> None:
    """Χωρίς current source το compare-only command δείχνει help χωρίς read."""
    eksodos = io.StringIO()
    with contextlib.redirect_stdout(eksodos):
        apotelesma = kyria(
            ["wrap", "--compare", str(prosorini_diathromi / "missing.json")]
        )

    assert apotelesma == 0
    assert "usage:" in eksodos.getvalue().lower()
    assert katastasi.kliseis_syllogis == []
    assert katastasi.kliseis_anaforas == []
