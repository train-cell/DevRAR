"""Ενώνει readers, full-stream metrics και ισορροπημένο bounded evidence."""

from __future__ import annotations

import hashlib
import heapq
import logging
import os
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from devrar.aporrita import katharise_aporrita
from devrar.git_metrika import syllexe_git_diafores
from devrar.metrika import SyllogistisMetrikon
from devrar.piges import diavase_pigi
from devrar.syllogi import syllexe_dedomena
from devrar.symvanta import SymvanErgasias

KATAGRAFI = logging.getLogger(__name__)

NEES_PIGES = {
    "opencode": "OpenCode",
    "gemini": "Gemini CLI",
    "antigravity": "Antigravity",
}
PALIES_PIGES = {"claude", "codex"}
ORIO_DEIGMATON = 600
ORIO_APOSPASMATOS = 500
METRIKA_AI = (
    "synedries",
    "rizikes",
    "ypopraktores",
    "minimata_xristi",
    "apantiseis",
    "kliseis_ergaleion",
)


def proepilegmenes_diadromes(pigi: str) -> tuple[Path, ...]:
    """Επιστρέφει μόνο τεκμηριωμένες app roots, χωρίς drive-wide discovery."""
    vasi = Path.home()
    if pigi == "opencode":
        diadromi = os.environ.get("OPENCODE_DB")
        return (
            (Path(diadromi),)
            if diadromi
            else (vasi / ".local/share/opencode/opencode.db",)
        )
    if pigi == "gemini":
        return (vasi / ".gemini/tmp",)
    if pigi == "antigravity":
        rizikes = tuple(
            vasi / ".gemini" / efarmogi / "brain"
            for efarmogi in ("antigravity", "antigravity-cli", "antigravity-ide")
        )
        yparxouses = tuple(riza for riza in rizikes if riza.exists())
        return yparxouses or rizikes[:1]
    raise ValueError(f"Unsupported source: {pigi}")


def _chronos_symvantos(chronos: str | None, zoni: ZoneInfo) -> datetime | None:
    """Αναλύει μόνο aware timestamps, χωρίς επινόηση timezone."""
    if not chronos:
        return None
    try:
        timi = datetime.fromisoformat(chronos)
    except ValueError:
        return None
    return timi.astimezone(zoni) if timi.tzinfo is not None else None


def _leksiko(timi: object) -> dict[str, object]:
    """Στενεύει serializable report mapping χωρίς type ignores."""
    return (
        {str(kleidi): axia for kleidi, axia in timi.items()}
        if isinstance(timi, Mapping)
        else {}
    )


def _grammes(timi: object) -> list[dict[str, object]]:
    """Επιστρέφει μόνο mapping rows γνωστού report field."""
    return (
        [_leksiko(grammi) for grammi in timi if isinstance(grammi, Mapping)]
        if isinstance(timi, list)
        else []
    )


def _plithos(timi: object) -> int:
    """Διαβάζει integer counter, κρατώντας τις άγνωστες τιμές εκτός αθροισμάτων."""
    return timi if isinstance(timi, int) and not isinstance(timi, bool) else 0


def _keno_git_diafores(
    apothitiria: Sequence[Path],
    apo: date | None,
    eos: date | None,
    zoni: str,
    author: str | None,
    sfalma: str,
) -> dict[str, object]:
    """Δηλώνει αποτυχία νέων Git deltas χωρίς να επινοεί μηδενικά."""
    simeioseis = [f"Git delta collection failed: {sfalma}"]
    apothikies = [
        {
            "onoma": apothikio.name,
            "commits": None,
            "merge_commits": None,
            "additions": None,
            "deletions": None,
            "file_changes": None,
            "binary_file_changes": None,
            "arxeia_tracked_HEAD": None,
        }
        for apothikio in apothitiria
    ]
    return {
        "adapter": "git-numstat-first-parent-v1",
        "katastasi": "partial",
        "periodos": {
            "apo": apo.isoformat() if apo else None,
            "eos": eos.isoformat() if eos else None,
            "zoni": zoni,
        },
        "filtro": {"author": author.casefold().strip() if author else None},
        "semantics": {
            "history": "first-parent only; non-first-parent-only commits are omitted",
            "merge": "included against first parent; counted separately",
        },
        "apothikies": apothikies,
        "synola": {
            "merge_commits": None,
            "additions": None,
            "deletions": None,
            "file_changes": None,
            "binary_file_changes": None,
            "unique_commits": None,
            "arxeia_tracked_HEAD": None,
        },
        "kalypsi": {
            "apothikies": len(apothitiria),
            "epityxeis": 0,
            "sfalmata": len(apothitiria),
            "agnostes_imerominies": 0,
            "perikopi": False,
            "katastasi": "partial",
            "simeioseis": simeioseis,
        },
    }


