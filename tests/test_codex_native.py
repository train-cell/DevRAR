"""Ελέγχει αποκωδικοποίηση Codex native με πλήρως συνθετικές εγγραφές."""

from __future__ import annotations

from devrar.codex_native import anagnorise_native


def test_agent_message_diatirei_id_phase_kai_legacy_projection() -> None:
    """Χαρτογραφεί assistant text item και το ίδιο legacy message ID."""
    eggrafi = {
        "type": "event_msg",
        "timestamp": "2026-10-26T12:00:00Z",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "AgentMessage",
                "id": "synthetic-message",
                "content": [{"type": "text", "text": "synthetic reply"}],
                "phase": "final_answer",
            },
        },
    }

    apotelesma = anagnorise_native(eggrafi)

    assert apotelesma is not None
    assert apotelesma.katigoria == "assistant"
    assert apotelesma.tautotita == "synthetic-message"
    assert apotelesma.chronos == "2026-10-26T12:00:00Z"
    assert apotelesma.rolos == "assistant"
    assert apotelesma.fasi == "final_answer"
    assert apotelesma.provoli_assistant is not None
    assert apotelesma.provoli_assistant.tautotita == apotelesma.tautotita
    assert apotelesma.provoli_assistant.keimeno == "synthetic reply"


def test_command_execution_diatirei_actual_output_exit_kai_safe_summary() -> None:
    """Κρατά output/recorded exit χωρίς να επιστρέφει command ή cwd paths."""
    eggrafi = {
        "type": "event_msg",
        "timestamp": "2026-10-26T12:00:01Z",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "CommandExecution",
                "id": "synthetic-command-id",
                "command": ["python", "-m", "pytest"],
                "cwd": "C:/private/workspace",
                "parsed_cmd": [],
                "source": "unified_exec_startup",
                "status": "failed",
                "aggregated_output": "synthetic test failure",
                "exit_code": 7,
                "duration": {"secs": 1, "nanos": 0},
            },
        },
    }

    apotelesma = anagnorise_native(eggrafi)

    assert apotelesma is not None
    assert apotelesma.katigoria == "command"
    assert apotelesma.tautotita == "synthetic-command-id"
    assert apotelesma.exodos_entolis == "synthetic test failure"
    assert apotelesma.kodikos_exodou == 7
    assert apotelesma.entoli == ("python", "-m", "pytest")
    assert apotelesma.provoli_assistant is None
    assert apotelesma.synopsi == {
        "status": "failed",
        "command_count": 3,
        "exit_code_recorded": True,
    }
    assert "cwd" not in apotelesma.synopsi
    assert "command" not in apotelesma.synopsi


def test_command_execution_missing_exit_does_not_infer_failure_code() -> None:
    """Status failure χωρίς exit code διατηρεί unknown recorded exit."""
    eggrafi = {
        "type": "event_msg",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "CommandExecution",
                "id": "synthetic-command-id",
                "command": ["synthetic-tool"],
                "status": "failed",
                "aggregated_output": "synthetic output",
            },
        },
    }

    apotelesma = anagnorise_native(eggrafi)

    assert apotelesma is not None
    assert apotelesma.kodikos_exodou is None
    assert apotelesma.synopsi["exit_code_recorded"] is False


def test_file_change_epistrefei_mono_asfali_structural_summary() -> None:
    """Μετρά file changes χωρίς paths, patches ή recorded diff text."""
    eggrafi = {
        "type": "event_msg",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "FileChange",
                "id": "synthetic-file-change",
                "changes": {
                    "C:/private/a.py": {"type": "update", "diff": "private diff"},
                    "C:/private/b.py": {"type": "add", "diff": "other diff"},
                },
                "status": "completed",
                "stdout": "private stdout",
                "stderr": "private stderr",
            },
        },
    }

    apotelesma = anagnorise_native(eggrafi)

    assert apotelesma is not None
    assert apotelesma.katigoria == "file_change"
    assert apotelesma.synopsi == {"status": "completed", "change_count": 2}
    assert apotelesma.exodos_entolis is None
    assert "private" not in repr(apotelesma)


