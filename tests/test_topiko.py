"""Tests for a local-only model analysis boundary."""

from __future__ import annotations

import io
import json
import threading
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import cast

import pytest

from devrar import topiko as topiko_modulo

KLEIDI_DOKIMIS = "phi4-mini:latest"


def _eyrima_synthetiko(
    epipedo: str = "strength",
    diastasi: str = "scope_acceptance",
    tekmiria: list[dict[str, str]] | None = None,
    **epipleon: object,
) -> dict[str, object]:
    """Returns one valid synthetic local-model proposal."""
    eyrima: dict[str, object] = {
        "polarity": epipedo,
        "dimension_id": diastasi,
        "observation": "The prompt asks for explicit acceptance criteria.",
        "action": "Keep the criteria beside the verification step.",
        "alternative": "The wording may be exploratory and not an established habit.",
        "counterevidence": "No task result or follow-through is represented here.",
        "evidence": tekmiria or [{"id": "prompt-1", "quote": "acceptance criteria"}],
    }
    eyrima.update(epipleon)
    return eyrima


class DiakomisHTTP:
    """Maintains configurable responses for one loopback Ollama mock."""

    def __init__(self) -> None:
        self.etiketes: object = {
            "models": [
                {
                    "name": KLEIDI_DOKIMIS,
                    "digest": "a" * 64,
                    "size": 1024,
                    "details": {"format": "gguf"},
                }
            ]
        }
        self.emfanisi: object = {
            "details": {"format": "gguf"},
            "modelfile": "FROM /local/models/blobs/sha256:abc123\n",
        }
        self.ekdosi: object = {"version": "0.40.11"}
        self.paragomeno: object = {"findings": [_eyrima_synthetiko()]}
        self.aitimata: list[tuple[str, dict[str, object] | None]] = []
        self.anakateythynsi_generate = False
        self.bytes_apantisis: bytes | None = None


@pytest.fixture
def topiko_synthetiko(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[DiakomisHTTP, int]]:
    """Serves actual HTTP requests on loopback without an external service."""
    katastasi = DiakomisHTTP()

    class DiakomisAitimaton(BaseHTTPRequestHandler):
        """Implements only the local Ollama endpoints used by the analyzer."""

        def do_GET(self) -> None:
            """Returns a mocked local model manifest or version."""
            if self.path == "/api/tags":
                _steile(self, katastasi.etiketes)
            elif self.path == "/api/version":
                _steile(self, katastasi.ekdosi)
            else:
                self.send_error(404)

        def do_POST(self) -> None:
            """Records request bodies and returns configured JSON responses."""
            megethos = int(self.headers.get("Content-Length", "0"))
            somataki = self.rfile.read(megethos)
            try:
                aitima = cast(dict[str, object], json.loads(somataki))
            except (json.JSONDecodeError, TypeError):
                aitima = {}
            katastasi.aitimata.append((self.path, aitima))
            if self.path == "/api/show":
                _steile(self, katastasi.emfanisi)
            elif self.path == "/api/generate":
                if katastasi.anakateythynsi_generate:
                    self.send_response(302)
                    self.send_header("Location", "http://example.invalid/collect")
                    self.end_headers()
                elif katastasi.bytes_apantisis is not None:
                    self.send_response(200)
                    self.send_header(
                        "Content-Length", str(len(katastasi.bytes_apantisis))
                    )
                    self.end_headers()
                    self.wfile.write(katastasi.bytes_apantisis)
                else:
                    _steile(
                        self,
                        {
                            "model": KLEIDI_DOKIMIS,
                            "done": True,
                            "response": json.dumps(katastasi.paragomeno),
                        },
                    )
            else:
                self.send_error(404)

        def log_message(self, _format: str, *_args: object) -> None:
            """Suppresses noisy HTTP server logs during tests."""

    def _steile(diakomis, somataki: object) -> None:
        """Writes one JSON response for the current mocked request."""
        somataki = json.dumps(somataki).encode("utf-8")
        diakomis.send_response(200)
        diakomis.send_header("Content-Type", "application/json")
        diakomis.send_header("Content-Length", str(len(somataki)))
        diakomis.end_headers()
        diakomis.wfile.write(somataki)

    diakomistis = ThreadingHTTPServer(("127.0.0.1", 0), DiakomisAitimaton)
    nima = threading.Thread(target=diakomistis.serve_forever, daemon=True)
    nima.start()
    monkeypatch.setattr(
        topiko_modulo, "_vrese_eleftheri_port", lambda: diakomistis.server_port
    )
    monkeypatch.setattr(topiko_modulo.time, "sleep", lambda _seconds: None)
    try:
        yield katastasi, diakomistis.server_port
    finally:
        diakomistis.shutdown()
        diakomistis.server_close()
        nima.join(timeout=2)


class PaidikoDiadikasia:
    """Tracks owned server shutdown calls and writes its cloud mode log."""

    def __init__(self, stdout: object, epiloges: dict[str, object]) -> None:
        self.termatise = False
        self.termatistike = False
        self.skotothike = False
        self.perimene = False
        self.epiloges = epiloges
        self.epivoli_timeout = False
        stdout.write(b"Ollama cloud disabled: true\n")  # type: ignore[attr-defined]
        stdout.flush()  # type: ignore[attr-defined]

    def poll(self) -> int | None:
        """Returns whether the owned child is still running."""
        return 0 if self.termatise else None

    def terminate(self) -> None:
        """Marks the owned child as terminated."""
        self.termatistike = True
        self.termatise = True

    def wait(self, timeout: float | None = None) -> int:
        """Records the child wait and returns a successful exit status."""
        del timeout
        if self.epivoli_timeout and not self.skotothike:
            raise topiko_modulo.subprocess.TimeoutExpired("ollama", 2)
        self.perimene = True
        return 0

    def kill(self) -> None:
        """Marks the child as force-killed."""
        self.skotothike = True
        self.termatise = True