class _Deigmata:
    """Κρατά deterministic bounded δείγματα ανά source/kind για όλο το stream."""

    def __init__(self, zoni: ZoneInfo) -> None:
        """Αρχικοποιεί heaps και metadata dedup χωρίς raw transcript archive."""
        self.zoni = zoni
        self.omades: dict[tuple[str, str], list[tuple[int, str, dict[str, object]]]] = (
            defaultdict(list)
        )
        self.idomenes: set[tuple[str, str]] = set()

    def prosthese(self, symvan: SymvanErgasias) -> bool:
        """Επιλέγει δείγματα με stable hash και απορρίπτει αντιγραμμένα event IDs."""
        kleidi = (symvan["pigi"], symvan["id"])
        if kleidi in self.idomenes:
            return False
        self.idomenes.add(kleidi)
        xronos = _chronos_symvantos(symvan["chronos"], self.zoni)
        grammi: dict[str, object] = {
            "id": symvan["id"],
            "pigi": symvan["pigi"],
            "synedria": symvan["synedria"],
            "rolos": symvan["rolos"],
            "eidos": symvan["eidos"],
            "keimeno": katharise_aporrita(symvan["keimeno"])[:ORIO_APOSPASMATOS],
            "locator": symvan["locator"],
            "imerominia": xronos.date().isoformat() if xronos else None,
        }
        vathmos = int(hashlib.sha256(symvan["id"].encode()).hexdigest(), 16)
        heap = self.omades[(symvan["pigi"], symvan["eidos"])]
        stoixeio = (-vathmos, symvan["id"], grammi)
        if len(heap) < ORIO_DEIGMATON:
            heapq.heappush(heap, stoixeio)
        elif stoixeio[:2] > heap[0][:2]:
            heapq.heapreplace(heap, stoixeio)
        return True

    def apotelesma(self) -> list[dict[str, object]]:
        """Επιστρέφει bounded round-robin δείγματα από source/kind groups."""
        omades = [
            sorted(heap, key=lambda stoixeio: (-stoixeio[0], stoixeio[1]))
            for _, heap in sorted(self.omades.items())
        ]
        deigmata: list[dict[str, object]] = []
        for deiktis in range(ORIO_DEIGMATON):
            for omada in omades:
                if deiktis < len(omada):
                    deigmata.append(omada[deiktis][2])
                    if len(deigmata) == ORIO_DEIGMATON:
                        return deigmata
        return deigmata


