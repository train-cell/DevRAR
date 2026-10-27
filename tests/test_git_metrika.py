"""Behavioral tests for bounded, read-only Git history deltas."""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

import devrar.git_metrika as git_metrika
from devrar.git_metrika import syllexe_git_diafores


def trexe_git(
    apothikio: Path, *orismata: str, env: dict[str, str] | None = None
) -> str:
    """Runs Git in a temporary test repository and returns decoded output."""
    perivallon = os.environ.copy()
    if env:
        perivallon.update(env)
    apotelesma = subprocess.run(
        ["git", "-C", str(apothikio), *orismata],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=perivallon,
    )
    return apotelesma.stdout


def ftiakse_apothikio(diadromi: Path) -> Path:
    """Creates a synthetic repository with deterministic author identity."""
    diadromi.mkdir()
    subprocess.run(["git", "init", "-q", str(diadromi)], check=True)
    trexe_git(diadromi, "config", "user.name", "Synthetic Author")
    trexe_git(diadromi, "config", "user.email", "synthetic@example.invalid")
    return diadromi


def prosthese_commit(
    apothikio: Path,
    arxeia: dict[str, bytes],
    *,
    imerominia: str,
    minima: str,
    grafeas: str = "Synthetic Author",
    email: str = "synthetic@example.invalid",
) -> str:
    """Creates one synthetic commit with a fixed author and timestamp."""
    for sxetiko, periexomeno in arxeia.items():
        stoxos = apothikio / sxetiko
        stoxos.parent.mkdir(parents=True, exist_ok=True)
        stoxos.write_bytes(periexomeno)
    trexe_git(apothikio, "add", "--all")
    env = {
        "GIT_AUTHOR_NAME": grafeas,
        "GIT_AUTHOR_EMAIL": email,
        "GIT_COMMITTER_NAME": grafeas,
        "GIT_COMMITTER_EMAIL": email,
        "GIT_AUTHOR_DATE": imerominia,
        "GIT_COMMITTER_DATE": imerominia,
    }
    trexe_git(apothikio, "commit", "-m", minima, env=env)
    return trexe_git(apothikio, "rev-parse", "HEAD").strip()


def test_syllexe_git_diafores_counts_changes_binary_and_tracked_head(
    tmp_path: Path,
) -> None:
    """Reports line and binary change counts separately from the HEAD inventory."""
    repo = ftiakse_apothikio(tmp_path / "project")
    prosthese_commit(
        repo,
        {"text.txt": b"old\n", "asset.bin": b"\x00\x01"},
        imerominia="2026-10-01T10:00:00+00:00",
        minima="initial",
    )
    prosthese_commit(
        repo,
        {"text.txt": b"new\nextra\n", "asset.bin": b"\x00\x02"},
        imerominia="2026-10-02T10:00:00+00:00",
        minima="updates",
    )

    report = syllexe_git_diafores([repo])

    assert report["adapter"] == "git-numstat-first-parent-v1"
    assert report["katastasi"] == "ok"
    assert report["apothikies"] == [
        {
            "onoma": "project",
            "commits": 2,
            "merge_commits": 0,
            "additions": 3,
            "deletions": 1,
            "file_changes": 4,
            "binary_file_changes": 2,
            "arxeia_tracked_HEAD": 2,
        }
    ]
    assert report["synola"] == {
        "unique_commits": 2,
        "merge_commits": 0,
        "additions": 3,
        "deletions": 1,
        "file_changes": 4,
        "binary_file_changes": 2,
        "arxeia_tracked_HEAD": 2,
    }


