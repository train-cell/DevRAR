"""Ορίζει το κοινό transient event contract των readers και των work metrics."""

from __future__ import annotations

from typing import Literal, TypedDict


class SymvanErgasias(TypedDict):
    """Μεταφέρει αποδεκτό event χωρίς εκτέλεση ή υποχρεωτική αποθήκευση raw logs."""

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
