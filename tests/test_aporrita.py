from __future__ import annotations

from devrar.aporrita import katharise_aporrita


def test_katharise_aporrita_kryvei_bearer_assignment_kai_api_keys() -> None:
    """Αφαιρεί γνωστές μορφές credentials πριν από εξαγωγή evidence."""
    keimeno = (
        "Bearer super-secret-token API_KEY=sk-proj-123456789abcdef "
        "password='do-not-export' standalone sk-ant-abcdefghijklmnopqrstuvwxyz"
    )

    katharo = katharise_aporrita(keimeno)

    assert "super-secret-token" not in katharo
    assert "sk-proj-123456789abcdef" not in katharo
    assert "do-not-export" not in katharo
    assert "sk-ant-abcdefghijklmnopqrstuvwxyz" not in katharo
    assert katharo.count("[REDACTED]") == 4


def test_katharise_aporrita_diatirei_athoo_keimeno() -> None:
    """Αφήνει απλό κείμενο αμετάβλητο όταν δεν περιέχει credential pattern."""
    keimeno = "Please review the parser and add a focused regression test."

    assert katharise_aporrita(keimeno) == keimeno


def test_katharise_aporrita_kryvei_github_pat() -> None:
    """Κρύβει GitHub fine-grained token πριν από τη δειγματοληψία excerpt."""
    kleidi = "github_pat_" + "A" * 40

    katharo = katharise_aporrita(f"synthetic credential {kleidi}")

    assert kleidi not in katharo
    assert "[REDACTED]" in katharo


def test_katharise_aporrita_kryvei_timi_se_quotes_me_kena() -> None:
    """Τα quoted credentials με κενά δεν αφήνουν τμήμα τους στο excerpt."""
    assert katharise_aporrita('password="two words here"') == "password=[REDACTED]"
    assert katharise_aporrita("api_key='one more secret'") == "api_key=[REDACTED]"


def test_katharise_aporrita_kryvei_json_kleidia() -> None:
    """Καλύπτει quoted JSON property names με απλά ή σύνθετα credentials."""
    keimeno = '{"password": "two words here", "api_key": "synthetic secret"}'

    katharo = katharise_aporrita(keimeno)

    assert "two words here" not in katharo
    assert "synthetic secret" not in katharo
