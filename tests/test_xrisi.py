from __future__ import annotations

from collections.abc import Mapping

import pytest

from devrar.xrisi import SyllogistisClaudeXrisis, SyllogistisCodexXrisis


def ftiakse_minima(
    tautotita: str | None,
    xrisi: Mapping[str, object],
    modelo: str = "claude-test",
    stop_reason: str | None = "end_turn",
) -> dict[str, object]:
    """Κατασκευάζει συνθετικό Claude API assistant record."""
    minima: dict[str, object] = {"model": modelo, "usage": dict(xrisi)}
    if tautotita is not None:
        minima["id"] = tautotita
    if stop_reason is not None:
        minima["stop_reason"] = stop_reason
    return {"type": "assistant", "message": {"role": "assistant", **minima}}


def test_claude_xrisi_deduparei_id_kai_pairnei_component_maxima() -> None:
    """Copied cumulative records ανά ID παίρνουν maxima, όχι άθροισμα."""
    syllogistis = SyllogistisClaudeXrisis()
    syllogistis.prosthese(
        ftiakse_minima(
            "msg-1",
            {
                "input_tokens": 10,
                "cache_creation_input_tokens": 1,
                "cache_read_input_tokens": 2,
                "output_tokens": 3,
            },
        )
    )
    syllogistis.prosthese(
        ftiakse_minima(
            "msg-1",
            {
                "input_tokens": 12,
                "cache_creation_input_tokens": 1,
                "cache_read_input_tokens": 4,
                "output_tokens": 5,
            },
        )
    )
    syllogistis.prosthese(
        ftiakse_minima(
            "msg-2",
            {
                "input_tokens": 7,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
                "output_tokens": 2,
            },
        )
    )

    apotelesma = syllogistis.synopsi()

    assert apotelesma.tokens == 31
    assert apotelesma.tokens_ana_modelo == {"claude-test": 31}
    assert apotelesma.gnostes_aitiseis == 2
    assert apotelesma.elleipeis_aitiseis == 0
    assert apotelesma.agnosta_records == 0
    assert apotelesma.pliris


@pytest.mark.parametrize(
    "eggrafi",
    [
        ftiakse_minima(
            "msg-bool",
            {
                "input_tokens": True,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
                "output_tokens": 1,
            },
        ),
        ftiakse_minima(
            "msg-negative",
            {
                "input_tokens": -1,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
                "output_tokens": 1,
            },
        ),
        ftiakse_minima(
            "msg-missing-component",
            {"input_tokens": 1, "output_tokens": 1},
        ),
    ],
)
def test_claude_xrisi_aporriptei_invalid_i_ellipi_components(
    eggrafi: dict[str, object],
) -> None:
    """Bool, αρνητικά και ελλιπή usage components δεν γίνονται μετρήσεις."""
    syllogistis = SyllogistisClaudeXrisis()
    syllogistis.prosthese(eggrafi)

    apotelesma = syllogistis.synopsi()

    assert apotelesma.tokens is None
    assert apotelesma.gnostes_aitiseis == 0
    assert apotelesma.elleipeis_aitiseis == 1
    assert not apotelesma.pliris


def test_claude_xrisi_markarei_id_conflict_kai_unknown_id() -> None:
    """Conflicts ή απουσία message ID αφήνουν usage ρητά άγνωστο."""
    syllogistis = SyllogistisClaudeXrisis()
    egkyri_xrisi = {
        "input_tokens": 1,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "output_tokens": 2,
    }
    syllogistis.prosthese(ftiakse_minima("msg-conflict", egkyri_xrisi))
    syllogistis.prosthese(
        ftiakse_minima("msg-conflict", egkyri_xrisi, modelo="claude-other")
    )
    syllogistis.prosthese(ftiakse_minima(None, egkyri_xrisi))

    apotelesma = syllogistis.synopsi()

    assert apotelesma.tokens is None
    assert apotelesma.gnostes_aitiseis == 0
    assert apotelesma.elleipeis_aitiseis == 1
    assert apotelesma.agnosta_records == 1
    assert not apotelesma.pliris


def test_claude_xrisi_aporriptei_stop_reason_conflict() -> None:
    """Αν copied record αλλάζει stop reason, το ID δεν είναι πλήρες."""
    syllogistis = SyllogistisClaudeXrisis()
    xrisi = {
        "input_tokens": 1,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "output_tokens": 2,
    }
    syllogistis.prosthese(ftiakse_minima("msg-stop", xrisi, stop_reason="tool_use"))
    syllogistis.prosthese(ftiakse_minima("msg-stop", xrisi, stop_reason="end_turn"))

    apotelesma = syllogistis.synopsi()

    assert apotelesma.tokens is None
    assert apotelesma.elleipeis_aitiseis == 1
    assert apotelesma.gnostes_aitiseis == 0


def test_claude_xrisi_apaitiei_stop_reason_kai_pliri_pigi() -> None:
    """Usage χωρίς completed stop ή με partial source δεν βεβαιώνεται."""
    syllogistis = SyllogistisClaudeXrisis()
    xrisi = {
        "input_tokens": 3,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "output_tokens": 4,
    }
    syllogistis.prosthese(ftiakse_minima("msg-open", xrisi, stop_reason=None))
    apotelesma = syllogistis.synopsi(pigi_pliris=False)

    assert apotelesma.tokens is None
    assert apotelesma.gnostes_aitiseis == 0
    assert apotelesma.elleipeis_aitiseis == 1
    assert not apotelesma.pliris


def test_claude_xrisi_xoris_records_den_bebaionei_miden() -> None:
    """Κενή πηγή δεν μετατρέπει απουσία usage σε μηδενικό token count."""
    apotelesma = SyllogistisClaudeXrisis().synopsi()

    assert apotelesma.tokens is None
    assert apotelesma.tokens_ana_modelo == {}
    assert apotelesma.gnostes_aitiseis == 0
    assert apotelesma.elleipeis_aitiseis == 0
    assert not apotelesma.pliris


def test_claude_xrisi_aporriptei_non_api_roles_kai_model_xoris_timi() -> None:
    """Αγνοεί non-assistant rows και κρατά ελλιπές το message χωρίς model."""
    syllogistis = SyllogistisClaudeXrisis()
    syllogistis.prosthese({"type": "user", "message": {"role": "user"}})
    syllogistis.prosthese({"type": "assistant", "message": {"role": "user"}})
    syllogistis.prosthese({"type": "assistant"})
    syllogistis.prosthese(
        {
            "type": "assistant",
            "message": {
                "id": "missing-model",
                "role": "assistant",
                "stop_reason": "end_turn",
                "usage": {
                    "input_tokens": 1,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 0,
                    "output_tokens": 1,
                },
            },
        }
    )

    apotelesma = syllogistis.synopsi()

    assert apotelesma.tokens is None
    assert apotelesma.elleipeis_aitiseis == 1
    assert apotelesma.agnosta_records == 2


def test_codex_xrisi_metra_snapshot_records_xoris_na_ta_erminevei() -> None:
    """Μετρά μόνο τα δύο γνωστά Codex token_count wire shapes ως snapshots."""
    syllogistis = SyllogistisCodexXrisis()
    syllogistis.prosthese(
        {"type": "event_msg", "payload": {"type": "token_count", "info": {}}}
    )
    syllogistis.prosthese({"type": "token_count", "payload": {}})
    syllogistis.prosthese({"type": "response_item", "payload": {"type": "message"}})

    assert syllogistis.agnosta_records() == 2