@pytest.fixture
def diadikasia_synthetiki(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[tuple[list[object], Path]]:
    """Replaces process creation while preserving real loopback HTTP."""
    paidika: list[object] = []
    ektelesimo = tmp_path / "ollama"
    ektelesimo.write_text("synthetic test executable", encoding="utf-8")

    def _ekkinise_paidiko(_entoli, **epiloges: object) -> PaidikoDiadikasia:
        """Creates a tracked mock child using the production Popen contract."""
        paidiko = PaidikoDiadikasia(epiloges["stdout"], epiloges)
        paidika.append(paidiko)
        return paidiko

    monkeypatch.setattr(topiko_modulo.subprocess, "Popen", _ekkinise_paidiko)
    yield paidika, ektelesimo


class ApantisiHTTP:
    """Supplies a deterministic HTTP response to the local transport helper."""

    def __init__(
        self, katastasi_http: int, epikefalida: str | None, somataki: bytes
    ) -> None:
        self.status = katastasi_http
        self.epikefalida = epikefalida
        self.somataki = somataki

    def getheader(self, _name: str) -> str | None:
        """Returns the configured content length."""
        return self.epikefalida

    def read(self, limit: int) -> bytes:
        """Returns no more than the requested bounded number of bytes."""
        return self.somataki[:limit]


def _dedomena() -> dict[str, object]:
    """Returns synthetic report data with normalized evidence and score gates."""
    return {
        "leitourgia": "live",
        "synola": {"minimata_xristi": 7, "tokens": None},
        "axiologisi": {
            "diathesimi": False,
            "synoliko": None,
            "diastaseis": [{"id": "scope_acceptance", "bathmos": None}],
        },
        "eyrimata": [],
        "deigmata": [
            {
                "id": "prompt-1",
                "pigi": "Claude Code",
                "synedria": "private-session-id",
                "rolos": "user",
                "eidos": "prompt",
                "keimeno": "Please define acceptance criteria. password=secretvalue",
                "locator": "private-session.jsonl:4",
                "imerominia": "2026-10-25",
            },
            {
                "id": "assistant-1",
                "pigi": "Claude Code",
                "synedria": "private-session-id",
                "rolos": "assistant",
                "eidos": "response",
                "keimeno": "I will test the implementation.",
                "locator": "private-session.jsonl:5",
                "imerominia": "2026-10-25",
            },
        ],
        "kalypsi_analysi": {"epilegmena": 2, "diathesima": 2, "perikopi": False},
    }


@pytest.mark.parametrize(
    ("modelo", "egkyro"),
    [("qwen3:8b", True), ("qwen3:8b-cloud", False), ("https://host/model", False)],
)
def test_epikyrwse_onoma_modelou(modelo: str, egkyro: bool) -> None:
    """Accepts local identifiers while rejecting cloud or URL forms."""
    if egkyro:
        assert topiko_modulo._epikyrwse_onoma_modelou(modelo) == modelo
    else:
        with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
            topiko_modulo._epikyrwse_onoma_modelou(modelo)


def test_epikyrwse_onoma_modelou_aporriptei_mi_keimeno() -> None:
    """Rejects non-string identifiers before process startup."""
    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
        topiko_modulo._epikyrwse_onoma_modelou(cast(str, None))


def test_vrese_ektelesimo_elegxei_epikalipsi_kai_elleipousa_diadromi(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Uses an explicit file path or errors instead of installing Ollama."""
    ektelesimo = tmp_path / "ollama.exe"
    ektelesimo.write_text("synthetic", encoding="utf-8")
    assert topiko_modulo._vrese_ektelesimo(ektelesimo) == str(ektelesimo.resolve())
    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
        topiko_modulo._vrese_ektelesimo(tmp_path / "missing.exe")
    monkeypatch.setattr(topiko_modulo.shutil, "which", lambda _name: str(ektelesimo))
    assert topiko_modulo._vrese_ektelesimo(None) == str(ektelesimo)
    monkeypatch.setattr(topiko_modulo.shutil, "which", lambda _name: None)
    with pytest.raises(
        topiko_modulo.SfalmaTopikisAnalysis, match="download it automatically"
    ):
        topiko_modulo._vrese_ektelesimo(None)


def test_analysi_topika_tyligei_aprosdokita_topika_sfalmata(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Turns unexpected startup errors into a local-analysis exception."""
    paidika, ektelesimo = diadikasia_synthetiki
    monkeypatch.setattr(
        topiko_modulo,
        "_perimene_topiko_server",
        lambda *_args: (_ for _ in ()).throw(OSError("local log error")),
    )
    with pytest.raises(
        topiko_modulo.SfalmaTopikisAnalysis, match="Local analysis failed"
    ):
        topiko_modulo.analysi_topika(_dedomena(), KLEIDI_DOKIMIS, ektelesimo)
    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


def test_ekkinise_ollama_anaferi_apotyxia_ekkinisis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cleans the temporary launch log and raises a targeted process error."""
    monkeypatch.setattr(
        topiko_modulo.subprocess,
        "Popen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("spawn failure")),
    )
    with pytest.raises(
        topiko_modulo.SfalmaTopikisAnalysis, match="Could not start the local"
    ):
        topiko_modulo._ekkinise_ollama("ollama")


def test_perimene_topiko_server_diakoptei_an_paidiko_termatisei() -> None:
    """Does not wait on an HTTP listener after the owned child exits."""
    paidiko = PaidikoDiadikasia(io.BytesIO(), {})
    paidiko.termatise = True
    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis, match="server exited"):
        topiko_modulo._perimene_topiko_server(paidiko, 1234, io.BytesIO())


def test_perimene_topiko_server_ligei_xoris_ygeia_i_sima_nefelis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fails closed when the isolated child does not become verifiably local."""
    paidiko = PaidikoDiadikasia(io.BytesIO(), {})
    chronoi = iter((0.0, 0.0, 0.06, 0.07, 1.0))
    monkeypatch.setattr(topiko_modulo.time, "monotonic", lambda: next(chronoi))
    monkeypatch.setattr(topiko_modulo.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(topiko_modulo, "OLLAMA_STARTUP_DEUTEROLEPTA", 0.05)
    monkeypatch.setattr(
        topiko_modulo,
        "_kane_aitima_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            topiko_modulo.SfalmaTopikisAnalysis("not ready")
        ),
    )
    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis, match="cloud"):
        topiko_modulo._perimene_topiko_server(paidiko, 1234, io.BytesIO())


def test_nefeliki_katagrafi_sfalmata_anagnosis_apotyxanoun_asfales() -> None:
    """Treats unreadable child startup logs as unverified cloud state."""

    class KatagrafiMeSfalma(io.BytesIO):
        """Raises a filesystem-style error on log inspection."""

        def seek(self, *_args: object, **_kwargs: object) -> int:
            """Simulates an inaccessible child log."""
            raise OSError("log unavailable")

    assert not topiko_modulo._cloud_apenergopoiimeno(KatagrafiMeSfalma())


def test_pare_deigmata_paraleipei_mi_egkyra_diplotypa_kai_mi_anthropina_aitimata() -> (
    None
):
    """Keeps bounded redacted rows and rejects ambiguous evidence identities."""
    grammes = [
        [],
        {"id": "duplicate", "rolos": "user", "eidos": "prompt"},
        {"id": "duplicate", "rolos": "user", "eidos": "prompt"},
        {"id": "bad", "rolos": "system", "eidos": "prompt"},
        {
            "id": "internal",
            "pigi": "Claude",
            "synedria": "s1",
            "rolos": "user",
            "eidos": "prompt",
            "keimeno": "internal",
            "locator": "private:1",
            "origin": {"kind": "task"},
        },
        {
            "id": "safe",
            "pigi": "Claude",
            "synedria": "s1",
            "rolos": "user",
            "eidos": "prompt",
            "keimeno": "password=secretvalue",
            "locator": "private:2",
        },
        {
            "id": "empty",
            "pigi": "Claude",
            "synedria": "s1",
            "rolos": "assistant",
            "eidos": "response",
            "keimeno": "",
            "locator": "private:3",
        },
    ]

    deigmata = topiko_modulo._pare_deigmata(grammes)

    assert [eggrafi["id"] for eggrafi in deigmata] == ["safe"]
    assert deigmata[0]["excerpt"] == "password=[REDACTED]"
    assert "private:2" not in json.dumps(
        [
            {
                kleidi: timi
                for kleidi, timi in deigmata[0].items()
                if not kleidi.startswith("_")
            }
        ]
    )


def test_pare_deigmata_epikyroni_simadia_proelefsis() -> None:
    """Rejects known agent and sidechain markers while retaining human markers."""
    vasi = {
        "id": "prompt",
        "pigi": "Claude",
        "synedria": "s1",
        "rolos": "user",
        "eidos": "prompt",
        "keimeno": "A human prompt.",
        "locator": "s.jsonl:1",
    }
    for sima in (
        {"promptSource": "subagent"},
        {"turnOrigin": "local_agent"},
        {"userType": "internal"},
        {"agentId": "child-agent"},
        {"isSidechain": True},
        {"parentSessionId": "root"},
    ):
        assert topiko_modulo._pare_deigmata([{**vasi, **sima}]) == []
    assert len(topiko_modulo._pare_deigmata([{**vasi, "origin": {"kind": "cli"}}])) == 1
    assert topiko_modulo._pare_deigmata(None) == []
    assert not topiko_modulo._apodosi_einai_anthropini(
        {"rolos": "assistant", "eidos": "prompt"}
    )
    assert not topiko_modulo._apodosi_einai_anthropini(
        {"rolos": "user", "eidos": "prompt", "actor": False}
    )
    assert not topiko_modulo._apodosi_einai_anthropini(
        {"rolos": "user", "eidos": "prompt", "origin": "task"}
    )
    assert not topiko_modulo._apodosi_einai_anthropini(
        {"rolos": "user", "eidos": "prompt", "origin": {"kind": "task"}}
    )
    assert not topiko_modulo._apodosi_einai_anthropini(
        {"rolos": "user", "eidos": "prompt", "userType": False}
    )
    assert not topiko_modulo._apodosi_einai_anthropini(
        {"rolos": "user", "eidos": "prompt", "agent": True}
    )


def test_apodosi_apo_rolous_derives_author_only_from_cited_source_roles() -> None:
    """Derives attribution deterministically from validated evidence roles."""
    xristis = {"role": "user", "kind": "prompt"}
    voithos = {"role": "assistant", "kind": "response"}
    klisi_ergaleiou = {"role": "tool", "kind": "tool_call"}
    apotelesma_ergaleiou = {"role": "tool", "kind": "tool_result"}
    assert topiko_modulo._apodosi_apo_rolous([xristis]) == "human_prompt"
    assert topiko_modulo._apodosi_apo_rolous([voithos, klisi_ergaleiou]) == "agent"
    assert topiko_modulo._apodosi_apo_rolous([apotelesma_ergaleiou]) == "environment"
    assert topiko_modulo._apodosi_apo_rolous([xristis, voithos]) == "unknown"
    assert topiko_modulo._apodosi_apo_rolous(
        [voithos, apotelesma_ergaleiou]
    ) == "unknown"
    assert topiko_modulo._apodosi_apo_rolous([]) == "unknown"


def test_epikyrwse_proza_periorizei_keimeno_kai_aporriptei_arithmous() -> None:
    """Flattens control whitespace and rejects empty, long, numeric, or wrong text."""
    assert topiko_modulo._epikyrwse_proza("A\n safe note", 20, "observation") == (
        "A safe note"
    )
    for mi_egkyro in ("", "mentions 3 outcomes", "too long"):
        with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
            topiko_modulo._epikyrwse_proza(mi_egkyro, 2, "observation")
    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
        topiko_modulo._epikyrwse_proza(cast(str, None), 20, "observation")


@pytest.mark.parametrize(
    ("katastasi_http", "epikefalida", "somataki", "prokalei_sfalma"),
    [
        (302, "2", b"{}", True),
        (200, "bad", b"{}", True),
        (200, str(topiko_modulo.MEGISTO_APANTISIS_BYTES + 1), b"", True),
        (200, None, b"x" * (topiko_modulo.MEGISTO_APANTISIS_BYTES + 1), True),
        (200, None, b"\xff", True),
        (200, None, b"{", True),
        (200, None, b"[]", True),
        (200, "12", b'{"ok":true}', False),
    ],
    ids=[
        "redirect",
        "bad-content-length",
        "large-declared-length",
        "large-body",
        "invalid-utf8",
        "invalid-json",
        "non-object",
        "valid-json",
    ],
)
def test_kane_aitima_json_epikyroni_katastasi_megethos_kai_json(
    monkeypatch: pytest.MonkeyPatch,
    katastasi_http: int,
    epikefalida: str | None,
    somataki: bytes,
    prokalei_sfalma: bool,
) -> None:
    """Rejects redirects, oversized and malformed responses on the HTTP boundary."""
    apantisi = ApantisiHTTP(katastasi_http, epikefalida, somataki)
    syndeseis: list[dict[str, object]] = []

    class SyndesiSynthetiki:
        """Captures a direct HTTP request without contacting a service."""

        def __init__(self, xost: str, porta: int, timeout: float) -> None:
            syndeseis.append(
                {"host": xost, "port": porta, "timeout": timeout, "closed": False}
            )

        def request(self, *_args: object, **_kwargs: object) -> None:
            """Accepts the fixed localhost request."""

        def getresponse(self) -> ApantisiHTTP:
            """Returns the test-specific response."""
            return apantisi

        def close(self) -> None:
            """Records transport cleanup."""
            syndeseis[-1]["closed"] = True

    monkeypatch.setattr(topiko_modulo.http.client, "HTTPConnection", SyndesiSynthetiki)
    if prokalei_sfalma:
        with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
            topiko_modulo._kane_aitima_json("GET", 1234, "/api/tags", None, 0)
    else:
        assert topiko_modulo._kane_aitima_json("GET", 1234, "/api/tags", None, 0) == {
            "ok": True
        }
    assert syndeseis[-1]["host"] == "127.0.0.1"
    assert syndeseis[-1]["timeout"] == 0.1
    assert syndeseis[-1]["closed"] is True


def test_kane_aitima_json_tyligei_sfalmata_ypodosoxis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Wraps transport errors while closing the connection."""
    syndeseis: list[bool] = []

    class SyndesiSynthetiki:
        """Raises before a request can leave the loopback client."""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def request(self, *_args: object, **_kwargs: object) -> None:
            """Raises a local socket error."""
            raise OSError("socket unavailable")

        def close(self) -> None:
            """Records transport cleanup."""
            syndeseis.append(True)

    monkeypatch.setattr(topiko_modulo.http.client, "HTTPConnection", SyndesiSynthetiki)
    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis, match="communicate safely"):
        topiko_modulo._kane_aitima_json("GET", 1234, "/api/tags", None, 1)
    assert syndeseis == [True]


def test_epikyrwse_modelo_aporriptei_elleiponta_kai_apomakrysmeni_dilosi(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
) -> None:
    """Requires one installed digest and a local non-cloud model base."""
    katastasi, porta = topiko_synthetiko
    egkyro = {
        "models": [
            {
                "name": KLEIDI_DOKIMIS,
                "digest": "a" * 64,
                "size": 100,
                "details": {"format": "gguf"},
            }
        ]
    }
    etiketες_modelou: list[dict[str, object]] = [
        {"models": []},
        {"models": [*egkyro["models"], *egkyro["models"]]},
    ]
    for etiketes in etiketες_modelou:
        with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis, match="manifest"):
            topiko_modulo._epikyrwse_topiko_modelo(porta, KLEIDI_DOKIMIS, etiketes)
    katastasi.emfanisi = {
        "details": {"format": "gguf"},
        "modelfile": "FROM https://models.example/model\n",
    }
    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis, match="local GGUF"):
        topiko_modulo._epikyrwse_topiko_modelo(porta, KLEIDI_DOKIMIS, egkyro)


def test_diavase_ekdosi_apaitiei_ekdosi_paroxou() -> None:
    """Rejects missing API versions instead of claiming a completed analysis."""
    assert topiko_modulo._diavase_ekdosi({"version": " 0.40.11 "}) == "0.40.11"
    for somataki in ({}, {"version": ""}, {"version": 40}):
        with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
            topiko_modulo._diavase_ekdosi(somataki)


@pytest.mark.parametrize(
    "apantisi",
    [
        {"done": False, "model": KLEIDI_DOKIMIS, "response": "{}"},
        {"done": True, "model": "different", "response": "{}"},
        {"done": True, "model": KLEIDI_DOKIMIS},
        {"done": True, "model": KLEIDI_DOKIMIS, "response": "not-json"},
        {"done": True, "model": KLEIDI_DOKIMIS, "response": "[]"},
    ],
    ids=["not-done", "wrong-model", "missing-response", "invalid-json", "non-object"],
)
def test_kane_analysh_aporriptei_ellipi_i_adiatakti_apantisi(
    monkeypatch: pytest.MonkeyPatch, apantisi: dict[str, object]
) -> None:
    """Requires a completed generation from the selected model and JSON object."""
    monkeypatch.setattr(topiko_modulo, "_kane_aitima_json", lambda *_args: apantisi)
    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
        topiko_modulo._kane_analysh(1234, KLEIDI_DOKIMIS, [])


def test_kane_analysh_xrisimopoiei_idioktito_paidiko_epopteia_prothesmias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Terminates only its owned server when inference exceeds the deadline."""
    monkeypatch.setattr(topiko_modulo, "OLLAMA_GENERATE_DEUTEROLEPTA", 0.01)

    def aitima_argoy(*_args: object) -> dict[str, object]:
        """Simulates a response that keeps making socket-level progress."""
        import time as modulo_xronou

        modulo_xronou.sleep(0.05)
        raise topiko_modulo.SfalmaTopikisAnalysis("transport timed out")

    monkeypatch.setattr(topiko_modulo, "_kane_aitima_json", aitima_argoy)

    class PaidikoMeSfalmaTermatismou(PaidikoDiadikasia):
        """Represents failure to signal an otherwise owned child process."""

        def terminate(self) -> None:
            """Raises the targeted OS failure handled by watchdog cleanup."""
            raise OSError("synthetic terminate failure")

    paidiko = PaidikoMeSfalmaTermatismou(io.BytesIO(), {})
    with pytest.raises(
        topiko_modulo.SfalmaTopikisAnalysis, match="150-second time limit"
    ):
        topiko_modulo._kane_analysh(1234, KLEIDI_DOKIMIS, [], paidiko=paidiko)
    assert paidiko.termatistike is False


def test_kane_analysh_aporriptei_apantisi_meta_tin_prothesmia(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Rejects a successful-looking response after the wall-clock deadline."""
    monkeypatch.setattr(topiko_modulo, "OLLAMA_GENERATE_DEUTEROLEPTA", 0.01)

    def aitima_kathysterimeno(*_args: object) -> dict[str, object]:
        """Simulates a response completed after the deadline watchdog fired."""
        import time as modulo_xronou

        modulo_xronou.sleep(0.05)
        return {
            "done": True,
            "model": KLEIDI_DOKIMIS,
            "response": json.dumps({"findings": []}),
        }

    monkeypatch.setattr(topiko_modulo, "_kane_aitima_json", aitima_kathysterimeno)
    paidiko = PaidikoDiadikasia(io.BytesIO(), {})
    with pytest.raises(
        topiko_modulo.SfalmaTopikisAnalysis, match="150-second time limit"
    ):
        topiko_modulo._kane_analysh(1234, KLEIDI_DOKIMIS, [], paidiko=paidiko)
    assert paidiko.termatistike is True


def test_analysi_topika_dinei_candidate_me_epikyromena_topika_tekmiria(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
) -> None:
    """Uses redacted normalized evidence and preserves metrics and score gates."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    arxika = _dedomena()
    apotelesma = topiko_modulo.analysi_topika(arxika, KLEIDI_DOKIMIS, ektelesimo)

    assert apotelesma["synola"] == arxika["synola"]
    assert apotelesma["axiologisi"] == arxika["axiologisi"]
    assert arxika["eyrimata"] == []
    assert apotelesma["analysi"]["methodos"] == "local"  # type: ignore[index]
    assert apotelesma["analysi"]["katastasi"] == "ok"  # type: ignore[index]
    assert apotelesma["analysi"]["modelo"] == "Ollama"  # type: ignore[index]
    assert apotelesma["analysi"]["model_id"] == KLEIDI_DOKIMIS  # type: ignore[index]
    assert apotelesma["analysi"]["provider_version"] == "0.40.11"  # type: ignore[index]
    assert apotelesma["eyrimata"][0]["katastasi"] == "candidate_only"  # type: ignore[index]
    assert apotelesma["eyrimata"][0]["vevaiotita"] == "low"  # type: ignore[index]
    tekmirio = apotelesma["eyrimata"][0]["tekmiria"][0]  # type: ignore[index]
    assert tekmirio["apospasma"] == "acceptance criteria"  # type: ignore[index]
    assert "The prompt asks" in apotelesma["eyrimata"][0]["keimeno"]  # type: ignore[index]
    assert "Keep the criteria" in apotelesma["eyrimata"][0]["protasi"]  # type: ignore[index]
    assert "secretvalue" not in json.dumps(apotelesma, ensure_ascii=False)
    assert len(paidika) == 1
    paidiko = cast(PaidikoDiadikasia, paidika[0])
    assert paidiko.termatistike is True and paidiko.perimene is True
    paragage_aitima_json = next(
        aitima for monopati, aitima in katastasi.aitimata if monopati == "/api/generate"
    )
    schema = cast(dict[str, object], paragage_aitima_json["format"])
    schema_properties = cast(dict[str, object], schema["properties"])
    finding_schema = cast(dict[str, object], schema_properties["findings"])
    finding_items = cast(dict[str, object], finding_schema["items"])
    finding_properties = cast(dict[str, object], finding_items["properties"])
    assert "attribution" not in finding_properties
    assert "attribution" not in cast(list[str], finding_items["required"])
    seiriopoiimeno = json.dumps(paragage_aitima_json, ensure_ascii=False)
    assert "secretvalue" not in seiriopoiimeno
    assert "private-session-id" not in seiriopoiimeno
    assert "private-session.jsonl" not in seiriopoiimeno
    assert "acceptance criteria" in seiriopoiimeno
    assert "I will test the implementation." in seiriopoiimeno
    epiloges_ekkinisis = paidiko.epiloges
    assert epiloges_ekkinisis["shell"] is False
    perivallon = cast(dict[str, str], epiloges_ekkinisis["env"])
    assert perivallon["OLLAMA_NO_CLOUD"] == "1"
    assert perivallon["OLLAMA_HOST"].startswith("127.0.0.1:")
    assert perivallon.get("HTTPS_PROXY") is None
    assert epiloges_ekkinisis["creationflags"] == getattr(
        topiko_modulo.subprocess, "CREATE_NO_WINDOW", 0
    )
    assert [monopati for monopati, _aitima in katastasi.aitimata] == [
        "/api/show",
        "/api/generate",
    ]


def test_analysi_topika_krata_eyrima_agent_me_apodosi_agent(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
) -> None:
    """Allows a candidate about agent text without assigning it to a human."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    dedomena = _dedomena()
    grammes = cast(list[dict[str, object]], dedomena["deigmata"])
    dedomena["deigmata"] = [{**grammes[1]}]
    katastasi.paragomeno = {
        "findings": [
            _eyrima_synthetiko(
                diastasi="context_handoffs",
                tekmiria=[{"id": "assistant-1", "quote": "I will test"}],
            )
        ]
    }

    apotelesma = topiko_modulo.analysi_topika(dedomena, KLEIDI_DOKIMIS, ektelesimo)

    assert apotelesma["eyrimata"][0]["drastis"] == "agent"  # type: ignore[index]
    assert any(monopati == "/api/generate" for monopati, _aitima in katastasi.aitimata)
    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


def test_analysi_topika_dexetai_apodosi_perivallontos_gia_apotelesma_ergaleiou(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
) -> None:
    """A tool result may support an environment finding, never a human one."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    dedomena = _dedomena()
    dedomena["deigmata"] = [
        {
            "id": "tool-result-1",
            "pigi": "Codex",
            "synedria": "session",
            "rolos": "tool",
            "eidos": "tool_result",
            "keimeno": "The command returned a permission error.",
            "locator": "session.jsonl:6",
            "imerominia": "2026-10-25",
        }
    ]
    katastasi.paragomeno = {
        "findings": [
            _eyrima_synthetiko(
                diastasi="debugging_evidence",
                tekmiria=[{"id": "tool-result-1", "quote": "permission error"}],
            )
        ]
    }

    apotelesma = topiko_modulo.analysi_topika(dedomena, KLEIDI_DOKIMIS, ektelesimo)

    assert apotelesma["eyrimata"][0]["drastis"] == "environment"  # type: ignore[index]
    assert (
        "does not attribute an outcome to a human"
        in apotelesma["eyrimata"][0][  # type: ignore[index]
            "eythyni"
        ]
    )
    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


@pytest.mark.parametrize(
    ("eggrafi", "apodosi", "quote"),
    [
        pytest.param(
            {
                "id": "assistant-only",
                "pigi": "Codex",
                "synedria": "synthetic-session",
                "rolos": "assistant",
                "eidos": "response",
                "keimeno": "I will compare the two proposals.",
                "locator": "session.jsonl:4",
                "imerominia": "2026-10-25",
            },
            "agent",
            "compare the two proposals",
            id="assistant-only",
        ),
        pytest.param(
            {
                "id": "tool-only",
                "pigi": "Codex",
                "synedria": "synthetic-session",
                "rolos": "tool",
                "eidos": "tool_result",
                "keimeno": "The command returned a permission error.",
                "locator": "session.jsonl:5",
                "imerominia": "2026-10-25",
            },
            "environment",
            "permission error",
            id="tool-result-only",
        ),
    ],
)
def test_analysi_topika_analyei_deigmata_xoris_anthropina_prompts(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
    eggrafi: dict[str, str],
    apodosi: str,
    quote: str,
) -> None:
    """Runs local analysis on agent/environment evidence without human prompts."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    dedomena = _dedomena()
    dedomena["deigmata"] = [eggrafi]
    synola_arxika = json.loads(json.dumps(dedomena["synola"]))
    axiologisi_arxiki = json.loads(json.dumps(dedomena["axiologisi"]))
    katastasi.paragomeno = {
        "findings": [
            _eyrima_synthetiko(
                diastasi="debugging_evidence",
                tekmiria=[{"id": eggrafi["id"], "quote": quote}],
            )
        ]
    }

    apotelesma = topiko_modulo.analysi_topika(dedomena, KLEIDI_DOKIMIS, ektelesimo)

    assert any(
        monopati == "/api/generate" for monopati, _aitima in katastasi.aitimata
    )
    assert apotelesma["eyrimata"][0]["drastis"] == apodosi  # type: ignore[index]
    assert apotelesma["synola"] == synola_arxika
    assert apotelesma["axiologisi"] == axiologisi_arxiki
    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


def test_analysi_topika_apokleiei_simadia_prompt_agent(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
) -> None:
    """Never sends user-role rows explicitly marked as internal agent instructions."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    dedomena = _dedomena()
    grammes = cast(list[dict[str, object]], dedomena["deigmata"])
    dedomena["deigmata"] = [
        {
            **grammes[0],
            "origin": {"kind": "task"},
            "keimeno": "internal agent task instructions",
        },
        grammes[1],
    ]
    katastasi.paragomeno = {"findings": []}

    topiko_modulo.analysi_topika(dedomena, KLEIDI_DOKIMIS, ektelesimo)

    paragage_aitima = next(
        somataki
        for monopati, somataki in katastasi.aitimata
        if monopati == "/api/generate"
    )
    assert "internal agent task instructions" not in str(paragage_aitima)
    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


def test_analysi_topika_periorizei_grammes_kai_xaraktires(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
) -> None:
    """Keeps submitted normalized text within the fixed sampling budget."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    dedomena = _dedomena()
    aitima = cast(list[dict[str, object]], dedomena["deigmata"])[0]
    dedomena["deigmata"] = [
        {
            **aitima,
            "id": f"prompt-{deiktis}",
            "synedria": f"session-{deiktis}",
            "keimeno": "a" * 1000,
        }
        for deiktis in range(45)
    ]
    katastasi.paragomeno = {"findings": []}

    topiko_modulo.analysi_topika(dedomena, KLEIDI_DOKIMIS, ektelesimo)

    aitima = next(
        aitima
        for monopati, aitima in katastasi.aitimata
        if aitima is not None and monopati == "/api/generate"
    )
    keimeno_prompt = str(aitima["prompt"])
    json_tekmirion = keimeno_prompt.split("Evidence JSON:\n", maxsplit=1)[-1]
    grammes = json.loads(json_tekmirion)
    assert len(grammes) == 40
    assert sum(len(eggrafi["excerpt"]) for eggrafi in grammes) <= 20_000
    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


@pytest.mark.parametrize(
    "apotelesma",
    [
        {
            "findings": [
                _eyrima_synthetiko(
                    tekmiria=[{"id": "unknown", "quote": "acceptance criteria"}]
                )
            ]
        },
        {
            "findings": [
                _eyrima_synthetiko(
                    tekmiria=[{"id": "prompt-1", "quote": "invented quotation"}]
                )
            ]
        },
        {"findings": [_eyrima_synthetiko(diastasi="unknown_dimension")]},
        {
            "findings": [
                _eyrima_synthetiko(
                    tekmiria=[{"id": "assistant-1", "quote": "I will test"}],
                    epipleon="forged",
                )
            ]
        },
        {"findings": [_eyrima_synthetiko(observation="The prompt has 3 examples.")]},
        {"findings": [_eyrima_synthetiko(action="Repeat this for 2 files.")]},
        {
            "findings": [
                _eyrima_synthetiko(
                    attribution="human_prompt",
                    tekmiria=[{"id": "prompt-1", "quote": "acceptance criteria"}],
                )
            ]
        },
        {
            "findings": [
                _eyrima_synthetiko(diastasi=diastasi)
                for diastasi in (
                    "scope_acceptance",
                    "context_handoffs",
                    "delegation_ownership",
                    "debugging_evidence",
                )
            ]
        },
    ],
)
def test_analysi_topika_aporriptei_mi_epikyromeno_apotelesma(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
    apotelesma: dict[str, object],
) -> None:
    """Rejects bad citations, attribution, dimensions and polarity claims."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    katastasi.paragomeno = apotelesma

    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
        topiko_modulo.analysi_topika(_dedomena(), KLEIDI_DOKIMIS, ektelesimo)

    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


def test_analysi_topika_epitrepei_growth_me_ypo_orous_anthropini_protasi(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
) -> None:
    """A growth proposal may be conditional without claiming a verified failure."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    dedomena = _dedomena()
    aitimata = cast(list[dict[str, object]], dedomena["deigmata"])
    aitimata[0]["keimeno"] = "Please clarify ownership and dependencies."
    katastasi.paragomeno = {
        "findings": [
            _eyrima_synthetiko(
                epipedo="growth",
                diastasi="delegation_ownership",
                tekmiria=[
                    {
                        "id": "prompt-1",
                        "quote": "clarify ownership and dependencies",
                    }
                ],
            )
        ]
    }

    apotelesma = topiko_modulo.analysi_topika(dedomena, KLEIDI_DOKIMIS, ektelesimo)

    assert apotelesma["eyrimata"][0]["epipedo"] == "growth"  # type: ignore[index]
    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


@pytest.mark.parametrize(
    "apotelesma_modelou",
    [
        {},
        {"findings": [None]},
        {"findings": [_eyrima_synthetiko(), _eyrima_synthetiko()]},
        {"findings": [_eyrima_synthetiko(tekmiria=[{"id": "prompt-1"}])]},
        {
            "findings": [
                _eyrima_synthetiko(tekmiria=[{"id": "prompt-1", "quote": "x" * 301}])
            ]
        },
        {
            "findings": [
                _eyrima_synthetiko(
                    tekmiria=[{"id": "prompt-1", "quote": "acceptance criteria"}] * 2
                )
            ]
        },
        {"findings": [_eyrima_synthetiko() for _deiktis in range(7)]},
    ],
    ids=[
        "missing-findings",
        "bad-finding-type",
        "duplicate-polarity-dimension",
        "malformed-citation",
        "long-quote",
        "duplicate-evidence-id",
        "too-many-findings",
    ],
)
def test_epikyrwse_apotelesma_aporriptei_mi_egkyres_protaseis(
    apotelesma_modelou: dict[str, object],
) -> None:
    """Rejects invalid schemas, duplicate claims and unbounded citations."""
    deigmata = topiko_modulo._pare_deigmata(_dedomena()["deigmata"])
    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
        topiko_modulo._epikyrwse_apotelesma(apotelesma_modelou, deigmata)


def test_epikyrwse_apotelesma_dexetai_agnosti_apodosi() -> None:
    """Computes unknown attribution when cited source roles are mixed."""
    dedomena = _dedomena()
    apotelesma_modelou = {
        "findings": [
            _eyrima_synthetiko(
                tekmiria=[
                    {"id": "prompt-1", "quote": "acceptance criteria"},
                    {"id": "assistant-1", "quote": "I will test"},
                ],
            )
        ]
    }
    eyrimata = topiko_modulo._epikyrwse_apotelesma(
        apotelesma_modelou, topiko_modulo._pare_deigmata(dedomena["deigmata"])
    )
    assert eyrimata[0]["attribution"] == "unknown"


def test_epikyrwse_apotelesma_aporriptei_model_authored_human_attribution(
) -> None:
    """A model cannot claim human authorship for a tool-result citation."""
    row_tool = {
        "id": "tool-result-1",
        "role": "tool",
        "kind": "tool_result",
        "excerpt": "The command returned a permission error.",
        "_source": "Codex",
        "_locator": "session.jsonl:6",
        "_session": "synthetic-session",
    }
    proposed = {
        "findings": [
            _eyrima_synthetiko(
                attribution="human_prompt",
                tekmiria=[
                    {"id": "tool-result-1", "quote": "permission error"}
                ],
            )
        ]
    }
    with pytest.raises(
        topiko_modulo.SfalmaTopikisAnalysis, match="invalid finding shape"
    ):
        topiko_modulo._epikyrwse_apotelesma(proposed, [row_tool])


def test_eyrimata_local_antikatastasi_idia_diastasi_kai_orio_epipedon() -> None:
    """Keeps local detail, replaces a duplicate rules candidate, and caps totals."""
    epikyromena = topiko_modulo._epikyrwse_apotelesma(
        {"findings": [_eyrima_synthetiko()]},
        topiko_modulo._pare_deigmata(_dedomena()["deigmata"]),
    )
    dedomena = {
        "eyrimata": [
            {
                "id": "R001",
                "epipedo": "strength",
                "diastasi": "scope_acceptance",
                "titlos": "Old rules candidate",
            },
            *[{"id": f"S{deiktis}", "epipedo": "strength"} for deiktis in range(4)],
            {"id": "INFO", "epipedo": "info"},
            {"id": "L001", "epipedo": "info"},
        ]
    }

    eyrimata = topiko_modulo._eyrimata_local(dedomena, epikyromena)

    dynates = [eggrafi for eggrafi in eyrimata if eggrafi["epipedo"] == "strength"]  # type: ignore[index]
    assert len(dynates) == 3
    assert dynates[0]["paragogos"] == topiko_modulo.LOCAL_GENERATOR  # type: ignore[index]
    assert all(
        not isinstance(eggrafi, dict) or eggrafi.get("titlos") != "Old rules candidate"
        for eggrafi in eyrimata
    )
    assert any(
        isinstance(eggrafi, dict) and eggrafi.get("epipedo") == "info"
        for eggrafi in eyrimata
    )
    assert any(
        isinstance(eggrafi, dict) and eggrafi.get("id") == "L002"
        for eggrafi in eyrimata
    )


def test_periorise_eyrimata_krata_agnostes_grammes_kai_orio_epipedon() -> None:
    """Caps findings without dimensions while preserving unrelated rows."""
    grammes: list[object] = [
        {"epipedo": "strength", "id": "S1"},
        "unstructured",
        {"epipedo": "growth", "id": "G1"},
        {"epipedo": "strength", "id": "S2"},
        {"epipedo": "strength", "id": "S3"},
        {"epipedo": "strength", "id": "S4"},
    ]
    periorismena = topiko_modulo._periorise_eyrimata(grammes)
    assert len(periorismena) == 5
    assert "unstructured" in periorismena


def test_antigrafo_tekmirion_apokryptei_mystika_kai_paraleipei_lathos_grammes() -> None:
    """Re-redacts returned normalized text without mutating the input."""
    arxiko = [{"keimeno": "password=secretvalue"}, 3, {"keimeno": None}]
    katharo = topiko_modulo._katharise_report_evidence(arxiko)
    assert katharo[0]["keimeno"] == "password=[REDACTED]"  # type: ignore[index]
    assert katharo[1] == 3
    assert topiko_modulo._katharise_report_evidence(None) == []
    arxiko_eggrafi = cast(dict[str, object], arxiko[0])
    assert arxiko_eggrafi["keimeno"] == "password=secretvalue"


def test_termatise_ollama_xeirizetai_termatismeno_paidiko_kai_sfalmata() -> None:
    """Leaves exited children alone and logs bounded cleanup failures."""
    termatise = PaidikoDiadikasia(io.BytesIO(), {})
    termatise.termatise = True
    topiko_modulo._termatise_ollama(termatise)
    assert termatise.termatistike is False

    class PaidikoMeSfalma:
        """Represents process APIs that fail during termination."""

        def __init__(self, prothesmia_meta_sfalma: bool) -> None:
            self.prothesmia_meta_sfalma = prothesmia_meta_sfalma

        def poll(self) -> int | None:
            """Reports the child still running."""
            return None

        def terminate(self) -> None:
            """Raises after a graceful-stop request."""
            if not self.prothesmia_meta_sfalma:
                raise OSError("terminate failed")

        def wait(self, timeout: float | None = None) -> int:
            """Raises timeout or cleanup error as configured."""
            del timeout
            if self.prothesmia_meta_sfalma:
                raise topiko_modulo.subprocess.TimeoutExpired("ollama", 2)
            raise OSError("wait failed")

        def kill(self) -> None:
            """Raises if the force-stop branch is unavailable."""
            raise OSError("kill failed")

    topiko_modulo._termatise_ollama(PaidikoMeSfalma(False))
    topiko_modulo._termatise_ollama(PaidikoMeSfalma(True))


@pytest.mark.parametrize(
    "modelo",
    ["qwen3:8b-cloud", "cloud", "ollama.com/library/qwen3:8b", "qwen3:8b\n"],
)
def test_analysi_topika_aporriptei_nefeliko_montelo_apo_ektelesi(
    diadikasia_synthetiki: tuple[list[object], Path],
    modelo: str,
) -> None:
    """Rejects cloud and malformed model identifiers before starting any child."""
    paidika, ektelesimo = diadikasia_synthetiki

    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
        topiko_modulo.analysi_topika(_dedomena(), modelo, ektelesimo)

    assert paidika == []


@pytest.mark.parametrize(
    "morfh",
    [
        {"format": "safetensors"},
        {"format": "gguf", "digest": "not-a-digest"},
        {"format": "gguf", "digest": "a" * 64, "size": 0},
    ],
)
def test_analysi_topika_aporriptei_mi_egkyro_topiko_manifest(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
    morfh: dict[str, object],
) -> None:
    """Fails before generation when the local GGUF manifest is not verifiable."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    katastasi.etiketes = {
        "models": [
            {
                "name": KLEIDI_DOKIMIS,
                "digest": morfh.get("digest", "a" * 64),
                "size": morfh.get("size", 100),
                "details": {"format": morfh["format"]},
            }
        ]
    }

    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis):
        topiko_modulo.analysi_topika(_dedomena(), KLEIDI_DOKIMIS, ektelesimo)

    assert not any(
        monopati == "/api/generate" for monopati, _aitima in katastasi.aitimata
    )
    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


