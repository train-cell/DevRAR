"""Synthetic tests for the explicit OpenAI-compatible cloud boundary."""

from __future__ import annotations

import http.client
import json
from collections.abc import Mapping
from typing import cast

import pytest

from devrar import cloud as cloud_modulo

KLEIDI_DOKIMIS = "synthetic-model"
ENDPOINT = "https://api.synthetic.invalid/v1/chat/completions"
ONOMA_ENV = "DEVRAR_SYNTHETIC_KEY"
KLEIDI_TIMI = "synthetic-secret-key"


def _eyrima() -> dict[str, object]:
    """Returns valid synthetic candidate output with one exact citation."""
    return {
        "polarity": "strength",
        "dimension_id": "scope_acceptance",
        "observation": "The prompt names acceptance criteria.",
        "action": "Keep the criteria beside verification.",
        "alternative": "The wording may be exploratory.",
        "counterevidence": "No execution evidence is shown.",
        "evidence": [{"id": "ev-1", "quote": "acceptance criteria"}],
    }


def _dedomena() -> dict[str, object]:
    """Returns a synthetic report containing private evidence and aggregates."""
    return {
        "leitourgia": "live",
        "synola": {"synedries": 9, "tokens": None},
        "axiologisi": {"synoliko": None},
        "deigmata": [
            {
                "id": "ev-1",
                "pigi": "private-source",
                "synedria": "private-session",
                "rolos": "user",
                "eidos": "prompt",
                "keimeno": "Define acceptance criteria.",
                "locator": "private-path.jsonl:8",
                "actor": "human",
            },
            {
                "id": "ev-2",
                "pigi": "private-source",
                "synedria": "private-session",
                "rolos": "assistant",
                "eidos": "response",
                "keimeno": "I will inspect the design.",
                "locator": "private-path.jsonl:9",
            },
        ],
        "eyrimata": [],
    }


class ApantisiDikomis:
    """Provides a bounded fake HTTPS response."""

    def __init__(self, katastasi: int, somataki: bytes) -> None:
        self.status = katastasi
        self.somataki = somataki
        self.epikefalides = {"Content-Length": str(len(somataki))}

    def getheader(self, onoma: str) -> str | None:
        """Returns the requested response header."""
        return self.epikefalides.get(onoma)

    def read(self, orio: int) -> bytes:
        """Returns no more than the requested bytes."""
        return self.somataki[:orio]


class SyndesiDikomis:
    """Records one fake HTTPS request without opening a socket."""

    def __init__(self, xost: str, timeout: float) -> None:
        self.xost = xost
        self.timeout = timeout
        self.aitima: tuple[str, str, Mapping[str, str], bytes] | None = None
        self.apantisi = ApantisiDikomis(200, b"")
        self.kleisto = False
        self.sfalma_aitimatos: OSError | None = None
        self.sfalma_kleisimatos = False

    def request(
        self,
        method: str,
        path: str,
        body: bytes,
        headers: Mapping[str, str],
    ) -> None:
        """Records the request for contract and privacy assertions."""
        if self.sfalma_aitimatos is not None:
            raise self.sfalma_aitimatos
        self.aitima = (method, path, headers, body)

    def getresponse(self) -> ApantisiDikomis:
        """Returns the configured response."""
        return self.apantisi

    def close(self) -> None:
        """Records connection cleanup."""
        self.kleisto = True
        if self.sfalma_kleisimatos:
            raise OSError("synthetic private close failure")


class DiakomistisDikomis(list[SyndesiDikomis]):
    """Stores one reusable response template for future fake connections."""

    def __init__(self) -> None:
        super().__init__()
        self.apantisi_epomeni = ApantisiDikomis(200, b"")
        self.close_error = False


