"""Εκκινεί το CLI όταν εκτελείται το πακέτο ως module."""

from devrar.cli import kyria


def ekkinisi() -> int:
    """Εκτελεί το DevRAR CLI με τα arguments της διεργασίας."""
    return kyria()


if __name__ == "__main__":
    raise SystemExit(ekkinisi())