def test_syllexe_git_diafores_inclusive_local_dates_author_and_unique_copy(
    tmp_path: Path,
) -> None:
    """Applies inclusive author-date filters and deduplicates copied history."""
    repo = ftiakse_apothikio(tmp_path / "project")
    first = prosthese_commit(
        repo,
        {"a.txt": b"a\n"},
        imerominia="2026-10-01T23:30:00-05:00",
        minima="boundary",
    )
    prosthese_commit(
        repo,
        {"a.txt": b"a\nolder\n"},
        imerominia="2026-10-01T12:00:00+00:00",
        minima="before local day",
    )
    prosthese_commit(
        repo,
        {"a.txt": b"a\nolder\nlater\n"},
        imerominia="2026-10-02T22:30:00+00:00",
        minima="after local day",
    )
    prosthese_commit(
        repo,
        {"a.txt": b"a\nolder\nlater\nother\n"},
        imerominia="2026-10-03T00:30:00+00:00",
        minima="outside",
        grafeas="Other Person",
        email="other@example.invalid",
    )
    copy = tmp_path / "copy"
    shutil.copytree(repo, copy, ignore=shutil.ignore_patterns("index.lock"))

    report = syllexe_git_diafores(
        [repo, copy, repo],
        apo=date(2026, 10, 2),
        eos=date(2026, 10, 2),
        zoni="Europe/Athens",
        author="synthetic@example.invalid",
    )

    assert report["synola"]["unique_commits"] == 1
    assert report["synola"]["additions"] == 1
    assert report["synola"]["arxeia_tracked_HEAD"] == 1
    assert [project["commits"] for project in report["apothikies"]] == [1, 1]
    assert report["kalypsi"]["apothikies"] == 2
    assert report["kalypsi"]["katastasi"] == "ok"
    assert first


def test_syllexe_git_diafores_separates_first_parent_merges(tmp_path: Path) -> None:
    """Counts first-parent merge diffs and exposes merge count separately."""
    repo = ftiakse_apothikio(tmp_path / "project")
    prosthese_commit(
        repo,
        {"base.txt": b"base\n"},
        imerominia="2026-10-01T10:00:00+00:00",
        minima="base",
    )
    main_branch = trexe_git(repo, "branch", "--show-current").strip()
    trexe_git(repo, "checkout", "-b", "feature")
    prosthese_commit(
        repo,
        {"feature.txt": b"feature\n"},
        imerominia="2026-10-02T10:00:00+00:00",
        minima="feature",
    )
    trexe_git(repo, "checkout", "-q", main_branch)
    prosthese_commit(
        repo,
        {"main.txt": b"main\n"},
        imerominia="2026-10-03T10:00:00+00:00",
        minima="main",
    )
    trexe_git(repo, "merge", "--no-ff", "-m", "merge feature", "feature")

    report = syllexe_git_diafores([repo])

    assert report["synola"]["unique_commits"] == 3
    assert report["synola"]["merge_commits"] == 1
    assert (
        report["semantics"]["merge"]
        == "included against first parent; counted separately"
    )
    assert report["synola"]["additions"] == 3


def test_syllexe_git_diafores_reports_invalid_repos_partial(tmp_path: Path) -> None:
    """Retains readable metrics and marks a bad repository as partial."""
    repo = ftiakse_apothikio(tmp_path / "project")
    prosthese_commit(
        repo,
        {"a.txt": b"a\n"},
        imerominia="2026-10-01T10:00:00+00:00",
        minima="initial",
    )

    report = syllexe_git_diafores([repo, tmp_path / "missing"])

    assert report["katastasi"] == "partial"
    assert report["synola"]["unique_commits"] == 1
    assert report["kalypsi"]["sfalmata"] == 1
    assert report["kalypsi"]["epityxeis"] == 1
    assert report["apothikies"][1]["commits"] is None


def test_syllexe_git_diafores_rejects_invalid_period_and_timezone(
    tmp_path: Path,
) -> None:
    """Rejects malformed reporting filters before executing Git."""
    repo = ftiakse_apothikio(tmp_path / "project")

    try:
        syllexe_git_diafores([repo], apo=date(2026, 10, 2), eos=date(2026, 10, 1))
    except ValueError as sfalma:
        assert "start date" in str(sfalma)
    else:
        raise AssertionError("reversed period was accepted")

    try:
        syllexe_git_diafores([repo], zoni="not/a-timezone")
    except ValueError as sfalma:
        assert "timezone" in str(sfalma)
    else:
        raise AssertionError("invalid timezone was accepted")