@pytest.fixture
def fake_https(monkeypatch: pytest.MonkeyPatch) -> DiakomistisDikomis:
    """Installs an in-memory HTTPS transport and returns captured connections."""
    syndeseis = DiakomistisDikomis()

    def ftiaxe_syndesi(
        xost: str, _port: int | None = None, timeout: float = 0.0
    ) -> SyndesiDikomis:
        """Creates one captured fake connection."""
        syndesi = SyndesiDikomis(xost, timeout)
        syndesi.apantisi = syndeseis.apantisi_epomeni
        syndesi.sfalma_kleisimatos = syndeseis.close_error
        syndeseis.append(syndesi)
        return syndesi

    monkeypatch.setattr(http.client, "HTTPSConnection", ftiaxe_syndesi)
    monkeypatch.setenv(ONOMA_ENV, KLEIDI_TIMI)
    return syndeseis


def _vale_apantisi(
    syndeses: DiakomistisDikomis, apotelesma: object, katastasi: int = 200
) -> None:
    """Configures one synthetic Chat Completions response body."""
    periexomeno = json.dumps(_response_body(apotelesma)).encode("utf-8")
    syndeses.apantisi_epomeni = ApantisiDikomis(katastasi, periexomeno)


def _response_body(periexomeno: object) -> dict[str, object]:
    """Wraps synthetic structured content in one Chat Completion choice."""
    return {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": json.dumps(periexomeno),
                },
            }
        ]
    }


