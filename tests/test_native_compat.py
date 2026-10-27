"""Synthetic compatibility cases for native Claude/Codex record envelopes."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from devrar.syllogi import _einai_eggrafi_anagnorismeni, syllexe_dedomena


def test_native_duplicate_commands_kai_unknown_timestamp_me_filtro(
    tmp_path: Path,
) -> None:
    """Replay commands δεν διπλομετρώνται και άγνωστο timestamp αποκλείεται."""
    arxeio = tmp_path / "synthetic-native-replay.jsonl"
    entoli = {
        "type": "event_msg",
        "timestamp": "2026-10-26T12:00:00Z",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "CommandExecution",
                "id": "replayed-command",
                "command": ["synthetic"],
                "status": "completed",
                "exit_code": 0,
            },
        },
    }
    _grapse_jsonl(
        arxeio,
        [
            entoli,
            entoli,
            {
                "type": "event_msg",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "FutureSubstantiveItem",
                        "id": "unknown-time",
                    },
                },
            },
        ],
    )
    dedomena = syllexe_dedomena(
        ["codex"],
        {"codex": arxeio},
        [],
        apo=date(2026, 10, 26),
        eos=date(2026, 10, 26),
    )
    native = dedomena["codex_native"]
    assert native["commands"] == 1
    assert native["command_exit_success"] == 1
    assert native["coverage"]["excluded_unknown_timestamps"] == 1
    assert native["coverage"]["unknown_records"] == 0
    assert dedomena["piges"][0]["katastasi"] == "partial"


def test_native_command_ids_einai_scoped_stin_synedria(tmp_path: Path) -> None:
    """Δύο πραγματικά sessions μπορούν να έχουν το ίδιο local command item ID."""
    for synedria in ("session-a", "session-b"):
        _grapse_jsonl(
            tmp_path / f"{synedria}.jsonl",
            [
                {
                    "type": "session_meta",
                    "timestamp": "2026-10-20T10:00:00Z",
                    "payload": {"id": synedria},
                },
                {
                    "type": "event_msg",
                    "timestamp": "2026-10-20T10:00:01Z",
                    "payload": {
                        "type": "item_completed",
                        "item": {
                            "type": "CommandExecution",
                            "id": "local-command-1",
                            "command": ["synthetic"],
                            "status": "completed",
                            "exit_code": 0,
                        },
                    },
                },
            ],
        )
    dedomena = syllexe_dedomena(["codex"], {"codex": tmp_path}, [])
    native = dedomena["codex_native"]
    assert native["commands"] == 2
    assert native["metrika_ergasias"]["events"] == 2
    assert native["usage"]["sums"] is None


def _grapse_jsonl(arxeio: Path, eggrafes: list[dict[str, object]]) -> None:
    """Writes synthetic JSONL only; fixtures never contain private transcripts."""
    arxeio.write_text(
        "".join(json.dumps(eggrafi) + "\n" for eggrafi in eggrafes),
        encoding="utf-8",
    )


def test_claude_replay_eggrafes_anagnorizontai_xoris_metrisi_turns(
    tmp_path: Path,
) -> None:
    """Recognizes request replay records while excluding embedded message data."""
    eggrafes: list[dict[str, object]] = [
        {
            "type": "api-request-shape",
            "shapeHash": "synthetic-shape-hash",
            "shape": {"system": "synthetic context", "tools": []},
            "timestamp": "2026-10-20T10:00:00Z",
        },
        {
            "type": "api-request-blob",
            "hash": "synthetic-message-hash",
            "message": {"role": "user", "content": "synthetic message"},
            "sessionId": "synthetic-session",
        },
        {
            "type": "api-request",
            "id": "synthetic-request",
            "params": {"model": "synthetic-model"},
            "shapeHash": "synthetic-shape-hash",
            "requestDigest": "synthetic-request-digest",
            "timestamp": "2026-10-20T10:00:00Z",
        },
    ]
    arxeio = tmp_path / "synthetic-claude.jsonl"
    _grapse_jsonl(arxeio, eggrafes)

    report = syllexe_dedomena(["claude"], {"claude": arxeio}, [])

    row = next(pigi for pigi in report["piges"] if pigi["onoma"] == "Claude Code")
    assert row["katastasi"] == "ok"
    assert row["sfalmata"] == 0
    assert report["synola"]["minimata_xristi"] == 0
    assert report["synola"]["apantiseis"] == 0


def test_claude_attachment_paramenei_agnosto_xoris_tekmiomeno_schema() -> None:
    """Does not whitelist observed attachment records without a proven schema."""
    eggrafi = {
        "type": "attachment",
        "timestamp": "2026-10-20T10:00:00Z",
        "attachment": {"synthetic": True},
    }

    assert not _einai_eggrafi_anagnorismeni("claude", eggrafi)


def test_codex_structural_eggrafes_anagnorizontai_xoris_turns(
    tmp_path: Path,
) -> None:
    """Accepts source-proven lifecycle/metadata envelopes, not as chat activity."""
    eggrafes: list[dict[str, object]] = [
        {
            "type": "event_msg",
            "payload": {
                "type": "task_started",
                "turn_id": "synthetic-turn",
                "started_at": 1_798_000_000,
            },
            "timestamp": "2026-10-20T10:00:00Z",
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "thread_settings_applied",
                "thread_id": "synthetic-thread",
                "thread_settings": {},
            },
            "timestamp": "2026-10-20T10:00:01Z",
        },
        {
            "type": "world_state",
            "payload": {"full": True, "state": {}},
            "timestamp": "2026-10-20T10:00:02Z",
        },
        {
            "type": "inter_agent_communication_metadata",
            "payload": {"trigger_turn": True},
            "timestamp": "2026-10-20T10:00:03Z",
        },
        {
            "type": "token_usage_record",
            "payload": {
                "response_id": "synthetic-response",
                "session_id": "synthetic-session",
                "thread_id": "synthetic-thread",
                "turn_id": "synthetic-turn",
                "root_turn_id": "synthetic-root",
                "usage": {
                    "input_tokens": 2,
                    "cached_input_tokens": 0,
                    "cache_write_input_tokens": 0,
                    "output_tokens": 1,
                    "reasoning_output_tokens": 0,
                    "total_tokens": 3,
                },
            },
            "timestamp": "2026-10-20T10:00:04Z",
        },
        {
            "type": "compacted",
            "payload": {
                "message": "synthetic summary",
                "window_number": 1,
            },
            "timestamp": "2026-10-20T10:00:05Z",
        },
    ]
    arxeio = tmp_path / "synthetic-codex.jsonl"
    _grapse_jsonl(arxeio, eggrafes)

    report = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    row = next(pigi for pigi in report["piges"] if pigi["onoma"] == "Codex")
    assert row["katastasi"] == "ok"
    assert row["sfalmata"] == 0
    assert report["synola"]["minimata_xristi"] == 0
    assert report["synola"]["apantiseis"] == 0


def test_codex_unknown_substantive_native_type_remains_partial(
    tmp_path: Path,
) -> None:
    """Does not hide future substantive item types as recognized metadata."""
    arxeio = tmp_path / "synthetic-future-codex.jsonl"
    _grapse_jsonl(
        arxeio,
        [
            {
                "type": "event_msg",
                "timestamp": "2026-10-26T12:00:00Z",
                "payload": {
                    "type": "item_completed",
                    "item": {"type": "FutureSubstantiveItem", "id": "future"},
                },
            }
        ],
    )

    report = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    assert report["piges"][0]["katastasi"] == "partial"
    assert report["codex_native"]["coverage"]["unknown_records"] == 1


def test_codex_agent_message_projection_deduplicates_in_either_order(
    tmp_path: Path,
) -> None:
    """One modern assistant projection and its legacy row count once either way."""
    native_row = {
        "type": "event_msg",
        "timestamp": "2026-10-26T12:00:00Z",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "AgentMessage",
                "id": "synthetic-shared-message",
                "content": [{"type": "text", "text": "synthetic shared answer"}],
                "phase": "final_answer",
            },
        },
    }
    legacy_row = {
        "type": "response_item",
        "timestamp": "2026-10-26T12:00:00Z",
        "payload": {
            "type": "message",
            "id": "synthetic-shared-message",
            "role": "assistant",
            "status": "completed",
            "content": [{"type": "output_text", "text": "synthetic shared answer"}],
        },
    }

    results: list[dict[str, object]] = []
    for index, rows in enumerate(((native_row, legacy_row), (legacy_row, native_row))):
        arxeio = tmp_path / f"synthetic-order-{index}.jsonl"
        _grapse_jsonl(arxeio, list(rows))
        results.append(syllexe_dedomena(["codex"], {"codex": arxeio}, []))

    for report in results:
        assert report["synola"]["apantiseis"] == 1
        assert report["codex_native"]["assistant_projections"] == 1
        matching = [
            row
            for row in report["deigmata"]
            if row["keimeno"] == "synthetic shared answer"
        ]
        assert len(matching) == 1


def test_codex_native_counts_usage_dedup_filter_and_channel_boundaries(
    tmp_path: Path,
) -> None:
    """Applies filters, response dedup, safe counters and separate metrics."""

    def usage(
        timestamp: str,
        response_id: str,
        input_tokens: int,
        session_id: str = "synthetic-session",
    ) -> dict[str, object]:
        return {
            "type": "token_usage_record",
            "timestamp": timestamp,
            "payload": {
                "response_id": response_id,
                "session_id": session_id,
                "thread_id": "synthetic-thread",
                "turn_id": "synthetic-turn",
                "root_turn_id": "synthetic-root",
                "usage": {
                    "input_tokens": input_tokens,
                    "cached_input_tokens": 2,
                    "cache_write_input_tokens": 1,
                    "output_tokens": 4,
                    "reasoning_output_tokens": 1,
                    "total_tokens": input_tokens + 4,
                },
                "turn_token_usage": {"total_tokens": 9000},
                "thread_token_usage": {"total_tokens": 19000},
            },
        }

    arxeio = tmp_path / "synthetic-native-metrics.jsonl"
    _grapse_jsonl(
        arxeio,
        [
            {
                "type": "session_meta",
                "timestamp": "2026-10-25T00:00:00Z",
                "payload": {"id": "synthetic-session"},
            },
            {
                "type": "turn_context",
                "timestamp": "2026-10-26T11:59:00Z",
                "payload": {
                    "turn_id": "synthetic-turn",
                    "root_turn_id": "synthetic-root",
                    "model": "synthetic-model",
                },
            },
            {
                "type": "event_msg",
                "timestamp": "2026-10-26T12:00:00Z",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "CommandExecution",
                        "id": "synthetic-command",
                        "command": ["python", "-m", "pytest"],
                        "cwd": "C:/private/workspace",
                        "parsed_cmd": [],
                        "source": "unified_exec_startup",
                        "status": "failed",
                        "aggregated_output": "1 failed in 0.2s",
                        "exit_code": 3,
                    },
                },
            },
            {
                "type": "event_msg",
                "timestamp": "2026-10-26T12:00:01Z",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "FileChange",
                        "id": "synthetic-patch",
                        "changes": {
                            "C:/private/a.py": {
                                "type": "update",
                                "unified_diff": "private",
                            },
                            "C:/private/b.py": {
                                "type": "add",
                                "unified_diff": "private",
                            },
                        },
                        "status": "completed",
                    },
                },
            },
            {
                "type": "event_msg",
                "timestamp": "2026-10-26T12:00:02Z",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "SubAgentActivity",
                        "id": "synthetic-collab-call",
                        "kind": "started",
                        "agent_thread_id": "synthetic-child",
                        "agent_path": "/root/child",
                    },
                },
            },
            {
                "type": "response_item",
                "timestamp": "2026-10-26T12:00:03Z",
                "payload": {
                    "type": "agent_message",
                    "id": "synthetic-agent-message",
                    "author": "/root/child",
                    "recipient": "/root",
                    "content": [
                        {
                            "type": "encrypted_content",
                            "data": "synthetic secret",
                        }
                    ],
                },
            },
            {
                "type": "response_item",
                "timestamp": "2026-10-26T12:00:04Z",
                "payload": {
                    "type": "function_call",
                    "call_id": "synthetic-legacy-call",
                    "name": "exec_command",
                    "arguments": "{}",
                },
            },
            usage("2026-10-26T12:00:05Z", "synthetic-response", 10),
            usage("2026-10-26T12:00:06Z", "synthetic-response", 10),
            usage(
                "2026-10-26T12:00:06Z",
                "synthetic-response",
                5,
                session_id="synthetic-other-session",
            ),
            usage("2026-10-25T12:00:00Z", "out-of-range-response", 99),
            {
                "type": "token_usage_record",
                "timestamp": "2026-10-26T12:00:07Z",
                "payload": {
                    "response_id": "invalid-response",
                    "session_id": "synthetic-session",
                    "thread_id": "synthetic-thread",
                    "turn_id": "synthetic-turn",
                    "root_turn_id": "synthetic-root",
                    "usage": {"input_tokens": True},
                },
            },
            {
                "type": "event_msg",
                "timestamp": "2026-10-26T12:00:08Z",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "CommandExecution",
                        "id": "synthetic-command-without-exit",
                        "command": ["synthetic-command"],
                        "status": "failed",
                    },
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "CommandExecution",
                        "id": "synthetic-command-unknown-time",
                        "command": ["synthetic-command"],
                        "status": "completed",
                    },
                },
            },
            {
                "type": "event_msg",
                "timestamp": "2026-10-25T11:00:00Z",
                "payload": {
                    "type": "item_completed",
                    "item": {"type": "FutureSubstantiveItem", "id": "outside-range"},
                },
            },
        ],
    )

    report = syllexe_dedomena(
        ["codex"],
        {"codex": arxeio},
        [],
        apo=date(2026, 10, 26),
        eos=date(2026, 10, 26),
    )

    native = report["codex_native"]
    assert report["synola"]["kliseis_ergaleion"] == 1
    assert native["commands"] == 2
    assert native["explicit_exits"] == 1
    assert native["patch_records"] == 1
    assert native["changed_files"] == 2
    assert native["collaboration_records"] == 1
    assert native["linked_agent_threads"] == 1
    assert native["command_exit_success"] == 0
    assert native["command_exit_failure"] == 1
    assert native["command_exit_unknown"] == 1
    assert native["inter_agent_messages"] == 1
    assert native["usage"]["known_records"] == 2
    assert native["usage"]["duplicate_records"] == 1
    assert native["usage"]["invalid_records"] == 1
    assert native["usage"]["sums"]["input_tokens"] == 15
    assert native["usage"]["sums"]["recorded_total_tokens"] == 23
    assert native["usage"]["sums"]["recorded_total_tokens"] != 9000
    assert native["coverage"]["excluded_unknown_timestamps"] == 1
    assert native["coverage"]["unknown_records"] == 1
    assert native["metrika_ergasias"]["test_summary"]["failed"] == 1
    assert "synthetic secret" not in repr(native)
    assert "private" not in repr(native)


def test_codex_native_full_stream_exit_counts_survive_episode_cap(
    tmp_path: Path,
) -> None:
    """Full-stream exit counts remain exact when isolated episodes are capped."""
    eggrafes: list[dict[str, object]] = []
    for index in range(501):
        timestamp = f"2026-10-26T00:{index // 60:02}:{index % 60:02}Z"
        eggrafes.extend(
            [
                {
                    "type": "session_meta",
                    "timestamp": timestamp,
                    "payload": {"id": f"synthetic-session-{index}"},
                },
                {
                    "type": "event_msg",
                    "timestamp": timestamp,
                    "payload": {
                        "type": "item_completed",
                        "item": {
                            "type": "CommandExecution",
                            "id": f"synthetic-command-{index}",
                            "command": ["synthetic-command"],
                            "status": "completed",
                            "exit_code": 0,
                        },
                    },
                },
            ]
        )
    arxeio = tmp_path / "synthetic-many-sessions.jsonl"
    _grapse_jsonl(arxeio, eggrafes)

    report = syllexe_dedomena(["codex"], {"codex": arxeio}, [])

    native = report["codex_native"]
    assert native["commands"] == 501
    assert native["command_exit_success"] == 501
    assert native["metrika_ergasias"]["episodes_eligible"] == 501
    assert native["metrika_ergasias"]["episodes_included"] == 500
