"""Read-only readers για OpenCode, Gemini CLI και ρητά exports."""

from __future__ import annotations

import json
import logging
import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator, Literal, TypedDict, cast

from devrar.aporrita import katharise_aporrita
from devrar.symvanta import SymvanErgasias

logger = logging.getLogger(__name__)

SFKALMATOS_JSON = (json.JSONDecodeError, UnicodeDecodeError)
ORME_PAGIDOS = 256
ORIO_KEIMENOU = 20_000
ROLES: dict[str, Literal["user", "assistant", "tool"]] = {
    "user": "user",
    "human": "user",
    "assistant": "assistant",
    "gemini": "assistant",
    "model": "assistant",
    "tool": "tool",
}
TYPOS_PIGON = {"opencode", "gemini", "antigravity", "jsonl"}
ANTIGRAVITY_TOOLS = {
    "ASK_QUESTION",
    "CODE_ACTION",
    "DEFINE_SUBAGENT",
    "FIND_BY_NAME",
    "GENERATE_IMAGE",
    "GREP_SEARCH",
    "INVOKE_SUBAGENT",
    "LIST_DIRECTORY",
    "LIST_PERMISSIONS",
    "MANAGE_SUBAGENTS",
    "MANAGE_TASK",
    "MULTI_REPLACE_FILE_CONTENT",
    "READ_URL_CONTENT",
    "REPLACE_FILE_CONTENT",
    "RUN_COMMAND",
    "SCHEDULE",
    "SEARCH_WEB",
    "SEND_MESSAGE",
    "VIEW_FILE",
    "WRITE_TO_FILE",
}


class ApotelesmaSymvantos(TypedDict):
    """Μικρό εσωτερικό record για τη μετατροπή ενός αναγνωρισμένου event."""

    id: str
    pigi: str
    synedria: str
    goneas: str | None
    chronos: str | None
    rolos: Literal["user", "assistant", "tool"]
    eidos: Literal["prompt", "response", "tool_call", "tool_result"]
    keimeno: str
    locator: str
    ergaleio: str | None
    montelo: str | None
    kodikos_exodou: int | None


@dataclass
class KalypsiPigis:
    """Καταγράφει observed coverage κατά την κατανάλωση του event iterator."""

    pigi: str
    adapter: str
    arxeia: int = 0
    morfes: list[str] = field(default_factory=list)
    anagnorismena: int = 0
    sfalmata: int = 0
    agnosta: int = 0
    simeioseis: list[str] = field(default_factory=list)

    @property
    def katastasi(self) -> Literal["ok", "partial", "missing"]:
        """Επιστρέφει missing για κενή πηγή και partial για ελλιπή κάλυψη."""
        if self.arxeia == 0:
            return "missing"
        if self.sfalmata or self.agnosta or self.anagnorismena == 0:
            return "partial"
        if self.pigi == "antigravity":
            return "partial"
        return "ok"

    def sto_schema(self) -> dict[str, object]:
        """Επιστρέφει serializable coverage χωρίς να ενσωματώνει transcript data."""
        return {
            "pigi": self.pigi,
            "adapter": self.adapter,
            "katastasi": self.katastasi,
            "arxeia": self.arxeia,
            "morfes": list(self.morfes),
            "anagnorismena": self.anagnorismena,
            "sfalmata": self.sfalmata,
            "agnosta": self.agnosta,
            "simeioseis": list(self.simeioseis),
        }


@dataclass
class ApotelesmaPigis:
    """Παρέχει stream transient events και mutable coverage της επιλεγμένης πηγής."""

    gegonota: Iterator[SymvanErgasias]
    kalypsi: KalypsiPigis


