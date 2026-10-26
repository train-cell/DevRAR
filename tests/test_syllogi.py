from __future__ import annotations

import json
import os
import subprocess
from datetime import date
from pathlib import Path
from typing import Protocol

import pytest
import zstandard

from devrar.syllogi import (
    _analuse_periexomeno_xristi,
    _einai_proelefsi_anthropini,
    _keimeno_keimenou,
    _tautotita_eggrafis,
    syllexe_dedomena,
)


class ElegxosAllagis(Protocol):
    """Ελάχιστο interface του pytest monkeypatch fixture."""

    def setattr(self, target: str, value: object) -> None:
        """Αλλάζει προσωρινά ένα attribute για τη διάρκεια της δοκιμής."""


def grapse_jsonl(arxeio: Path, eggrafes: list[dict[str, object]]) -> None:
    """Γράφει συνθετικά records JSONL για τις δοκιμές συλλογής."""
    arxeio.parent.mkdir(parents=True, exist_ok=True)
    arxeio.write_text(
        "".join(json.dumps(eggrafi) + "\n" for eggrafi in eggrafes), encoding="utf-8"
    )


def test_syllogi_aporriptei_anapoda_periodo_kai_agnosti_zoni() -> None:
    """Απορρίπτει range με ανάποδη σειρά και μη έγκυρο IANA timezone."""
    with pytest.raises(ValueError, match="apo"):
        syllexe_dedomena([], {}, [], date(2026, 10, 2), date(2026, 10, 1))
    with pytest.raises(ValueError, match="IANA timezone"):
        syllexe_dedomena([], {}, [], zoni="Mars/Olympus")


def test_syllogi_dilonei_unsupported_source_partial() -> None:
    """Μη υποστηριζόμενη πηγή εμφανίζεται με partial coverage και σημείωση."""
    apotelesma = syllexe_dedomena(["other"], {}, [])
    assert apotelesma["piges"] == [
        {
            "onoma": "other",
            "katastasi": "partial",
            "arxeia": 0,
            "sfalmata": 1,
            "simeiosi": "Μη υποστηριζόμενη πηγή.",
            "adapter": None,
            "morfes": [],
            "periodos_diathesimon": {"apo": None, "eos": None},
        }
    ]
    assert apotelesma["simeioseis"] == ["Μη υποστηριζόμενη πηγή: other."]


def test_syllogi_provenance_diavazei_periodo_prin_to_date_filter(
    tmp_path: Path,
) -> None:
    """Source period περιλαμβάνει recognized events έξω από το επιλεγμένο range."""
    arxeio = tmp_path / "claude.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "session_meta",
                "timestamp": "2026-10-01T10:00:00Z",
                "sessionId": "s1",
            },
            {
                "type": "user",
                "uuid": "within",
                "sessionId": "s1",
                "timestamp": "2026-10-15T10:00:00Z",
                "message": {"role": "user", "content": "in selected period"},
            },
            {
                "type": "user",
                "uuid": "malformed-time",
                "sessionId": "s1",
                "timestamp": "not-a-timestamp",
                "message": {"role": "user", "content": "unknown period"},
            },
        ],
    )

    apotelesma = syllexe_dedomena(
        ["claude"], {"claude": arxeio}, [], date(2026, 10, 10), date(2026, 10, 20)
    )

    assert apotelesma["synola"]["minimata_xristi"] == 1
    assert apotelesma["piges"][0]["adapter"] == "claude-jsonl-v1"
    assert apotelesma["piges"][0]["morfes"] == ["jsonl"]
    assert apotelesma["piges"][0]["periodos_diathesimon"] == {
        "apo": "2026-10-01",
        "eos": "2026-10-15",
    }


def test_syllogi_dilonei_kena_kai_kakoforismena_jsonl_partial(
    tmp_path: Path,
) -> None:
    """Κενά, μη-object και κακοφορμισμένα records αφήνουν partial κατάσταση."""
    riziko = tmp_path / "claude"
    riziko.mkdir()
    (riziko / "empty.jsonl").write_text("", encoding="utf-8")
    (riziko / "mixed.jsonl").write_text(
        '\n{"type":"session_meta","payload":{"id":"s1"}}\n[]\nnull\n{bad\n',
        encoding="utf-8",
    )
    apotelesma = syllexe_dedomena(["claude"], {"claude": riziko}, [])
    assert apotelesma["piges"][0]["katastasi"] == "partial"
    assert apotelesma["piges"][0]["arxeia"] == 2
    assert apotelesma["piges"][0]["sfalmata"] == 4
    assert apotelesma["piges"][0]["morfes"] == ["jsonl"]
    assert apotelesma["piges"][0]["periodos_diathesimon"] == {
        "apo": None,
        "eos": None,
    }


def test_syllogi_apokodikopoiei_zstd_jsonl_otan_yparxei_decoder(tmp_path: Path) -> None:
    """Διαβάζει πραγματικά συμπιεσμένο synthetic JSONL όταν υπάρχει zstandard."""
    arxeio = tmp_path / "claude.jsonl.zst"
    eggrafi = {
        "type": "user",
        "uuid": "u1",
        "sessionId": "s1",
        "timestamp": "2026-10-25T10:00:00Z",
        "message": {"role": "user", "content": "compressed prompt"},
    }
    dedomena_syz = (json.dumps(eggrafi) + "\n").encode("utf-8")
    arxeio.write_bytes(zstandard.ZstdCompressor().compress(dedomena_syz))
    apotelesma = syllexe_dedomena(["claude"], {"claude": arxeio}, [])
    assert apotelesma["synola"]["minimata_xristi"] == 1
    assert apotelesma["piges"][0]["katastasi"] == "ok"
    assert apotelesma["piges"][0]["adapter"] == "claude-jsonl-v1"
    assert apotelesma["piges"][0]["morfes"] == ["jsonl.zst"]


def test_syllogi_metra_anthropina_prompts_kai_apokleiei_tool_apotelesmata(
    tmp_path: Path,
) -> None:
    """Μετρά ανθρώπινο κείμενο, όχι tool-result payloads ή assistant tool calls."""
    arxeio = tmp_path / "claude" / "session.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "user",
                "uuid": "u1",
                "sessionId": "s1",
                "timestamp": "2026-10-25T22:30:00Z",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "Review this"}],
                },
            },
            {
                "type": "user",
                "uuid": "u2",
                "sessionId": "s1",
                "timestamp": "2026-10-25T22:31:00Z",
                "message": {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "content": "secret tool output"}
                    ],
                },
            },
            {
                "type": "assistant",
                "uuid": "a1",
                "sessionId": "s1",
                "timestamp": "2026-10-25T22:32:00Z",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "tool_use", "id": "call-1", "name": "Read"}],
                },
            },
        ],
    )
    apotelesma = syllexe_dedomena(["claude"], {"claude": arxeio}, [])
    assert apotelesma["synola"]["minimata_xristi"] == 1
    assert apotelesma["synola"]["kliseis_ergaleion"] == 1


