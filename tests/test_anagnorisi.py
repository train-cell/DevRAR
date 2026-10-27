"""Ελέγχει deterministic recognition χωρίς grades ή ψυχολογική ταξινόμηση."""

import pytest

from devrar.anagnorisi import ftiaxe_anagnorisi


@pytest.mark.parametrize(
    ("synola", "piges", "titlos"),
    [
        ({"ypopraktores": 3}, [{"prompts": 2}, {"prompts": 1}], "Multi-tool conductor"),
        ({"ypopraktores": 1}, [], "Agent conductor"),
        ({}, [{"prompts": 2}, {"prompts": 1}], "Toolbox explorer"),
        ({"minimata_xristi": 2}, [], "Focused builder"),
        ({"commits": 1}, [], "Repository replay"),
        ({"minimata_xristi": None}, [], "An unwritten chapter"),
    ],
)
def test_deskriptiko_profile_apo_katagrafes(
    synola: dict[str, object],
    piges: list[dict[str, object]],
    titlos: str,
) -> None:
    """Κάθε profile περιγράφει το selected report και δεν βαθμολογεί άνθρωπο."""
    dedomena = {"synola": synola, "ergaleia": piges}
    prin = repr(dedomena)
    apotelesma = ftiaxe_anagnorisi(dedomena)
    assert apotelesma["profile"]["titlos"] == titlos
    assert apotelesma["profile"]["aitia"]
    assert "skill" in apotelesma["periorismos"]
    assert repr(dedomena) == prin


def test_highlights_ekfrasis_kai_missing_data() -> None:
    """Αναγνωρίζει πραγματικά μεγέθη, κρατά όλα τα ties και αγνοεί malformed rows."""
    apotelesma = ftiaxe_anagnorisi(
        {
            "synola": {"minimata_xristi": True, "imeres": 2, "commits": -1},
            "ergaleia": [None, {"onoma": "Synthetic CLI", "prompts": 12}],
            "drastiriotita": [
                None,
                {"imerominia": "day-a", "prompts": 6},
                {"imerominia": "day-b", "prompts": 6},
            ],
            "metrika_ergasias": {"test_summary": {"passed": 7, "failed": 1}},
        }
    )
    keimeno = repr(apotelesma)
    assert "Synthetic CLI" in keimeno and "day-a" in keimeno and "day-b" in keimeno
    assert "7" in keimeno and "1" in keimeno
    assert len(apotelesma["highlights"]) <= 4
    assert not ftiaxe_anagnorisi({"synola": None})["highlights"]
