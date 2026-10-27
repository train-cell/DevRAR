"""Redaction commonly recognizable credentials before exporting excerpts."""

from __future__ import annotations

import re

ETIKETA_APORRITOS = "[REDACTED]"
PATTERNA_ASSIGNMENT = re.compile(
    r"(?i)([\"']?)\b(password|passwd|api[_-]?key|access[_-]?token|secret|token)"
    r"\b([\"']?)(\s*[:=]\s*)"
    r"(?:\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|"
    r"[^\s,;\"']+)"
)
PATTERNA_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*")
PATTERNA_GNOSTON_KLEIDI = re.compile(
    r"\b(?:sk-(?:ant|proj)-[A-Za-z0-9_-]{8,}|sk-[A-Za-z0-9_-]{16,}|"
    r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"AKIA[0-9A-Z]{16}|AIza[A-Za-z0-9_-]{30,})\b"
)


def katharise_aporrita(keimeno: str) -> str:
    """Κρύβει Bearer, assigned credentials και συνηθισμένα API-key formats."""
    katharo = PATTERNA_BEARER.sub(f"Bearer {ETIKETA_APORRITOS}", keimeno)
    katharo = PATTERNA_ASSIGNMENT.sub(
        lambda tairiasma: (
            f"{tairiasma.group(1)}{tairiasma.group(2)}{tairiasma.group(3)}"
            f"{tairiasma.group(4)}{ETIKETA_APORRITOS}"
        ),
        katharo,
    )
    return PATTERNA_GNOSTON_KLEIDI.sub(ETIKETA_APORRITOS, katharo)