def test_syllogi_claude_content_item_kinds_filtrarei_internal_kai_kraetai_user_text(
    tmp_path: Path,
) -> None:
    """Τα Claude content kinds ξεχωρίζουν άνθρωπο από injected context."""
    arxeio = tmp_path / "claude-content-kinds.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "user",
                "uuid": "environment-context",
                "sessionId": "s1",
                "timestamp": "2026-10-25T10:00:00Z",
                "internal_chat_message_metadata_passthrough": json.dumps(
                    {"content_item_kinds": ["environments.environment_context"]}
                ),
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "local environment"}],
                },
            },
            {
                "type": "user",
                "uuid": "open-page",
                "sessionId": "s1",
                "timestamp": "2026-10-25T10:01:00Z",
                "internal_chat_message_metadata_passthrough": json.dumps(
                    {"content_item_kinds": ["additional_content.codex_apps_open_page"]}
                ),
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "opened a page"}],
                },
            },
            {
                "type": "user",
                "uuid": "actual-human",
                "sessionId": "s1",
                "timestamp": "2026-10-25T10:02:00Z",
                "client_authored": False,
                "internal_chat_message_metadata_passthrough": json.dumps(
                    {"content_item_kinds": ["user.text"]}
                ),
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "human request"}],
                },
            },
            {
                "type": "user",
                "uuid": "mixed-context-human",
                "sessionId": "s1",
                "timestamp": "2026-10-25T10:03:00Z",
                "internal_chat_message_metadata_passthrough": json.dumps(
                    {
                        "content_item_kinds": [
                            "environments.environment_context",
                            "user.text",
                        ]
                    }
                ),
                "message": {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "environment secret context"},
                        {"type": "text", "text": "human follow-up"},
                    ],
                },
            },
            {
                "type": "user",
                "uuid": "human-image-only",
                "sessionId": "s1",
                "timestamp": "2026-10-25T10:04:00Z",
                "internal_chat_message_metadata_passthrough": json.dumps(
                    {"content_item_kinds": ["user.image"]}
                ),
                "message": {
                    "role": "user",
                    "content": [{"type": "image", "source": {"data": "synthetic"}}],
                },
            },
        ],
    )

    apotelesma = syllexe_dedomena(["claude"], {"claude": arxeio}, [])

    assert apotelesma["synola"]["minimata_xristi"] == 3
    assert [row["keimeno"] for row in apotelesma["deigmata"]] == [
        "human request",
        "human follow-up",
    ]
    assert "environment secret context" not in str(apotelesma["deigmata"])
    assert any(
        "image-only human prompts are counted without text evidence" in note.casefold()
        for note in apotelesma["simeioseis"]
    )


def test_syllogi_claude_markers_den_exagoun_amfivolo_context() -> None:
    """Malformed markers δεν εξάγουν αμφίβολο context ως ανθρώπινο κείμενο."""
    block_keimenou: dict[str, object] = {"type": "text", "text": "visible text"}
    periexomeno = [block_keimenou]
    assert _analuse_periexomeno_xristi(
        {"internal_chat_message_metadata_passthrough": "{"}, periexomeno
    ) == (None, False, None)
    assert _analuse_periexomeno_xristi(
        {"internal_chat_message_metadata_passthrough": []}, periexomeno
    ) == (None, False, None)
    assert _analuse_periexomeno_xristi(
        {
            "internal_chat_message_metadata_passthrough": {
                "content_item_kinds": "user.text"
            }
        },
        periexomeno,
    ) == ("visible text", False, periexomeno)
    assert _analuse_periexomeno_xristi(
        {"internal_chat_message_metadata_passthrough": {"content_item_kinds": [None]}},
        periexomeno,
    ) == (None, False, None)
    assert _analuse_periexomeno_xristi(
        {
            "internal_chat_message_metadata_passthrough": {
                "content_item_kinds": ["future_vendor.item"]
            }
        },
        periexomeno,
    ) == ("visible text", False, periexomeno)
    assert _analuse_periexomeno_xristi(
        {
            "internal_chat_message_metadata_passthrough": {
                "content_item_kinds": ["user.text"]
            }
        },
        "aplo keimeno",
    ) == ("aplo keimeno", False, "aplo keimeno")
    assert _analuse_periexomeno_xristi(
        {
            "internal_chat_message_metadata_passthrough": {
                "content_item_kinds": ["environments.environment_context", "user.text"]
            }
        },
        "amfivolo mikto keimeno",
    ) == (None, False, None)
    assert _analuse_periexomeno_xristi(
        {
            "internal_chat_message_metadata_passthrough": {
                "content_item_kinds": ["environments.environment_context", "user.text"]
            }
        },
        periexomeno,
    ) == (None, False, None)
    assert _analuse_periexomeno_xristi(
        {
            "internal_chat_message_metadata_passthrough": {
                "content_item_kinds": ["user.text"]
            }
        },
        [block_keimenou, block_keimenou],
    ) == (
        "visible text\nvisible text",
        False,
        [block_keimenou, block_keimenou],
    )


def test_syllogi_codex_native_user_item_filtrarei_context_markers(
    tmp_path: Path,
) -> None:
    """Τα Codex user records τιμούν native markers και κρύβουν injected blocks."""
    arxeio = tmp_path / "codex-content-kinds.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "environment"}],
                    "internal_chat_message_metadata_passthrough": json.dumps(
                        {"content_item_kinds": ["environments.environment_context"]}
                    ),
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "opened page"}],
                    "internal_chat_message_metadata_passthrough": json.dumps(
                        {
                            "content_item_kinds": [
                                "additional_content.codex_apps_open_page"
                            ]
                        }
                    ),
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "client_authored": False,
                    "content": [{"type": "input_text", "text": "human request"}],
                    "internal_chat_message_metadata_passthrough": json.dumps(
                        {"content_item_kinds": ["user.text"]}
                    ),
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "context not exported"},
                        {"type": "input_text", "text": "human follow-up"},
                    ],
                    "internal_chat_message_metadata_passthrough": json.dumps(
                        {
                            "content_item_kinds": [
                                "environments.environment_context",
                                "user.text",
                            ]
                        }
                    ),
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_image", "image_url": "synthetic"}],
                    "internal_chat_message_metadata_passthrough": json.dumps(
                        {"content_item_kinds": ["user.image"]}
                    ),
                },
            },
        ],
    )

    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    assert apotelesma["synola"]["minimata_xristi"] == 3
    assert [row["keimeno"] for row in apotelesma["deigmata"]] == [
        "human request",
        "human follow-up",
    ]
    assert "context not exported" not in str(apotelesma["deigmata"])
    assert any(
        "image-only human prompts are counted without text evidence" in note.casefold()
        for note in apotelesma["simeioseis"]
    )