def diavase_pigi(pigi: str, diadromi: Path) -> ApotelesmaPigis:
    """Επιλέγει reader βάσει source key και επέκτασης, χωρίς side effects."""
    onoma = pigi.casefold()
    if onoma not in TYPOS_PIGON:
        raise ValueError(f"Unsupported source key: {pigi}")
    adapter = {
        "opencode": "opencode-sqlite-message-part-v1",
        "gemini": "gemini-cli-session-jsonl-v1",
        "antigravity": "antigravity-export-v1",
        "jsonl": "explicit-jsonl-v1",
    }[onoma]
    if onoma == "gemini" and diadromi.suffix.lower() == ".json":
        adapter = "gemini-cli-json-export-v1"
    if onoma == "antigravity" and diadromi.suffix.lower() in {".md", ".markdown"}:
        adapter = "antigravity-markdown-export-v1"
    if onoma == "antigravity" and _is_antigravity_native_path(diadromi):
        adapter = "antigravity-transcript-jsonl-observed-v1"
    kalypsi = KalypsiPigis(onoma, adapter)
    if not diadromi.exists():
        kalypsi.simeioseis.append("Selected path does not exist.")
        return ApotelesmaPigis(iter(()), kalypsi)
    arxeia = _vres_arxeia(onoma, diadromi)
    kalypsi.arxeia = len(arxeia)
    return ApotelesmaPigis(_diavase_arxeia(onoma, arxeia, kalypsi), kalypsi)


def _vres_arxeia(pigi: str, diadromi: Path) -> list[Path]:
    """Επιστρέφει καθορισμένα files, χωρίς αναζήτηση εκτός δοσμένου path."""
    if diadromi.is_file():
        return [diadromi]
    if not diadromi.is_dir():
        return []
    if pigi == "opencode":
        return sorted(diadromi.rglob("*.db"))
    if pigi == "gemini":
        return sorted(
            arxeio
            for arxeio in diadromi.rglob("session-*.jsonl")
            if arxeio.parent.name == "chats"
        )
    if pigi == "antigravity":
        return sorted(
            arxeio
            for arxeio in diadromi.rglob("transcript.jsonl")
            if _is_antigravity_native_path(arxeio)
        )
    return sorted(arxeio for arxeio in diadromi.rglob("*") if arxeio.is_file())


def _diavase_arxeia(
    pigi: str, arxeia: list[Path], kalypsi: KalypsiPigis
) -> Iterator[SymvanErgasias]:
    """Διαβάζει κάθε επιλεγμένο αρχείο και ενημερώνει coverage σε bounded ροή."""
    for arxeio in arxeia:
        morfi = _morfi_arxeiou(arxeio)
        if morfi not in kalypsi.morfes:
            kalypsi.morfes.append(morfi)
        try:
            if pigi == "opencode" and morfi == "sqlite":
                yield from _diavase_opencode(arxeio, kalypsi)
            elif (
                pigi == "antigravity"
                and morfi == "jsonl"
                and _is_antigravity_native_path(arxeio)
            ):
                yield from _diavase_antigravity_jsonl(arxeio, kalypsi)
            elif morfi == "jsonl":
                yield from _diavase_jsonl(arxeio, pigi, kalypsi)
            elif morfi == "json":
                yield from _diavase_json(arxeio, pigi, kalypsi)
            elif morfi == "markdown" and pigi == "antigravity":
                yield from _diavase_markdown(arxeio, pigi, kalypsi)
            elif morfi == "protobuf" and pigi == "antigravity":
                kalypsi.agnosta += 1
                _simeiose_agnosto(
                    kalypsi, "Antigravity native .pb format is unsupported."
                )
            else:
                kalypsi.agnosta += 1
                _simeiose_agnosto(kalypsi, f"Unsupported {morfi} file for {pigi}.")
        except (OSError, sqlite3.Error) as sfalma:
            logger.warning(
                "Source reader failed for %s (%s)", arxeio.name, type(sfalma).__name__
            )
            kalypsi.sfalmata += 1
            kalypsi.simeioseis.append(f"Could not read a selected {morfi} file.")
        except SFKALMATOS_JSON:
            kalypsi.sfalmata += 1
            kalypsi.simeioseis.append(f"Malformed or truncated {morfi} input.")
    if pigi == "antigravity":
        if kalypsi.adapter == "antigravity-transcript-jsonl-observed-v1":
            simeiosi = (
                "Native transcript rows are parsed using observed local fields; "
                "the row schema is not officially versioned."
            )
        else:
            simeiosi = (
                "Explicit JSON/Markdown exports only; "
                "they do not imply full native history."
            )
        _simeiose_agnosto(kalypsi, simeiosi)


