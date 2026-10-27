"""Συνθετικές δοκιμές για νέους readers χωρίς πρόσβαση σε προσωπικά histories."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from devrar import piges
from devrar.piges import diavase_pigi
from devrar.syndesi import syllexe_pliri


def grapse_jsonl(arxeio: Path, eggrafes: list[dict[str, object]]) -> None:
    """Γράφει συνθετικές γραμμές JSONL σε προσωρινό αρχείο."""
    arxeio.write_text(
        "".join(json.dumps(eggrafi) + "\n" for eggrafi in eggrafes),
        encoding="utf-8",
    )


def test_opencode_minimata_parts_call_result_kai_goneas(tmp_path: Path) -> None:
    """Ένα multipart input είναι ένα prompt, με χωριστά tool call/result."""
    arxeio = tmp_path / "opencode.db"
    with sqlite3.connect(arxeio) as syndesi:
        syndesi.executescript(
            "CREATE TABLE session (id TEXT, parent_id TEXT);"
            "CREATE TABLE message (id TEXT, session_id TEXT, "
            "time_created INTEGER, data TEXT);"
            "CREATE TABLE part (id TEXT, message_id TEXT, session_id TEXT, "
            "time_created INTEGER, data TEXT);"
        )
        syndesi.execute("INSERT INTO session VALUES ('s1', NULL)")
        for tautotita, fortio in (
            ("u1", {"role": "user"}),
            ("a1", {"role": "assistant", "parentID": "u1"}),
        ):
            syndesi.execute(
                "INSERT INTO message VALUES (?, 's1', ?, ?)",
                (tautotita, 1792490400000, json.dumps(fortio)),
            )
        for tautotita, minima, fortio in (
            ("p1", "u1", {"type": "text", "text": "First fragment"}),
            ("p2", "u1", {"type": "text", "text": "Second fragment"}),
            (
                "p3",
                "u1",
                {"type": "text", "text": "Injected context", "synthetic": True},
            ),
            ("p4", "a1", {"type": "text", "text": "Checking."}),
            (
                "p5",
                "a1",
                {
                    "type": "tool",
                    "tool": "bash",
                    "callID": "c1",
                    "state": {
                        "status": "completed",
                        "input": {"command": "synthetic"},
                        "output": "=== 2 passed in 0.1s ===",
                        "metadata": {"exit": 0},
                    },
                },
            ),
        ):
            syndesi.execute(
                "INSERT INTO part VALUES (?, ?, 's1', ?, ?)",
                (tautotita, minima, 1792490400000, json.dumps(fortio)),
            )
    dedomena = syllexe_pliri(["opencode"], {"opencode": arxeio}, [])
    assert dedomena["synola"]["minimata_xristi"] == 1
    assert dedomena["synola"]["apantiseis"] == 1
    assert dedomena["synola"]["kliseis_ergaleion"] == 1
    assert dedomena["synola"]["ypopraktores"] == 0
    keimeno = " ".join(grammi["keimeno"] for grammi in dedomena["deigmata"])
    assert "First fragment" in keimeno and "Second fragment" in keimeno
    assert "Injected context" not in keimeno
    epeisodio = dedomena["metrika_ergasias"]["epeisodia"][0]
    assert epeisodio["tool_results"] == 1 and epeisodio["exit_success"] == 1


def test_gemini_session_jsonl_apodidei_role_parent_model_kai_redaction(
    tmp_path: Path,
) -> None:
    """Χαρτογραφεί Gemini user/gemini messages, model, timestamps και id."""
    arxeio = tmp_path / "session-synthetic.jsonl"
    grapse_jsonl(
        arxeio,
        [
            {
                "sessionId": "session-1",
                "projectHash": "project-1",
                "startTime": "2026-10-20T10:00:00Z",
                "lastUpdated": "2026-10-20T10:01:00Z",
            },
            {
                "id": "user-1",
                "type": "user",
                "content": "Use api_key=private-value",
                "timestamp": "2026-10-20T10:00:00Z",
            },
            {
                "id": "model-1",
                "type": "gemini",
                "content": "Done",
                "timestamp": "2026-10-20T10:00:30Z",
                "model": "gemini-test-model",
                "toolCalls": [
                    {
                        "id": "call-1",
                        "name": "read_file",
                        "args": {"path": "src/main.py"},
                        "result": "file contents",
                        "status": "success",
                        "timestamp": "2026-10-20T10:00:29Z",
                    }
                ],
            },
        ],
    )

    apotelesma = diavase_pigi("gemini", arxeio)
    gegonota = list(apotelesma.gegonota)

    assert [(g["rolos"], g["eidos"]) for g in gegonota] == [
        ("user", "prompt"),
        ("assistant", "response"),
        ("assistant", "tool_call"),
        ("tool", "tool_result"),
    ]
    assert gegonota[0]["keimeno"] == "Use api_key=[REDACTED]"
    assert gegonota[1]["montelo"] == "gemini-test-model"
    assert gegonota[2]["ergaleio"] == "read_file"
    assert gegonota[3]["keimeno"] == "file contents"
    assert all(gegonoto["goneas"] is None for gegonoto in gegonota)
    assert gegonota[0]["chronos"] == "2026-10-20T10:00:00+00:00"
    assert apotelesma.kalypsi.anagnorismena == 4
    assert apotelesma.kalypsi.sfalmata == 0


def test_opencode_sqlite_readonly_maps_message_parts_and_outcome(
    tmp_path: Path,
) -> None:
    """Διαβάζει το τεκμηριωμένο OpenCode DB shape χωρίς writes ή raw leakage."""
    arxeio = tmp_path / "opencode.db"
    syndesi = sqlite3.connect(arxeio)
    syndesi.executescript(
        "CREATE TABLE session (id TEXT, parent_id TEXT, time_created INTEGER, "
        "title TEXT);"
        "CREATE TABLE session_v2 (id TEXT, parent_id TEXT);"
        "CREATE TABLE message (id TEXT, session_id TEXT, time_created INTEGER, "
        "data TEXT);"
        "CREATE TABLE part (id TEXT, message_id TEXT, session_id TEXT, "
        "time_created INTEGER, data TEXT);"
    )
    syndesi.execute(
        "INSERT INTO session VALUES (?, ?, ?, ?)", ("ses_1", None, 1792490400000, "x")
    )
    syndesi.execute("INSERT INTO session_v2 VALUES (?, ?)", ("ses_2", None))
    syndesi.execute(
        "INSERT INTO message VALUES (?, ?, ?, ?)",
        (
            "msg_1",
            "ses_1",
            1792490400000,
            json.dumps(
                {
                    "role": "assistant",
                    "parentID": "msg_0",
                    "modelID": "model-test",
                    "providerID": "provider-test",
                }
            ),
        ),
    )
    syndesi.execute(
        "INSERT INTO part VALUES (?, ?, ?, ?, ?)",
        (
            "prt_1",
            "msg_1",
            "ses_1",
            1792490400000,
            json.dumps({"type": "text", "text": "Bearer abc.secret"}),
        ),
    )
    syndesi.execute(
        "INSERT INTO message VALUES (?, ?, ?, ?)",
        (
            "msg_2",
            "ses_2",
            1792490401000,
            json.dumps({"role": "user", "model": {"providerID": "p", "modelID": "m"}}),
        ),
    )
    syndesi.execute(
        "INSERT INTO part VALUES (?, ?, ?, ?, ?)",
        (
            "prt_2",
            "msg_2",
            "ses_2",
            1792490401000,
            json.dumps({"type": "text", "text": "Hi"}),
        ),
    )
    syndesi.commit()
    syndesi.close()
    source_snapshots = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in tmp_path.glob("opencode.db*")
    }

    apotelesma = diavase_pigi("opencode", arxeio)
    gegonota = list(apotelesma.gegonota)

    assert [gegonoto["id"] for gegonoto in gegonota] == [
        "msg_1:prt_1",
        "msg_2:prt_2",
    ]
    assert gegonota[0]["goneas"] is None
    assert gegonota[0]["montelo"] == "provider-test/model-test"
    assert gegonota[0]["keimeno"] == "Bearer [REDACTED]"
    with sqlite3.connect(arxeio) as elegktis:
        assert elegktis.execute("PRAGMA query_only").fetchone() == (0,)
        assert elegktis.execute("SELECT COUNT(*) FROM session").fetchone() == (1,)
    assert apotelesma.kalypsi.anagnorismena == 2
    assert source_snapshots == {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in tmp_path.glob("opencode.db*")
    }


def test_agnosto_kai_kakoforismeno_jsonl_dinei_partial_coverage(
    tmp_path: Path,
) -> None:
    """Δεν βαφτίζει άγνωστα ή κομμένα records ως κενό history."""
    arxeio = tmp_path / "export.jsonl"
    arxeio.write_text(
        '{"unrelated":"shape"}\n{"type":"user","content":\n',
        encoding="utf-8",
    )

    apotelesma = diavase_pigi("jsonl", arxeio)
    assert list(apotelesma.gegonota) == []
    assert apotelesma.kalypsi.katastasi == "partial"
    assert apotelesma.kalypsi.agnosta == 1
    assert apotelesma.kalypsi.sfalmata == 1


def test_gemini_conversation_json_apodidei_ola_ta_text_parts(tmp_path: Path) -> None:
    """Διαβάζει JSON conversation export και ενώνει μόνο τα recorded text parts."""
    arxeio = tmp_path / "conversation.json"
    arxeio.write_text(
        json.dumps(
            {
                "sessionId": "json-session",
                "messages": [
                    {
                        "id": "u-json",
                        "type": "user",
                        "timestamp": "2026-10-20T10:00:00+03:00",
                        "content": [{"text": "first"}, {"text": "second"}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    apotelesma = diavase_pigi("gemini", arxeio)
    gegonota = list(apotelesma.gegonota)

    assert gegonota[0]["synedria"] == "json-session"
    assert gegonota[0]["keimeno"] == "first\nsecond"
    assert gegonota[0]["chronos"] == "2026-10-20T10:00:00+03:00"
    assert apotelesma.kalypsi.adapter == "gemini-cli-json-export-v1"


def test_antigravity_native_pb_remains_explicitly_unsupported(tmp_path: Path) -> None:
    """Αρνείται να ισχυριστεί κάλυψη native .pb format χωρίς τεκμηριωμένο schema."""
    arxeio = tmp_path / "native.pb"
    arxeio.write_bytes(b"synthetic placeholder")

    apotelesma = diavase_pigi("antigravity", arxeio)
    assert list(apotelesma.gegonota) == []
    assert apotelesma.kalypsi.katastasi == "partial"
    assert apotelesma.kalypsi.agnosta == 1
    assert "unsupported" in apotelesma.kalypsi.simeioseis[0]


def test_antigravity_native_transcript_jsonl_preserves_roles_tools_and_timestamps(
    tmp_path: Path,
) -> None:
    """Χαρτογραφεί το documented transcript path με observed native record fields."""
    transcript = (
        tmp_path
        / "brain"
        / "conversation-synthetic"
        / ".system_generated"
        / "logs"
        / "transcript.jsonl"
    )
    transcript.parent.mkdir(parents=True)
    grapse_jsonl(
        transcript,
        [
            {
                "type": "USER_INPUT",
                "source": "USER_EXPLICIT",
                "content": "Change the parser",
                "created_at": "2026-10-20T10:00:00Z",
                "step_index": 0,
                "status": "DONE",
            },
            {
                "type": "PLANNER_RESPONSE",
                "source": "MODEL",
                "content": "I will inspect the parser",
                "created_at": "2026-10-20T10:00:01Z",
                "step_index": 1,
                "status": "DONE",
                "tool_calls": [{"name": "view_file", "args": {"path": "a.py"}}],
            },
            {
                "type": "RUN_COMMAND",
                "source": "MODEL",
                "content": "2 tests failed",
                "created_at": "2026-10-20T10:00:03Z",
                "step_index": 1,
                "status": "DONE",
                "exit_code": 2,
            },
            {
                "type": "SYSTEM_MESSAGE",
                "source": "SYSTEM",
                "content": "hidden system note",
                "created_at": "2026-10-20T10:00:04Z",
                "step_index": 1,
                "status": "DONE",
            },
            {
                "type": "USER_INPUT",
                "source": "USER_EXPLICIT",
                "content": None,
                "created_at": "2026-10-20T10:00:04Z",
                "step_index": 1,
                "status": "DONE",
            },
            {
                "type": "GENERIC",
                "source": "MODEL",
                "content": "partial model response",
                "created_at": "2026-10-20T10:00:05Z",
                "step_index": 2,
                "status": "RUNNING",
            },
            {
                "type": "PLANNER_RESPONSE",
                "source": "MODEL",
                "content": None,
                "created_at": "2026-10-20T10:00:06Z",
                "step_index": 3,
                "status": "DONE",
            },
            {
                "type": "RUN_COMMAND",
                "source": "MODEL",
                "content": None,
                "created_at": "2026-10-20T10:00:07Z",
                "step_index": 4,
                "status": "DONE",
            },
            {
                "type": "PLANNER_RESPONSE",
                "source": "MODEL",
                "content": "One call",
                "created_at": "2026-10-20T10:00:08Z",
                "step_index": 5,
                "status": "DONE",
                "tool_calls": [None, {}],
            },
        ],
    )
    with transcript.open("a", encoding="utf-8") as stream:
        stream.write("\n{broken\n[]\n")

    apotelesma = diavase_pigi("antigravity", transcript)
    gegonota = list(apotelesma.gegonota)

    assert [(event["rolos"], event["eidos"]) for event in gegonota] == [
        ("user", "prompt"),
        ("assistant", "response"),
        ("assistant", "tool_call"),
        ("tool", "tool_result"),
        ("assistant", "response"),
    ]
    assert gegonota[0]["synedria"] == "conversation-synthetic"
    assert gegonota[0]["chronos"] == "2026-10-20T10:00:00+00:00"
    assert gegonota[2]["goneas"] is None
    assert gegonota[2]["ergaleio"] == "view_file"
    assert gegonota[3]["kodikos_exodou"] == 2
    assert apotelesma.kalypsi.adapter == "antigravity-transcript-jsonl-observed-v1"
    assert apotelesma.kalypsi.agnosta == 8
    assert apotelesma.kalypsi.sfalmata == 1
    assert apotelesma.kalypsi.katastasi == "partial"
    brain_result = diavase_pigi("antigravity", transcript.parents[3])
    assert len(list(brain_result.gegonota)) == 5


def test_kalypsi_serializes_without_source_text_and_reports_each_state() -> None:
    """Δίνει schema-safe coverage και διακρίνει empty, partial και ok."""
    missing = piges.KalypsiPigis("gemini", "adapter")
    partial = piges.KalypsiPigis("gemini", "adapter", arxeia=1, sfalmata=1)
    successful = piges.KalypsiPigis(
        "gemini", "adapter", arxeia=1, morfes=["jsonl"], anagnorismena=2
    )
    antigravity = piges.KalypsiPigis(
        "antigravity", "adapter", arxeia=1, anagnorismena=2
    )

    assert missing.katastasi == "missing"
    assert partial.katastasi == "partial"
    assert successful.katastasi == "ok"
    assert antigravity.katastasi == "partial"
    assert "keimeno" not in successful.sto_schema()


def test_reader_source_path_and_source_key_errors_are_explicit(tmp_path: Path) -> None:
    """Απορρίπτει άγνωστα source keys και επισημαίνει missing/empty roots."""
    with pytest.raises(ValueError, match="Unsupported source key"):
        diavase_pigi("unknown", tmp_path)

    missing = diavase_pigi("gemini", tmp_path / "absent.jsonl")
    empty = diavase_pigi("gemini", tmp_path / "empty-folder")
    assert missing.kalypsi.katastasi == "missing"
    assert list(missing.gegonota) == []
    assert empty.kalypsi.katastasi == "missing"


def test_jsonl_handles_malformed_nonobject_unknown_and_explicit_tool_records(
    tmp_path: Path,
) -> None:
    """Διαχωρίζει parse errors, unknown shapes, tool roles και explicit kinds."""
    arxeio = tmp_path / "mixed.jsonl"
    arxeio.write_text(
        "\n{bad\n[]\n"
        + json.dumps({"type": "not-a-role", "content": "skip"})
        + "\n"
        + json.dumps(
            {
                "id": "result",
                "role": "tool",
                "eventType": "tool_result",
                "content": "exit 3",
                "exit_code": 3,
                "timestamp": "2026-10-20T10:00:00",
            }
        )
        + "\n"
        + json.dumps(
            {
                "id": "call-event",
                "type": "assistant",
                "kind": "tool_call",
                "content": "run",
                "toolName": "shell",
                "toolCalls": [1, {"args": {}}],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    apotelesma = diavase_pigi("jsonl", arxeio)
    gegonota = list(apotelesma.gegonota)

    assert len(gegonota) == 2
    assert (gegonota[0]["rolos"], gegonota[0]["eidos"]) == ("tool", "tool_result")
    assert gegonota[0]["kodikos_exodou"] == 3
    assert gegonota[0]["chronos"] is None
    assert apotelesma.kalypsi.sfalmata == 1
    assert (gegonota[1]["rolos"], gegonota[1]["eidos"]) == ("assistant", "tool_call")
    assert apotelesma.kalypsi.agnosta == 4


def test_json_reader_accepts_list_and_nested_conversation_but_rejects_bad_shapes(
    tmp_path: Path,
) -> None:
    """Δοκιμάζει list, nested export, malformed JSON και κενό/άσχετο JSON."""
    list_file = tmp_path / "list.json"
    list_file.write_text(json.dumps([{"role": "user", "content": "hello"}]))
    list_result = diavase_pigi("antigravity", list_file)
    assert [event["keimeno"] for event in list(list_result.gegonota)] == ["hello"]

    nested = tmp_path / "nested.json"
    nested.write_text(
        json.dumps(
            {"conversation": {"messages": [{"type": "assistant", "content": "answer"}]}}
        )
    )
    nested_result = diavase_pigi("antigravity", nested)
    assert [event["eidos"] for event in list(nested_result.gegonota)] == ["response"]

    no_records = tmp_path / "no-records.json"
    no_records.write_text(json.dumps({"messages": "not-a-list"}))
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{truncated")
    scalar = tmp_path / "scalar.json"
    scalar.write_text("42")
    no_records_result = diavase_pigi("gemini", no_records)
    assert list(no_records_result.gegonota) == []
    assert no_records_result.kalypsi.agnosta == 1
    malformed_result = diavase_pigi("gemini", malformed)
    assert list(malformed_result.gegonota) == []
    assert malformed_result.kalypsi.sfalmata == 1
    scalar_result = diavase_pigi("gemini", scalar)
    assert list(scalar_result.gegonota) == []
    assert scalar_result.kalypsi.agnosta == 1
    array_invalid = tmp_path / "array-invalid.json"
    array_invalid.write_text(json.dumps([1, {"role": "nope", "content": "x"}]))
    invalid_result = diavase_pigi("gemini", array_invalid)
    assert list(invalid_result.gegonota) == []
    assert invalid_result.kalypsi.agnosta == 2


def test_opencode_rejects_unknown_empty_and_malformed_sqlite_schemas(
    tmp_path: Path,
) -> None:
    """Δεν μετατρέπει DB άλλου τύπου, κενή βάση ή broken rows σε μηδενικά."""
    unknown = tmp_path / "unknown.db"
    with sqlite3.connect(unknown) as connection:
        connection.execute("CREATE TABLE unrelated (id TEXT)")
    empty = tmp_path / "empty.db"
    with sqlite3.connect(empty) as connection:
        connection.executescript(
            "CREATE TABLE session_v2 (id TEXT, parent_id TEXT);"
            "CREATE TABLE message (id TEXT, session_id TEXT, "
            "time_created INTEGER, data TEXT);"
            "CREATE TABLE part (id TEXT, message_id TEXT, session_id TEXT, "
            "time_created INTEGER, data TEXT);"
        )
    broken = tmp_path / "broken.db"
    with sqlite3.connect(broken) as connection:
        connection.executescript(
            "CREATE TABLE session (id TEXT, parent_id TEXT);"
            "CREATE TABLE message (id TEXT, session_id TEXT, "
            "time_created INTEGER, data TEXT);"
            "CREATE TABLE part (id TEXT, message_id TEXT, session_id TEXT, "
            "time_created INTEGER, data TEXT);"
            "INSERT INTO session VALUES ('s1', NULL);"
            "INSERT INTO message VALUES ('m1', 's1', 1, '[]');"
            "INSERT INTO part VALUES ('p1', 'm1', 's1', 1, '{}');"
        )

    unknown_result = diavase_pigi("opencode", unknown)
    empty_result = diavase_pigi("opencode", empty)
    broken_result = diavase_pigi("opencode", broken)
    assert list(unknown_result.gegonota) == []
    assert unknown_result.kalypsi.agnosta == 1
    assert list(empty_result.gegonota) == []
    assert empty_result.kalypsi.agnosta == 1
    assert list(broken_result.gegonota) == []
    assert broken_result.kalypsi.sfalmata == 1


def test_opencode_tool_variants_keep_only_recorded_result_and_tool_fields(
    tmp_path: Path,
) -> None:
    """Χαρτογραφεί v1/v2 tool call-result variants και αγνοεί malformed part."""
    arxeio = tmp_path / "tools.db"
    with sqlite3.connect(arxeio) as connection:
        connection.executescript(
            "CREATE TABLE session_v2 (id TEXT, parent_id TEXT);"
            "CREATE TABLE message (id TEXT, session_id TEXT, "
            "time_created INTEGER, data TEXT);"
            "CREATE TABLE part (id TEXT, message_id TEXT, session_id TEXT, "
            "time_created INTEGER, data TEXT);"
            "INSERT INTO session_v2 VALUES ('s1', 'parent-s');"
        )
        messages = [
            (
                "m1",
                {
                    "role": "assistant",
                    "metadata": {"assistant": {"modelID": "m", "providerID": "p"}},
                },
                {
                    "type": "tool",
                    "tool": "shell",
                    "state": {"status": "completed", "output": "ok"},
                },
            ),
            (
                "m2",
                {"role": "assistant", "parentID": "p2"},
                {
                    "type": "tool",
                    "tool": "shell",
                    "state": {
                        "status": "running",
                        "input": {"cmd": "test"},
                        "exitCode": 2,
                    },
                },
            ),
            (
                "m3",
                {"role": "assistant"},
                {
                    "type": "tool-invocation",
                    "toolInvocation": {
                        "state": "call",
                        "toolCallId": "c3",
                        "toolName": "read",
                        "args": {"file": "a"},
                    },
                },
            ),
            (
                "m4",
                {"role": "assistant"},
                {
                    "type": "tool-invocation",
                    "toolInvocation": {
                        "state": "result",
                        "toolCallId": "c4",
                        "toolName": "read",
                        "result": "done",
                    },
                },
            ),
            ("m5", {"role": "assistant"}, {"type": "unknown"}),
            (
                "m6",
                {"role": "assistant"},
                {"type": "tool-invocation", "toolInvocation": {"state": "call"}},
            ),
            ("m7", {"role": "system"}, {"type": "text", "text": "unattributed"}),
            ("m8", {"role": "assistant"}, {"type": "text"}),
            (
                "m9",
                {"role": "assistant"},
                {"type": "tool", "tool": "shell", "state": "broken"},
            ),
            (
                "m10",
                {"role": "assistant"},
                {"type": "tool-invocation", "toolInvocation": []},
            ),
        ]
        for index, (message_id, message_data, part_data) in enumerate(messages, 1):
            connection.execute(
                "INSERT INTO message VALUES (?, 's1', ?, ?)",
                (message_id, index, json.dumps(message_data)),
            )
            connection.execute(
                "INSERT INTO part VALUES (?, ?, 's1', ?, ?)",
                (f"p{index}", message_id, index, json.dumps(part_data)),
            )

    apotelesma = diavase_pigi("opencode", arxeio)
    gegonota = list(apotelesma.gegonota)

    assert [event["eidos"] for event in gegonota] == [
        "tool_result",
        "tool_call",
        "tool_call",
        "tool_result",
    ]
    assert gegonota[0]["rolos"] == "tool"
    assert gegonota[0]["montelo"] == "p/m"
    assert gegonota[1]["kodikos_exodou"] == 2
    assert apotelesma.kalypsi.agnosta == 6


def test_helpers_handle_timestamp_bounds_roles_ids_and_output_limits() -> None:
    """Καλύπτει invalid/naive/overflow timestamps και recorded metadata bounds."""
    assert piges._morfi_arxeiou(Path("README")) == "unknown"
    assert piges._gemini_metadata({"sessionId": "s"})
    assert not piges._gemini_metadata({"sessionId": "s", "type": "user"})
    assert piges._nullable_string(4) is None
    assert piges._nullable_string("") is None
    assert piges._exit_code({"exitCode": True}) is None
    assert piges._exit_code({"exit_code": 8}) == 8
    assert piges._iso_timestamp(None) is None
    assert piges._iso_timestamp(True) is None
    assert piges._iso_timestamp("not-time") is None
    assert piges._iso_timestamp("2026-10-20T10:00:00") is None
    assert piges._iso_timestamp(10**100) is None
    assert piges._iso_timestamp(1792490400000) is not None
    assert piges._text_payload({"inlineData": "private"}) is None
    assert piges._text_payload("plain") == "plain"
    assert piges._text_payload([1, {"text": "ok"}]) == "ok"
    assert piges._text_payload(["direct"]) == "direct"
    assert piges._text_payload([{"text": 1}]) == ""
    assert piges._text_payload(1) is None
    assert piges._text_payload([]) == ""
    assert piges._text_content({"recorded": True}) == '{"recorded": true}'
    with pytest.raises(ValueError, match="serialized JSON object"):
        piges._json_object(None)
    with pytest.raises(ValueError, match="JSON object"):
        piges._json_object("[]")
    assert piges._opencode_model({}) is None
    assert piges._opencode_model({"modelID": "m"}) == "m"
    assert (
        piges._opencode_model({"model": {"providerID": "p", "modelID": "m"}}) == "p/m"
    )
    output = piges._make_event(
        "gemini",
        "id",
        "s",
        None,
        None,
        "user",
        "prompt",
        "a" * (piges.ORIO_KEIMENOU + 1),
        "loc",
        None,
        None,
        None,
    )
    assert len(output["keimeno"]) == piges.ORIO_KEIMENOU


def test_paths_unsupported_files_and_read_errors_keep_partial_coverage(
    tmp_path: Path,
) -> None:
    """Ανακαλύπτει μόνο Gemini sessions και καταγράφει read errors."""
    root = tmp_path / "exports"
    chats = root / "project-hash" / "chats"
    chats.mkdir(parents=True)
    (root / "artifact.bin").write_bytes(b"not a transcript")
    (root / "request.json").write_text(
        json.dumps({"role": "user", "content": "artifact"}), encoding="utf-8"
    )
    grapse_jsonl(
        chats / "session-synthetic.jsonl",
        [
            {
                "id": "u1",
                "type": "user",
                "content": "hi",
                "timestamp": "2026-10-20T10:00:00Z",
            }
        ],
    )
    grapse_jsonl(root / "other.jsonl", [{"type": "user", "content": "not a session"}])
    result = diavase_pigi("gemini", root)
    assert [event["keimeno"] for event in list(result.gegonota)] == ["hi"]
    assert result.kalypsi.arxeia == 1
    assert result.kalypsi.agnosta == 0
    assert result.kalypsi.morfes == ["jsonl"]
    assert result.kalypsi.sfalmata == 0

    selected = diavase_pigi("gemini", root / "request.json")
    assert list(selected.gegonota) == []
    assert selected.kalypsi.agnosta == 1

    malformed_utf8 = tmp_path / "invalid.json"
    malformed_utf8.write_bytes(b"\xff")
    invalid = diavase_pigi("gemini", malformed_utf8)
    assert list(invalid.gegonota) == []
    assert invalid.kalypsi.sfalmata == 1

    invalid_db = tmp_path / "not-a-db.db"
    invalid_db.write_bytes(b"not sqlite")
    db_result = diavase_pigi("opencode", invalid_db)
    assert list(db_result.gegonota) == []
    assert db_result.kalypsi.sfalmata == 1

    selected = tmp_path / "selected.bin"
    selected.write_bytes(b"unknown")
    unsupported = diavase_pigi("gemini", selected)
    assert list(unsupported.gegonota) == []
    assert unsupported.kalypsi.agnosta == 1


def test_unreadable_reader_and_content_schema_errors_are_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Καταγράφει read OSError και JSON message με content χωρίς text semantics."""
    arxeio = tmp_path / "io.jsonl"
    arxeio.write_text("{}", encoding="utf-8")

    def fail_reader(*args: object) -> None:
        """Προσομοιώνει OS-level reader error μετά την επιλογή αρχείου."""
        raise OSError("synthetic read failure")

    with monkeypatch.context() as context:
        context.setattr(piges, "_diavase_jsonl", fail_reader)
        io_result = diavase_pigi("gemini", arxeio)
        assert list(io_result.gegonota) == []
        assert io_result.kalypsi.sfalmata == 1

    bad_content = tmp_path / "bad-content.jsonl"
    bad_content.write_text(
        json.dumps({"role": "user", "content": {"image": "opaque"}}),
        encoding="utf-8",
    )
    content_result = diavase_pigi("jsonl", bad_content)
    assert list(content_result.gegonota) == []
    assert content_result.kalypsi.agnosta == 1


