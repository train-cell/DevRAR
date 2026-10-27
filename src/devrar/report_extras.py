"""Αποδίδει τα πρόσθετα aggregates και bounded evidence στο private Markdown."""

from collections.abc import Callable, Mapping

ORIO_EPEISODION_MARKDOWN = 20


def _xartis(timi: object) -> Mapping[str, object]:
    """Κρατά mappings χωρίς υπόθεση για malformed optional report πεδία."""
    return timi if isinstance(timi, Mapping) else {}


def _grammes(timi: object) -> list[Mapping[str, object]]:
    """Επιστρέφει μόνο τα έγκυρα mapping rows μίας λίστας."""
    return (
        [eggrafi for eggrafi in timi if isinstance(eggrafi, Mapping)]
        if isinstance(timi, list)
        else []
    )


def prostheto_markdown(
    dedomena: Mapping[str, object], asfales: Callable[[object], str]
) -> list[str]:
    """Παράγει επιλεγμένες private ενότητες με safe κείμενο και ρητά nulls."""
    apotelesma: list[str] = []

    def timi(antikeimeno: object) -> str:
        """Διατηρεί null ως unknown χωρίς ενεργό Markdown από τις πηγές."""
        return "Not recorded" if antikeimeno is None else asfales(antikeimeno)

    if "anagnorisi" in dedomena:
        anagnorisi = _xartis(dedomena["anagnorisi"])
        profile = _xartis(anagnorisi.get("profile"))
        apotelesma.extend(
            (
                "",
                "## Your work, replayed",
                "",
                f"**{timi(profile.get('titlos'))}**",
                timi(profile.get("aitia")),
                timi(anagnorisi.get("periorismos")),
                "",
            )
        )
        for highlight in _grammes(anagnorisi.get("highlights")):
            apotelesma.append(
                f"- **{timi(highlight.get('titlos'))}:** "
                f"{timi(highlight.get('keimeno'))}"
            )

    for kleidi, titlos, pedia in (
        (
            "metrika_ergasias",
            "Work patterns",
            (
                "zoni",
                "events",
                "timestamps_unknown",
                "interval_estimate_minutes",
                "interval_estimate_status",
                "episodes_included",
                "episodes_eligible",
                "episodes_truncated",
            ),
        ),
        (
            "energos_xronos",
            "Supplied active time",
            (
                "status",
                "scope",
                "note",
                "active_seconds",
                "afk_seconds",
            ),
        ),
        ("kostos", "Supplied cost ledger", ("status", "note")),
        ("git_diafores", "Git change metadata", ("katastasi",)),
    ):
        if kleidi not in dedomena:
            continue
        xartis = _xartis(dedomena[kleidi])
        apotelesma.extend(("", f"## {titlos}", ""))
        for pedio in pedia:
            apotelesma.append(f"- {pedio}: {timi(xartis.get(pedio))}")
        for upopedio in ("coverage", "kalypsi", "test_summary", "semantics", "synola"):
            for onoma, metrisi in _xartis(xartis.get(upopedio)).items():
                apotelesma.append(
                    f"- {asfales(upopedio)} / {asfales(onoma)}: {timi(metrisi)}"
                )
        for eggrafi in _grammes(xartis.get("totals")):
            apotelesma.append(
                f"- {timi(eggrafi.get('currency'))} / {timi(eggrafi.get('kind'))}: "
                f"{timi(eggrafi.get('amount'))}"
            )
        if kleidi == "metrika_ergasias":
            apotelesma.extend(
                (
                    "",
                    "Observed-event intervals are an estimate, not actual PC time.",
                    "Test totals count recorded executions, including reruns.",
                    "",
                    "| Local hour | Human prompts |",
                    "|---|---|",
                )
            )
            for eggrafi in _grammes(xartis.get("ora")):
                apotelesma.append(
                    f"| {timi(eggrafi.get('ora'))} | {timi(eggrafi.get('prompts'))} |"
                )
    if "epeisodia_ergasias" in dedomena:
        epeisodia = _xartis(dedomena["epeisodia_ergasias"])
        paratiriseis = _grammes(epeisodia.get("paratiriseis"))
        epilogi = paratiriseis[:ORIO_EPEISODION_MARKDOWN]
        apotelesma.extend(
            (
                "",
                "## Observed check outcomes",
                "",
                f"Showing {len(epilogi)} of {len(paratiriseis)} "
                "included episode summaries.",
                "Checks do not establish task completion, code quality, "
                "or human blame.",
                "",
            )
        )
        for epeisodio in epilogi:
            apotelesma.extend(
                (
                    f"### {timi(epeisodio.get('pigi'))} / "
                    f"{timi(epeisodio.get('synedria'))}",
                    f"{timi(epeisodio.get('katastasi'))}: "
                    f"{timi(epeisodio.get('apotelesma'))}",
                )
            )
            for tekmirio in _grammes(epeisodio.get("tekmiria")):
                apotelesma.append(
                    f"- {timi(tekmirio.get('pigi'))} / "
                    f"{timi(tekmirio.get('locator'))}: "
                    f"{timi(tekmirio.get('apospasma'))}"
                )
        for protasi in _grammes(epeisodia.get("proteraiotites")):
            apotelesma.append(
                f"- **{timi(protasi.get('titlos'))}:** {timi(protasi.get('protasi'))}"
            )
    if "sygkrisi" in dedomena:
        sygkrisi = _xartis(dedomena["sygkrisi"])
        apotelesma.extend(
            (
                "",
                "## Report comparison",
                "",
                f"Status: {timi(sygkrisi.get('katastasi'))}",
                "Deltas describe recorded activity; volume does not establish skill.",
                "",
            )
        )
        for paragontas, stoixeia in _xartis(sygkrisi.get("symvatotita")).items():
            xartis = _xartis(stoixeia)
            apotelesma.append(
                f"- {asfales(paragontas)}: {timi(xartis.get('katastasi'))} / "
                f"{timi(xartis.get('aitia'))}"
            )
        apotelesma.extend(
            (
                "",
                "| Metric | Current | Baseline | Delta | Percent | Status |",
                "|---|---|---|---|---|---|",
            )
        )
        for onoma, stoixeia in _xartis(sygkrisi.get("metrika")).items():
            xartis = _xartis(stoixeia)
            times = [asfales(onoma)] + [
                timi(xartis.get(pedio))
                for pedio in (
                    "trexousa",
                    "proigoumeni",
                    "delta",
                    "pososto",
                    "katastasi",
                )
            ]
            apotelesma.append(f"| {' | '.join(times)} |")
    return apotelesma