def test_syllexe_git_diafores_empty_and_duplicate_inputs_have_explicit_coverage(
    tmp_path: Path,
) -> None:
    """Marks an empty selection missing and ignores repeated canonical paths."""
    missing = syllexe_git_diafores([])

    assert missing["katastasi"] == "missing"
    assert missing["synola"]["unique_commits"] == 0
    assert missing["synola"]["arxeia_tracked_HEAD"] is None
    assert missing["kalypsi"]["simeioseis"] == ["No Git repositories were selected."]

    repo = ftiakse_apothikio(tmp_path / "project")
    prosthese_commit(
        repo,
        {"a.txt": b"a\n"},
        imerominia="2026-10-01T10:00:00+00:00",
        minima="initial",
    )
    repeated = syllexe_git_diafores([repo, repo])

    assert repeated["kalypsi"]["apothikies"] == 1
    assert repeated["synola"]["unique_commits"] == 1


def test_syllexe_git_diafores_caps_history_with_partial_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Caps unusually long histories visibly instead of silently truncating."""
    repo = ftiakse_apothikio(tmp_path / "project")
    for index in range(2):
        prosthese_commit(
            repo,
            {"a.txt": f"line {index}\n".encode()},
            imerominia=f"2026-10-0{index + 1}T10:00:00+00:00",
            minima=f"commit {index}",
        )
    monkeypatch.setattr(git_metrika, "GIT_ORIO_COMMITS", 1)

    report = syllexe_git_diafores([repo])

    assert report["katastasi"] == "partial"
    assert report["synola"]["unique_commits"] == 1
    assert report["kalypsi"]["perikopi"] is True
    assert "capped at 1" in report["kalypsi"]["simeioseis"][0]


def test_syllexe_git_diafores_unknown_date_with_filter_is_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Excludes malformed author dates only under a date filter and marks partial."""
    repo = tmp_path / "synthetic-repo"
    repo.mkdir()

    def fake_git(_repo: Path, *orismata: str) -> bytes:
        """Supplies synthetic log bytes and deterministic HEAD inventory."""
        if orismata[0] == "log":
            return (
                b"commit-id\x1fSynthetic Author\x1fsynthetic@example.invalid"
                b"\x1fnot-an-iso-date\x1f\x00"
            )
        if orismata[0] == "rev-parse":
            return b"tree-id\n"
        return b"file.txt\x00"

    monkeypatch.setattr(git_metrika, "_git", fake_git)

    report = syllexe_git_diafores([repo], apo=date(2026, 10, 1))

    assert report["katastasi"] == "partial"
    assert report["synola"]["unique_commits"] == 0
    assert report["kalypsi"]["agnostes_imerominies"] == 1


def test_git_history_helpers_reject_malformed_records_without_inventing_counts() -> (
    None
):
    """Ignores malformed headers and numstat records while retaining valid binaries."""
    header = (
        b"commit\x1fSynthetic Author\x1fsynthetic@example.invalid"
        b"\x1f2026-10-01T10:00:00+00:00\x1fparent\x00"
    )
    history = (
        b"bad\x1fheader\x00"
        + b"1\t1\tignored.txt\x00"
        + header
        + b"bad-row\x00-\t-\tasset.bin\x00x\t1\tbroken.txt\x00"
    )
    parsed, perikopi = git_metrika._analuse_numstat(history, ZoneInfo("UTC"))

    assert perikopi is False
    assert len(parsed) == 1
    assert parsed[0].allages_arxeion == 1
    assert parsed[0].allages_dyadikon == 1
    assert git_metrika._analuse_commit(b"bad\x1fheader", ZoneInfo("UTC")) is None
    assert git_metrika._imerominia_zonis("2026-10-01T10:00:00", ZoneInfo("UTC")) is None
    assert (
        git_metrika._imerominia_zonis(
            "9999-12-31T23:59:59-14:00", ZoneInfo("Pacific/Kiritimati")
        )
        is None
    )


def test_syllexe_git_diafores_path_resolution_failure_falls_back_to_absolute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Records a path resolution error but can still read a valid repository."""
    repo = ftiakse_apothikio(tmp_path / "project")
    prosthese_commit(
        repo,
        {"a.txt": b"a\n"},
        imerominia="2026-10-01T10:00:00+00:00",
        minima="initial",
    )
    resolve_original = Path.resolve

    def fake_resolve(path: Path, *args: object, **kwargs: object) -> Path:
        """Injects one resolution error without changing subprocess paths."""
        if path == repo:
            raise OSError("synthetic resolution error")
        return resolve_original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", fake_resolve)

    report = syllexe_git_diafores([repo])

    assert report["katastasi"] == "ok"
    assert report["synola"]["unique_commits"] == 1