def test_opencode_directory_discovery_reads_only_database_files(tmp_path: Path) -> None:
    """Directory source discovery picks DB files while ignoring unrelated assets."""
    root = tmp_path / "opencode-data"
    root.mkdir()
    (root / "auth.json").write_text("{}", encoding="utf-8")
    with sqlite3.connect(root / "history.db") as connection:
        connection.execute("CREATE TABLE unrelated (id TEXT)")

    result = diavase_pigi("opencode", root)
    assert list(result.gegonota) == []
    assert result.kalypsi.arxeia == 1
    assert result.kalypsi.agnosta == 1
    assert piges._vres_arxeia("gemini", tmp_path / "not-a-folder") == []


def test_explicit_jsonl_import_directory_walks_files(tmp_path: Path) -> None:
    """Generic explicit JSONL import recursively discovers selected folder files."""
    root = tmp_path / "jsonl-import"
    nested = root / "nested"
    nested.mkdir(parents=True)
    grapse_jsonl(
        nested / "chat.jsonl",
        [{"role": "user", "content": "selected import"}],
    )
    (nested / "notes.md").write_text("not a transcript", encoding="utf-8")

    result = diavase_pigi("jsonl", root)

    assert [event["keimeno"] for event in result.gegonota] == ["selected import"]
    assert result.kalypsi.arxeia == 2
    assert result.kalypsi.agnosta == 1