def test_analysi_cloud_aporriptei_xoris_opt_in_prin_env_i_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Explicit denial wins before key lookup or transport construction."""

    def apogorevmeni_syndesi(*_orismata: object, **_epiloges: object) -> None:
        """Fails if denied cloud analysis reaches the network boundary."""
        raise AssertionError("No connection should be created")

    monkeypatch.delenv(ONOMA_ENV, raising=False)
    monkeypatch.setattr(http.client, "HTTPSConnection", apogorevmeni_syndesi)

    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis, match="explicit opt-in"):
        cloud_modulo.analysi_cloud(
            _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, onoma_env_key=ONOMA_ENV
        )


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://api.synthetic.invalid/v1/chat/completions",
        "https://user:password@api.synthetic.invalid/v1/chat/completions",
        "https://api.synthetic.invalid/v1/chat/completions?x=1",
        "https://api.synthetic.invalid/v1/chat/completions?",
        "https://api.synthetic.invalid/v1/chat/completions#fragment",
        "https://api.synthetic.invalid/v1/chat/completions#",
        "https://api.synthetic.invalid/v1/other",
        "",
        "https://api.synthetic.invalid:invalid/v1/chat/completions",
        "https://",
    ],
)
def test_analysi_cloud_aporriptei_endpoint_mi_asfales(
    fake_https: DiakomistisDikomis, endpoint: str
) -> None:
    """Only an explicit HTTPS chat-completions endpoint is accepted."""
    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis):
        cloud_modulo.analysi_cloud(
            _dedomena(),
            KLEIDI_DOKIMIS,
            endpoint,
            epitrepetai=True,
            onoma_env_key=ONOMA_ENV,
        )
    assert fake_https == []


@pytest.mark.parametrize("onoma_env_key", ["", "NOT VALID", "KEY-NAME"])
def test_analysi_cloud_aporriptei_mi_egkyro_onoma_env(
    fake_https: DiakomistisDikomis, onoma_env_key: str
) -> None:
    """Environment variable names are validated without transport access."""
    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis):
        cloud_modulo.analysi_cloud(
            _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, True, onoma_env_key
        )
    assert fake_https == []


@pytest.mark.parametrize("modelo", ["", " padded ", "unsafe\nmodel", "x" * 193])
def test_analysi_cloud_aporriptei_mi_egkyro_modelo(
    fake_https: DiakomistisDikomis, modelo: str
) -> None:
    """Malformed model identifiers are rejected before transport access."""
    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis):
        cloud_modulo.analysi_cloud(_dedomena(), modelo, ENDPOINT, True, ONOMA_ENV)
    assert fake_https == []


def test_analysi_cloud_aporriptei_elleipon_i_mi_asfali_key(
    monkeypatch: pytest.MonkeyPatch, fake_https: DiakomistisDikomis
) -> None:
    """Missing and control-character keys fail before opening HTTPS."""
    for kleidi in (None, "key\r\nInjected: value"):
        if kleidi is None:
            monkeypatch.delenv(ONOMA_ENV, raising=False)
        else:
            monkeypatch.setenv(ONOMA_ENV, kleidi)
        with pytest.raises(cloud_modulo.SfalmaCloudAnalysis):
            cloud_modulo.analysi_cloud(
                _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
            )
    assert fake_https == []


def test_analysi_cloud_stelnei_allowlist_kai_epikyromena_tekmiria(
    fake_https: DiakomistisDikomis,
) -> None:
    """Sends only redacted evidence and preserves report metrics and score gates."""
    _vale_apantisi(fake_https, {"findings": [_eyrima()]})
    arxika = _dedomena()
    grammes = cast(list[dict[str, object]], arxika["deigmata"])
    grammes[0]["keimeno"] = (
        "Define acceptance criteria and key=sk-12345678901234567890123"
    )

    apotelesma = cloud_modulo.analysi_cloud(
        arxika, KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
    )

    assert len(fake_https) == 1
    syndesi = fake_https[0]
    assert syndesi.xost == "api.synthetic.invalid"
    assert syndesi.timeout <= cloud_modulo.CLOUD_TIMEOUT_SECONDS <= 150
    assert syndesi.kleisto
    aitima = syndesi.aitima
    assert aitima is not None
    method, path, headers, body = aitima
    assert method == "POST"
    assert path == "/v1/chat/completions"
    assert headers["Authorization"] == f"Bearer {KLEIDI_TIMI}"
    payload = cast(dict[str, object], json.loads(body))
    minimata = cast(list[dict[str, object]], payload["messages"])
    assert payload["stream"] is False
    assert payload["n"] == 1
    structured = cast(dict[str, object], payload["response_format"])
    assert structured["type"] == "json_schema"
    schema_options = cast(dict[str, object], structured["json_schema"])
    assert schema_options["strict"] is True
    content = cast(str, minimata[1]["content"])
    evidence = cast(list[dict[str, str]], json.loads(content))
    assert evidence == [
        {
            "id": "ev-1",
            "role": "user",
            "kind": "prompt",
            "excerpt": "Define acceptance criteria and key=[REDACTED]",
        },
        {
            "id": "ev-2",
            "role": "assistant",
            "kind": "response",
            "excerpt": "I will inspect the design.",
        },
    ]
    assert "private-source" not in body.decode()
    assert "private-session" not in body.decode()
    assert "private-path" not in body.decode()
    assert "synola" not in body.decode()
    assert "sk-12345678901234567890123" not in body.decode()
    assert apotelesma["synola"] == arxika["synola"]
    assert apotelesma["axiologisi"] == arxika["axiologisi"]
    assert arxika["eyrimata"] == []
    analysi = cast(Mapping[str, object], apotelesma["analysi"])
    assert analysi["methodos"] == "cloud"
    assert analysi["provider"] == "openai_compatible"
    assert analysi["endpoint_host"] == "api.synthetic.invalid"
    assert analysi["model_id"] == KLEIDI_DOKIMIS
    assert "key" not in json.dumps(analysi).casefold()
    eyrimata = cast(list[dict[str, object]], apotelesma["eyrimata"])
    assert eyrimata[0]["paragogos"] == cloud_modulo.CLOUD_GENERATOR
    assert eyrimata[0]["drastis"] == "human_prompt"
    tekmiria = cast(list[dict[str, str]], eyrimata[0]["tekmiria"])
    assert tekmiria[0]["apospasma"] == "acceptance criteria"
    assert "cloud" in str(eyrimata[0]["keimeno"]).casefold()


@pytest.mark.parametrize("katastasi_http", [301, 302, 307, 400, 429, 500])
def test_analysi_cloud_aporriptei_redirects_kai_http_errors(
    fake_https: DiakomistisDikomis, katastasi_http: int
) -> None:
    """Redirects and provider errors are not retried or followed."""
    fake_https.apantisi_epomeni = ApantisiDikomis(
        katastasi_http, b"private server error"
    )

    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis) as sfalma:
        cloud_modulo.analysi_cloud(
            _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
        )

    assert len(fake_https) == 1
    assert fake_https[0].kleisto
    assert "private server error" not in str(sfalma.value)
    assert KLEIDI_TIMI not in str(sfalma.value)


def test_analysi_cloud_periorizei_rows_kai_apospasmata(
    fake_https: DiakomistisDikomis,
) -> None:
    """Only the shared bounded sample count and excerpt cap cross the boundary."""
    _vale_apantisi(fake_https, {"findings": []})
    dedomena = _dedomena()
    dedomena["deigmata"] = [
        {
            "id": f"row-{deiktis}",
            "pigi": "private-source",
            "synedria": "private-session",
            "rolos": "user",
            "eidos": "prompt",
            "keimeno": "x" * 600,
            "locator": f"private-{deiktis}",
            "actor": "human",
        }
        for deiktis in range(55)
    ]

    cloud_modulo.analysi_cloud(dedomena, KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV)

    aitima = fake_https[0].aitima
    assert aitima is not None
    payload = cast(dict[str, object], json.loads(aitima[3]))
    minimata = cast(list[dict[str, object]], payload["messages"])
    periexomeno = cast(str, minimata[1]["content"])
    deigmata = cast(list[dict[str, str]], json.loads(periexomeno))
    assert len(deigmata) == 40
    assert all(
        set(eggrafi) == {"id", "role", "kind", "excerpt"} for eggrafi in deigmata
    )
    assert all(len(eggrafi["excerpt"]) <= 500 for eggrafi in deigmata)
    assert sum(len(eggrafi["excerpt"]) for eggrafi in deigmata) <= 20_000


def test_analysi_cloud_aporriptei_timeout_xoris_retry(
    fake_https: DiakomistisDikomis, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A timeout becomes a typed safe error and does not create a retry."""

    def ftiaxe_syndesi(
        xost: str, _port: int | None = None, timeout: float = 0.0
    ) -> SyndesiDikomis:
        """Creates one transport that raises a synthetic timeout."""
        syndesi = SyndesiDikomis(xost, timeout)
        syndesi.sfalma_aitimatos = TimeoutError("synthetic private timeout")
        fake_https.append(syndesi)
        return syndesi

    monkeypatch.setattr(http.client, "HTTPSConnection", ftiaxe_syndesi)
    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis, match="safely"):
        cloud_modulo.analysi_cloud(
            _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
        )

    assert len(fake_https) == 1
    assert fake_https[0].kleisto