def test_syllogi_paragei_asfali_evidence_rows(tmp_path: Path) -> None:
    """Συλλέγει ανθρώπινα prompts, text, tool names/results και redacts secrets."""
    arxeio = tmp_path / "claude.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "user",
                "uuid": "prompt-1",
                "sessionId": "session-1",
                "timestamp": "2026-10-25T10:00:00Z",
                "message": {
                    "role": "user",
                    "content": (
                        "Please check Bearer top-secret-token password="
                        + "topsecret" * 100
                        + " github_pat_"
                        + "A" * 35
                    ),
                },
            },
            {
                "type": "assistant",
                "uuid": "assistant-1",
                "sessionId": "session-1",
                "timestamp": "2026-10-25T10:01:00Z",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "I found API_KEY=sk-123456789abcdef " + "x" * 600,
                        },
                        {
                            "type": "tool_use",
                            "id": "tool-1",
                            "name": "Read",
                            "input": {"path": "private.txt", "password": "secret"},
                        },
                    ],
                },
            },
            {
                "type": "user",
                "uuid": "tool-result-1",
                "sessionId": "session-1",
                "timestamp": "2026-10-25T10:02:00Z",
                "message": {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "content": "password=tool-secret"}
                    ],
                },
            },
            {
                "type": "user",
                "uuid": "child-prompt-1",
                "sessionId": "session-1",
                "timestamp": "2026-10-25T10:03:00Z",
                "origin": {"kind": "task"},
                "message": {"role": "user", "content": "Subagent instruction"},
            },
            {
                "type": "user",
                "uuid": "prompt-source-agent",
                "sessionId": "session-1",
                "timestamp": "2026-10-25T10:04:00Z",
                "promptSource": "subagent",
                "turnOrigin": "local_agent",
                "userType": "internal",
                "message": {"role": "user", "content": "Agent instruction"},
            },
        ],
    )

    apotelesma = syllexe_dedomena(["claude"], {"claude": arxeio}, [])
    deigmata = apotelesma["deigmata"]

    assert [row["eidos"] for row in deigmata] == [
        "prompt",
        "response",
        "tool_call",
        "tool_result",
    ]
    assert [row["rolos"] for row in deigmata] == [
        "user",
        "assistant",
        "tool",
        "tool",
    ]
    assert apotelesma["synola"]["minimata_xristi"] == 1
    assert apotelesma["drastiriotita"][0]["prompts"] == 1
    assert "top-secret-token" not in str(deigmata)
    assert "sk-123456789abcdef" not in str(deigmata)
    assert "tool-secret" not in str(deigmata)
    assert "topsecret" not in str(deigmata)
    assert "github_pat_" not in str(deigmata)
    assert "private.txt" not in str(deigmata)
    assert all(len(row["keimeno"]) <= 500 for row in deigmata)
    assert all(row["locator"].startswith("claude.jsonl:") for row in deigmata)
    assert apotelesma["kalypsi_analysi"] == {
        "epilegmena": 4,
        "diathesima": 4,
        "perikopi": False,
    }
    assert any(
        "Claude token usage remains unavailable" in simeiosi
        for simeiosi in apotelesma["simeioseis"]
    )


def test_syllogi_metra_claude_usage_megisto_ana_api_message_id(
    tmp_path: Path,
) -> None:
    """Claude cumulative copies dedupe by API message ID, independent of UUID."""
    arxeio = tmp_path / "claude-usage.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "assistant",
                "uuid": "copy-a",
                "timestamp": "2026-10-25T10:00:00Z",
                "message": {
                    "id": "msg-1",
                    "role": "assistant",
                    "model": "claude-test",
                    "stop_reason": "end_turn",
                    "usage": {
                        "input_tokens": 10,
                        "cache_creation_input_tokens": 1,
                        "cache_read_input_tokens": 2,
                        "output_tokens": 3,
                    },
                    "content": [{"type": "text", "text": "first snapshot"}],
                },
            },
            {
                "type": "assistant",
                "uuid": "copy-b",
                "timestamp": "2026-10-25T10:00:00Z",
                "message": {
                    "id": "msg-1",
                    "role": "assistant",
                    "model": "claude-test",
                    "stop_reason": "end_turn",
                    "usage": {
                        "input_tokens": 12,
                        "cache_creation_input_tokens": 1,
                        "cache_read_input_tokens": 4,
                        "output_tokens": 5,
                    },
                    "content": [{"type": "text", "text": "copied snapshot"}],
                },
            },
        ],
    )

    apotelesma = syllexe_dedomena(["claude"], {"claude": arxeio}, [])

    assert apotelesma["synola"]["apantiseis"] == 2
    assert apotelesma["synola"]["tokens"] == 22
    assert apotelesma["ergaleia"][0]["tokens"] == 22
    assert apotelesma["montela"] == [
        {"onoma": "claude-test", "kliseis": 2, "tokens": 22, "pigi": "claude"}
    ]
    assert apotelesma["kalypsi_tokens"] == {
        "piges": {
            "claude": {
                "gnostes_aitiseis": 1,
                "elleipeis_aitiseis": 0,
                "agnosta_records": 0,
                "methodos": "claude_api_message_usage",
                "pliris": True,
            }
        },
        "pliris": True,
    }


def test_syllogi_claude_usage_missing_and_out_of_range_do_not_become_zero(
    tmp_path: Path,
) -> None:
    """Missing usage is unknown; date filter excludes API messages outside range."""
    arxeio = tmp_path / "claude-usage.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "assistant",
                "uuid": "outside",
                "timestamp": "2026-10-01T10:00:00Z",
                "message": {
                    "id": "outside-id",
                    "role": "assistant",
                    "model": "claude-test",
                    "stop_reason": "end_turn",
                    "usage": {
                        "input_tokens": 90,
                        "cache_creation_input_tokens": 0,
                        "cache_read_input_tokens": 0,
                        "output_tokens": 10,
                    },
                    "content": [{"type": "text", "text": "outside"}],
                },
            },
            {
                "type": "assistant",
                "uuid": "missing-usage",
                "timestamp": "2026-10-15T10:00:00Z",
                "message": {
                    "id": "missing-usage-id",
                    "role": "assistant",
                    "model": "claude-test",
                    "stop_reason": "end_turn",
                    "content": [{"type": "text", "text": "unknown usage"}],
                },
            },
            {
                "type": "assistant",
                "uuid": "unknown-date-usage",
                "message": {
                    "id": "unknown-date-id",
                    "role": "assistant",
                    "model": "claude-test",
                    "stop_reason": "end_turn",
                    "usage": {
                        "input_tokens": 40,
                        "cache_creation_input_tokens": 0,
                        "cache_read_input_tokens": 0,
                        "output_tokens": 4,
                    },
                    "content": [{"type": "text", "text": "unknown date"}],
                },
            },
        ],
    )

    apotelesma = syllexe_dedomena(
        ["claude"],
        {"claude": arxeio},
        [],
        date(2026, 10, 10),
        date(2026, 10, 20),
    )

    assert apotelesma["synola"]["tokens"] is None
    assert apotelesma["kalypsi_tokens"]["piges"]["claude"] == {
        "gnostes_aitiseis": 0,
        "elleipeis_aitiseis": 1,
        "agnosta_records": 0,
        "methodos": "claude_api_message_usage",
        "pliris": False,
    }


def test_syllogi_codex_usage_remains_cumulative_and_unknown(
    tmp_path: Path,
) -> None:
    """Codex cumulative snapshots are counted as records, never as requests."""
    arxeio = tmp_path / "codex-usage.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "timestamp": "2026-10-25T10:00:00Z",
                "type": "event_msg",
                "payload": {"type": "token_count", "info": {}},
            },
            {
                "timestamp": "2026-10-25T10:01:00Z",
                "type": "token_count",
                "payload": {},
            },
        ],
    )

    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    assert apotelesma["synola"]["tokens"] is None
    assert apotelesma["synola"]["apantiseis"] == 0
    assert apotelesma["synola"]["kliseis_ergaleion"] == 0
    assert apotelesma["kalypsi_tokens"]["piges"]["codex"] == {
        "gnostes_aitiseis": None,
        "elleipeis_aitiseis": None,
        "agnosta_records": 2,
        "methodos": "unsupported_cumulative_snapshots",
        "pliris": False,
    }