def _morfi_arxeiou(arxeio: Path) -> str:
    """Ταξινομεί μόνο σαφείς SQLite, JSON/JSONL, Markdown και protobuf endings."""
    suffix = arxeio.suffix.lower()
    if suffix in {".db", ".sqlite", ".sqlite3"}:
        return "sqlite"
    if suffix == ".jsonl":
        return "jsonl"
    if suffix == ".json":
        return "json"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix == ".pb":
        return "protobuf"
    return suffix.lstrip(".") or "unknown"


def _is_antigravity_native_path(diadromi: Path) -> bool:
    """Αναγνωρίζει μόνο το documented transcript path μέσα στο brain store."""
    if diadromi.is_dir():
        return diadromi.name == "brain" or (diadromi / "brain").is_dir()
    return (
        diadromi.name == "transcript.jsonl"
        and len(diadromi.parents) >= 3
        and diadromi.parent.name == "logs"
        and diadromi.parent.parent.name == ".system_generated"
    )


def _diavase_antigravity_jsonl(
    arxeio: Path, kalypsi: KalypsiPigis
) -> Iterator[SymvanErgasias]:
    """Διαβάζει το official transcript path με observed Antigravity row fields."""
    synedria = arxeio.parents[2].name
    with arxeio.open("r", encoding="utf-8") as source:
        for arithmos, grammh in enumerate(source, 1):
            if not grammh.strip():
                continue
            try:
                record = json.loads(grammh)
            except json.JSONDecodeError:
                kalypsi.sfalmata += 1
                continue
            if not isinstance(record, dict):
                kalypsi.agnosta += 1
                continue
            record_map = cast(dict[str, object], record)
            event = _antigravity_event(
                record_map, synedria, f"{synedria}/transcript.jsonl:{arithmos}"
            )
            if event is None:
                kalypsi.agnosta += 1
                continue
            kalypsi.anagnorismena += 1
            yield event
            yield from _antigravity_tool_call_events(
                record_map, synedria, event["id"], arxeio.name, arithmos, kalypsi
            )


def _antigravity_event(
    record: dict[str, object], synedria: str, locator: str
) -> SymvanErgasias | None:
    """Χαρτογραφεί μόνο γνωστούς user/model/tool event types με recorded source."""
    event_type = record.get("type")
    source = record.get("source")
    status = record.get("status")
    content = record.get("content")
    if status == "RUNNING":
        return None
    timestamp = _iso_timestamp(record.get("created_at"))
    model = _nullable_string(record.get("model"))
    code = _exit_code(record)
    if event_type == "USER_INPUT" and source == "USER_EXPLICIT":
        if not isinstance(content, str):
            return None
        return _make_event(
            "antigravity",
            locator,
            synedria,
            None,
            timestamp,
            "user",
            "prompt",
            content,
            locator,
            None,
            model,
            code,
        )
    if source == "MODEL" and event_type in {"PLANNER_RESPONSE", "GENERIC"}:
        if not isinstance(content, str):
            return None
        return _make_event(
            "antigravity",
            locator,
            synedria,
            None,
            timestamp,
            "assistant",
            "response",
            content,
            locator,
            None,
            model,
            code,
        )
    if source == "MODEL" and event_type in ANTIGRAVITY_TOOLS:
        if not isinstance(content, str):
            return None
        return _make_event(
            "antigravity",
            locator,
            synedria,
            None,
            timestamp,
            "tool",
            "tool_result",
            content,
            locator,
            str(event_type).lower(),
            model,
            code,
        )
    return None


def _antigravity_tool_call_events(
    record: dict[str, object],
    synedria: str,
    tautotita_minimatos: str,
    filename: str,
    arithmos: int,
    kalypsi: KalypsiPigis,
) -> Iterator[SymvanErgasias]:
    """Εξάγει recorded `tool_calls` από PLANNER_RESPONSE χωρίς inference."""
    calls = record.get("tool_calls")
    if not isinstance(calls, list):
        return
    for index, call in enumerate(calls):
        if not isinstance(call, dict):
            kalypsi.agnosta += 1
            continue
        call_map = cast(dict[str, object], call)
        tool_name = _nullable_string(call_map.get("name"))
        if not tool_name:
            kalypsi.agnosta += 1
            continue
        args = call_map.get("args")
        kalypsi.anagnorismena += 1
        yield _make_event(
            "antigravity",
            f"{tautotita_minimatos}:call:{index}",
            synedria,
            None,
            _iso_timestamp(record.get("created_at")),
            "assistant",
            "tool_call",
            _text_content(args) if args is not None else "",
            f"{filename}:{arithmos}/tool-call-{index}",
            tool_name,
            _nullable_string(record.get("model")),
            _exit_code(call_map),
        )


