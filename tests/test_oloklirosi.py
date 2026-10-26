"""Verify real CLI collection, assessment and safe artifacts as one journey."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from devrar.cli import kyria


def test_cli_elliniki_diadromi_me_periorismeni_kodikopoiisi(tmp_path: Path) -> None:
    """Redirected Windows output must not fail after writing a Greek report path."""
    exodos = tmp_path / "αναφορά"
    perivallon = dict(os.environ, PYTHONIOENCODING="cp1252")
    apotelesma = subprocess.run(
        [sys.executable, "-m", "devrar", "wrap", "--demo", "--output", str(exodos)],
        capture_output=True,
        env=perivallon,
        check=False,
    )
    assert apotelesma.returncode == 0, apotelesma.stderr
    assert len(list(exodos.glob("run-*/index.html"))) == 1
    assert b"Report created:" in apotelesma.stdout


def test_idiotika_reports_aginountai_apo_to_git(tmp_path: Path) -> None:
    """A custom output inside another repository must stay private by default."""
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    exodos = tmp_path / "custom-reports"
    assert kyria(["wrap", "--demo", "--output", str(exodos)]) == 0
    index = next(exodos.glob("run-*/index.html"))
    elegxos = subprocess.run(
        ["git", "-C", str(tmp_path), "check-ignore", "-q", str(index)],
        check=False,
        capture_output=True,
    )
    assert elegxos.returncode == 0
    katastasi = subprocess.run(
        ["git", "-C", str(tmp_path), "status", "--porcelain", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert katastasi.stdout == ""


def test_pragmatiki_diadromi_cli_me_synthetiki_pigi(tmp_path: Path) -> None:
    """Supported history yields cited observations without rewriting its source."""
    pigi = tmp_path / "synthetic-history.jsonl"
    eggrafes = [
        {
            "type": "user",
            "uuid": f"prompt-{deiktis}",
            "sessionId": f"session-{deiktis}",
            "timestamp": f"2026-10-{12 + deiktis}T12:00:00Z",
            "message": {
                "role": "user",
                "content": "Define acceptance criteria. Reproduce the bug from logs, "
                "then run pytest and write a handoff.",
            },
        }
        for deiktis in range(3)
    ]
    pigi.write_text("\n".join(json.dumps(grammi) for grammi in eggrafes), "utf-8")
    prin = hashlib.sha256(pigi.read_bytes()).hexdigest()
    exodos = tmp_path / "reports"
    apotelesma = kyria(
        [
            "wrap",
            "--claude-path",
            str(pigi),
            "--since",
            "2026-10-12",
            "--until",
            "2026-10-15",
            "--output",
            str(exodos),
        ]
    )
    assert apotelesma == 0
    assert hashlib.sha256(pigi.read_bytes()).hexdigest() == prin
    arxeio = next(exodos.glob("run-*/apotelesmata.json"))
    dedomena = json.loads(arxeio.read_text(encoding="utf-8"))
    assert dedomena["synola"]["minimata_xristi"] == 3
    assert len(dedomena["axiologisi"]["diastaseis"]) == 5
    assert dedomena["axiologisi"]["synoliko"] is None
    assert dedomena["analysi"]["methodos"] == "rules"
    assert dedomena["kalypsi_analysi"]["epilegmena"] == 3
    assert any(eyrima["tekmiria"] for eyrima in dedomena["eyrimata"])
    tekmiria = (arxeio.parent / "tekmiria.jsonl").read_text(encoding="utf-8")
    assert pigi.name in tekmiria
    assert "acceptance criteria" in tekmiria
    share = (arxeio.parent / "share/scorecard.svg").read_text(encoding="utf-8")
    assert pigi.name not in share
    assert "acceptance criteria" not in share
