"""Read-only Git history deltas with explicit first-parent coverage semantics."""

from __future__ import annotations

import logging
import subprocess
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

logger = logging.getLogger(__name__)

GIT_TIMEOUT_DEFTEROLEPTA = 30
GIT_ORIO_COMMITS = 10_000
GIT_DELIMITER = b"\x1f"
GIT_LOG_FORMAT = "%H%x1f%aN%x1f%aE%x1f%aI%x1f%P"


@dataclass
class KatagrafiGit:
    """Per-commit author metadata and numstat counters used for deduplication."""

    tautotita: str
    grafeas: str
    email: str
    imerominia: date | None
    goneis: int
    prosthikes: int = 0
    diagrafes: int = 0
    allages_arxeion: int = 0
    allages_dyadikon: int = 0


@dataclass
class ApotelesmaApothikis:
    """Successful repository statistics before report aggregation."""

    onoma: str
    katagrafes: dict[str, KatagrafiGit]
    arxeia_tracked: int
    tautotita_dentrou: str
    perikopi: bool
    agnostes_imerominies: int


def syllexe_git_diafores(
    apothitiria: Sequence[Path],
    apo: date | None = None,
    eos: date | None = None,
    zoni: str = "Europe/Athens",
    author: str | None = None,
) -> dict[str, object]:
    """Συλλέγει Git numstat σε HEAD με φίλτρα author-date συμβατά με collector."""
    if apo is not None and eos is not None and apo > eos:
        raise ValueError("start date must be on or before end date")
    try:
        antikeimeno_zonis = ZoneInfo(zoni)
    except (ZoneInfoNotFoundError, ValueError) as sfalma:
        raise ValueError(f"invalid timezone: {zoni}") from sfalma
    filtro_grafea = author.casefold().strip() if author and author.strip() else None
    apothikies = _diavase_apothikies(
        apothitiria, antikeimeno_zonis, apo, eos, filtro_grafea
    )
    commits_synola: dict[str, KatagrafiGit] = {}
    dentra: dict[str, int] = {}
    apothikies_report: list[dict[str, object]] = []
    sfalmata = 0
    agnostes_imerominies = 0
    perikopi = False
    for apothikio, apotelesma in apothikies:
        if apotelesma is None:
            sfalmata += 1
            apothikies_report.append(_grammi_sfalmatos(apothikio))
            continue
        apothikies_report.append(_grammi_apothikiou(apotelesma))
        agnostes_imerominies += apotelesma.agnostes_imerominies
        perikopi = perikopi or apotelesma.perikopi
        dentra.setdefault(apotelesma.tautotita_dentrou, apotelesma.arxeia_tracked)
        for katagrafi in apotelesma.katagrafes.values():
            commits_synola.setdefault(katagrafi.tautotita, katagrafi)
    if perikopi:
        logger.warning("Git history limit reached for one or more repositories")
    if agnostes_imerominies:
        logger.warning("Git commits with unknown author dates were excluded")
    katastasi = "ok"
    if sfalmata or agnostes_imerominies or perikopi or not apothikies:
        katastasi = "partial" if apothikies else "missing"
    simeioseis: list[str] = []
    if sfalmata:
        simeioseis.append(f"{sfalmata} repository/repositories could not be read.")
    if agnostes_imerominies:
        simeioseis.append(
            f"{agnostes_imerominies} matching commits with unknown author dates "
            "were excluded by the active date filter."
        )
    if perikopi:
        simeioseis.append(
            f"History was capped at {GIT_ORIO_COMMITS} commits per repository."
        )
    if not apothikies:
        simeioseis.append("No Git repositories were selected.")
    synola: dict[str, int | None] = {
        **_synola_commit(commits_synola.values()),
        "unique_commits": len(commits_synola),
        "arxeia_tracked_HEAD": sum(dentra.values()) if dentra else None,
    }
    return {
        "adapter": "git-numstat-first-parent-v1",
        "katastasi": katastasi,
        "periodos": {
            "apo": apo.isoformat() if apo else None,
            "eos": eos.isoformat() if eos else None,
            "zoni": zoni,
        },
        "filtro": {"author": filtro_grafea},
        "semantics": {
            "history": "first-parent only; non-first-parent-only commits are omitted",
            "merge": "included against first parent; counted separately",
            "renames": "disabled; a rename is recorded as deletion and addition",
            "binary": (
                "binary numstat rows count as binary file changes; "
                "line counts exclude them"
            ),
            "limit_commits_per_repository": GIT_ORIO_COMMITS,
        },
        "apothikies": apothikies_report,
        "synola": synola,
        "kalypsi": {
            "apothikies": len(apothikies),
            "epityxeis": sum(apotelesma is not None for _, apotelesma in apothikies),
            "sfalmata": sfalmata,
            "agnostes_imerominies": agnostes_imerominies,
            "perikopi": perikopi,
            "katastasi": katastasi,
            "simeioseis": simeioseis,
        },
    }