def syllexe_pliri(
    piges: Sequence[str],
    fakeloi: Mapping[str, Path],
    apothitiria: Sequence[Path],
    apo: date | None = None,
    eos: date | None = None,
    zoni: str = "Europe/Athens",
    author: str | None = None,
    idle_minutes: int = 15,
) -> dict[str, object]:
    """Συλλέγει παλιές/νέες πηγές με κοινά metrics και διαφανή coverage."""
    if set(piges) - PALIES_PIGES - NEES_PIGES.keys():
        raise ValueError("Unsupported source selected")
    zoni_anaforas = ZoneInfo(zoni)
    metrika = SyllogistisMetrikon(zoni=zoni, idle_minutes=idle_minutes)
    deigmata = _Deigmata(zoni_anaforas)

    def paratiritis(symvan: SymvanErgasias) -> None:
        """Δίνει ολόκληρη την αποδεκτή ροή στα metrics και bounded quotes στο report."""
        if deigmata.prosthese(symvan):
            metrika.prosthese(symvan)

    palies = [pigi for pigi in piges if pigi in PALIES_PIGES]
    anafora = syllexe_dedomena(
        palies,
        fakeloi,
        apothitiria,
        apo,
        eos,
        zoni,
        author,
        paratiritis=paratiritis,
        idle_minutes=idle_minutes,
    )
    synola = _leksiko(anafora["synola"])
    piges_report = _grammes(anafora["piges"])
    ergaleia = _grammes(anafora["ergaleia"])
    montela = _grammes(anafora["montela"])
    simeioseis_raw = anafora.get("simeioseis")
    simeioseis = list(simeioseis_raw) if isinstance(simeioseis_raw, list) else []
    imeres: dict[str, dict[str, object]] = {
        str(grammi["imerominia"]): grammi
        for grammi in _grammes(anafora["drastiriotita"])
    }
    yparxei_ai = synola.get("synedries") is not None
    yparxei_kalypsi_metrikon = yparxei_ai
    kalypsi_tokens = _leksiko(anafora.get("kalypsi_tokens"))
    kalypsi_pigon_tokens = _leksiko(kalypsi_tokens.get("piges"))
    for pigi in dict.fromkeys(piges):
        if pigi not in NEES_PIGES:
            continue
        rizikes = (
            (fakeloi[pigi],) if pigi in fakeloi else proepilegmenes_diadromes(pigi)
        )
        synedries: set[str] = set()
        paidia: set[str] = set()
        plithi = Counter({kleidi: 0 for kleidi in METRIKA_AI})
        modela_pigis: Counter[str] = Counter()
        sfalmata = arxeia = anagnorismena = 0
        agnostoi_chronoi = 0
        imerominies_gnostes = 0
        symvanta_entos_filtrou = 0
        morfes: set[str] = set()
        adapter = ""
        katastaseis: list[str] = []
        periodos_apo: str | None = None
        periodos_eos: str | None = None
        for riza in rizikes:
            apotelesma = diavase_pigi(pigi, riza)
            for symvan_akatharto in apotelesma.gegonota:
                kanoniko = symvan_akatharto.copy()
                kanoniko["pigi"] = NEES_PIGES[pigi]
                kanoniko["id"] = hashlib.sha256(
                    f"{pigi}\0{kanoniko['synedria']}\0{kanoniko['id']}".encode()
                ).hexdigest()
                xronos = _chronos_symvantos(symvan_akatharto["chronos"], zoni_anaforas)
                if xronos:
                    imerominies_gnostes += 1
                    imera_diathesimi = xronos.date().isoformat()
                    periodos_apo = (
                        min(periodos_apo, imera_diathesimi)
                        if periodos_apo
                        else imera_diathesimi
                    )
                    periodos_eos = (
                        max(periodos_eos, imera_diathesimi)
                        if periodos_eos
                        else imera_diathesimi
                    )
                elif apo is not None or eos is not None:
                    agnostoi_chronoi += 1
                    continue
                if xronos and (
                    (apo is not None and xronos.date() < apo)
                    or (eos is not None and xronos.date() > eos)
                ):
                    continue
                if not deigmata.prosthese(kanoniko):
                    continue
                symvanta_entos_filtrou += 1
                metrika.prosthese(kanoniko)
                synedries.add(kanoniko["synedria"])
                if kanoniko["goneas"]:
                    paidia.add(kanoniko["synedria"])
                eidos = kanoniko["eidos"]
                if eidos == "prompt" and kanoniko["rolos"] == "user":
                    plithi["minimata_xristi"] += 1
                elif eidos == "response":
                    plithi["apantiseis"] += 1
                elif eidos == "tool_call":
                    plithi["kliseis_ergaleion"] += 1
                if kanoniko["montelo"] and eidos in {"response", "tool_call"}:
                    modela_pigis[kanoniko["montelo"]] += 1
                if xronos:
                    imera = xronos.date().isoformat()
                    grammi = imeres.setdefault(
                        imera,
                        {
                            "imerominia": imera,
                            "prompts": 0,
                            "commits": 0 if apothitiria else None,
                        },
                    )
                    if eidos == "prompt" and kanoniko["rolos"] == "user":
                        grammi["prompts"] = _plithos(grammi["prompts"]) + 1
            kalypsi = apotelesma.kalypsi
            arxeia += kalypsi.arxeia
            anagnorismena += kalypsi.anagnorismena
            sfalmata += kalypsi.sfalmata + kalypsi.agnosta
            morfes.update(kalypsi.morfes)
            adapter = kalypsi.adapter
            katastaseis.append(kalypsi.katastasi)
            simeioseis.extend(kalypsi.simeioseis)
        katastasi = (
            "missing"
            if not arxeia
            else (
                "partial"
                if sfalmata or agnostoi_chronoi or "partial" in katastaseis
                else "ok"
            )
        )
        piges_report.append(
            {
                "onoma": NEES_PIGES[pigi],
                "katastasi": katastasi,
                "arxeia": arxeia,
                "sfalmata": sfalmata + agnostoi_chronoi,
                "adapter": adapter,
                "morfes": sorted(morfes),
                "simeiosi": "Unknown timestamps excluded by date filter."
                if agnostoi_chronoi
                else "",
                "periodos_diathesimon": {
                    "apo": periodos_apo,
                    "eos": periodos_eos,
                },
            }
        )
        metrika_diathesimi = bool(anagnorismena) and (
            apo is None
            and eos is None
            or symvanta_entos_filtrou > 0
            or (agnostoi_chronoi == 0 and imerominies_gnostes > 0)
        )
        if metrika_diathesimi:
            for kleidi in METRIKA_AI:
                if not yparxei_ai:
                    synola[kleidi] = 0
            plithi.update(
                synedries=len(synedries),
                ypopraktores=len(paidia),
                rizikes=len(synedries - paidia),
            )
            for kleidi in METRIKA_AI:
                if synola.get(kleidi) is not None:
                    synola[kleidi] = _plithos(synola[kleidi]) + plithi[kleidi]
            yparxei_ai = True
            yparxei_kalypsi_metrikon = True
        ergaleia.append(
            {
                "onoma": NEES_PIGES[pigi],
                "synedries": len(synedries) if anagnorismena else None,
                "prompts": plithi["minimata_xristi"] if anagnorismena else None,
                "tokens": None,
            }
        )
        montela.extend(
            {"onoma": modelo, "kliseis": plithos, "tokens": None, "pigi": pigi}
            for modelo, plithos in sorted(modela_pigis.items())
        )
        synola["tokens"] = None
        kalypsi_pigon_tokens[pigi] = {
            "gnostes_aitiseis": None,
            "elleipeis_aitiseis": None,
            "agnosta_records": None,
            "methodos": "source_does_not_report_token_usage",
            "pliris": False,
        }
    synola["imeres"] = len(imeres) if yparxei_kalypsi_metrikon else None
    if kalypsi_pigon_tokens:
        kalypsi_tokens["piges"] = kalypsi_pigon_tokens
        kalypsi_tokens["pliris"] = all(
            isinstance(kalypsi, Mapping) and kalypsi.get("pliris") is True
            for kalypsi in kalypsi_pigon_tokens.values()
        )
    else:
        kalypsi_tokens = {"piges": {}, "pliris": False}
    deigmata_epilegmena = deigmata.apotelesma()
    metrika_apotelesma = metrika.apotelesma()
    if not yparxei_ai:
        metrika_apotelesma["ora"] = []
    anafora.update(
        scope_git={
            "rev": "HEAD",
            "author": (author.casefold().strip() or None)
            if author and apothitiria
            else None,
            "repositories": sorted(
                {
                    hashlib.sha256(
                        os.path.normcase(str(apothikio.absolute())).encode()
                    ).hexdigest()
                    for apothikio in apothitiria
                }
            ),
        },
        synola=synola,
        piges=piges_report,
        ergaleia=ergaleia,
        montela=montela,
        simeioseis=simeioseis,
        drastiriotita=[imeres[imera] for imera in sorted(imeres)],
        deigmata=deigmata_epilegmena,
        kalypsi_analysi={
            "epilegmena": len(deigmata_epilegmena),
            "diathesima": len(deigmata.idomenes),
            "perikopi": len(deigmata.idomenes) > len(deigmata_epilegmena),
        },
        metrika_ergasias=metrika_apotelesma,
        kalypsi_tokens=kalypsi_tokens,
    )
    if apothitiria:
        try:
            anafora["git_diafores"] = syllexe_git_diafores(
                apothitiria, apo, eos, zoni, author
            )
        except (OSError, RuntimeError, ValueError) as sfalma:
            KATAGRAFI.exception("Git delta collection failed")
            anafora["git_diafores"] = _keno_git_diafores(
                apothitiria, apo, eos, zoni, author, str(sfalma) or "unavailable"
            )
    return anafora