def test_syllogi_miktes_piges_krata_claude_tokens_alla_den_synolizei(
    tmp_path: Path,
) -> None:
    """Πλήρες Claude usage μένει per-tool γνωστό με επιλεγμένο unknown Codex."""
    claude_arxeio = tmp_path / "claude.jsonl"
    codex_arxeio = tmp_path / "codex.jsonl"
    grapse_jsonl(
        claude_arxeio,
        [
            {
                "type": "assistant",
                "uuid": "claude-assistant",
                "timestamp": "2026-10-25T10:00:00Z",
                "message": {
                    "id": "claude-msg",
                    "role": "assistant",
                    "model": "claude-test",
                    "stop_reason": "end_turn",
                    "usage": {
                        "input_tokens": 2,
                        "cache_creation_input_tokens": 1,
                        "cache_read_input_tokens": 1,
                        "output_tokens": 2,
                    },
                    "content": [{"type": "text", "text": "answer"}],
                },
            }
        ],
    )
    grapse_jsonl(
        codex_arxeio,
        [
            {
                "timestamp": "2026-10-25T10:00:00Z",
                "type": "event_msg",
                "payload": {"type": "token_count", "info": {}},
            }
        ],
    )

    apotelesma = syllexe_dedomena(
        ["claude", "codex"],
        {"claude": claude_arxeio, "codex": codex_arxeio},
        [],
    )

    assert apotelesma["synola"]["tokens"] is None
    assert apotelesma["ergaleia"] == [
        {"onoma": "Claude Code", "synedries": 1, "prompts": 0, "tokens": 6},
        {"onoma": "Codex", "synedries": 0, "prompts": 0, "tokens": None},
    ]
    assert apotelesma["montela"] == [
        {"onoma": "claude-test", "kliseis": 1, "tokens": 6, "pigi": "claude"}
    ]
    assert apotelesma["kalypsi_tokens"]["pliris"] is False


def test_syllogi_paragei_codex_evidence_apo_anagnorismena_payloads(
    tmp_path: Path,
) -> None:
    """Αναγνωρίζει Codex message, tool-call και tool-output χωρίς tool-as-prompt."""
    arxeio = tmp_path / "codex.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "timestamp": "2026-10-25T10:00:00Z",
                "type": "session_meta",
                "payload": {"id": "codex-session"},
            },
            {
                "timestamp": "2026-10-25T10:01:00Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Explain this"}],
                },
            },
            {
                "timestamp": "2026-10-25T10:01:30Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Subagent instruction"}],
                    "origin": {"kind": "task"},
                },
            },
            {
                "timestamp": "2026-10-25T10:02:00Z",
                "type": "event_msg",
                "payload": {"type": "agent_message", "message": "Event response"},
            },
            {
                "timestamp": "2026-10-25T10:02:30Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "A concise answer"}],
                },
            },
            {
                "timestamp": "2026-10-25T10:03:00Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "call_id": "call-1",
                    "name": "shell",
                    "arguments": "do-not-export-secret",
                },
            },
            {
                "timestamp": "2026-10-25T10:04:00Z",
                "id": "tool-output-copy-a",
                "type": "response_item",
                "payload": {
                    "type": "function_call_output",
                    "call_id": "call-1",
                    "output": "Bearer codex-secret-token",
                },
            },
            {
                "timestamp": "2026-10-25T10:04:00Z",
                "id": "tool-output-copy-b",
                "type": "response_item",
                "payload": {
                    "type": "function_call_output",
                    "call_id": "call-1",
                    "output": "Bearer codex-secret-token",
                },
            },
        ],
    )

    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])
    deigmata = apotelesma["deigmata"]

    assert [row["eidos"] for row in deigmata] == [
        "prompt",
        "response",
        "response",
        "tool_call",
        "tool_result",
    ]
    assert [row["keimeno"] for row in deigmata] == [
        "Explain this",
        "Event response",
        "A concise answer",
        "shell",
        "Bearer [REDACTED]",
    ]
    assert apotelesma["synola"]["minimata_xristi"] == 1
    assert all("do-not-export-secret" not in str(row) for row in deigmata)


def test_syllogi_deduparei_codex_reply_channels_me_vas_turn_kai_multiplicity(
    tmp_path: Path,
) -> None:
    """Deduplicates cross-channel replies by turn while preserving canonical repeats."""
    arxeio = tmp_path / "codex-replies.jsonl"
    minima = [
        {
            "timestamp": "2026-10-25T10:00:00Z",
            "type": "session_meta",
            "payload": {"id": "s1"},
        },
        {"type": "turn_context", "payload": {"turn_id": "turn-a", "model": "gpt-test"}},
        {
            "type": "response_item",
            "id": "canonical-a",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "identical reply"}],
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "agent_message",
                "turn_id": "turn-a",
                "message": "identical reply",
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "task_complete",
                "turn_id": "turn-a",
                "message": "identical reply",
            },
        },
        {
            "type": "response_item",
            "id": "canonical-b",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "identical reply"}],
            },
        },
        {
            "type": "response_item",
            "id": "canonical-a",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "identical reply"}],
            },
        },
        {"type": "turn_context", "payload": {"turn_id": "turn-b", "model": "gpt-test"}},
        {
            "type": "response_item",
            "id": "canonical-c",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "identical reply"}],
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "agent_message",
                "turn_id": "turn-b",
                "message": "identical reply",
            },
        },
        {"type": "turn_context", "payload": {"turn_id": "turn-c", "model": "gpt-test"}},
        {
            "type": "event_msg",
            "payload": {"type": "agent_message", "message": "event-only reply"},
        },
        {
            "type": "event_msg",
            "payload": {"type": "task_complete", "message": "event-only reply"},
        },
        {
            "type": "turn_context",
            "payload": {"turn_id": "turn-d", "model": "gpt-test"},
        },
        {
            "type": "response_item",
            "timestamp": "2026-10-25T11:00:00Z",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "timestamp copy"}],
            },
        },
        {
            "type": "response_item",
            "timestamp": "2026-10-25T11:00:00Z",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "timestamp copy"}],
            },
        },
    ]
    grapse_jsonl(arxeio, minima)

    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    assert apotelesma["synola"]["apantiseis"] == 5
    assert apotelesma["montela"] == [
        {"onoma": "gpt-test", "kliseis": 5, "tokens": None, "pigi": "codex"}
    ]
    assert [
        row["keimeno"] for row in apotelesma["deigmata"] if row["eidos"] == "response"
    ] == [
        "identical reply",
        "identical reply",
        "identical reply",
        "event-only reply",
        "timestamp copy",
    ]


def test_syllogi_codex_reply_xoris_turn_linkage_dilonei_ambiguous(
    tmp_path: Path,
) -> None:
    """Identical cross-channel text without turn identity yields unknown replies."""
    arxeio = tmp_path / "codex-ambiguous.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {"type": "session_meta", "payload": {"id": "s1"}},
            {
                "type": "response_item",
                "id": "canonical",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "model": "gpt-test",
                    "content": [{"type": "output_text", "text": "same text"}],
                },
            },
            {
                "type": "event_msg",
                "payload": {"type": "agent_message", "message": "same text"},
            },
        ],
    )

    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    assert apotelesma["synola"]["apantiseis"] is None
    assert apotelesma["piges"][0]["katastasi"] == "partial"
    assert apotelesma["montela"][0]["kliseis"] is None
    assert any(
        "Codex assistant reply attribution is ambiguous" in note
        for note in apotelesma["simeioseis"]
    )


def test_syllogi_record_identity_uses_source_specific_call_ids() -> None:
    """Claude IDs stay raw; Codex output IDs are namespaced from call IDs."""
    assert _tautotita_eggrafis({}, {"call_id": "claude-tool"}, "claude") == (
        "claude-tool"
    )
    assert (
        _tautotita_eggrafis(
            {}, {"type": "event_msg", "call_id": "codex-record"}, "codex"
        )
        == "codex-record"
    )


def test_syllogi_helpers_reject_untrusted_source_markers_and_nontext() -> None:
    """Άγνωστα attribution markers και non-text tool output δεν γίνονται evidence."""
    assert not _einai_proelefsi_anthropini({"origin": "unrecognized"})
    assert not _einai_proelefsi_anthropini({"promptSource": 17})
    assert not _einai_proelefsi_anthropini({"is_subagent": True})
    assert not _einai_proelefsi_anthropini({"payload": {"agentId": "agent-1"}})
    assert _einai_proelefsi_anthropini({"origin": {"kind": "channel"}})
    assert _keimeno_keimenou({"output": "not a text block"}, {"text"}) is None