def _diavase_opencode(arxeio: Path, kalypsi: KalypsiPigis) -> Iterator[SymvanErgasias]:
    """Διαβάζει OpenCode SQLite v1 message/part tables σε read-only snapshot."""
    uri = arxeio.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as syndesi:
        with syndesi:
            syndesi.execute("PRAGMA query_only=ON")
            syndesi.execute("BEGIN")
            pinakes = {
                grammi[0]
                for grammi in syndesi.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            if not {"message", "part"}.issubset(pinakes) or not (
                {"session"}.issubset(pinakes) or {"session_v2"}.issubset(pinakes)
            ):
                kalypsi.agnosta += 1
                _simeiose_agnosto(kalypsi, "Unrecognized OpenCode SQLite schema.")
                return
            if {"session", "session_v2"}.issubset(pinakes):
                query = (
                    "SELECT id, parent_id FROM session_v2 UNION ALL "
                    "SELECT id, parent_id FROM session "
                    "WHERE id NOT IN (SELECT id FROM session_v2)"
                )
            else:
                table = "session_v2" if "session_v2" in pinakes else "session"
                query = f"SELECT id, parent_id FROM {table}"
            cursor = syndesi.execute(
                "SELECT s.id, s.parent_id, m.id, m.data, m.time_created, "
                "p.id, p.data, p.time_created "
                f"FROM ({query}) AS s "
                "JOIN message AS m ON m.session_id=s.id "
                "JOIN part AS p ON p.message_id=m.id "
                "ORDER BY s.id, m.time_created, m.id, p.id"
            )
            trexon_minima: tuple[str, str] | None = None
            keimeno_minimatos: SymvanErgasias | None = None
            while grammes := cursor.fetchmany(ORME_PAGIDOS):
                for grammi in grammes:
                    try:
                        (
                            session_id,
                            session_parent,
                            message_id,
                            message_data,
                            msg_time,
                            part_id,
                            part_data,
                            part_time,
                        ) = grammi
                        kleidi_minimatos = (str(session_id), str(message_id))
                        if kleidi_minimatos != trexon_minima:
                            if keimeno_minimatos is not None:
                                yield keimeno_minimatos
                                keimeno_minimatos = None
                            trexon_minima = kleidi_minimatos
                        minima = _json_object(message_data)
                        meros = _json_object(part_data)
                        if (
                            minima.get("role") == "user"
                            and meros.get("type") == "text"
                            and (
                                meros.get("synthetic") is True
                                or meros.get("ignored") is True
                            )
                        ):
                            kalypsi.anagnorismena += 1
                            continue
                        event = _opencode_event(
                            str(session_id),
                            _nullable_string(session_parent),
                            str(message_id),
                            minima,
                            _nullable_string(part_id),
                            meros,
                            part_time if part_time is not None else msg_time,
                        )
                        if event is None:
                            kalypsi.agnosta += 1
                            continue
                        kalypsi.anagnorismena += 1
                        if event["eidos"] in {"prompt", "response"}:
                            if keimeno_minimatos is None:
                                keimeno_minimatos = event
                                keimeno_minimatos["locator"] = (
                                    f"{session_id}/{message_id}/text-parts"
                                )
                            else:
                                keimeno_minimatos["keimeno"] = (
                                    keimeno_minimatos["keimeno"]
                                    + "\n"
                                    + event["keimeno"]
                                )[:ORIO_KEIMENOU]
                            continue
                        klisi = _klisi_opencode_apo_apotelesma(event, meros)
                        if klisi is not None:
                            kalypsi.anagnorismena += 1
                            yield klisi
                        yield event
                    except (ValueError, TypeError, json.JSONDecodeError):
                        kalypsi.sfalmata += 1
                        _simeiose_agnosto(
                            kalypsi, "A malformed OpenCode message or part was skipped."
                        )
            if keimeno_minimatos is not None:
                yield keimeno_minimatos
            if kalypsi.anagnorismena == 0 and kalypsi.agnosta == 0:
                kalypsi.agnosta += 1
                _simeiose_agnosto(
                    kalypsi, "OpenCode SQLite contains no readable message parts."
                )


def _opencode_event(
    synedria: str,
    session_parent: str | None,
    message_id: str,
    minima: dict[str, object],
    part_id: str | None,
    meros: dict[str, object],
    chronos_millis: object,
) -> SymvanErgasias | None:
    """Μεταφράζει OpenCode text/tool parts, διατηρώντας ids και model metadata."""
    part_type = meros.get("type")
    role_v = minima.get("role")
    if part_type == "text" and role_v in {"user", "assistant"}:
        text_v = meros.get("text")
        if not isinstance(text_v, str):
            return None
        role: Literal["user", "assistant"] = "user" if role_v == "user" else "assistant"
        kind: Literal["prompt", "response", "tool_call", "tool_result"] = (
            "prompt" if role == "user" else "response"
        )
        return _make_event(
            "opencode",
            f"{message_id}:{part_id or 'text'}",
            synedria,
            session_parent,
            _iso_timestamp(chronos_millis),
            role,
            kind,
            text_v,
            f"{synedria}/{message_id}/{part_id or 'text'}",
            None,
            _opencode_model(minima),
            _exit_code(meros),
        )
    if part_type == "tool" and role_v == "assistant":
        state = meros.get("state")
        if not isinstance(state, dict):
            return None
        state_map = cast(dict[str, object], state)
        status = state_map.get("status")
        is_result = status in {"completed", "error"}
        tool_name = _nullable_string(meros.get("tool"))
        content = (
            state_map.get("output", state_map.get("error"))
            if is_result
            else state_map.get("input")
        )
        if not isinstance(content, str):
            content = (
                json.dumps(content, ensure_ascii=False) if content is not None else ""
            )
        return _make_event(
            "opencode",
            f"{message_id}:{part_id or 'tool'}:{'result' if is_result else 'call'}",
            synedria,
            session_parent,
            _iso_timestamp(chronos_millis),
            "tool" if is_result else "assistant",
            "tool_result" if is_result else "tool_call",
            content,
            f"{synedria}/{message_id}/{part_id or 'tool'}",
            tool_name,
            _opencode_model(minima),
            _exit_code(state_map),
        )
    if part_type == "tool-invocation" and role_v == "assistant":
        invocation = meros.get("toolInvocation")
        if not isinstance(invocation, dict):
            return None
        invocation_map = cast(dict[str, object], invocation)
        is_result = invocation_map.get("state") == "result"
        tool_name = _nullable_string(invocation_map.get("toolName"))
        content_v = (
            invocation_map.get("result") if is_result else invocation_map.get("args")
        )
        if not tool_name:
            return None
        content = _text_content(content_v) if content_v is not None else ""
        return _make_event(
            "opencode",
            f"{message_id}:{part_id or 'tool'}:{'result' if is_result else 'call'}",
            synedria,
            session_parent,
            _iso_timestamp(chronos_millis),
            "tool" if is_result else "assistant",
            "tool_result" if is_result else "tool_call",
            content,
            f"{synedria}/{message_id}/{part_id or 'tool'}",
            tool_name,
            _opencode_model(minima),
            _exit_code(invocation_map),
        )
    return None


def _klisi_opencode_apo_apotelesma(
    symvan: SymvanErgasias, meros: dict[str, object]
) -> SymvanErgasias | None:
    """Το terminal persisted tool part καταγράφει και invocation με ρητό input."""
    if symvan["eidos"] != "tool_result" or not symvan["ergaleio"]:
        return None
    if meros.get("type") == "tool":
        katastasi = meros.get("state")
        pedio = "input"
    else:
        katastasi = meros.get("toolInvocation")
        pedio = "args"
    if not isinstance(katastasi, dict) or pedio not in katastasi:
        return None
    klisi = symvan.copy()
    klisi["id"] = symvan["id"].removesuffix(":result") + ":call"
    klisi["rolos"] = "assistant"
    klisi["eidos"] = "tool_call"
    klisi["kodikos_exodou"] = None
    klisi["keimeno"] = katharise_aporrita(
        json.dumps(katastasi[pedio], ensure_ascii=False)
    )[:ORIO_KEIMENOU]
    return klisi


def _diavase_jsonl(
    arxeio: Path, pigi: str, kalypsi: KalypsiPigis
) -> Iterator[SymvanErgasias]:
    """Διαβάζει JSONL κατά γραμμή, συμπεριλαμβανομένου του Gemini session log."""
    synedria_default = arxeio.stem
    with arxeio.open("r", encoding="utf-8") as source:
        for arithmos, grammh in enumerate(source, 1):
            if not grammh.strip():
                continue
            try:
                record = json.loads(grammh)
            except json.JSONDecodeError:
                kalypsi.sfalmata += 1
                continue
            if not isinstance(record, dict):
                kalypsi.agnosta += 1
                continue
            record_map = cast(dict[str, object], record)
            if _gemini_metadata(record_map):
                synedria_default = str(record_map.get("sessionId", synedria_default))
                continue
            event = _generic_event(
                pigi,
                record_map,
                synedria_default,
                f"{arxeio.name}:{arithmos}",
                kalypsi.adapter,
            )
            if event is None:
                kalypsi.agnosta += 1
                continue
            kalypsi.anagnorismena += 1
            yield event
            yield from _gemini_tool_call_events(
                pigi,
                record_map,
                synedria_default,
                f"{arxeio.name}:{arithmos}",
                kalypsi,
            )


def _diavase_json(
    arxeio: Path, pigi: str, kalypsi: KalypsiPigis
) -> Iterator[SymvanErgasias]:
    """Διαβάζει export JSON object/list με αναγνωρίσιμα message records."""
    with arxeio.open("r", encoding="utf-8") as source:
        data = json.load(source)
    if isinstance(data, list):
        records = data
        root: dict[str, object] = {}
    elif isinstance(data, dict):
        root = cast(dict[str, object], data)
        records_v = root.get("messages")
        if not isinstance(records_v, list) and isinstance(
            root.get("conversation"), dict
        ):
            records_v = cast(dict[str, object], root["conversation"]).get("messages")
        records = records_v if isinstance(records_v, list) else []
    else:
        kalypsi.agnosta += 1
        return
    synedria = str(root.get("sessionId", root.get("id", arxeio.stem)))
    for arithmos, record in enumerate(records, 1):
        if not isinstance(record, dict):
            kalypsi.agnosta += 1
            continue
        event = _generic_event(
            pigi,
            cast(dict[str, object], record),
            synedria,
            f"{arxeio.name}:{arithmos}",
            kalypsi.adapter,
        )
        if event is None:
            kalypsi.agnosta += 1
            continue
        kalypsi.anagnorismena += 1
        yield event
        yield from _gemini_tool_call_events(
            pigi,
            cast(dict[str, object], record),
            synedria,
            f"{arxeio.name}:{arithmos}",
            kalypsi,
        )
    if not records and not kalypsi.simeioseis:
        kalypsi.agnosta += 1


def _generic_event(
    pigi: str,
    record: dict[str, object],
    synedria_default: str,
    locator: str,
    adapter: str,
) -> SymvanErgasias | None:
    """Κανονικοποιεί documented Gemini records ή explicit role-based exports."""
    role_v = record.get("type", record.get("role"))
    if not isinstance(role_v, str) or role_v.casefold() not in ROLES:
        return None
    role = ROLES[role_v.casefold()]
    content = _text_payload(record.get("content", record.get("text", "")))
    if content is None:
        return None
    synedria = str(record.get("sessionId", synedria_default))
    record_id = str(record.get("id", locator))
    event_type = record.get("eventType")
    kind_v = record.get("kind")
    kind: Literal["prompt", "response", "tool_call", "tool_result"]
    if event_type in {"tool_call", "tool_result"}:
        kind = event_type
    elif kind_v in {"tool_call", "tool_result"}:
        kind = kind_v
    else:
        kind = (
            "prompt"
            if role == "user"
            else "tool_result"
            if role == "tool"
            else "response"
        )
    timestamp = record.get("timestamp", record.get("time"))
    model = _nullable_string(record.get("model"))
    tool = _nullable_string(record.get("toolName", record.get("name")))
    created = _make_event(
        pigi,
        record_id,
        synedria,
        _goneas_synedrias(record),
        _iso_timestamp(timestamp),
        role,
        kind,
        content,
        locator,
        tool,
        model,
        _exit_code(record),
    )
    return created


def _gemini_tool_call_events(
    pigi: str,
    record: dict[str, object],
    synedria: str,
    locator: str,
    kalypsi: KalypsiPigis,
) -> Iterator[SymvanErgasias]:
    """Εξάγει μόνο τα tool calls που είναι ρητά καταγεγραμμένα σε Gemini record."""
    calls = record.get("toolCalls")
    if not isinstance(calls, list):
        return
    synedria = _nullable_string(record.get("sessionId")) or synedria
    for index, call in enumerate(calls):
        if not isinstance(call, dict):
            kalypsi.agnosta += 1
            continue
        call_map = cast(dict[str, object], call)
        tool_name = _nullable_string(call_map.get("name"))
        call_id = _nullable_string(call_map.get("id")) or f"{locator}:call-{index}"
        args = call_map.get("args")
        if not tool_name:
            kalypsi.agnosta += 1
            continue
        text_v = json.dumps(args, ensure_ascii=False) if args is not None else ""
        kalypsi.anagnorismena += 1
        yield _make_event(
            pigi,
            call_id,
            synedria,
            _goneas_synedrias(record),
            _iso_timestamp(record.get("timestamp")),
            "assistant",
            "tool_call",
            text_v,
            f"{locator}/tool-call-{index}",
            tool_name,
            _nullable_string(record.get("model")),
            _exit_code(call_map),
        )
        result = call_map.get("result")
        if result is not None:
            kalypsi.anagnorismena += 1
            yield _make_event(
                pigi,
                f"{call_id}:result",
                synedria,
                _goneas_synedrias(record),
                _iso_timestamp(call_map.get("timestamp")),
                "tool",
                "tool_result",
                _text_content(result),
                f"{locator}/tool-result-{index}",
                tool_name,
                _nullable_string(record.get("model")),
                _exit_code(call_map),
            )


def _diavase_markdown(
    arxeio: Path, pigi: str, kalypsi: KalypsiPigis
) -> Iterator[SymvanErgasias]:
    """Διαβάζει explicit Markdown exports partitioned by User/Assistant headings."""
    current_role: Literal["user", "assistant"] | None = None
    contenuto: list[str] = []
    ordinal = 0

    def emit() -> SymvanErgasias | None:
        """Δημιουργεί event για heading που περιέχει πραγματικό κείμενο."""
        nonlocal ordinal
        text_v = "\n".join(contenuto).strip()
        if current_role is None or not text_v:
            return None
        ordinal += 1
        kind: Literal["prompt", "response", "tool_call", "tool_result"] = (
            "prompt" if current_role == "user" else "response"
        )
        return _make_event(
            pigi,
            f"{arxeio.name}:{ordinal}",
            arxeio.stem,
            None,
            None,
            current_role,
            kind,
            text_v,
            f"{arxeio.name}:message-{ordinal}",
            None,
            None,
            None,
        )

    with arxeio.open("r", encoding="utf-8") as source:
        for grammh in source:
            match = re.match(
                r"^#{1,6}\s+(User|Human|Assistant|Gemini)\s*$", grammh.strip(), re.I
            )
            if match:
                event = emit()
                if event is not None:
                    kalypsi.anagnorismena += 1
                    yield event
                current_role = cast(
                    Literal["user", "assistant"], ROLES[match.group(1).casefold()]
                )
                contenuto = []
            elif current_role is not None:
                contenuto.append(grammh.rstrip())
    event = emit()
    if event is not None:
        kalypsi.anagnorismena += 1
        yield event
    if kalypsi.anagnorismena == 0:
        kalypsi.agnosta += 1


def _make_event(
    pigi: str,
    event_id: str,
    synedria: str,
    goneas: str | None,
    chronos: str | None,
    rolos: Literal["user", "assistant", "tool"],
    eidos: Literal["prompt", "response", "tool_call", "tool_result"],
    keimeno: str,
    locator: str,
    ergaleio: str | None,
    montelo: str | None,
    kodikos_exodou: int | None,
) -> SymvanErgasias:
    """Εφαρμόζει κοινό truncation/redaction και δημιουργεί transient event."""
    safe_text = katharise_aporrita(
        keimeno if eidos == "tool_result" else keimeno[:ORIO_KEIMENOU]
    )
    return {
        "id": event_id,
        "pigi": pigi,
        "synedria": synedria,
        "goneas": goneas,
        "chronos": chronos,
        "rolos": rolos,
        "eidos": eidos,
        "keimeno": safe_text,
        "locator": locator,
        "ergaleio": ergaleio,
        "montelo": montelo,
        "kodikos_exodou": kodikos_exodou,
    }


def _goneas_synedrias(eggrafi: dict[str, object]) -> str | None:
    """Δέχεται μόνο ρητό session parent, ποτέ message/tool parent identifiers."""
    return _nullable_string(
        eggrafi.get("parentSessionId", eggrafi.get("parentSessionID"))
    )


def _gemini_metadata(record: dict[str, object]) -> bool:
    """Ξεχωρίζει το πρώτο Gemini conversation metadata row από message rows."""
    return "sessionId" in record and "type" not in record and "role" not in record


def _json_object(value: object) -> dict[str, object]:
    """Αποκωδικοποιεί JSON text και απαιτεί top-level object."""
    if not isinstance(value, str):
        raise ValueError("Expected serialized JSON object")
    decoded = json.loads(value)
    if not isinstance(decoded, dict):
        raise ValueError("Expected JSON object")
    return cast(dict[str, object], decoded)


def _opencode_model(minima: dict[str, object]) -> str | None:
    """Επιστρέφει μόνο model/provider ids καταγεγραμμένα στο message data."""
    metadata = minima.get("metadata")
    if isinstance(metadata, dict):
        assistant = cast(dict[str, object], metadata).get("assistant")
        if isinstance(assistant, dict):
            minima = {**minima, **cast(dict[str, object], assistant)}
    model = minima.get("model")
    model_map = cast(dict[str, object], model) if isinstance(model, dict) else {}
    model_id = _nullable_string(minima.get("modelID")) or _nullable_string(
        model_map.get("modelID")
    )
    provider_id = _nullable_string(minima.get("providerID")) or _nullable_string(
        model_map.get("providerID")
    )
    if model_id and provider_id:
        return f"{provider_id}/{model_id}"
    return model_id or provider_id


def _iso_timestamp(value: object) -> str | None:
    """Μετατρέπει epoch milliseconds ή aware ISO timestamp· απορρίπτει naive."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return datetime.fromtimestamp(value / 1000, tz=UTC).isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.isoformat() if parsed.tzinfo is not None else None


def _nullable_string(value: object) -> str | None:
    """Επιστρέφει μη κενό string ή None για μη διαθέσιμο metadata."""
    return value if isinstance(value, str) and value else None


def _text_content(value: object) -> str:
    """Διατηρεί text tool result ή serializes structured recorded content."""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _text_payload(value: object) -> str | None:
    """Εξάγει text parts από Gemini PartListUnion χωρίς να σειριοποιεί media."""
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        return None
    texts: list[str] = []
    for item in value:
        if isinstance(item, str):
            texts.append(item)
        elif isinstance(item, dict) and isinstance(item.get("text"), str):
            texts.append(cast(str, item["text"]))
    return "\n".join(texts) if texts else ""


def _exit_code(record: dict[str, object]) -> int | None:
    """Κρατά explicit integer exit code, χωρίς inference από status text."""
    code = record.get("exitCode", record.get("exit_code"))
    metadata = record.get("metadata")
    if code is None and isinstance(metadata, dict):
        code = metadata.get("exit", metadata.get("exitCode", metadata.get("exit_code")))
    return code if isinstance(code, int) and not isinstance(code, bool) else None


def _simeiose_agnosto(kalypsi: KalypsiPigis, simeiosi: str) -> None:
    """Προσθέτει μοναδική σύντομη σημείωση χωρίς source transcript content."""
    if simeiosi not in kalypsi.simeioseis:
        kalypsi.simeioseis.append(simeiosi)