def test_opencode_wal_snapshot_does_not_change_db_wal_or_shm(tmp_path: Path) -> None:
    """Διαβάζει committed WAL state και αφήνει db/WAL/SHM byte-identical."""
    arxeio = tmp_path / "live-opencode.db"
    writer = sqlite3.connect(arxeio)
    writer.execute("PRAGMA journal_mode=WAL")
    writer.execute("PRAGMA wal_autocheckpoint=0")
    writer.executescript(
        "CREATE TABLE session_v2 (id TEXT, parent_id TEXT);"
        "CREATE TABLE message (id TEXT, session_id TEXT, "
        "time_created INTEGER, data TEXT);"
        "CREATE TABLE part (id TEXT, message_id TEXT, session_id TEXT, "
        "time_created INTEGER, data TEXT);"
        "INSERT INTO session_v2 VALUES ('s1', NULL);"
    )
    writer.execute(
        "INSERT INTO message VALUES ('m1', 's1', 1792490400000, ?)",
        (json.dumps({"role": "user"}),),
    )
    writer.execute(
        "INSERT INTO part VALUES ('p1', 'm1', 's1', 1792490400000, ?)",
        (json.dumps({"type": "text", "text": "synthetic wal row"}),),
    )
    writer.commit()
    source_files = [arxeio, Path(str(arxeio) + "-wal")]
    snapshots = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source_files
        if path.exists()
    }
    assert "live-opencode.db-wal" in snapshots

    try:
        apotelesma = diavase_pigi("opencode", arxeio)
        assert [event["keimeno"] for event in list(apotelesma.gegonota)] == [
            "synthetic wal row"
        ]
        assert snapshots == {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in source_files
            if path.exists()
        }
    finally:
        writer.close()