def test_subagent_activity_krata_child_identity_kai_call_id() -> None:
    """Διατηρεί collaboration call identity χωριστά από το child thread ID."""
    eggrafi = {
        "type": "event_msg",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "SubAgentActivity",
                "id": "synthetic-collaboration-call",
                "kind": "interacted",
                "agent_thread_id": "synthetic-child-thread",
                "agent_path": "/root/child",
                "model": "synthetic-model",
                "reasoning_effort": "high",
            },
        },
    }

    apotelesma = anagnorise_native(eggrafi)

    assert apotelesma is not None
    assert apotelesma.katigoria == "collaboration"
    assert apotelesma.tautotita == "synthetic-collaboration-call"
    assert apotelesma.synopsi == {
        "kind": "interacted",
        "agent_thread_id": "synthetic-child-thread",
    }
    assert apotelesma.nima_id is None
    assert "agent_path" not in apotelesma.synopsi


def test_inter_agent_message_never_returns_encrypted_or_plain_body() -> None:
    """Τα agent-message envelopes κρατούν attribution και παραλείπουν body."""
    eggrafi = {
        "type": "response_item",
        "timestamp": "2026-10-26T12:00:02Z",
        "payload": {
            "type": "agent_message",
            "id": "synthetic-inter-agent-id",
            "author": "/root/child",
            "recipient": "/root",
            "content": [
                {"type": "input_text", "text": "synthetic private message"},
                {"type": "encrypted_content", "data": "synthetic ciphertext"},
            ],
        },
    }

    apotelesma = anagnorise_native(eggrafi)

    assert apotelesma is not None
    assert apotelesma.katigoria == "inter_agent"
    assert apotelesma.tautotita == "synthetic-inter-agent-id"
    assert apotelesma.synopsi == {
        "author": "/root/child",
        "recipient": "/root",
    }
    assert apotelesma.provoli_assistant is None
    assert "private message" not in repr(apotelesma)
    assert "ciphertext" not in repr(apotelesma)


def test_usage_diatires_mono_per_request_counters_kai_ids() -> None:
    """Κρατά request usage και cumulative snapshots χωριστά, χωρίς άθροιση."""
    eggrafi = {
        "type": "token_usage_record",
        "timestamp": "2026-10-26T12:00:03Z",
        "payload": {
            "response_id": "synthetic-response",
            "session_id": "synthetic-session",
            "thread_id": "synthetic-thread",
            "turn_id": "synthetic-turn",
            "root_turn_id": "synthetic-root-turn",
            "usage": {
                "input_tokens": 11,
                "cached_input_tokens": 3,
                "cache_write_input_tokens": 2,
                "output_tokens": 7,
                "reasoning_output_tokens": 1,
                "total_tokens": 18,
            },
            "turn_token_usage": {"input_tokens": 1100, "total_tokens": 1700},
            "thread_token_usage": {"input_tokens": 2100, "total_tokens": 2700},
        },
    }

    apotelesma = anagnorise_native(eggrafi)

    assert apotelesma is not None
    assert apotelesma.katigoria == "usage"
    assert apotelesma.xrisi is not None
    assert apotelesma.xrisi.apantisi_id == "synthetic-response"
    assert apotelesma.xrisi.synedria_id == "synthetic-session"
    assert apotelesma.xrisi.strofi_id == "synthetic-turn"
    assert apotelesma.xrisi.riziki_strofi_id == "synthetic-root-turn"
    assert apotelesma.xrisi.nima_id == "synthetic-thread"
    assert apotelesma.xrisi.eisagomena_tokens == 11
    assert apotelesma.xrisi.apothikevmena_eisagomena_tokens == 3
    assert apotelesma.xrisi.grammena_cache_tokens == 2
    assert apotelesma.xrisi.paragomena_tokens == 7
    assert apotelesma.xrisi.reasoning_paragomena_tokens == 1
    assert apotelesma.xrisi.recorded_synolika_tokens == 18
    assert "turn_token_usage" not in repr(apotelesma)
    assert "thread_token_usage" not in repr(apotelesma)


def test_invalid_usage_rejects_bool_negative_missing_and_bad_ids() -> None:
    """Δεν αποδέχεται counters που θα παρήγαγαν αμφίβολη χρέωση/διπλομέτρηση."""
    base_usage: dict[str, object] = {
        "input_tokens": 1,
        "cached_input_tokens": 0,
        "cache_write_input_tokens": 0,
        "output_tokens": 1,
        "reasoning_output_tokens": 0,
        "total_tokens": 2,
    }
    base_payload: dict[str, object] = {
        "response_id": "synthetic-response",
        "session_id": "synthetic-session",
        "thread_id": "synthetic-thread",
        "turn_id": "synthetic-turn",
        "root_turn_id": "synthetic-root-turn",
        "usage": base_usage,
    }

    for key, value in (
        ("input_tokens", True),
        ("output_tokens", -1),
        ("total_tokens", None),
    ):
        eggrafi: dict[str, object] = {
            "type": "token_usage_record",
            "payload": {
                **base_payload,
                "usage": {**base_usage, key: value},
            },
        }
        assert anagnorise_native(eggrafi) is None

    bad_id_eggrafi: dict[str, object] = {
        "type": "token_usage_record",
        "payload": {**base_payload, "response_id": ""},
    }
    assert anagnorise_native(bad_id_eggrafi) is None