def test_syllogi_orizei_orio_evidence_kai_metra_ola_ta_candidates(
    tmp_path: Path,
) -> None:
    """Κρατά έως 600 evidence rows αλλά αναφέρει όλα τα eligible candidates."""
    arxeio = tmp_path / "codex.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "timestamp": f"2026-10-25T10:{arithmos // 60:02d}:{arithmos % 60:02d}Z",
                "type": "event_msg",
                "payload": {
                    "type": "user_message",
                    "message": f"prompt-{arithmos}",
                },
            }
            for arithmos in range(601)
        ],
    )

    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    assert len(apotelesma["deigmata"]) == 600
    assert apotelesma["kalypsi_analysi"] == {
        "epilegmena": 600,
        "diathesima": 601,
        "perikopi": True,
    }


def test_syllogi_afairei_diplotypes_eggrafes_kai_metra_rizes_paidia(
    tmp_path: Path,
) -> None:
    """Αποφεύγει διπλές identities και ξεχωρίζει δηλωμένα child sessions."""
    arxeio = tmp_path / "codex.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "timestamp": "2026-10-25T10:00:00Z",
                "type": "session_meta",
                "payload": {"id": "root", "cwd": str(tmp_path)},
            },
            {
                "timestamp": "2026-10-25T10:01:00Z",
                "type": "event_msg",
                "id": "same",
                "payload": {"type": "user_message", "message": "one"},
            },
            {
                "timestamp": "2026-10-25T10:02:00Z",
                "type": "event_msg",
                "id": "same",
                "payload": {"type": "user_message", "message": "duplicate"},
            },
            {
                "timestamp": "2026-10-25T10:03:00Z",
                "type": "session_meta",
                "payload": {
                    "id": "child",
                    "parent_session_id": "root",
                    "cwd": str(tmp_path),
                },
            },
        ],
    )
    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])
    assert apotelesma["synola"]["synedries"] == 1
    assert apotelesma["synola"]["rizikes"] == 1
    assert apotelesma["synola"]["ypopraktores"] == 0
    assert apotelesma["synola"]["minimata_xristi"] == 1


def test_syllogi_afairei_antigrafes_codex_prompts_xoris_record_id(
    tmp_path: Path,
) -> None:
    """Forked rollouts με ίδιο timestamp και prompt δεν μετρούνται διπλά."""
    chronos = "2026-10-25T10:01:00Z"
    grapse_jsonl(
        tmp_path / "fork-a.jsonl",
        [
            {
                "timestamp": chronos,
                "type": "session_meta",
                "payload": {"id": "fork-a"},
            },
            {
                "timestamp": chronos,
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "same inherited prompt"},
            },
        ],
    )
    grapse_jsonl(
        tmp_path / "fork-b.jsonl",
        [
            {
                "timestamp": chronos,
                "type": "session_meta",
                "payload": {"id": "fork-b"},
            },
            {
                "timestamp": chronos,
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "same inherited prompt"}
                    ],
                },
            },
        ],
    )
    apotelesma = syllexe_dedomena(["codex"], {"codex": tmp_path}, [])
    assert apotelesma["synola"]["synedries"] == 1
    assert apotelesma["synola"]["minimata_xristi"] == 1


def test_syllogi_diatirei_idia_prompts_sto_idio_rollout_xoris_ids(
    tmp_path: Path,
) -> None:
    """Identical same-time prompts in one rollout remain separate without record IDs."""
    arxeio = tmp_path / "codex.jsonl"
    chronos = "2026-10-25T10:01:00Z"
    grapse_jsonl(
        arxeio,
        [
            {"timestamp": chronos, "type": "session_meta", "payload": {"id": "s1"}},
            {
                "timestamp": chronos,
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "retry this"},
            },
            {
                "timestamp": chronos,
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "retry this"},
            },
        ],
    )
    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])
    assert apotelesma["synola"]["minimata_xristi"] == 2


def test_syllogi_distinguishei_claude_channel_prompt_apo_synthetic_meta(
    tmp_path: Path,
) -> None:
    """Εξαιρεί synthetic `isMeta`, αλλά μετρά channel prompt ανθρώπου."""
    arxeio = tmp_path / "claude.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "user",
                "uuid": "synthetic",
                "sessionId": "s1",
                "isMeta": True,
                "timestamp": "2026-10-25T10:00:00Z",
                "message": {
                    "role": "user",
                    "content": "Continue from where you left off.",
                },
            },
            {
                "type": "user",
                "uuid": "channel",
                "sessionId": "s1",
                "isMeta": True,
                "origin": {"kind": "channel"},
                "timestamp": "2026-10-25T10:01:00Z",
                "message": {"role": "user", "content": "Human request from channel"},
            },
        ],
    )
    apotelesma = syllexe_dedomena(["claude"], {"claude": arxeio}, [])
    assert apotelesma["synola"]["minimata_xristi"] == 1


def test_syllogi_codex_synolika_token_snapshots_menoun_null(
    tmp_path: Path,
) -> None:
    """Cumulative token snapshots are not summed or exposed as known usage."""
    arxeio = tmp_path / "codex.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "timestamp": "2026-10-25T10:00:00Z",
                "type": "session_meta",
                "payload": {"id": "s1"},
            },
            {
                "timestamp": "2026-10-25T10:01:00Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"total_tokens": 100}},
                },
            },
            {
                "timestamp": "2026-10-25T10:02:00Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"total_tokens": 250}},
                },
            },
        ],
    )
    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])
    assert apotelesma["synola"]["tokens"] is None
    assert apotelesma["ergaleia"][0]["tokens"] is None


def test_syllogi_diavazei_nees_codex_response_items_kai_model(tmp_path: Path) -> None:
    """Υποστηρίζει response_item records και μοντέλο από turn_context."""
    arxeio = tmp_path / "codex.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "timestamp": "2026-10-25T10:00:00Z",
                "type": "session_meta",
                "payload": {"id": "s1"},
            },
            {
                "timestamp": "2026-10-25T10:01:00Z",
                "type": "turn_context",
                "payload": {"model": "gpt-test"},
            },
            {
                "timestamp": "2026-10-25T10:02:00Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Inspect"}],
                },
            },
            {
                "timestamp": "2026-10-25T10:03:00Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "Done"}],
                },
            },
            {
                "timestamp": "2026-10-25T10:04:00Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "call_id": "call-1",
                    "name": "shell",
                },
            },
        ],
    )
    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])
    assert apotelesma["synola"]["minimata_xristi"] == 1
    assert apotelesma["synola"]["apantiseis"] == 1
    assert apotelesma["synola"]["kliseis_ergaleion"] == 1
    assert apotelesma["montela"] == [
        {"onoma": "gpt-test", "kliseis": 2, "tokens": None, "pigi": "codex"}
    ]