def test_markdown_without_explicit_role_headings_is_not_chat(tmp_path: Path) -> None:
    """Δεν μετρά Markdown task artifact χωρίς ρητά headings ρόλων ως transcript."""
    arxeio = tmp_path / "artifact.md"
    arxeio.write_text("# Task\nCompleted a feature.\n## Notes\nUseful work.")

    apotelesma = diavase_pigi("antigravity", arxeio)

    assert list(apotelesma.gegonota) == []
    assert apotelesma.kalypsi.agnosta == 1


def test_antigravity_markdown_export_markarei_limited_coverage(
    tmp_path: Path,
) -> None:
    """Διαβάζει role-heading export και δηλώνει ότι δεν είναι native history."""
    arxeio = tmp_path / "antigravity-export.md"
    arxeio.write_text(
        "# Exported conversation\n\n## User\nHi\n\n## Assistant\nHello\n",
        encoding="utf-8",
    )

    apotelesma = diavase_pigi("antigravity", arxeio)
    gegonota = list(apotelesma.gegonota)

    assert [g["keimeno"] for g in gegonota] == ["Hi", "Hello"]
    assert apotelesma.kalypsi.adapter == "antigravity-markdown-export-v1"
    assert apotelesma.kalypsi.katastasi == "partial"
    assert "Explicit JSON/Markdown exports only" in apotelesma.kalypsi.simeioseis[0]
