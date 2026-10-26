(() => {
  "use strict";

  const KINISI_AUTO_MS = 6200;
  const MIN_POSITIVE_RECOGNITION_COUNT = 1;
  const MAX_RECOGNITION_BADGES = 3;
  const MEGISTO_EPOMENA_VIMATA = 3;
  const MEGISTO_DEIGMATA = 12;
  const SVG_XOROS = "http://www.w3.org/2000/svg";
  const dedomenaSkript = document.getElementById("devrar-data");
  let dedomena = {};
  try {
    dedomena = JSON.parse(dedomenaSkript ? dedomenaSkript.textContent : "{}");
  } catch (sfalma) {
    dedomena = {};
  }
  const synola =
    dedomena.synola && typeof dedomena.synola === "object"
      ? dedomena.synola
      : {};
  const ergaleia = Array.isArray(dedomena.ergaleia) ? dedomena.ergaleia : [];
  const montela = Array.isArray(dedomena.montela) ? dedomena.montela : [];
  const drastiriotita = Array.isArray(dedomena.drastiriotita)
    ? dedomena.drastiriotita
    : [];
  const erga = Array.isArray(dedomena.projects) ? dedomena.projects : [];
  const eyrimata = Array.isArray(dedomena.eyrimata) ? dedomena.eyrimata : [];
  const deigmata = Array.isArray(dedomena.deigmata) ? dedomena.deigmata : [];
  const oroshma = Array.isArray(dedomena.oroshma) ? dedomena.oroshma : [];
  const piges = Array.isArray(dedomena.piges) ? dedomena.piges : [];
  const katastasi = {
    skini: 0,
    proboli: "story",
    enotita: "overview",
    pigi: "all",
    timer: null,
    dialogReturn: null,
    paused: true,
  };
  const skines = [
    "welcome",
    "tools",
    "numbers",
    "rhythm",
    "agents",
    "projects",
    "recognition",
    "growth",
    "next",
  ];
  /** Returns a report element by its stable HTML id. */
  const stoixeia = (stoixeioTaftotita) => document.getElementById(stoixeioTaftotita);
  const arithmos = (timi) =>
    timi === null || timi === undefined || !Number.isFinite(Number(timi))
      ? "Not recorded"
      : new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(
          Number(timi),
        );
  const timi = (arithmoTimi, monada = "") =>
    arithmoTimi === null || arithmoTimi === undefined
      ? "Not recorded"
      : `${arithmos(arithmoTimi)}${monada}`;
  const einaiMetrikoPositiko = (arithmoTimi) =>
    arithmoTimi !== null &&
    arithmoTimi !== undefined &&
    Number.isFinite(Number(arithmoTimi)) &&
    Number(arithmoTimi) >= MIN_POSITIVE_RECOGNITION_COUNT;
  const keimeno = (antikeimeno, kleidi, efedrikiTimi = "") =>
    antikeimeno && typeof antikeimeno[kleidi] === "string"
      ? antikeimeno[kleidi]
      : efedrikiTimi;
  const periodos = () => {
    const apo =
      dedomena.periodos && dedomena.periodos.apo ? dedomena.periodos.apo : "";
    const eos =
      dedomena.periodos && dedomena.periodos.eos ? dedomena.periodos.eos : "";
    return apo && eos ? `${apo} — ${eos}` : "Selected period";
  };
  /** Explains whose repository activity is represented by the commit counters. */
  const eurosGit = () => {
    if (!erga.length) return "No selected repositories";
    const euros = dedomena.scope_git;
    if (!euros || typeof euros !== "object") return "Git author scope not recorded";
    const grafeas = keimeno(euros, "author");
    return grafeas ? `Git author filter: ${grafeas} · HEAD` : "Git: all authors · HEAD";
  };
  /** Creates a DOM node and inserts supplied display copy as plain text. */
  const ftiakse = (typosStoixeiou, onomaKlasis, keimenoKombou = "") => {
    const stoixeio = document.createElement(typosStoixeiou);
    if (onomaKlasis) stoixeio.className = onomaKlasis;
    if (keimenoKombou !== "") stoixeio.textContent = keimenoKombou;
    return stoixeio;
  };
  /** Creates and appends a DOM node under the requested parent. */
  const asto = (goneas, typosStoixeiou, onomaKlasis, keimenoKombou = "") => {
    const stoixeio = ftiakse(typosStoixeiou, onomaKlasis, keimenoKombou);
    goneas.append(stoixeio);
    return stoixeio;
  };
  /** Creates a normalized display metric used by cards and details. */
  const metrika = (
    titlos,
    arithmetikiTimi,
    monada,
    perigrafi,
    pigi,
    analysh = [],
    periodosReport = periodos(),
  ) => ({
    titlos,
    value: arithmetikiTimi,
    unit: monada,
    description: perigrafi,
    source: pigi,
    breakdown: analysh,
    period: periodosReport,
  });
  /** Builds the report-wide metric set from schema aggregates. */
  const synolikaMetrika = () => [
    metrika(
      "Sessions",
      synola.synedries,
      "sessions",
      "Distinct recorded work sessions in the selected period.",
      onomataPigwn(),
      ergaleia
        .map((grammi) => [keimeno(grammi, "onoma", "Tool"), grammi.synedries])
        .filter((grammi) => grammi[1] !== null && grammi[1] !== undefined),
    ),
    metrika(
      "Root sessions",
      synola.rizikes,
      "roots",
      "Top-level sessions. Child sessions are counted separately when recorded.",
      onomataPigwn(),
    ),
    metrika(
      "Subagents",
      synola.ypopraktores,
      "agents",
      "Recorded child or delegated agent sessions.",
      onomataPigwn(),
    ),
    metrika(
      "User prompts",
      synola.minimata_xristi,
      "prompts",
      "User messages found in the selected local history.",
      onomataPigwn(),
    ),
    metrika(
      "Assistant replies",
      synola.apantiseis,
      "replies",
      "Assistant responses found in the selected local history.",
      onomataPigwn(),
    ),
    metrika(
      "Tool calls",
      synola.kliseis_ergaleion,
      "calls",
      "Recorded tool invocations. This does not imply successful execution.",
      onomataPigwn(),
    ),
    metrika(
      "Tokens",
      synola.tokens,
      "tokens",
      "Token totals appear only where the local source recorded them.",
      onomataPigwn(),
      montela
        .map((grammi) => [keimeno(grammi, "onoma", "Model"), grammi.tokens])
        .filter((grammi) => grammi[1] !== null && grammi[1] !== undefined),
    ),
    metrika(
      "Commits",
      synola.commits,
      "commits",
      `Recorded commit total. Repository names appear only for explicitly selected repositories. ${eurosGit()}. Commits describe activity, not code quality.`,
      onomataPigwn(),
      erga
        .map((grammi) => [keimeno(grammi, "onoma", "Project"), grammi.commits])
        .filter((grammi) => grammi[1] !== null && grammi[1] !== undefined),
    ),
    metrika(
      "Active days",
      synola.imeres,
      "days",
      "Calendar dates with activity. Timestamps use the report timezone.",
      onomataPigwn(),
      dedomena.periodos && dedomena.periodos.zoni
        ? [["Timezone", dedomena.periodos.zoni]]
        : [],
    ),
  ];
  const onomataPigwn = () =>
    piges
      .map((grammi) => keimeno(grammi, "onoma", ""))
      .filter(Boolean)
      .join(", ") || "Selected local sources";
  const synoloErgaleiou = (kleidiLocal) =>
    ergaleia.reduce(
      (athroisma, grammi) =>
        athroisma + (Number.isFinite(Number(grammi[kleidiLocal])) ? Number(grammi[kleidiLocal]) : 0),
      0,
    );
  const filtrismenaErgaleia = () =>
    katastasi.pigi === "all"
      ? ergaleia
      : ergaleia.filter((grammi) => keimeno(grammi, "onoma") === katastasi.pigi);
  const ftiakseSkines = () => {
    const koryfaio = [...ergaleia]
      .filter(
        (grammi) =>
          grammi.prompts !== null &&
          grammi.prompts !== undefined &&
          Number.isFinite(Number(grammi.prompts)),
      )
      .sort((aAristera, bDexia) => (Number(bDexia.prompts) || 0) - (Number(aAristera.prompts) || 0))[0];
    const protoEyrima = eyrimata.find((grammi) => grammi.epipedo === "strength");
    const eyrimaAnaptyksis = eyrimata.find((grammi) => grammi.epipedo === "growth");
    const protoOrosimo = oroshma[0];
    const meraKorifis = [...drastiriotita]
      .filter(
        (grammi) =>
          grammi.prompts !== null &&
          grammi.prompts !== undefined &&
          Number.isFinite(Number(grammi.prompts)),
      )
      .sort((aAristera, bDexia) => Number(bDexia.prompts) - Number(aAristera.prompts))[0];
    const epilegmenaProjects = erga.length;
    const axiologisiData =
      dedomena.axiologisi && typeof dedomena.axiologisi === "object"
        ? dedomena.axiologisi
        : {};
    const analisiTopiki =
      dedomena.analysi && typeof dedomena.analysi === "object"
        ? dedomena.analysi
        : null;
    const bathmosDiathesimos =
      axiologisiData.diathesimi === true &&
      axiologisiData.synoliko !== null &&
      axiologisiData.synoliko !== undefined &&
      analisiTopiki?.katastasi !== "failed";
    const epomenaVimata = eyrimata
      .filter((grammi) => grammi.epipedo === "growth" && keimeno(grammi, "protasi"))
      .slice(0, MEGISTO_EPOMENA_VIMATA);
    const simeiosiImerominias = meraKorifis
      ? `${meraKorifis.imerominia} · ${timi(meraKorifis.prompts)} prompts`
      : "No dated activity is recorded.";
    const synoloPrompts = timi(synola.minimata_xristi);
    const synoloApantiseon = timi(synola.apantiseis);
    const kliseisErgaleion = timi(synola.kliseis_ergaleion);
    return [
      {
        kicker: "WELCOME TO YOUR REPLAY",
        title: "Your work,\n<em>in motion.</em>",
        copy: `A local recap from ${periodos()}. Counts reflect only recorded activity in the selected sources.`,
        aside: `${timi(synola.synedries)} sessions · ${timi(synola.imeres)} active days`,
        visual: "star",
        detail: synolikaMetrika()[0],
      },
      {
        kicker: "TOOLS THAT SHOWED UP",
        title: koryfaio
          ? `${keimeno(koryfaio, "onoma", "Your tool")}<em>led the count.</em>`
          : "Tool counts\n<em>not recorded.</em>",
        stat: koryfaio ? timi(koryfaio.prompts) : "—",
        unit: "RECORDED PROMPTS",
        copy: koryfaio
          ? `${keimeno(koryfaio, "onoma", "This tool")} had the highest recorded prompt count in this report.`
          : "Tool ranking is unavailable because no tool-level prompt counts were recorded.",
        aside: koryfaio
          ? `${timi(koryfaio.synedries)} sessions · tokens ${timi(koryfaio.tokens)}`
          : "Unknown counts stay unknown until a supported source records them.",
        visual: "podium",
        detail: metrika(
          "Tool prompts",
          koryfaio ? koryfaio.prompts : null,
          "prompts",
          "Prompts counted for the highest-count tool in this report.",
          koryfaio ? keimeno(koryfaio, "onoma") : onomataPigwn(),
          ergaleia.map((grammi) => [keimeno(grammi, "onoma", "Tool"), grammi.prompts]),
        ),
      },
      {
        kicker: "THE COUNTS",
        title: "Messages moved\n<em>through the tools.</em>",
        stat: synoloPrompts,
        unit: "USER PROMPTS",
        copy: `${synoloApantiseon} assistant replies · ${kliseisErgaleion} recorded tool calls. These are counts, not a measure of code quality or outcome.`,
        aside:
          "Each total is limited to the source records available in this report.",
        visual: "podium",
        detail: synolikaMetrika()[3],
      },
      {
        kicker: "THE RHYTHM",
        title:
          synola.imeres === null || synola.imeres === undefined
            ? "Activity days\n<em>not recorded.</em>"
            : `${timi(synola.imeres)}<em>active days.</em>`,
        stat: timi(synola.imeres),
        unit: "RECORDED DATES",
        copy: `Peak day: ${simeiosiImerominias}`,
        aside: `Timezone: ${dedomena.periodos && dedomena.periodos.zoni ? dedomena.periodos.zoni : "not recorded"} · ${drastiriotita.length} dated activity rows`,
        visual: "activity",
        detail: synolikaMetrika()[8],
      },
      {
        kicker: "AGENT WORK",
        title: "Parallel work,\n<em>counted separately.</em>",
        stat: timi(synola.ypopraktores),
        unit: "RECORDED SUBAGENTS",
        copy: `Root sessions: ${timi(synola.rizikes)} · all sessions: ${timi(synola.synedries)}.`,
        aside:
          synola.ypopraktores === null || synola.ypopraktores === undefined
            ? "Subagent totals were not recorded; this report does not infer delegation from names."
            : "Child sessions remain separate from root sessions.",
        visual: "spark",
        detail: synolikaMetrika()[2],
      },
      {
        kicker: "WHERE CHANGES WERE RECORDED",
        title: erga.length
          ? `${timi(synola.commits)} commits<em> across ${epilegmenaProjects} projects.</em>`
          : "Project totals\n<em>not recorded.</em>",
        stat: timi(synola.commits),
        unit: "RECORDED COMMITS",
        copy: erga.length
          ? `Counts from selected repositories. ${eurosGit()}.`
          : "No project breakdown is available. This is unknown, not an asserted zero.",
        aside: erga.length
          ? erga
              .map(
                (grammi) =>
                  `${keimeno(grammi, "onoma", "Project")}: ${timi(grammi.commits)}`,
              )
              .join(" · ")
          : "Select a repository on a future run to add project scope.",
        visual: "podium",
        detail: synolikaMetrika()[7],
      },
      {
        key: "recognition",
        kicker: "A MOMENT IN THE RECORD",
        title: protoOrosimo
          ? `${keimeno(protoOrosimo, "titlos", "Verified milestone")}<em>was recorded.</em>`
          : meraKorifis
            ? `${timi(meraKorifis.prompts)} prompts<em> on ${meraKorifis.imerominia}.</em>`
            : protoEyrima
              ? `${keimeno(protoEyrima, "titlos", "Recorded activity")}<em>has evidence.</em>`
              : "A milestone\n<em>is not recorded.</em>",
        copy: protoOrosimo
          ? keimeno(
              protoOrosimo,
              "keimeno",
              "A verified milestone from selected sources.",
            )
          : meraKorifis
            ? "That was the highest prompt count among the dated activity rows. It describes activity, not the result of the work."
            : protoEyrima
              ? keimeno(
                  protoEyrima,
                  "keimeno",
                  "An observation based on recorded data.",
                )
              : "No verified event is available in this report, so this chapter stays honest about the gap.",
        aside:
          "Debra: “A number can mark the moment. It can’t tell the whole story.”",
        visual: "spark",
        detail: protoOrosimo
          ? metrika(
              keimeno(protoOrosimo, "titlos", "Verified milestone"),
              null,
              "verified milestone",
              keimeno(
                protoOrosimo,
                "keimeno",
                "A verified milestone from selected sources.",
              ),
              "Selected source evidence",
            )
          : meraKorifis
            ? metrika(
                "Peak recorded day",
                meraKorifis.prompts,
                "prompts",
                "Highest prompt count in the dated activity rows.",
                "Recorded activity",
                [["Date", meraKorifis.imerominia]],
              )
            : synolikaMetrika()[0],
      },
      {
        kicker: "ASSESSMENT · EVIDENCE FIRST",
        title: "Strengths and\n<em>room to grow.</em>",
        copy: eyrimaAnaptyksis
          ? keimeno(
              eyrimaAnaptyksis,
              "keimeno",
              "A bounded growth observation from the recorded evidence.",
            )
          : "Dimension scores stay unavailable until a validated rubric has enough evidence to calibrate them.",
        aside:
          bathmosDiathesimos
            ? `Calibrated score: ${timi(axiologisiData.synoliko)}`
            : `Score unavailable · ${Array.isArray(axiologisiData.diastaseis) ? axiologisiData.diastaseis.length : 0} dimensions shown without a grade`,
        visual: "stamp",
        detail: metrika(
          "Engineering score",
          bathmosDiathesimos ? axiologisiData.synoliko : null,
          "score",
          keimeno(
            axiologisiData,
            "aitia",
            "Score unavailable until the rubric and evidence are calibrated.",
          ),
          "Assessment coverage",
          Array.isArray(axiologisiData.diastaseis)
            ? axiologisiData.diastaseis.map((grammi) => [
                keimeno(grammi, "onoma", "Dimension"),
                grammi.bathmos,
              ])
            : [],
        ),
      },
      {
        kicker: "YOUR NEXT CHAPTER",
        title: "Keep the facts.\n<em>Choose what to share.</em>",
        copy: epomenaVimata.length
          ? epomenaVimata.map((grammi) => keimeno(grammi, "protasi")).join(" · ")
          : "Your share card uses aggregate counts only. Add project context next time for a more personal recap.",
        aside:
          "Save a share card without source paths, excerpts, or project names.",
        visual: "star",
        action: "share",
        detail: metrika(
          "Share card aggregates",
          null,
          "private evidence omitted",
          "The export contains aggregate counts and a synthetic-data label when this is a demo.",
          "Selected report totals",
        ),
      },
    ];
  };
  let skiniData = ftiakseSkines();

  /** Builds the nine visual variants without interpreting imported text as markup. */
  function emfaniseSkini() {
    const skiniContainer = stoixeia("story-stage");
    const periexomeno = stoixeia("scene-content");
    const grammi = skiniData[katastasi.skini];
    skiniContainer.dataset.scene = String(katastasi.skini);
    periexomeno.replaceChildren();
    asto(periexomeno, "div", "scene-kicker", grammi.kicker);
    const titlos = asto(periexomeno, "h1", "scene-title");
    grammi.title.split("\n").forEach((grammiKeimenou) => {
      let emfasi = false;
      grammiKeimenou.split(/(<em>|<\/em>)/g).forEach((tmima) => {
        if (tmima === "<em>") {
          emfasi = true;
          return;
        }
        if (tmima === "</em>") {
          emfasi = false;
          return;
        }
        if (!tmima) return;
        const komvos = document.createElement(emfasi ? "em" : "span");
        komvos.textContent = tmima;
        titlos.append(komvos);
      });
    });
    if (grammi.stat) asto(periexomeno, "div", "scene-stat", grammi.stat);
    if (grammi.unit && grammi.stat)
      asto(periexomeno.lastElementChild, "small", "", grammi.unit);
    asto(periexomeno, "p", "scene-copy", grammi.copy);
    asto(periexomeno, "p", "scene-aside", grammi.aside);
    if (grammi.key === "recognition") prosthesBadgeAnagnorisis(periexomeno);
    if (grammi.visual) {
      const optiko = asto(periexomeno, "div", `scene-visual visual-${grammi.visual}`);
      if (grammi.visual === "podium") {
        const vathro = asto(optiko, "div", "podium");
        for (let deiktisI = 0; deiktisI < 5; deiktisI += 1) asto(vathro, "i", "");
      } else if (grammi.visual === "activity")
        asto(optiko, "div", "activity-orb", "✳");
      else if (grammi.visual === "stamp") {
        const sfragida = asto(optiko, "div", "growth-stamp");
        asto(sfragida, "span", "", "↗");
        sfragida.append(document.createTextNode(" NEXT\nMOVE"));
      } else
        asto(optiko, "div", "starburst", grammi.visual === "spark" ? "✦" : "✳");
    }
    const koumpiLeptomereion = stoixeia("scene-detail");
    const etiketaLeptomereion =
      grammi.action === "share" ? "Save a share card" : "Explore this stat";
    stoixeia("scene-detail-label").textContent = etiketaLeptomereion;
    koumpiLeptomereion.setAttribute(
      "aria-label",
      `${etiketaLeptomereion}: ${grammi.detail.titlos}`,
    );
    emfaniseProodo();
    stoixeia("sr-status").textContent =
      `Chapter ${katastasi.skini + 1} of ${skiniData.length}: ${grammi.kicker}`;
  }

  /** Adds up to three positive, recorded-fact badges to the recognition chapter. */
  function prosthesBadgeAnagnorisis(goneas) {
    const protaseis = [];
    if (einaiMetrikoPositiko(synola.imeres))
      protaseis.push({
        keimeno: `${arithmos(synola.imeres)} · Recorded days`,
        analisi: synolikaMetrika()[8],
      });
    if (einaiMetrikoPositiko(synola.ypopraktores))
      protaseis.push({
        keimeno: `Agent ensemble · ${arithmos(synola.ypopraktores)}`,
        analisi: synolikaMetrika()[2],
      });
    if (einaiMetrikoPositiko(synola.commits))
      protaseis.push({
        keimeno: `Repository footprint · ${arithmos(synola.commits)}`,
        analisi: synolikaMetrika()[7],
      });
    const badges = protaseis.slice(0, MAX_RECOGNITION_BADGES);
    if (!badges.length) return;
    const lista = asto(
      goneas,
      "div",
      "recognition-badges",
    );
    lista.setAttribute("role", "group");
    lista.setAttribute("aria-label", "Recorded facts");
    badges.forEach((badge) => {
      const koumpi = ftiakse("button", "scene-pill recognition-badge", badge.keimeno);
      koumpi.type = "button";
      koumpi.setAttribute("aria-label", `${badge.keimeno}. Open details.`);
      koumpi.addEventListener("click", () =>
        anoixeLeptomereia(badge.analisi, koumpi),
      );
      lista.append(koumpi);
    });
  }

  /** Updates the clickable chapter progress strip. */
  function emfaniseProodo() {
    const riza = stoixeia("story-progress");
    riza.replaceChildren();
    skines.forEach((skini, deiktis) => {
      const koumpi = ftiakse(
        "button",
        `progress-step${deiktis === katastasi.skini ? " is-current" : deiktis < katastasi.skini ? " is-done" : ""}`,
      );
      koumpi.type = "button";
      koumpi.setAttribute("aria-label", `Go to chapter ${deiktis + 1}`);
      koumpi.setAttribute(
        "aria-current",
        deiktis === katastasi.skini ? "step" : "false",
      );
      asto(koumpi, "span", "");
      koumpi.addEventListener("click", () => {
        pausaIstoria();
        katastasi.skini = deiktis;
        emfaniseSkini();
      });
      riza.append(koumpi);
    });
  }

  /** Stops automatic scene changes and leaves the current chapter readable. */
  function pausaIstoria() {
    window.clearTimeout(katastasi.timer);
    katastasi.timer = null;
    katastasi.paused = true;
    stoixeia("play-story").textContent = "▶ Play";
    stoixeia("play-story").setAttribute("aria-label", "Play story");
  }

  /** Advances to a bounded chapter, optionally continuing the story. */
  function proxori(deiktis) {
    katastasi.skini = (deiktis + skiniData.length) % skiniData.length;
    emfaniseSkini();
    if (!katastasi.paused)
      katastasi.timer = window.setTimeout(
        () => proxori(katastasi.skini + 1),
        KINISI_AUTO_MS,
      );
  }

  /** Switches between Story and Explore while keeping the active chapter. */
  function setProvoli(provoli) {
    katastasi.proboli = provoli;
    const istoria = provoli === "story";
    stoixeia("story-view").hidden = !istoria;
    stoixeia("explore-view").hidden = istoria;
    stoixeia("story-tab").classList.toggle("is-selected", istoria);
    stoixeia("explore-tab").classList.toggle("is-selected", !istoria);
    stoixeia("story-tab").setAttribute("aria-selected", String(istoria));
    stoixeia("explore-tab").setAttribute("aria-selected", String(!istoria));
    if (!istoria) emfaniseExplore();
  }

  /** Creates an SVG sparkline from recorded numeric activity points. */
  function ftiakseSparkline(times) {
    const stoixeioSvg = document.createElementNS(SVG_XOROS, "svg");
    stoixeioSvg.setAttribute("viewBox", "0 0 100 40");
    stoixeioSvg.setAttribute("class", "metric-spark");
    stoixeioSvg.setAttribute("aria-hidden", "true");
    const egkyresTimi = times.map(Number).filter(Number.isFinite);
    if (!egkyresTimi.length) return stoixeioSvg;
    const megisto = Math.max(1, ...egkyresTimi);
    const elaxistiTimi = Math.min(...egkyresTimi);
    const evros = Math.max(1, megisto - elaxistiTimi);
    const simeia = egkyresTimi
      .map(
        (timiValue, deiktis) =>
          `${egkyresTimi.length === 1 ? 50 : (deiktis * 96) / (egkyresTimi.length - 1) + 2},${36 - ((timiValue - elaxistiTimi) / evros) * 30}`,
      )
      .join(" ");
    const polugrammi = document.createElementNS(SVG_XOROS, "polyline");
    polugrammi.setAttribute("points", simeia);
    polugrammi.setAttribute("fill", "none");
    polugrammi.setAttribute("stroke", "currentColor");
    polugrammi.setAttribute("stroke-width", "2.5");
    polugrammi.setAttribute("stroke-linecap", "round");
    polugrammi.setAttribute("stroke-linejoin", "round");
    stoixeioSvg.append(polugrammi);
    return stoixeioSvg;
  }

  /** Adds a selectable metrika card with an honest unavailable state. */
  function prosthesMetriko(goneas, stoixeio, epiloges = {}) {
    const karta = ftiakse(
      "button",
      `metric-card${epiloges.className ? ` ${epiloges.className}` : ""}`,
    );
    karta.type = "button";
    asto(karta, "span", "metric-label", stoixeio.titlos);
    const timiValue =
      stoixeio.value === null || stoixeio.value === undefined
        ? "Not recorded"
        : `${arithmos(stoixeio.value)} ${stoixeio.unit}`;
    asto(
      karta,
      "div",
      `metric-value${stoixeio.value === null || stoixeio.value === undefined ? " is-null" : ""}`,
      timiValue,
    );
    asto(
      karta,
      "span",
      "metric-caption",
      stoixeio.value === null || stoixeio.value === undefined
        ? stoixeio.description
        : `${stoixeio.source} · Open breakdown`,
    );
    asto(karta, "span", "metric-arrow", "↗");
    if (epiloges.spark) karta.append(ftiakseSparkline(epiloges.spark));
    karta.addEventListener("click", () => anoixeLeptomereia(stoixeio, karta));
    goneas.append(karta);
  }

  /** Renders a real activity line chart using only the supplied dated aggregates. */
  function prosthesGrafimaDrastiriotitas(goneas) {
    const karta = ftiakse("button", "metric-card chart-card");
    karta.type = "button";
    asto(karta, "div", "metric-label", "ACTIVITY · RECORDED BY DATE");
    const stoixeioSvg = document.createElementNS(SVG_XOROS, "svg");
    stoixeioSvg.setAttribute("viewBox", "0 0 600 150");
    stoixeioSvg.setAttribute("class", "chart-svg");
    stoixeioSvg.setAttribute("role", "img");
    stoixeioSvg.setAttribute("aria-label", "Recorded prompts by date");
    const orismoiSvg = document.createElementNS(SVG_XOROS, "defs");
    const klimosi = document.createElementNS(SVG_XOROS, "linearGradient");
    klimosi.id = "chart-fill";
    klimosi.setAttribute("x1", "0");
    klimosi.setAttribute("x2", "0");
    klimosi.setAttribute("y1", "0");
    klimosi.setAttribute("y2", "1");
    const diakopi1 = document.createElementNS(SVG_XOROS, "stop");
    diakopi1.setAttribute("offset", "0%");
    diakopi1.setAttribute("stop-color", "#c6ff4a");
    diakopi1.setAttribute("stop-opacity", ".25");
    const diakopi2 = document.createElementNS(SVG_XOROS, "stop");
    diakopi2.setAttribute("offset", "100%");
    diakopi2.setAttribute("stop-color", "#c6ff4a");
    diakopi2.setAttribute("stop-opacity", "0");
    klimosi.append(diakopi1, diakopi2);
    orismoiSvg.append(klimosi);
    stoixeioSvg.append(orismoiSvg);
    [25, 65, 105].forEach((syntetagmeniY) => {
      const grammiKeimenou = document.createElementNS(SVG_XOROS, "line");
      grammiKeimenou.setAttribute("x1", "4");
      grammiKeimenou.setAttribute("x2", "596");
      grammiKeimenou.setAttribute("y1", String(syntetagmeniY));
      grammiKeimenou.setAttribute("y2", String(syntetagmeniY));
      grammiKeimenou.setAttribute("class", "chart-grid");
      stoixeioSvg.append(grammiKeimenou);
    });
    const grammesPigwn = katastasi.pigi === "all" ? drastiriotita : [];
    const times = grammesPigwn.map((grammi) => Number(grammi.prompts) || 0);
    if (times.length) {
      const megisto = Math.max(1, ...times);
      const syntetagmenes = times.map(
        (timiN, deiktisI) =>
          `${times.length === 1 ? 300 : 8 + (deiktisI * 584) / (times.length - 1)},${130 - (timiN / megisto) * 112}`,
      );
      const epifaneia = document.createElementNS(SVG_XOROS, "polygon");
      epifaneia.setAttribute("points", `8,140 ${syntetagmenes.join(" ")} 592,140`);
      epifaneia.setAttribute("class", "chart-area");
      stoixeioSvg.append(epifaneia);
      const polugrammi = document.createElementNS(SVG_XOROS, "polyline");
      polugrammi.setAttribute("points", syntetagmenes.join(" "));
      polugrammi.setAttribute("class", "chart-line");
      stoixeioSvg.append(polugrammi);
      asto(
        karta,
        "span",
        "metric-caption",
        `${times.length} dated activity points · prompt counts`,
      );
    } else
      asto(
        karta,
        "span",
        "metric-caption",
        katastasi.pigi === "all"
          ? "No dated activity recorded."
          : "Date aggregates are not available per source; this chart shows all-source data only.",
      );
    karta.prepend(stoixeioSvg);
    karta.addEventListener("click", () =>
      anoixeLeptomereia(
        metrika(
          "Activity by date",
          times.length ? times.reduce((aAristera, bDexia) => aAristera + bDexia, 0) : null,
          "prompts",
          "Daily prompt totals from recorded activity points. Dates are retained as provided by the source.",
          dedomena.periodos && dedomena.periodos.zoni
            ? dedomena.periodos.zoni
            : onomataPigwn(),
          grammesPigwn.map((grammi) => [grammi.imerominia, grammi.prompts]),
        ),
        karta,
      ),
    );
    goneas.append(karta);
  }

  /** Displays ranked tool counts from the source-filtered aggregate list. */
  function prosthesGrafimaErgaleion(goneas) {
    const grammes = filtrismenaErgaleia()
      .filter((grammi) => grammi.prompts !== null && grammi.prompts !== undefined)
      .sort((aAristera, bDexia) => (Number(bDexia.prompts) || 0) - (Number(aAristera.prompts) || 0));
    const karta = ftiakse("button", "metric-card chart-card");
    karta.type = "button";
    asto(karta, "span", "metric-label", "TOOLS · PROMPTS BY SOURCE");
    if (!grammes.length) asto(karta, "p", "metric-value is-null", "Not recorded");
    else {
      const megisto = Math.max(1, ...grammes.map((grammi) => Number(grammi.prompts) || 0));
      const lista = asto(karta, "div", "bar-list");
      grammes.slice(0, 6).forEach((grammi) => {
        const grammiKeimenou = asto(lista, "div", "bar-row");
        asto(grammiKeimenou, "span", "bar-name", keimeno(grammi, "onoma", "Tool"));
        const diadromi = asto(grammiKeimenou, "span", "bar-track");
        const gemisma = asto(diadromi, "span", "bar-fill");
        gemisma.style.width = `${Math.max(2, ((Number(grammi.prompts) || 0) / megisto) * 100)}%`;
        asto(grammiKeimenou, "span", "bar-count", arithmos(grammi.prompts));
      });
    }
    asto(
      karta,
      "span",
      "metric-caption",
      katastasi.pigi === "all"
        ? "Ranked by recorded prompts"
        : `Filtered to ${katastasi.pigi}`,
    );
    karta.addEventListener("click", () =>
      anoixeLeptomereia(
        metrika(
          "Tool prompts",
          grammes.length
            ? grammes.reduce((athroisma, grammi) => athroisma + (Number(grammi.prompts) || 0), 0)
            : null,
          "prompts",
          "Tool-specific prompt counts as recorded by each selected source.",
          katastasi.pigi === "all" ? onomataPigwn() : katastasi.pigi,
          grammes.map((grammi) => [keimeno(grammi, "onoma", "Tool"), grammi.prompts]),
        ),
        karta,
      ),
    );
    goneas.append(karta);
  }

  /** Renders evidence-based findings and keeps strengths and growth equally visible. */
  function prosthesEyrimata(goneas) {
    const grammes = [...eyrimata].sort(
      (aAristera, bDexia) =>
        ["strength", "growth", "info"].indexOf(aAristera.epipedo) -
        ["strength", "growth", "info"].indexOf(bDexia.epipedo),
    );
    if (!grammes.length) {
      asto(
        goneas,
        "div",
        "empty-card",
        "No verified observations yet. As more supported history is available, this space will show evidence and practical next steps.",
      );
      return;
    }
    let epomenaVimataPouFainontai = 0;
    grammes.forEach((grammi) => {
      const karta = ftiakse("button", "metric-card finding-card");
      karta.type = "button";
      const epipedoLocal = ["strength", "growth", "info"].includes(grammi.epipedo)
        ? grammi.epipedo
        : "info";
      const eyrimaYpopsifio = grammi.katastasi === "candidate_only";
      asto(
        karta,
        "span",
        `finding-tag ${eyrimaYpopsifio ? "info" : epipedoLocal}`,
        eyrimaYpopsifio
          ? "◌ OBSERVED PROMPT CUE"
          : epipedoLocal === "strength"
          ? "✦ RECOGNITION"
          : epipedoLocal === "growth"
            ? "↗ NEXT MOVE"
            : "● OBSERVATION",
      );
      asto(karta, "h3", "finding-title", keimeno(grammi, "titlos", "Observation"));
      asto(
        karta,
        "p",
        "finding-copy",
        keimeno(grammi, "keimeno", "No description recorded."),
      );
      const epomeno = keimeno(grammi, "protasi");
      if (epomeno && epomenaVimataPouFainontai < MEGISTO_EPOMENA_VIMATA) {
        asto(karta, "p", "finding-next", `Try next: ${epomeno}`);
        epomenaVimataPouFainontai += 1;
      }
      karta.addEventListener("click", () => anoixeEyrima(grammi, karta));
      goneas.append(karta);
    });
  }

  /** Shows dimension assessment without filling unknown grades with invented numbers. */
  function prosthesAxiologisi(goneas) {
    const karta = ftiakse("div", "assessment-card");
    const keimenoLocal = asto(karta, "div", "");
    const analisiTopiki =
      dedomena.analysi && typeof dedomena.analysi === "object"
        ? dedomena.analysi
        : null;
    const bathmosDiathesimos =
      dedomena.axiologisi &&
      dedomena.axiologisi.diathesimi &&
      dedomena.axiologisi.synoliko !== null &&
      dedomena.axiologisi.synoliko !== undefined &&
      analisiTopiki?.katastasi !== "failed";
    asto(keimenoLocal, "span", "eyebrow", "ASSESSMENT · EVIDENCE FIRST");
    asto(keimenoLocal, "h3", "", "Your workflow, with receipts.");
    asto(
      keimenoLocal,
      "p",
      "",
      bathmosDiathesimos
        ? keimeno(
            dedomena.axiologisi,
            "aitia",
            "A rules-based score is available; inspect its evidence.",
          )
        : analisiTopiki?.katastasi === "failed"
          ? "Local analysis failed; no derived score is shown."
          : (dedomena.axiologisi && keimeno(dedomena.axiologisi, "aitia")) ||
            "Score unavailable. A validated rubric and enough verified evidence are required before a score can be shown.",
    );
    const bathmosLocal = asto(
      karta,
      "div",
      "assessment-score",
      bathmosDiathesimos
        ? arithmos(dedomena.axiologisi.synoliko)
        : "—",
    );
    asto(
      bathmosLocal,
      "small",
      "",
      bathmosDiathesimos
        ? "RULES SCORE"
        : "SCORE UNAVAILABLE",
    );
    goneas.append(karta);
  }

  /** Shows missing sources and calibration limits in both Story and Explore. */
  function emfaniseKalypsi() {
    const alerta = stoixeia("coverage-alert");
    const minimataKalypsis = [];
    const provlimataPigon = piges.filter(
      (pigi) => pigi && ["partial", "missing"].includes(pigi.katastasi),
    );
    if (!piges.length)
      minimataKalypsis.push(
        "No source data is attached. Unknown metrics stay unknown until sources are selected.",
      );
    provlimataPigon.forEach((pigi) => {
      const onomaPigis = keimeno(pigi, "onoma", "Selected source");
      const simeiosiPigis = keimeno(pigi, "simeiosi");
      minimataKalypsis.push(
        `${onomaPigis}: ${pigi.katastasi}${simeiosiPigis ? ` · ${simeiosiPigis}` : ""}`,
      );
    });
    const kalypsi =
      dedomena.kalypsi_analysi && typeof dedomena.kalypsi_analysi === "object"
        ? dedomena.kalypsi_analysi
        : null;
    if (kalypsi) {
      const epilegmena = arithmos(kalypsi.epilegmena);
      const diathesima = arithmos(kalypsi.diathesima);
      const perikopiKeimeno =
        kalypsi.perikopi === true
          ? " · bounded sample"
          : " · complete available sample";
      minimataKalypsis.push(
        `Assessment evidence: ${epilegmena} selected of ${diathesima} available${perikopiKeimeno}`,
      );
    } else
      minimataKalypsis.push("Assessment evidence coverage is unavailable.");
    const analisiTopiki =
      dedomena.analysi && typeof dedomena.analysi === "object"
        ? dedomena.analysi
        : null;
    if (!analisiTopiki)
      minimataKalypsis.push("Local analysis status was not recorded.");
    else if (analisiTopiki.katastasi === "failed") {
      const aitia = keimeno(
        analisiTopiki,
        "aitia",
        "The reason was not recorded.",
      );
      minimataKalypsis.push(
        `Local analysis failed: ${aitia} No derived score is shown.`,
      );
    } else if (analisiTopiki.katastasi === "ok") {
      const methodos = keimeno(
        analisiTopiki,
        "methodoslocal",
        "method not recorded",
      );
      const modelo = keimeno(analisiTopiki, "model_id", keimeno(analisiTopiki, "modelo"));
      minimataKalypsis.push(
        `Local analysis complete · ${methodos}${modelo ? ` · ${modelo}` : ""} · based on selected local sources. Numeric scoring still requires rubric calibration.`,
      );
    } else
      minimataKalypsis.push("Local analysis status was not recorded.");
    if (!dedomena.axiologisi || dedomena.axiologisi.diathesimi !== true)
      minimataKalypsis.push(
        "Score unavailable until the rubric and evidence are calibrated.",
      );
    alerta.hidden = minimataKalypsis.length === 0;
    alerta.dataset.level =
      provlimataPigon.length || !piges.length ? "warning" : "info";
    alerta.textContent = minimataKalypsis.join(" · ");
    return minimataKalypsis.join(" · ");
  }

  /** Adds rubric dimensions with null grades and evidence episodes. */
  function prosthesDiastaseis(goneas) {
    const axiologisi =
      dedomena.axiologisi && typeof dedomena.axiologisi === "object"
        ? dedomena.axiologisi
        : {};
    const diastaseis = Array.isArray(axiologisi.diastaseis)
      ? axiologisi.diastaseis
      : [];
    if (!diastaseis.length) {
      asto(
        goneas,
        "div",
        "empty-card",
        "No rubric dimensions were supplied. Scores remain unavailable.",
      );
      return;
    }
    diastaseis.slice(0, 5).forEach((diastasi) => {
      const karta = ftiakse("button", "metric-card dimension-card");
      karta.type = "button";
      const arxeiaTekmirion = Array.isArray(diastasi.tekmiria)
        ? diastasi.tekmiria
        : [];
      const anaforeis = new Set(
        arxeiaTekmirion
          .map((tekmirio) =>
            typeof tekmirio === "string"
              ? tekmirio
              : keimeno(tekmirio, "locator"),
          )
          .filter(Boolean),
      );
      const sindedemenaDeigmata = deigmata.filter(
        (deigma) => anaforeis.has(deigma.id) || anaforeis.has(deigma.locator),
      );
      const plithosSynedrion = new Set(
        sindedemenaDeigmata.map((deigma) => deigma.synedria).filter(Boolean),
      ).size;
      const episodia =
        diastasi.episodia !== null &&
        diastasi.episodia !== undefined &&
        Number.isFinite(Number(diastasi.episodia))
        ? Number(diastasi.episodia)
        : null;
      const einaiPrompt = sindedemenaDeigmata.some(
        (deigma) => deigma.rolos === "user" && deigma.eidos === "prompt",
      );
      asto(
        karta,
        "span",
        "metric-label",
        keimeno(diastasi, "onoma", "Engineering dimension"),
      );
      asto(
        karta,
        "div",
        "dimension-status",
        diastasi.bathmos === null || diastasi.bathmos === undefined
          ? "UNSCORED"
          : `SCORE ${arithmos(diastasi.bathmos)}`,
      );
      asto(
        karta,
        "div",
        "dimension-cues",
        plithosSynedrion
          ? `${arithmos(plithosSynedrion)} cue-bearing ${plithosSynedrion === 1 ? "session" : "sessions"}`
          : episodia !== null
            ? `${arithmos(episodia)} evidence ${episodia === 1 ? "episode" : "episodes"}`
            : arxeiaTekmirion.length
              ? `${arithmos(arxeiaTekmirion.length)} linked evidence ${arxeiaTekmirion.length === 1 ? "cue" : "cues"}`
              : "Evidence count not recorded",
      );
      asto(
        karta,
        "p",
        "metric-caption",
        einaiPrompt
          ? "Prompt signals; inspect evidence."
          : episodia !== null && episodia > 0
            ? "Recorded cues; inspect evidence."
            : "No prompt cue in the selected sample.",
      );
      asto(karta, "span", "metric-arrow", "↗");
      karta.addEventListener("click", () => anoixeDiastasi(diastasi, karta));
      goneas.append(karta);
    });
  }

  /** Shows normalized event evidence without displaying raw excerpts on cards. */
  function prosthesDeigmata(goneas) {
    if (!deigmata.length) return;
    deigmata.slice(0, MEGISTO_DEIGMATA).forEach((deigma) => {
      const karta = ftiakse("button", "metric-card evidence-card");
      karta.type = "button";
      const rolos = keimeno(deigma, "rolos", "record");
      const eidos = keimeno(deigma, "eidos", "evidence").replaceAll("-", " ");
      asto(
        karta,
        "span",
        "metric-label",
        `${rolos.toUpperCase()} · ${eidos.toUpperCase()}`,
      );
      asto(
        karta,
        "h3",
        "finding-title",
        keimeno(deigma, "pigi", "Selected source"),
      );
      asto(
        karta,
        "p",
        "metric-caption",
        `${keimeno(deigma, "imerominia", "Date unavailable")} · Recorded event · open private evidence`,
      );
      asto(karta, "span", "metric-arrow", "↗");
      karta.addEventListener("click", () => anoixeDeigma(deigma, karta));
      goneas.append(karta);
    });
  }

  /** Draws all cards for the selected category from the shared report data. */
  function emfaniseExplore() {
    const riza = stoixeia("explore-cards");
    riza.replaceChildren();
    const titlosXartis = {
      overview: "This period, in detail.",
      tools: "The tools behind the work.",
      activity: "A rhythm you can see.",
      agents: "Work that moved in parallel.",
      projects: "Where the work landed.",
      growth: "Strengths and next moves.",
    };
    stoixeia("explore-title").textContent =
      titlosXartis[katastasi.enotita] || titlosXartis.overview;
    const epilogiPigis = stoixeia("source-filter");
    epilogiPigis.replaceChildren();
    const epilogiOlon = ftiakse("option", "", "All sources");
    epilogiOlon.value = "all";
    epilogiPigis.append(epilogiOlon);
    piges.forEach((grammi) => {
      const onoma = keimeno(grammi, "onoma");
      if (!onoma) return;
      const epilogi = ftiakse("option", "", onoma);
      epilogi.value = onoma;
      epilogiPigis.append(epilogi);
    });
    epilogiPigis.value = katastasi.pigi;
    const simeiosi =
      katastasi.pigi === "all"
        ? "The source filter applies to the prompts-by-source chart; other cards stay report-wide."
        : `Prompt chart filtered to ${katastasi.pigi}. Other cards stay report-wide.`;
    stoixeia("explore-subtitle").textContent = `${simeiosi} ${eurosGit()}.`;
    const enotita = katastasi.enotita;
    if (enotita === "overview") {
      prosthesGrafimaDrastiriotitas(riza);
      prosthesGrafimaErgaleion(riza);
      synolikaMetrika().forEach((grammi) =>
        prosthesMetriko(riza, grammi, {
          spark:
            grammi.titlos === "Active days"
              ? drastiriotita.map((simeio) => simeio.prompts)
              : null,
        }),
      );
    }
    if (enotita === "tools") {
      prosthesGrafimaErgaleion(riza);
      montela.forEach((grammi) =>
        prosthesMetriko(
          riza,
          metrika(
            keimeno(grammi, "onoma", "Recorded model"),
            grammi.tokens,
            "tokens",
            "Recorded tokens associated with this model. A missing value means the source did not report tokens.",
            onomataPigwn(),
            [
              ["Calls", grammi.kliseis],
              ["Tokens", grammi.tokens],
            ],
          ),
        ),
      );
      ergaleia.forEach((grammi) =>
        prosthesMetriko(
          riza,
          metrika(
            keimeno(grammi, "onoma", "Tool"),
            grammi.prompts,
            "prompts",
            "Prompt and session totals recorded for this tool.",
            keimeno(grammi, "onoma"),
            [
              ["Sessions", grammi.synedries],
              ["Prompts", grammi.prompts],
              ["Tokens", grammi.tokens],
            ],
          ),
        ),
      );
    }
    if (enotita === "activity") {
      prosthesGrafimaDrastiriotitas(riza);
      [
        synolikaMetrika()[0],
        synolikaMetrika()[3],
        synolikaMetrika()[4],
        synolikaMetrika()[8],
      ].forEach((grammi) => prosthesMetriko(riza, grammi));
    }
    if (enotita === "agents") {
      prosthesMetriko(riza, synolikaMetrika()[1]);
      prosthesMetriko(riza, synolikaMetrika()[2]);
      prosthesMetriko(riza, synolikaMetrika()[5]);
      if (synola.ypopraktores === null || synola.ypopraktores === undefined)
        asto(
          riza,
          "div",
          "empty-card",
          "Agent totals were not recorded. This report does not infer delegation from session names.",
        );
      else if (Number(synola.ypopraktores) === 0)
        asto(
          riza,
          "div",
          "empty-card",
          "No child sessions were recorded in this period. Root sessions remain separate.",
        );
    }
    if (enotita === "projects") {
      prosthesMetriko(riza, synolikaMetrika()[7]);
      if (!erga.length)
        asto(
          riza,
          "div",
          "empty-card",
          "No project breakdown was recorded. Repository names and counts are only included when a repository was explicitly selected.",
        );
      erga.forEach((grammi) =>
        prosthesMetriko(
          riza,
          metrika(
            keimeno(grammi, "onoma", "Project"),
            grammi.commits,
            "commits",
            "Commits and file counts from the explicitly selected repository scope.",
            onomataPigwn(),
            [
              ["Commits", grammi.commits],
              ["Files", grammi.arxeia],
            ],
          ),
        ),
      );
    }
    if (enotita === "growth") {
      prosthesAxiologisi(riza);
      prosthesDiastaseis(riza);
      prosthesEyrimata(riza);
      prosthesDeigmata(riza);
    }
    const keimenoKalypsis = emfaniseKalypsi();
    stoixeia("coverage-note").textContent =
      `${keimenoKalypsis || "Based on recorded data"} · ${simeiosi}`;
    document
      .querySelectorAll(".nav-item,.category-tab")
      .forEach((koumpi) =>
        koumpi.classList.toggle("is-active", koumpi.dataset.view === enotita),
      );
  }

  /** Opens a metrika detail dialog and remembers the trigger for focus restoration. */
  function anoixeLeptomereia(stoixeio, energopoiitis) {
    pausaIstoria();
    katastasi.dialogReturn = energopoiitis || document.activeElement;
    const soma = stoixeia("dialog-body");
    soma.replaceChildren();
    asto(soma, "h2", "dialog-title", stoixeio.titlos);
    asto(
      soma,
      "div",
      `dialog-value${stoixeio.value === null || stoixeio.value === undefined ? " is-null" : ""}`,
      stoixeio.value === null || stoixeio.value === undefined
        ? "Not recorded"
        : arithmos(stoixeio.value),
    );
    asto(
      soma,
      "div",
      "dialog-unit",
      stoixeio.value === null || stoixeio.value === undefined
        ? "VALUE UNAVAILABLE"
        : stoixeio.unit.toUpperCase(),
    );
    asto(soma, "p", "dialog-description", stoixeio.description);
    const metadedomena = asto(soma, "div", "dialog-meta");
    const pote = asto(metadedomena, "div", "meta-block");
    asto(pote, "small", "", "PERIOD");
    asto(pote, "span", "", stoixeio.period);
    const apoPigi = asto(metadedomena, "div", "meta-block");
    asto(apoPigi, "small", "", "SOURCE");
    asto(apoPigi, "span", "", stoixeio.source || "Not recorded");
    if (stoixeio.breakdown && stoixeio.breakdown.length) {
      const enotitaDialogou = asto(soma, "div", "detail-breakdown");
      asto(enotitaDialogou, "h3", "", "BREAKDOWN");
      stoixeio.breakdown.forEach((eggrafi) => {
        const grammiKeimenou = asto(enotitaDialogou, "div", "detail-row");
        asto(grammiKeimenou, "span", "", String(eggrafi[0]));
        asto(
          grammiKeimenou,
          "span",
          "",
            eggrafi[1] === null || eggrafi[1] === undefined
              ? "Not recorded"
              : typeof eggrafi[1] === "number"
                ? arithmos(eggrafi[1])
                : String(eggrafi[1]),
        );
      });
    }
    stoixeia("detail-dialog").showModal();
    stoixeia("close-dialog").focus();
  }

  /** Opens an evidence detail for a finding with safe text-only rendering. */
  function anoixeEyrima(grammi, energopoiitis) {
    anoixeLeptomereia(
      metrika(
        keimeno(grammi, "titlos", "Observation"),
        null,
        "finding",
        keimeno(grammi, "keimeno", "Observation based on available history."),
        onomataPigwn(),
      ),
      energopoiitis,
    );
    const soma = stoixeia("dialog-body");
    const epomeno = keimeno(grammi, "protasi");
    if (epomeno) asto(soma, "p", "dialog-description", `Try next: ${epomeno}`);
    for (const [kleidi, etiketa] of [
      ["eythyni", "RESPONSIBILITY"],
      ["vevaiotita", "CONFIDENCE"],
      ["aitiologia_vevaiotitas", "CONFIDENCE LIMIT"],
      ["enallaktiki", "ALTERNATIVE EXPLANATION"],
      ["antitheta", "LIMITING EVIDENCE"],
    ]) {
      const timiValue = keimeno(grammi, kleidi);
      if (!timiValue) continue;
      const plaisio = asto(soma, "div", "evidence-context");
      asto(plaisio, "small", "", etiketa);
      asto(plaisio, "p", "", timiValue);
    }
    const tekmiriaData = Array.isArray(grammi.tekmiria) ? grammi.tekmiria : [];
    if (tekmiriaData.length) {
      const enotitaDialogou = asto(soma, "div", "dialog-evidence");
      asto(enotitaDialogou, "h3", "", "RECORDED EVIDENCE");
      tekmiriaData.forEach((stoixeio) => {
        const parathesi = asto(
          enotitaDialogou,
          "blockquote",
          "",
          keimeno(stoixeio, "apospasma", "Evidence excerpt unavailable."),
        );
        asto(
          parathesi,
          "cite",
          "",
          `${keimeno(stoixeio, "pigi", "Source")} · ${keimeno(stoixeio, "locator", "record")}`,
        );
      });
    }
  }

  /** Opens one rubric dimension with its reason, episode count, and private evidence. */
  function anoixeDiastasi(diastasi, energopoiitis) {
    const tekmiria = Array.isArray(diastasi.tekmiria) ? diastasi.tekmiria : [];
    const leptomereiaMetrikou = metrika(
      keimeno(diastasi, "onoma", "Engineering dimension"),
      diastasi.bathmos,
      "grade",
      keimeno(diastasi, "aitia", "No calibrated grade is available."),
      "Assessment rubric",
      [["Evidence episodes", diastasi.episodia]],
    );
    anoixeLeptomereia(leptomereiaMetrikou, energopoiitis);
    if (!tekmiria.length) return;
    const soma = stoixeia("dialog-body");
    const enotitaDialogou = asto(soma, "div", "dialog-evidence");
    asto(enotitaDialogou, "h3", "", "PRIVATE EVIDENCE");
    tekmiria.slice(0, MEGISTO_DEIGMATA).forEach((anafora) => {
      const tekmirio =
        typeof anafora === "string"
          ? deigmata.find((deigma) => deigma.id === anafora)
          : anafora;
      const parathesi = asto(
        enotitaDialogou,
        "blockquote",
        "",
        keimeno(
          tekmirio,
          "apospasma",
          keimeno(tekmirio, "keimeno", "Evidence excerpt unavailable."),
        ),
      );
      asto(
        parathesi,
        "cite",
        "",
        `${keimeno(tekmirio, "pigi", "Source")} · ${keimeno(tekmirio, "locator", "record")}`,
      );
    });
  }

  /** Opens one normalized event record inside the private evidence dialog. */
  function anoixeDeigma(deigma, energopoiitis) {
    const leptomereiaDeigmatos = metrika(
      `${keimeno(deigma, "rolos", "record")} · ${keimeno(deigma, "eidos", "evidence")}`,
      null,
      "private evidence",
      "This source excerpt remains in the local private report.",
      keimeno(deigma, "pigi", "Selected source"),
      [
        ["Session", deigma.synedria],
        ["Date", deigma.imerominia],
        ["Locator", deigma.locator],
      ],
    );
    anoixeLeptomereia(leptomereiaDeigmatos, energopoiitis);
    const soma = stoixeia("dialog-body");
    const enotitaDialogou = asto(soma, "div", "dialog-evidence");
    asto(enotitaDialogou, "h3", "", "PRIVATE SOURCE EXCERPT");
    asto(
      enotitaDialogou,
      "blockquote",
      "",
      keimeno(deigma, "keimeno", "No source text was recorded."),
    );
  }

  /** Restores focus to the exact control that opened the dialog. */
  function kleiseLeptomereia() {
    const dialogos = stoixeia("detail-dialog");
    if (dialogos.open) dialogos.close();
    if (
      katastasi.dialogReturn &&
      typeof katastasi.dialogReturn.focus === "function"
    )
      katastasi.dialogReturn.focus();
  }

  /** Downloads a share SVG containing only allowlisted report-wide aggregates. */
  function apothikefseKartaKoinopoiisis() {
    const stoixeioSvg = document.createElementNS(SVG_XOROS, "svg");
    stoixeioSvg.setAttribute("xmlns", SVG_XOROS);
    stoixeioSvg.setAttribute("width", "1080");
    stoixeioSvg.setAttribute("height", "1350");
    stoixeioSvg.setAttribute("viewBox", "0 0 1080 1350");
    const orthog = document.createElementNS(SVG_XOROS, "rect");
    orthog.setAttribute("width", "1080");
    orthog.setAttribute("height", "1350");
    orthog.setAttribute("rx", "36");
    orthog.setAttribute("fill", "#111115");
    stoixeioSvg.append(orthog);
    const sfera = document.createElementNS(SVG_XOROS, "circle");
    sfera.setAttribute("cx", "900");
    sfera.setAttribute("cy", "210");
    sfera.setAttribute("r", "205");
    sfera.setAttribute("fill", "#9762ff");
    stoixeioSvg.append(sfera);
    const keimena = [
      ["DEVRAR / WORK REPLAY", 88, 110, 24, "#c6ff4a", "800"],
      [timi(synola.synedries), 88, 365, 82, "#f7f6f0", "900"],
      ["RECORDED SESSIONS", 92, 410, 18, "#c6ff4a", "800"],
      [timi(synola.minimata_xristi), 88, 565, 68, "#ff4fc8", "900"],
      ["USER PROMPTS", 92, 608, 18, "#f7f6f0", "800"],
      [timi(synola.imeres), 88, 760, 68, "#5de2e5", "900"],
      ["ACTIVE DAYS", 92, 804, 18, "#f7f6f0", "800"],
      [timi(synola.commits), 88, 950, 68, "#c6ff4a", "900"],
      ["RECORDED COMMITS", 92, 994, 18, "#f7f6f0", "800"],
      ["MY WORK. MY MACHINE. MY DATA.", 88, 1220, 23, "#a3a1ad", "700"],
    ];
    keimena.forEach(([timiValue, x, syntetagmeniY, size, gemisma, weight]) => {
      const keimenoSvg = document.createElementNS(SVG_XOROS, "text");
      keimenoSvg.setAttribute("x", String(x));
      keimenoSvg.setAttribute("y", String(syntetagmeniY));
      keimenoSvg.setAttribute("font-size", String(size));
      keimenoSvg.setAttribute("font-family", "Arial, sans-serif");
      keimenoSvg.setAttribute("font-weight", String(weight));
      keimenoSvg.setAttribute("fill", String(gemisma));
      keimenoSvg.textContent = String(timiValue);
      stoixeioSvg.append(keimenoSvg);
    });
    if (dedomena.leitourgia === "demo") {
      const etiketa = document.createElementNS(SVG_XOROS, "text");
      etiketa.setAttribute("x", "88");
      etiketa.setAttribute("y", "1100");
      etiketa.setAttribute("font-size", "20");
      etiketa.setAttribute("font-family", "Arial, sans-serif");
      etiketa.setAttribute("font-weight", "900");
      etiketa.setAttribute("letter-spacing", "2");
      etiketa.setAttribute("fill", "#c6ff4a");
      etiketa.textContent = "SYNTHETIC DEMO DATA";
      stoixeioSvg.append(etiketa);
    }
    const arxeioBlob = new Blob([new XMLSerializer().serializeToString(stoixeioSvg)], {
      type: "image/svg+xml;charset=utf-8",
    });
    const urlTopikisLipsis = URL.createObjectURL(arxeioBlob);
    const syndesmos = ftiakse("a", "");
    syndesmos.href = urlTopikisLipsis;
    syndesmos.download = "devrar-share-card.svg";
    document.body.append(syndesmos);
    syndesmos.click();
    syndesmos.remove();
    window.setTimeout(() => URL.revokeObjectURL(urlTopikisLipsis), 1500);
  }

  /** Wires view navigation, story controls, dialog, keyboard and mobile gestures. */
  function syndeseXeiristiria() {
    stoixeia("period-text").textContent = periodos();
    stoixeia("demo-banner").hidden = dedomena.leitourgia !== "demo";
    const keimenoPeiragmatos =
      typeof dedomena.afigisi_roast === "string"
        ? dedomena.afigisi_roast.trim()
        : "";
    stoixeia("debra-quote").textContent =
      keimenoPeiragmatos || "Your work has a shape.";
    const simeiosiPeiragmatos = stoixeia("roast-note");
    simeiosiPeiragmatos.hidden = !keimenoPeiragmatos;
    if (keimenoPeiragmatos)
      simeiosiPeiragmatos.textContent = `Debra: ${keimenoPeiragmatos}`;
    stoixeia("story-tab").addEventListener("click", () => setProvoli("story"));
    stoixeia("explore-tab").addEventListener("click", () =>
      setProvoli("explore"),
    );
    stoixeia("footer-story").addEventListener("click", () =>
      setProvoli("story"),
    );
    document.querySelectorAll(".nav-item,.category-tab").forEach((koumpi) =>
      koumpi.addEventListener("click", () => {
        katastasi.enotita = koumpi.dataset.view;
        setProvoli("explore");
      }),
    );
    stoixeia("prev-scene").addEventListener("click", () => {
      pausaIstoria();
      proxori(katastasi.skini - 1);
    });
    stoixeia("next-scene").addEventListener("click", () => {
      pausaIstoria();
      proxori(katastasi.skini + 1);
    });
    stoixeia("replay-scene").addEventListener("click", () => {
      const deiktis = katastasi.skini;
      pausaIstoria();
      katastasi.skini = deiktis;
      emfaniseSkini();
    });
    stoixeia("play-story").addEventListener("click", () => {
      if (katastasi.paused) {
        katastasi.paused = false;
        stoixeia("play-story").textContent = "Ⅱ Pause";
        stoixeia("play-story").setAttribute("aria-label", "Pause story");
        katastasi.timer = window.setTimeout(
          () => proxori(katastasi.skini + 1),
          KINISI_AUTO_MS,
        );
      } else pausaIstoria();
    });
    stoixeia("scene-detail").addEventListener("click", () => {
      const grammi = skiniData[katastasi.skini];
      if (grammi.action === "share") {
        apothikefseKartaKoinopoiisis();
        return;
      }
      anoixeLeptomereia(grammi.detail, stoixeia("scene-detail"));
    });
    stoixeia("source-filter").addEventListener("change", (symvan) => {
      katastasi.pigi = symvan.currentTarget.value;
      emfaniseExplore();
    });
    stoixeia("share-card").addEventListener(
      "click",
      apothikefseKartaKoinopoiisis,
    );
    stoixeia("close-dialog").addEventListener("click", kleiseLeptomereia);
    stoixeia("detail-dialog").addEventListener("click", (symvan) => {
      if (symvan.target === stoixeia("detail-dialog")) kleiseLeptomereia();
    });
    stoixeia("detail-dialog").addEventListener("close", () => {
      if (
        katastasi.dialogReturn &&
        typeof katastasi.dialogReturn.focus === "function"
      )
        katastasi.dialogReturn.focus();
    });
    document.addEventListener("keydown", (symvan) => {
      if (
        stoixeia("detail-dialog").open ||
        katastasi.proboli !== "story" ||
        symvan.altKey ||
        symvan.ctrlKey ||
        symvan.metaKey
      )
        return;
      if (symvan.key === "ArrowRight" || symvan.key === "PageDown") {
        symvan.preventDefault();
        pausaIstoria();
        proxori(katastasi.skini + 1);
      }
      if (symvan.key === "ArrowLeft" || symvan.key === "PageUp") {
        symvan.preventDefault();
        pausaIstoria();
        proxori(katastasi.skini - 1);
      }
      if (
        symvan.key === " " &&
        !["BUTTON", "INPUT", "SELECT"].includes(document.activeElement.typosStoixeiou)
      ) {
        symvan.preventDefault();
        stoixeia("play-story").click();
      }
    });
    let afixiX = null;
    let afixiY = null;
    stoixeia("story-stage").addEventListener(
      "touchstart",
      (symvan) => {
        const afixi = symvan.changedTouches[0];
        afixiX = afixi.clientX;
        afixiY = afixi.clientY;
      },
      { passive: true },
    );
    stoixeia("story-stage").addEventListener(
      "touchend",
      (symvan) => {
        if (afixiX === null || afixiY === null) return;
        const afixi = symvan.changedTouches[0];
        const diaforaX = afixi.clientX - afixiX;
        const diaforaY = afixi.clientY - afixiY;
        if (Math.abs(diaforaX) > 55 && Math.abs(diaforaX) > Math.abs(diaforaY) * 1.2) {
          pausaIstoria();
          proxori(katastasi.skini + (diaforaX < 0 ? 1 : -1));
        }
        afixiX = null;
        afixiY = null;
      },
      { passive: true },
    );
  }

  syndeseXeiristiria();
  emfaniseSkini();
  emfaniseExplore();
})();