def test_syllogi_akolouthei_parallages_eggrafon_codex_kai_claude(
    tmp_path: Path,
) -> None:
    """Καλύπτει παραλλαγές εγγραφών Codex και Claude χωρίς ανθρώπινο κείμενο."""
    diadromi_claude = tmp_path / "claude.jsonl"
    grapse_jsonl(
        diadromi_claude,
        [
            {
                "type": "assistant",
                "uuid": "answer-text",
                "sessionId": "claude-session",
                "timestamp": "2026-10-25T11:00:00Z",
                "message": {"role": "assistant", "content": "Text answer"},
            },
            {
                "type": "assistant",
                "uuid": "answer-blocks",
                "sessionId": "claude-session",
                "timestamp": "2026-10-25T11:01:00Z",
                "message": {
                    "role": "assistant",
                    "content": ["Plain block", 4, {"type": "tool_use", "name": "Read"}],
                },
            },
            {
                "type": "assistant",
                "uuid": "empty-blocks",
                "sessionId": "claude-session",
                "timestamp": "2026-10-25T11:02:00Z",
                "message": {
                    "role": "assistant",
                    "content": [4, {"type": "text", "text": 9}],
                },
            },
            {
                "type": "user",
                "uuid": "non-text-user",
                "sessionId": "claude-session",
                "timestamp": "2026-10-25T11:03:00Z",
                "message": {
                    "role": "user",
                    "content": {"type": "text", "text": "not a block list"},
                },
            },
            {
                "type": "assistant",
                "uuid": "non-text-assistant",
                "sessionId": "claude-session",
                "timestamp": "2026-10-25T11:04:00Z",
                "message": {
                    "role": "assistant",
                    "content": {"type": "text", "text": "not a block list"},
                },
            },
        ],
    )
    diadromi_codex = tmp_path / "codex.jsonl"
    grapse_jsonl(
        diadromi_codex,
        [
            {
                "timestamp": "2026-10-25T12:00:00Z",
                "type": "session_meta",
                "payload": {"id": "codex-session"},
            },
            {
                "timestamp": "2026-10-25T12:01:00Z",
                "type": "event_msg",
                "payload": {"type": "user_message", "message": {"not": "text"}},
            },
            {
                "timestamp": "2026-10-25T12:02:00Z",
                "type": "event_msg",
                "payload": {"type": "agent_message", "message": "Agent answer"},
            },
            {
                "timestamp": "2026-10-25T12:03:00Z",
                "type": "event_msg",
                "payload": {
                    "type": "task_complete",
                    "last_agent_message": "Final answer",
                },
            },
            {
                "timestamp": "2026-10-25T12:04:00Z",
                "type": "event_msg",
                "payload": {"type": "tool_call", "call_id": "call-1"},
            },
            {
                "timestamp": "2026-10-25T12:05:00Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "image", "data": "synthetic"}],
                },
            },
            {
                "timestamp": "2026-10-25T12:06:00Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": ["not-an-object"],
                },
            },
        ],
    )
    apotelesma = syllexe_dedomena(
        ["claude", "codex"],
        {"claude": diadromi_claude, "codex": diadromi_codex},
        [],
    )
    assert apotelesma["synola"]["apantiseis"] == 4
    assert apotelesma["synola"]["kliseis_ergaleion"] == 2
    assert apotelesma["synola"]["minimata_xristi"] == 0


def test_syllogi_periodos_xrisimopoiei_imerologikes_imeres_topikis_zonis(
    tmp_path: Path,
) -> None:
    """Εφαρμόζει inclusive ημερολογιακά όρια στη ζητούμενη ζώνη ώρας."""
    arxeio = tmp_path / "codex.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "timestamp": "2026-10-24T21:30:00Z",
                "type": "session_meta",
                "payload": {"id": "s1"},
            },
            {
                "timestamp": "2026-10-24T21:30:00Z",
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "local Oct 25"},
            },
            {
                "timestamp": "2026-10-25T22:30:00Z",
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "local Oct 26"},
            },
            {
                "timestamp": "2026-10-26T22:30:00Z",
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "local Oct 27"},
            },
        ],
    )
    apotelesma = syllexe_dedomena(
        ["codex"],
        {"codex": arxeio},
        [],
        date(2026, 10, 25),
        date(2026, 10, 26),
        "Europe/Athens",
    )
    assert apotelesma["synola"]["minimata_xristi"] == 2
    assert apotelesma["synola"]["imeres"] == 2


def test_syllogi_paraleipei_kakoforismeni_grammi_kai_dilonei_partial(
    tmp_path: Path,
) -> None:
    """Συνεχίζει μετά από malformed γραμμή και δηλώνει partial coverage."""
    arxeio = tmp_path / "claude.jsonl"
    arxeio.write_text(
        json.dumps(
            {
                "type": "user",
                "uuid": "u1",
                "sessionId": "s1",
                "timestamp": "2026-10-25T10:00:00Z",
                "message": {"role": "user", "content": "Keep this"},
            }
        )
        + "\n{bad json\n",
        encoding="utf-8",
    )
    apotelesma = syllexe_dedomena(["claude"], {"claude": arxeio}, [])
    assert apotelesma["synola"]["minimata_xristi"] == 1
    assert apotelesma["piges"][0]["katastasi"] == "partial"
    assert apotelesma["piges"][0]["sfalmata"] == 1


def test_syllogi_apokleiei_agnosto_chrono_apo_filtered_period_kai_dilonei_partial(
    tmp_path: Path,
) -> None:
    """Εξαιρεί events χωρίς ημερομηνία από το εύρος και καταγράφει partial coverage."""
    arxeio = tmp_path / "codex.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "timestamp": "2026-10-15T10:00:00Z",
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "inside"},
            },
            {
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "No timestamp"},
            },
            {
                "timestamp": "2026-10-16T10:00:00",
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "Naive timestamp"},
            },
            {
                "timestamp": "not-an-iso-date",
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "Malformed timestamp"},
            },
        ],
    )
    apotelesma = syllexe_dedomena(
        ["codex"],
        {"codex": arxeio},
        [],
        date(2026, 10, 1),
        date(2026, 10, 31),
    )
    assert apotelesma["synola"]["minimata_xristi"] == 1
    assert apotelesma["drastiriotita"] == [
        {"imerominia": "2026-10-15", "prompts": 1, "commits": None},
    ]
    assert apotelesma["piges"][0]["katastasi"] == "partial"
    assert any(
        "3 events with unknown timestamps were excluded from filtered totals"
        in simeiosi
        for simeiosi in apotelesma["simeioseis"]
    )


def test_syllogi_agnosto_record_den_kanei_dedup_egkyro_record(tmp_path: Path) -> None:
    """Άγνωστο event εκτός φίλτρου δεν αποκλείει ίδιο in-range ID."""
    arxeio = tmp_path / "claude.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "user",
                "uuid": "shared-event",
                "sessionId": "s1",
                "message": {"role": "user", "content": "unknown timestamp copy"},
            },
            {
                "type": "user",
                "uuid": "shared-event",
                "sessionId": "s1",
                "timestamp": "2026-10-15T10:00:00Z",
                "message": {"role": "user", "content": "in range copy"},
            },
        ],
    )

    apotelesma = syllexe_dedomena(
        ["claude"],
        {"claude": arxeio},
        [],
        date(2026, 10, 1),
        date(2026, 10, 31),
    )

    assert apotelesma["synola"]["minimata_xristi"] == 1
    assert apotelesma["drastiriotita"][0]["prompts"] == 1
    assert apotelesma["piges"][0]["katastasi"] == "partial"


def test_syllogi_diatirei_child_metadata_ektos_filtrou(tmp_path: Path) -> None:
    """Out-of-range session metadata διατηρεί σχέση παιδιού για in-range activity."""
    arxeio = tmp_path / "codex.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "timestamp": "2026-10-01T10:00:00Z",
                "type": "session_meta",
                "payload": {"id": "child", "parentSessionId": "root"},
            },
            {
                "timestamp": "2026-10-15T10:00:00Z",
                "type": "event_msg",
                "payload": {"type": "user_message", "message": "child activity"},
            },
        ],
    )

    apotelesma = syllexe_dedomena(
        ["codex"],
        {"codex": arxeio},
        [],
        date(2026, 10, 10),
        date(2026, 10, 20),
    )

    assert apotelesma["synola"]["synedries"] == 1
    assert apotelesma["synola"]["rizikes"] == 0
    assert apotelesma["synola"]["ypopraktores"] == 1
    assert apotelesma["synola"]["minimata_xristi"] == 0
    assert apotelesma["drastiriotita"][0]["prompts"] == 0


