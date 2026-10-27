"""Ελέγχει την ασφαλή ισοτιμία των νέων private Markdown summaries."""

import json
from pathlib import Path

from devrar.anafora import apothikefse_anafora
from devrar.deigma import fortose_deigma


def test_markdown_nees_enotites_kai_asfaleia(tmp_path: Path) -> None:
    """Τα outcomes, deltas και supplied imports παραμένουν ρητά και escaped."""
    dedomena = fortose_deigma()
    dedomena["energos_xronos"] = {
        "status": "partial",
        "scope": "Supplied intervals only",
        "active_seconds": 3600,
        "afk_seconds": 600,
    }
    dedomena["kostos"] = {
        "status": "ok",
        "note": "Explicit ledger only",
        "totals": [{"currency": "EUR", "kind": "billed", "amount": "0.123456789"}],
    }
    dedomena["git_diafores"] = {
        "katastasi": "partial",
        "synola": {"additions": 12, "deletions": 3},
        "semantics": {"history": "first-parent"},
    }
    dedomena["epeisodia_ergasias"]["paratiriseis"][0]["tekmiria"] = [
        {
            "pigi": "<script>",
            "locator": "[bad](https://private.invalid)",
            "apospasma": "<iframe>injected</iframe>",
        }
    ]
    selida = apothikefse_anafora(dedomena, tmp_path)
    markdown = (selida.parent / "anafora.md").read_text(encoding="utf-8")
    for titlos in (
        "Work patterns",
        "Observed check outcomes",
        "Report comparison",
        "Supplied active time",
        "Supplied cost ledger",
        "Git change metadata",
    ):
        assert titlos in markdown
    assert "0.123456789" in markdown
    assert "first-parent" in markdown
    assert "not actual PC time" in markdown
    assert "<script>" not in markdown and "<iframe>" not in markdown
    assert "\\[bad\\]" in markdown
    tekmiria = [
        json.loads(grammi)
        for grammi in (selida.parent / "tekmiria.jsonl").read_text("utf-8").splitlines()
    ]
    assert any(grammi.get("katigoria") == "observed_check" for grammi in tekmiria)


def test_markdown_nees_enotites_agnosta_kai_orio(tmp_path: Path) -> None:
    """Ελλιπή και malformed rows έχουν unknown τιμές και εμφανή όρια."""
    dedomena = fortose_deigma()
    dedomena["metrika_ergasias"] = {"ora": [None, {"ora": 9, "prompts": None}]}
    dedomena["epeisodia_ergasias"] = {
        "paratiriseis": [None] + [{"katastasi": "unknown", "tekmiria": [None]}] * 22,
        "proteraiotites": [
            None,
            {"titlos": "Retain a result", "protasi": "Try a check"},
        ],
    }
    dedomena["sygkrisi"] = {"metrika": {"x": None, "tokens": {"delta": None}}}
    dedomena["energos_xronos"] = {"active_seconds": None}
    dedomena["kostos"] = {"totals": [None, {}]}
    dedomena["git_diafores"] = {"synola": None}
    selida = apothikefse_anafora(dedomena, tmp_path)
    markdown = (selida.parent / "anafora.md").read_text(encoding="utf-8")
    assert "Not recorded" in markdown
    assert "20 of 22" in markdown
    assert "Retain a result" in markdown