def test_analysi_cloud_aporriptei_megethos_request_prin_transport(
    fake_https: DiakomistisDikomis, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Oversized bounded request is rejected before opening a connection."""
    monkeypatch.setattr(cloud_modulo, "MAX_CLOUD_REQUEST_BYTES", 10)

    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis, match="size limit"):
        cloud_modulo.analysi_cloud(
            _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
        )
    assert fake_https == []


@pytest.mark.parametrize(
    "periexomeno",
    [b"not-json", b"[]", json.dumps({"choices": []}).encode(), b" " * 300_000],
    ids=["invalid-json", "non-object", "empty-choices", "oversized"],
)
def test_analysi_cloud_aporriptei_response_invalid_i_ypermegethes(
    fake_https: DiakomistisDikomis, periexomeno: bytes
) -> None:
    """Invalid or oversized non-streaming responses fail with a safe error."""
    fake_https.apantisi_epomeni = ApantisiDikomis(200, periexomeno)

    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis) as sfalma:
        cloud_modulo.analysi_cloud(
            _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
        )
    assert KLEIDI_TIMI not in str(sfalma.value)
    assert "not-json" not in str(sfalma.value)
    assert fake_https[0].kleisto


def test_analysi_cloud_aporriptei_response_ypermegethes_xoris_length(
    fake_https: DiakomistisDikomis,
) -> None:
    """Response bytes are capped even without Content-Length."""
    apantisi = ApantisiDikomis(200, b" " * (cloud_modulo.MAX_CLOUD_RESPONSE_BYTES + 1))
    apantisi.epikefalides.clear()
    fake_https.apantisi_epomeni = apantisi

    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis, match="size limit"):
        cloud_modulo.analysi_cloud(
            _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
        )
    assert fake_https[0].kleisto


def test_analysi_cloud_aporriptei_malformed_content_length(
    fake_https: DiakomistisDikomis,
) -> None:
    """Malformed response size metadata fails without reading arbitrary data."""
    apantisi = ApantisiDikomis(200, b"{}")
    apantisi.epikefalides["Content-Length"] = "unknown"
    fake_https.apantisi_epomeni = apantisi

    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis, match="size is invalid"):
        cloud_modulo.analysi_cloud(
            _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
        )
    assert fake_https[0].kleisto


def test_analysi_cloud_antimetopizei_close_error_xoris_key_leak(
    fake_https: DiakomistisDikomis,
) -> None:
    """Socket cleanup failure cannot replace the safe successful result."""
    _vale_apantisi(fake_https, {"findings": []})
    fake_https.close_error = True
    apotelesma = cloud_modulo.analysi_cloud(
        _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
    )
    assert cast(Mapping[str, object], apotelesma["analysi"])["katastasi"] == "ok"


@pytest.mark.parametrize(
    "response_body",
    [
        _response_body(
            {
                "findings": [
                    {**_eyrima(), "evidence": [{"id": "ev-1", "quote": "success"}]}
                ]
            }
        ),
        _response_body(
            {"findings": [{**_eyrima(), "evidence": [{"id": "missing", "quote": "x"}]}]}
        ),
        _response_body(
            {"findings": [{**_eyrima(), "observation": "There are 2 criteria."}]}
        ),
        _response_body({"findings": [{**_eyrima(), "attribution": "human"}]}),
        _response_body({"findings": "malformed"}),
        {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"role": "assistant", "content": "{}"},
                }
            ]
        },
        _response_body({"findings": []})
        | {
            "choices": [
                {"finish_reason": "stop", "message": {"role": "user", "content": "{}"}}
            ]
        },
        _response_body({"findings": []})
        | {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": None},
                }
            ]
        },
        _response_body({"findings": []})
        | {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "not-json"},
                }
            ]
        },
        _response_body([]),
    ],
    ids=[
        "non-exact-citation",
        "unknown-citation",
        "digits-in-prose",
        "model-attribution",
        "invalid-findings",
        "incomplete",
        "wrong-role",
        "missing-content",
        "invalid-content-json",
        "non-object-content",
    ],
)
def test_analysi_cloud_aporriptei_invalid_schema_i_citations(
    fake_https: DiakomistisDikomis, response_body: object
) -> None:
    """Only exact citations and allowed, non-scoring findings are accepted."""
    fake_https.apantisi_epomeni = ApantisiDikomis(
        200, json.dumps(response_body).encode("utf-8")
    )

    with pytest.raises(cloud_modulo.SfalmaCloudAnalysis):
        cloud_modulo.analysi_cloud(
            _dedomena(), KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
        )


def test_analysi_cloud_den_kalei_provider_xoris_egkyra_deigmata(
    fake_https: DiakomistisDikomis,
) -> None:
    """No usable evidence returns metadata without making a cloud request."""
    dedomena = _dedomena()
    dedomena["deigmata"] = []

    apotelesma = cloud_modulo.analysi_cloud(
        dedomena, KLEIDI_DOKIMIS, ENDPOINT, True, ONOMA_ENV
    )

    assert fake_https == []
    assert apotelesma["eyrimata"] == []
    analysi = cast(Mapping[str, object], apotelesma["analysi"])
    assert analysi["katastasi"] == "ok"
    assert analysi["egkyra_deigmata_cloud"] == 0