def test_syllogi_timezone_overflow_ginetai_partial(tmp_path: Path) -> None:
    """Timestamp που υπερχειλίζει στη μετατροπή ζώνης εξαιρείται με partial."""
    arxeio = tmp_path / "claude.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "user",
                "uuid": "overflow",
                "sessionId": "s1",
                "timestamp": "0001-01-01T00:00:00+23:00",
                "message": {"role": "user", "content": "overflow timestamp"},
            }
        ],
    )

    apotelesma = syllexe_dedomena(
        ["claude"],
        {"claude": arxeio},
        [],
        date(2026, 10, 10),
        date(2026, 10, 20),
    )

    assert apotelesma["synola"]["minimata_xristi"] == 0
    assert apotelesma["piges"][0]["katastasi"] == "partial"
    assert any(
        "1 events with unknown timestamps" in simeiosi
        for simeiosi in apotelesma["simeioseis"]
    )


def test_syllogi_apousa_pigi_dilonei_missing_xoris_epinoimena_metrics(
    tmp_path: Path,
) -> None:
    """Άγνωστη πηγή δίνει missing coverage και null σε μη διαθέσιμα metrics."""
    apotelesma = syllexe_dedomena(["claude"], {"claude": tmp_path / "absent.jsonl"}, [])
    assert apotelesma["piges"][0]["katastasi"] == "missing"
    assert apotelesma["piges"][0]["adapter"] == "claude-jsonl-v1"
    assert apotelesma["piges"][0]["morfes"] == []
    assert apotelesma["piges"][0]["periodos_diathesimon"] == {
        "apo": None,
        "eos": None,
    }
    assert apotelesma["synola"]["tokens"] is None
    assert apotelesma["synola"]["minimata_xristi"] is None
    assert apotelesma["synola"]["synedries"] is None
    assert apotelesma["synola"]["apantiseis"] is None
    assert apotelesma["synola"]["kliseis_ergaleion"] is None
    assert apotelesma["kalypsi_tokens"]["piges"]["claude"] == {
        "gnostes_aitiseis": None,
        "elleipeis_aitiseis": None,
        "agnosta_records": None,
        "methodos": "source_unavailable",
        "pliris": False,
    }
    assert apotelesma["axiologisi"]["diathesimi"] is False
    assert apotelesma["axiologisi"]["synoliko"] is None


def test_syllogi_xoris_epilegmeni_ai_pigi_afinei_activity_agnosti() -> None:
    """Repo-only ή κενό source selection δεν παρουσιάζει άγνωστη δραστηριότητα ως 0."""
    apotelesma = syllexe_dedomena([], {}, [])

    assert apotelesma["synola"]["synedries"] is None
    assert apotelesma["synola"]["rizikes"] is None
    assert apotelesma["synola"]["ypopraktores"] is None
    assert apotelesma["synola"]["minimata_xristi"] is None
    assert apotelesma["synola"]["apantiseis"] is None
    assert apotelesma["synola"]["kliseis_ergaleion"] is None
    assert apotelesma["synola"]["tokens"] is None
    assert apotelesma["kalypsi_tokens"] == {"piges": {}, "pliris": False}


def test_syllogi_metadata_only_den_emfanizei_drastiria_synedria(
    tmp_path: Path,
) -> None:
    """Codex session metadata χωρίς prompt/response/tool δεν μετριέται ως activity."""
    arxeio = tmp_path / "codex.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "timestamp": "2026-10-25T10:00:00Z",
                "type": "session_meta",
                "payload": {
                    "id": "metadata-only",
                    "source": "vscode",
                    "base_instructions": "private local instructions",
                    "context_window": 160000,
                    "history_mode": "all",
                },
            },
            {
                "timestamp": "2026-10-25T10:00:01Z",
                "type": "queue_operation",
                "sessionId": "metadata-only",
                "operation": "enqueue",
            },
        ],
    )

    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    assert apotelesma["synola"]["synedries"] == 0
    assert apotelesma["synola"]["rizikes"] == 0
    assert apotelesma["synola"]["ypopraktores"] == 0
    assert apotelesma["deigmata"] == []
    assert apotelesma["piges"][0]["katastasi"] == "ok"
    assert apotelesma["piges"][0]["adapter"] == "codex-jsonl-v1"
    assert apotelesma["piges"][0]["morfes"] == ["jsonl"]
    assert apotelesma["piges"][0]["periodos_diathesimon"] == {
        "apo": "2026-10-25",
        "eos": "2026-10-25",
    }


def test_syllogi_agnosti_schema_menei_partial_kai_metrics_unknown(
    tmp_path: Path,
) -> None:
    """Valid JSON unknown schema δεν εμφανίζεται ως πλήρες μηδενικό report."""
    arxeio = tmp_path / "future.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "future_vendor_event",
                "timestamp": "2026-10-25T10:00:00Z",
                "payload": {"opaque": "unrecognized"},
            }
        ],
    )

    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    assert apotelesma["piges"][0]["katastasi"] == "partial"
    assert apotelesma["synola"]["minimata_xristi"] is None
    assert apotelesma["synola"]["synedries"] is None
    assert any("unrecognized" in simeiosi for simeiosi in apotelesma["simeioseis"])


def test_syllogi_agnosti_schema_den_midenizei_anagnorismeno_activity(
    tmp_path: Path,
) -> None:
    """Mixed schema κρατά γνωστό prompt ως lower bound και δηλώνει partial."""
    arxeio = tmp_path / "mixed.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "type": "session_meta",
                "timestamp": "2026-10-25T10:00:00Z",
                "payload": {"id": "s1"},
            },
            {"type": "future_vendor_event", "payload": {"opaque": "x"}},
            {
                "type": "event_msg",
                "timestamp": "2026-10-25T10:01:00Z",
                "payload": {"type": "user_message", "message": "known prompt"},
            },
        ],
    )

    apotelesma = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    assert apotelesma["piges"][0]["katastasi"] == "partial"
    assert apotelesma["synola"]["minimata_xristi"] == 1


def test_syllogi_anagnorizei_benign_claude_metadata(tmp_path: Path) -> None:
    """Claude mode/bridge/queue records δεν γίνονται unsupported events."""
    arxeio = tmp_path / "claude.jsonl"
    eggrafes: list[dict[str, object]] = [
        {"type": "control", "payload": {"mode": "compact"}},
        {"type": "mode", "mode": "normal"},
        {"type": "permission-mode", "mode": "default"},
        {"type": "bridge-session", "sessionId": "s1"},
        {"type": "queue-operation", "operation": "enqueue"},
        {
            "type": "user",
            "uuid": "prompt",
            "sessionId": "s1",
            "timestamp": "2026-10-25T10:00:00Z",
            "message": {"role": "user", "content": "human prompt"},
        },
    ]
    grapse_jsonl(arxeio, eggrafes)

    apotelesma = syllexe_dedomena(["claude"], {"claude": arxeio}, [])

    assert apotelesma["piges"][0]["katastasi"] == "ok"
    assert apotelesma["synola"]["minimata_xristi"] == 1