def _diavase_apothikies(
    apothitiria: Sequence[Path],
    antikeimeno_zonis: ZoneInfo,
    apo: date | None,
    eos: date | None,
    author: str | None,
) -> list[tuple[Path, ApotelesmaApothikis | None]]:
    """Διαβάζει μοναδικά paths σε HEAD και κρατά αποτυχίες ανά repository."""
    diathesimes: set[str] = set()
    apotelesmata: list[tuple[Path, ApotelesmaApothikis | None]] = []
    for apothikio in apothitiria:
        try:
            kleidi = str(apothikio.resolve()).casefold()
        except OSError as sfalma:
            logger.warning("Cannot resolve Git repository path: %s", sfalma)
            kleidi = str(apothikio.absolute()).casefold()
        if kleidi in diathesimes:
            continue
        diathesimes.add(kleidi)
        try:
            apotelesma = _diavase_apothikio(
                apothikio, antikeimeno_zonis, apo, eos, author
            )
        except (OSError, subprocess.SubprocessError, ValueError) as sfalma:
            logger.warning(
                "Cannot read Git repository %s (%s)",
                apothikio.name,
                type(sfalma).__name__,
            )
            apotelesma = None
        apotelesmata.append((apothikio, apotelesma))
    return apotelesmata


def _diavase_apothikio(
    apothikio: Path,
    antikeimeno_zonis: ZoneInfo,
    apo: date | None,
    eos: date | None,
    author: str | None,
) -> ApotelesmaApothikis:
    """Διαβάζει περιορισμένο log, tree identity και inventory χωρίς writes."""
    exodos = _git(
        apothikio,
        "log",
        "--first-parent",
        "--no-renames",
        "--no-ext-diff",
        "--no-textconv",
        "--format=" + GIT_LOG_FORMAT,
        "--numstat",
        "-z",
        f"--max-count={GIT_ORIO_COMMITS + 1}",
        "HEAD",
    )
    katagrafes, perikopi = _analuse_numstat(exodos, antikeimeno_zonis)
    epitylexthenta: dict[str, KatagrafiGit] = {}
    agnostes_imerominies = 0
    for katagrafi in katagrafes[:GIT_ORIO_COMMITS]:
        if author and author not in f"{katagrafi.grafeas} {katagrafi.email}".casefold():
            continue
        if apo is not None or eos is not None:
            if katagrafi.imerominia is None:
                agnostes_imerominies += 1
                continue
            if apo is not None and katagrafi.imerominia < apo:
                continue
            if eos is not None and katagrafi.imerominia > eos:
                continue
        epitylexthenta[katagrafi.tautotita] = katagrafi
    tautotita_dentrou = (
        _git(apothikio, "rev-parse", "HEAD^{tree}").decode("ascii").strip()
    )
    arxeia_tracked = len(
        _git(apothikio, "ls-tree", "-r", "-z", "--name-only", "HEAD").split(b"\0")[:-1]
    )
    return ApotelesmaApothikis(
        apothikio.name,
        epitylexthenta,
        arxeia_tracked,
        tautotita_dentrou,
        perikopi,
        agnostes_imerominies,
    )


def _git(apothikio: Path, *orismata: str) -> bytes:
    """Τρέχει read-only Git argv με timeout και χωρίς shell interpolation."""
    apotelesma = subprocess.run(
        ["git", "-C", str(apothikio), *orismata],
        check=True,
        capture_output=True,
        timeout=GIT_TIMEOUT_DEFTEROLEPTA,
    )
    return apotelesma.stdout


def _analuse_numstat(
    exodos: bytes, antikeimeno_zonis: ZoneInfo
) -> tuple[list[KatagrafiGit], bool]:
    """Αναλύει NUL-safe `git log --numstat` output με όριο commits."""
    katagrafes: list[KatagrafiGit] = []
    trexon: KatagrafiGit | None = None
    perikopi = False
    for tmima in exodos.split(b"\0"):
        if not tmima:
            continue
        katharo = tmima.lstrip(b"\n")
        if GIT_DELIMITER in katharo:
            if len(katagrafes) == GIT_ORIO_COMMITS:
                perikopi = True
                break
            trexon = _analuse_commit(katharo, antikeimeno_zonis)
            if trexon is not None:
                katagrafes.append(trexon)
            else:
                trexon = None
            continue
        if trexon is not None:
            _prosthese_numstat(trexon, katharo)
    return katagrafes, perikopi