def test_analysi_topika_den_akolouthei_anakateythynseis(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
) -> None:
    """Rejects a generate redirect instead of forwarding evidence to its target."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    katastasi.anakateythynsi_generate = True

    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis, match="HTTP 302"):
        topiko_modulo.analysi_topika(_dedomena(), KLEIDI_DOKIMIS, ektelesimo)

    assert sum(monopati == "/api/generate" for monopati, _ in katastasi.aitimata) == 1
    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


def test_analysi_topika_aporriptei_megali_apantisi(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
) -> None:
    """Bounds response bytes and cleans up the owned child after rejection."""
    katastasi, _porta = topiko_synthetiko
    paidika, ektelesimo = diadikasia_synthetiki
    katastasi.bytes_apantisis = b"x" * (topiko_modulo.MEGISTO_APANTISIS_BYTES + 1)

    with pytest.raises(topiko_modulo.SfalmaTopikisAnalysis, match="too large"):
        topiko_modulo.analysi_topika(_dedomena(), KLEIDI_DOKIMIS, ektelesimo)

    assert cast(PaidikoDiadikasia, paidika[0]).termatistike is True


def test_analysi_topika_termatizei_me_kill_an_paidiko_den_termatisei(
    topiko_synthetiko: tuple[DiakomisHTTP, int],
    diadikasia_synthetiki: tuple[list[object], Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Kills only the owned process after graceful termination times out."""
    katastasi, _porta = topiko_synthetiko
    del katastasi
    paidika, ektelesimo = diadikasia_synthetiki
    arxiki_thesi = cast(
        Callable[..., PaidikoDiadikasia], topiko_modulo.subprocess.Popen
    )

    def _ekkinise_paidiko(entoli: list[str], **epiloges: object) -> PaidikoDiadikasia:
        """Creates a child that needs the bounded kill fallback."""
        paidiko = cast(PaidikoDiadikasia, arxiki_thesi(entoli, **epiloges))
        paidiko.epivoli_timeout = True
        return paidiko

    monkeypatch.setattr(topiko_modulo.subprocess, "Popen", _ekkinise_paidiko)

    topiko_modulo.analysi_topika(_dedomena(), KLEIDI_DOKIMIS, ektelesimo)

    paidiko = cast(PaidikoDiadikasia, paidika[0])
    assert paidiko.termatistike is True
    assert paidiko.skotothike is True
    assert paidiko.perimene is True