def test_syllogi_metra_mono_dilomena_git_repositories_kai_afairei_diplotypa(
    tmp_path: Path,
) -> None:
    """Μετρά commits μόνο στα δηλωμένα repos και αφαιρεί κοινά commit IDs."""
    apothikio = tmp_path / "repo"
    apothikio.mkdir()
    subprocess.run(["git", "init", "-q", str(apothikio)], check=True)
    (apothikio / "tracked.txt").write_text("synthetic file\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(apothikio), "add", "tracked.txt"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(apothikio),
            "-c",
            "user.name=Dev",
            "-c",
            "user.email=dev@example.test",
            "commit",
            "-m",
            "first",
        ],
        check=True,
        capture_output=True,
    )
    (apothikio / "tracked.txt").write_text("second revision\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(apothikio), "add", "tracked.txt"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(apothikio),
            "-c",
            "user.name=Dev",
            "-c",
            "user.email=dev@example.test",
            "commit",
            "-m",
            "second",
        ],
        check=True,
        capture_output=True,
    )
    (apothikio / "Δείγμα.txt").write_text("unicode filename\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(apothikio), "add", "Δείγμα.txt"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(apothikio),
            "-c",
            "user.name=Dev",
            "-c",
            "user.email=dev@example.test",
            "commit",
            "-m",
            "third",
        ],
        check=True,
        capture_output=True,
    )
    apotelesma = syllexe_dedomena([], {}, [apothikio, apothikio], author="Dev")
    assert apotelesma["synola"]["commits"] == 3
    assert apotelesma["projects"][0]["commits"] == 3
    assert apotelesma["projects"][0]["arxeia"] == 2
    assert apotelesma["scope_git"] == {"rev": "HEAD", "author": "dev"}
    periodos_git = apotelesma["piges"][0]["periodos_diathesimon"]
    assert apotelesma["piges"][0]["adapter"] == "git-head-v1"
    assert apotelesma["piges"][0]["morfes"] == ["git"]
    assert periodos_git["apo"] is not None
    assert periodos_git["eos"] is not None

    apotelesma_me_filtro_grafea = syllexe_dedomena(
        [], {}, [apothikio], author="not-the-author"
    )
    assert apotelesma_me_filtro_grafea["synola"]["commits"] == 0
    assert apotelesma_me_filtro_grafea["projects"][0]["arxeia"] == 2

    apotelesma_me_filtro_imerominias = syllexe_dedomena(
        [],
        {},
        [apothikio],
        apo=date(2100, 1, 1),
        author="Dev",
    )
    assert apotelesma_me_filtro_imerominias["synola"]["commits"] == 0
    assert apotelesma_me_filtro_imerominias["projects"][0]["arxeia"] == 2
    assert (
        apotelesma_me_filtro_imerominias["piges"][0]["periodos_diathesimon"]
        == periodos_git
    )


def test_syllogi_git_shared_commit_metra_drastiriotita_mono_mia_fora(
    tmp_path: Path,
) -> None:
    """Ίδιο commit σε δύο δηλωμένα repos μετρά μία φορά και στην ημερήσια σειρά."""
    proto = tmp_path / "proto"
    antigrafo = tmp_path / "antigrafo"
    proto.mkdir()
    subprocess.run(["git", "init", "-q", str(proto)], check=True)
    (proto / "tracked.txt").write_text("synthetic\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(proto), "add", "tracked.txt"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(proto),
            "-c",
            "user.name=Dev",
            "-c",
            "user.email=dev@example.test",
            "commit",
            "-m",
            "shared",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "clone", "-q", str(proto), str(antigrafo)],
        check=True,
        capture_output=True,
    )

    apotelesma = syllexe_dedomena([], {}, [proto, antigrafo])

    assert apotelesma["synola"]["commits"] == 1
    assert apotelesma["synola"]["synedries"] is None
    assert apotelesma["drastiriotita"][0]["commits"] == 1


@pytest.mark.skipif(
    os.name == "nt", reason="Το Windows filesystem δεν διακρίνει case-only paths."
)
def test_syllogi_git_case_distinct_repositories_remain_separate(
    tmp_path: Path,
) -> None:
    """Δύο repos με paths που διαφέρουν μόνο σε case διαβάζονται ξεχωριστά."""
    mikra = tmp_path / "repo"
    kefalaia = tmp_path / "Repo"

    for apothikio, arxeio in ((mikra, "small.txt"), (kefalaia, "large.txt")):
        apothikio.mkdir()
        subprocess.run(["git", "init", "-q", str(apothikio)], check=True)
        (apothikio / arxeio).write_text(f"{arxeio}\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(apothikio), "add", arxeio], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(apothikio),
                "-c",
                "user.name=Dev",
                "-c",
                "user.email=dev@example.test",
                "commit",
                "-m",
                arxeio,
            ],
            check=True,
            capture_output=True,
        )

    apotelesma = syllexe_dedomena([], {}, [mikra, kefalaia])

    assert apotelesma["synola"]["commits"] == 2
    assert [ergasia["commits"] for ergasia in apotelesma["projects"]] == [1, 1]


def test_syllogi_git_repository_xoris_git_markarei_partial(tmp_path: Path) -> None:
    """Unreadable repository κρατά counts unknown και partial coverage."""
    apothikio = tmp_path / "not-a-repository"
    apothikio.mkdir()
    apotelesma = syllexe_dedomena([], {}, [apothikio])
    assert apotelesma["synola"]["commits"] is None
    assert apotelesma["projects"][0]["commits"] is None
    assert apotelesma["projects"][0]["arxeia"] is None
    assert apotelesma["scope_git"] == {"rev": "HEAD", "author": None}
    assert apotelesma["piges"][0]["katastasi"] == "partial"
    assert apotelesma["piges"][0]["sfalmata"] == 1
    assert apotelesma["piges"][0]["adapter"] == "git-head-v1"
    assert apotelesma["piges"][0]["morfes"] == ["git"]
    assert apotelesma["piges"][0]["periodos_diathesimon"] == {
        "apo": None,
        "eos": None,
    }
    assert apotelesma["simeioseis"] == ["Git: 1 repositories δεν ήταν αναγνώσιμα."]


def test_syllogi_git_malformatted_header_is_skipped_safely(
    tmp_path: Path,
    monkeypatch: ElegxosAllagis,
) -> None:
    """Git header χωρίς όλα τα metadata fields δεν δημιουργεί commit."""
    apothikio = tmp_path / "synthetic-repository"
    apothikio.mkdir()

    def ftiakse_git_apotelesma(
        entoli: list[str],
        check: bool,
        capture_output: bool,
        text: bool,
        encoding: str,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            entoli,
            0,
            stdout="incomplete\x1fauthor\n",
            stderr="",
        )

    monkeypatch.setattr("devrar.syllogi.subprocess.run", ftiakse_git_apotelesma)
    apotelesma = syllexe_dedomena([], {}, [apothikio])
    assert apotelesma["synola"]["commits"] == 0
    assert apotelesma["piges"][0]["katastasi"] == "ok"


def test_syllogi_zst_xoris_decoder_dilonei_partial(
    tmp_path: Path, monkeypatch: ElegxosAllagis
) -> None:
    """Αρχείο zstd παραμένει partial όταν ο optional decoder λείπει."""
    arxeio = tmp_path / "claude.jsonl.zst"
    arxeio.write_bytes(b"synthetic")
    monkeypatch.setattr("devrar.syllogi.ZSTANDARD_DIATHESIMO", False)
    apotelesma = syllexe_dedomena(["claude"], {"claude": arxeio}, [])
    assert apotelesma["piges"][0]["katastasi"] == "partial"
    assert apotelesma["piges"][0]["sfalmata"] == 1