def _analuse_commit(tmima: bytes, antikeimeno_zonis: ZoneInfo) -> KatagrafiGit | None:
    """Διαβάζει τα author/date/parent fields ενός commit header."""
    tmimata = tmima.split(GIT_DELIMITER)
    if len(tmimata) != 5:
        return None
    tautotita, grafeas, email, xronos, goneis = tmimata
    imerominia = _imerominia_zonis(xronos.decode("utf-8", "replace"), antikeimeno_zonis)
    return KatagrafiGit(
        tautotita.decode("ascii", "replace"),
        grafeas.decode("utf-8", "replace"),
        email.decode("utf-8", "replace"),
        imerominia,
        len(goneis.split()) if goneis else 0,
    )


def _prosthese_numstat(katagrafi: KatagrafiGit, tmima: bytes) -> None:
    """Προσθέτει ένα αρχείο numstat, διακρίνοντας binary από line deltas."""
    tmimata = tmima.split(b"\t", 2)
    if len(tmimata) != 3:
        return
    prosthikes, diagrafes, _onoma_arxeiou = tmimata
    if prosthikes == b"-" and diagrafes == b"-":
        katagrafi.allages_arxeion += 1
        katagrafi.allages_dyadikon += 1
        return
    try:
        plithos_prostheseon = int(prosthikes)
        plithos_diagrafon = int(diagrafes)
    except ValueError:
        return
    katagrafi.allages_arxeion += 1
    katagrafi.prosthikes += plithos_prostheseon
    katagrafi.diagrafes += plithos_diagrafon


def _imerominia_zonis(xronos: str, antikeimeno_zonis: ZoneInfo) -> date | None:
    """Μετατρέπει author date ISO σε ημερομηνία τοπικής ζώνης αναφοράς."""
    try:
        analyomeno = datetime.fromisoformat(xronos.replace("Z", "+00:00"))
    except ValueError:
        return None
    if analyomeno.tzinfo is None:
        return None
    try:
        return analyomeno.astimezone(antikeimeno_zonis).date()
    except (OverflowError, ValueError):
        return None


def _grammi_apothikiou(apotelesma: ApotelesmaApothikis) -> dict[str, object]:
    """Δημιουργεί report row για ένα επιτυχώς αναγνώσιμο repository."""
    metriseis = _synola_commit(apotelesma.katagrafes.values())
    return {
        "onoma": apotelesma.onoma,
        "commits": len(apotelesma.katagrafes),
        "merge_commits": metriseis["merge_commits"],
        "additions": metriseis["additions"],
        "deletions": metriseis["deletions"],
        "file_changes": metriseis["file_changes"],
        "binary_file_changes": metriseis["binary_file_changes"],
        "arxeia_tracked_HEAD": apotelesma.arxeia_tracked,
    }


def _grammi_sfalmatos(apothikio: Path) -> dict[str, object]:
    """Δημιουργεί null counters όταν repository δεν είναι αναγνώσιμο."""
    return {
        "onoma": apothikio.name,
        "commits": None,
        "merge_commits": None,
        "additions": None,
        "deletions": None,
        "file_changes": None,
        "binary_file_changes": None,
        "arxeia_tracked_HEAD": None,
    }


def _synola_commit(katagrafes: Iterable[KatagrafiGit]) -> dict[str, int]:
    """Αθροίζει counters για unique commit objects."""
    prosthikes = 0
    diagrafes = 0
    allages_arxeion = 0
    allages_dyadikon = 0
    sygxonefseis = 0
    for katagrafi in katagrafes:
        prosthikes += katagrafi.prosthikes
        diagrafes += katagrafi.diagrafes
        allages_arxeion += katagrafi.allages_arxeion
        allages_dyadikon += katagrafi.allages_dyadikon
        if katagrafi.goneis > 1:
            sygxonefseis += 1
    return {
        "merge_commits": sygxonefseis,
        "additions": prosthikes,
        "deletions": diagrafes,
        "file_changes": allages_arxeion,
        "binary_file_changes": allages_dyadikon,
    }