def test_metadata_types_recognized_without_returning_private_payload() -> None:
    """Recognizes supported metadata subtypes without exposing reasoning data."""
    for subtype in ("Reasoning", "ContextCompaction"):
        eggrafi = {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {"type": subtype, "id": f"synthetic-{subtype}"},
            },
        }

        apotelesma = anagnorise_native(eggrafi)

        assert apotelesma is not None
        assert apotelesma.katigoria == "metadata"
        assert apotelesma.synopsi == {"item_type": subtype}


def test_unknown_or_malformed_substantive_records_remain_unrecognized() -> None:
    """Keeps unknown native subtypes and malformed known fields outside coverage."""
    eggrafes: list[dict[str, object]] = [
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {"type": "FutureSubstantiveItem", "id": "synthetic"},
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {
                    "type": "AgentMessage",
                    "id": "synthetic",
                    "content": [{"type": "future_text", "text": "ignored"}],
                },
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {
                    "type": "CommandExecution",
                    "id": "synthetic",
                    "command": "not-a-list",
                    "status": "failed",
                    "exit_code": True,
                },
            },
        },
        {"type": "token_usage_record", "payload": {"usage": {}}},
        {"type": "response_item", "payload": {"type": "agent_message"}},
        {"type": "event_msg", "payload": {"type": "item_completed"}},
        {"type": "event_msg", "payload": {"type": "item_completed", "item": []}},
        {"type": "other_record", "payload": {}},
        {"type": "event_msg", "payload": {"type": "task_started"}},
        {"type": "response_item", "payload": {"type": "message"}},
        {"type": "token_usage_record", "payload": []},
        {"type": "event_msg", "payload": []},
        {
            "type": "event_msg",
            "payload": {"type": "item_completed", "item": {"type": "AgentMessage"}},
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {"type": "AgentMessage", "id": "synthetic", "content": "bad"},
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {
                    "type": "AgentMessage",
                    "id": "synthetic",
                    "content": [],
                    "phase": 3,
                },
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {
                    "type": "AgentMessage",
                    "id": "synthetic",
                    "content": [{"type": "text", "text": 1}],
                },
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {
                    "type": "CommandExecution",
                    "id": "synthetic",
                    "command": ["synthetic"],
                    "status": "failed",
                    "aggregated_output": [],
                },
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {
                    "type": "FileChange",
                    "id": "synthetic",
                    "changes": {"not-a-path": "not-a-change-object"},
                },
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {
                    "type": "SubAgentActivity",
                    "id": "synthetic",
                    "kind": "unknown-kind",
                    "agent_thread_id": "synthetic-child",
                    "agent_path": "synthetic-agent-path",
                },
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {"type": "Reasoning", "id": ""},
            },
        },
        {
            "type": "response_item",
            "payload": {
                "type": "agent_message",
                "id": "synthetic",
                "author": "synthetic-author",
                "recipient": "synthetic-recipient",
                "content": "not-a-list",
            },
        },
    ]

    assert [anagnorise_native(eggrafi) for eggrafi in eggrafes] == [None] * len(
        eggrafes
    )


def test_invalid_timestamp_and_optional_metadata_do_not_become_private_fields() -> None:
    """Timestamp errors stay absent and metadata decoder accepts only stable IDs."""
    eggrafi = {
        "type": "event_msg",
        "timestamp": "2026-10-26T12:00:00",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "AgentMessage",
                "id": "synthetic-message",
                "content": [],
            },
        },
    }

    apotelesma = anagnorise_native(eggrafi)

    assert apotelesma is not None
    assert apotelesma.chronos is None
    assert apotelesma.fasi is None
    assert apotelesma.provoli_assistant is not None
    assert apotelesma.provoli_assistant.fasi is None
    assert anagnorise_native({**eggrafi, "timestamp": 123}) is not None
    assert anagnorise_native(
        {**eggrafi, "timestamp": "not-a-date"}
    ) is not None
