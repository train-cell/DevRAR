"""Exercise generated local HTML in an isolated headless Chromium context."""

import os
import re
from pathlib import Path

import pytest

if os.environ.get("DEVRAR_BROWSER_TESTS") != "1":
    pytest.skip(
        "Set DEVRAR_BROWSER_TESTS=1 for browser checks", allow_module_level=True
    )

from playwright.sync_api import expect, sync_playwright

from devrar.anafora import apothikefse_anafora
from devrar.deigma import fortose_deigma

pytestmark = pytest.mark.browser


def test_browser_deixnei_tin_pragmatiki_methodo_analisis(tmp_path: Path) -> None:
    """Rules mode is not a missing local run; local success shows its real method."""
    dedomena = fortose_deigma()
    rules = apothikefse_anafora(dedomena, tmp_path)
    dedomena["analysi"] = {
        "methodos": "local",
        "katastasi": "ok",
        "model_id": "synthetic-model",
    }
    topiko = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(rules.as_uri(), wait_until="networkidle")
        expect(page.locator("#coverage-alert")).to_contain_text("Rules-based coaching")
        expect(page.locator("#coverage-alert")).not_to_contain_text(
            "Local analysis status was not recorded"
        )
        page.goto(topiko.as_uri(), wait_until="networkidle")
        expect(page.locator("#coverage-alert")).to_contain_text(
            "Local analysis complete · local · synthetic-model"
        )
        browser.close()


def test_browser_proepiskopisi_share_prin_tin_apothikefsi(tmp_path: Path) -> None:
    """Both share entries allow inspection and cancellation before saving."""
    dedomena = fortose_deigma()
    dedomena["projects"] = [{"onoma": "PRIVATE_CANARY", "commits": 1, "arxeia": 1}]
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        lipseis: list[str] = []
        page.on("download", lambda lipsi: lipseis.append(lipsi.suggested_filename))
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator("#explore-tab").click()
        page.locator("#share-card").click()
        expect(page.locator("#detail-dialog")).to_be_visible()
        expect(page.locator("#dialog-title")).to_have_text("Preview your share card")
        proepiskopisi = page.locator(".share-preview")
        expect(proepiskopisi).to_be_visible()
        expect(proepiskopisi).to_contain_text("SYNTHETIC DEMO DATA")
        assert "PRIVATE_CANARY" not in proepiskopisi.text_content()
        assert "2026-10-12" not in proepiskopisi.text_content()
        assert not lipseis
        page.locator("#cancel-share").click()
        expect(page.locator("#detail-dialog")).not_to_be_visible()
        expect(page.locator("#share-card")).to_be_focused()
        assert not lipseis
        page.locator("#story-tab").click()
        page.get_by_role("button", name="Go to chapter 9", exact=True).click()
        page.locator("#scene-detail").click()
        expect(page.locator("#detail-dialog")).to_be_visible()
        expect(page.locator("#detail-dialog")).to_have_accessible_name(re.compile(".+"))
        with page.expect_download() as lipsi:
            page.locator("#save-share").click()
        lipsi.value.save_as(str(tmp_path / "share.svg"))
        expect(page.locator("#detail-dialog")).not_to_be_visible()
        expect(page.locator("#scene-detail")).to_be_focused()
        assert lipseis == ["devrar-share-card.svg"]
        assert "PRIVATE_CANARY" not in (tmp_path / "share.svg").read_text()
        browser.close()


def test_browser_recognition_profile_explains_its_recorded_basis(
    tmp_path: Path,
) -> None:
    """Το profile έχει definition και highlights σε Story/Explore χωρίς grade."""
    selida = apothikefse_anafora(fortose_deigma(), tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(reduced_motion="reduce")
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.get_by_role("button", name="Go to chapter 7", exact=True).click()
        expect(page.locator(".recognition-profile-label")).to_have_text(
            "Multi-tool conductor"
        )
        page.locator(".recognition-profile-label").click()
        expect(page.locator("#dialog-body")).to_contain_text("16 explicit child")
        expect(page.locator("#dialog-body")).to_contain_text("not a personality")
        page.locator("#close-dialog").click()
        page.locator("#explore-tab").click()
        expect(page.locator(".recognition-panel")).to_contain_text(
            "Your work, replayed"
        )
        expect(page.locator(".recognition-panel")).to_contain_text("Claude Code")
        browser.close()


def test_browser_png_export_kai_katharo_error_state(tmp_path: Path) -> None:
    """Το PNG εξάγει το aggregate preview offline και αποτυχία κρατά το dialog."""
    dedomena = fortose_deigma()
    dedomena["projects"] = [{"onoma": "PRIVATE_PNG_CANARY"}]
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        aitimata: list[str] = []
        page.on("request", lambda aitima: aitimata.append(aitima.url))
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator("#explore-tab").click()
        page.locator("#share-card").click()
        expect(page.locator("#save-share-png")).to_be_visible()
        assert "PRIVATE_PNG_CANARY" not in page.locator(".share-preview").text_content()
        with page.expect_download() as lipsi:
            page.locator("#save-share-png").click()
        assert lipsi.value.suggested_filename == "devrar-share-card.png"
        diadromi = tmp_path / "share.png"
        lipsi.value.save_as(str(diadromi))
        eikona = diadromi.read_bytes()
        assert eikona[:8] == b"\x89PNG\r\n\x1a\n"
        assert int.from_bytes(eikona[16:20], "big") == 1080
        assert int.from_bytes(eikona[20:24], "big") == 1350
        assert b"PRIVATE_PNG_CANARY" not in eikona
        assert not [url for url in aitimata if url.startswith(("http:", "https:"))]
        expect(page.locator("#detail-dialog")).not_to_be_visible()
        page.add_init_script(
            "HTMLCanvasElement.prototype.getContext = function() { return null; };"
        )
        page.reload(wait_until="networkidle")
        page.locator("#explore-tab").click()
        page.locator("#share-card").click()
        page.locator("#save-share-png").click()
        expect(page.locator("#share-error")).to_contain_text("PNG export failed")
        expect(page.locator("#detail-dialog")).to_be_visible()
        expect(page.locator("#save-share")).to_be_enabled()
        browser.close()


def test_browser_cloud_consent_kai_failed_fallback_fainontai_orthos(
    tmp_path: Path,
) -> None:
    """Cloud coaching reports consent separately from local inference."""
    dedomena = fortose_deigma()
    dedomena["analysi"] = {
        "methodos": "cloud",
        "katastasi": "failed",
        "cloud_opt_in": True,
        "provider": "openai_compatible",
        "model_id": "synthetic-cloud-model",
        "endpoint_host": "cloud.synthetic.invalid",
        "aitia": "Synthetic provider timeout.",
        "efarmostike": "rules",
    }
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        aitimata: list[str] = []
        page.on("request", lambda aitima: aitimata.append(aitima.url))
        page.goto(selida.as_uri(), wait_until="networkidle")
        kalypsi = page.locator("#coverage-alert")
        expect(kalypsi).to_contain_text("Cloud coaching")
        expect(kalypsi).to_contain_text("explicitly opted in")
        expect(kalypsi).to_contain_text("openai_compatible")
        expect(kalypsi).to_contain_text("synthetic-cloud-model")
        expect(kalypsi).to_contain_text("cloud.synthetic.invalid")
        expect(kalypsi).to_contain_text("rules-based")
        expect(kalypsi).not_to_contain_text("Local analysis failed")
        page.locator("#explore-tab").click()
        page.locator('.category-tab[data-view="growth"]').click()
        expect(page.locator(".assessment-card")).to_contain_text(
            "Cloud coaching failed"
        )
        expect(page.locator(".assessment-card")).not_to_contain_text("Local analysis")
        dedomenaXwrisSygkatathesi = fortose_deigma()
        dedomenaXwrisSygkatathesi["analysi"] = {
            "methodos": "cloud",
            "katastasi": "failed",
            "cloud_opt_in": False,
            "provider": "synthetic-provider",
        }
        selidaXwrisSygkatathesi = apothikefse_anafora(
            dedomenaXwrisSygkatathesi, tmp_path / "no-consent"
        )
        page.goto(selidaXwrisSygkatathesi.as_uri(), wait_until="networkidle")
        expect(page.locator("#coverage-alert")).to_contain_text("not opted in")
        expect(page.locator("#coverage-alert")).not_to_contain_text(
            "explicitly opted in"
        )
        assert not [url for url in aitimata if url.startswith(("http:", "https:"))]
        browser.close()


def test_browser_codex_native_subset_kai_outcomes_menoun_xwrista(
    tmp_path: Path,
) -> None:
    """Native subsets stay separate, nullable and usable across mobile/themes."""
    dedomena = fortose_deigma()
    dedomena["synola"]["tokens"] = 987654
    dedomena["codex_native"] = {
        "adapter": "codex-native-v1",
        "coverage": {
            "recognized_records": 8,
            "unknown_records": None,
            "excluded_unknown_timestamps": 2,
            "complete": False,
        },
        "assistant_projections": 3,
        "commands": 5,
        "explicit_exits": 2,
        "command_exit_success": 1,
        "command_exit_failure": 1,
        "command_exit_unknown": None,
        "patch_records": 4,
        "changed_files": 7,
        "collaboration_records": 2,
        "linked_agent_threads": 1,
        "inter_agent_messages": 6,
        "usage": {
            "method": "recorded_request_fields",
            "known_records": 2,
            "duplicate_records": 1,
            "invalid_records": 0,
            "sums": {
                "input_tokens": 100,
                "cached_input_tokens": 20,
                "cache_write_input_tokens": 5,
                "output_tokens": 40,
                "reasoning_output_tokens": 10,
                "recorded_total_tokens": 140,
            },
            "complete": False,
        },
        "metrika_ergasias": {
            "test_summary": {
                "status": "partial",
                "passed": 4,
                "failed": 1,
                "skipped": None,
            }
        },
        "epeisodia_ergasias": {
            "katastasi": "partial",
            "paratiriseis": [
                {
                    "katastasi": "observed_success",
                    "apotelesma": "Codex native command: 1 successful explicit exit.",
                    "pigi": "Codex native",
                    "synedria": "PRIVATE_NATIVE_SESSION",
                    "metrisi": {
                        "tests_passed": 4,
                        "tests_failed": None,
                        "tests_skipped": 0,
                    },
                    "tekmiria": [
                        {
                            "pigi": "Codex native",
                            "synedria": "PRIVATE_NATIVE_SESSION",
                            "locator": "PRIVATE_NATIVE_LOCATOR",
                            "apospasma": "PRIVATE_NATIVE_QUOTE",
                        }
                    ],
                },
                {
                    "katastasi": "mystery-state",
                    "apotelesma": "<img src=x onerror=alert(1)>",
                    "pigi": "Codex native",
                    "synedria": "PRIVATE_UNKNOWN_SESSION",
                    "tekmiria": [None, "malformed-citation"],
                },
            ],
        },
    }
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 390, "height": 844}, reduced_motion="reduce"
        )
        aitimata: list[str] = []
        page.on("request", lambda aitima: aitimata.append(aitima.url))
        page.on("pageerror", lambda error: aitimata.append(f"JSERROR:{error}"))
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator("#appearance-select").select_option("blue-hour")
        page.locator("#explore-tab").click()
        page.locator('.category-tab[data-view="activity"]').click()
        native_activity = page.locator(".codex-native-panel")
        expect(native_activity).to_be_visible()
        expect(native_activity).to_contain_text("observed subset")
        expect(native_activity).to_contain_text("Recognized records")
        assert "Unknown records" in native_activity.text_content()
        assert "Not recorded" in native_activity.text_content()
        expect(native_activity).to_contain_text("Patch records are not commits")
        expect(native_activity).to_contain_text(
            "Cached input and reasoning output are subset counters"
        )
        expect(native_activity).to_contain_text("Passed: 4")
        expect(native_activity).to_contain_text("Failed: 1")
        assert "987,654" not in native_activity.text_content()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator('.category-tab[data-view="growth"]').click()
        native_outcomes = page.locator(".native-outcomes-panel")
        expect(native_outcomes).to_be_visible()
        assert all(
            "Codex native" in card.text_content()
            for card in native_outcomes.locator(".outcome-card").all()
        )
        expect(native_outcomes.locator('[data-status="unknown"]')).to_be_visible()
        assert page.locator("img").count() == 0
        page.locator("#explore-tab").click()
        page.locator("#share-card").click()
        expect(page.locator(".share-preview")).to_be_visible()
        assert (
            "PRIVATE_NATIVE_QUOTE" not in page.locator(".share-preview").text_content()
        )
        assert not [
            url
            for url in aitimata
            if url.startswith(("http:", "https:")) or url.startswith("JSERROR:")
        ]
        browser.close()


def test_browser_codex_native_zero_known_records_keeps_usage_unknown(
    tmp_path: Path,
) -> None:
    """Zero known request rows do not turn absent native token sums into zero spend."""
    dedomena = fortose_deigma()
    dedomena["codex_native"] = {
        "coverage": {"recognized_records": "malformed", "complete": True},
        "usage": {
            "method": "recorded_request_fields",
            "known_records": 0,
            "duplicate_records": None,
            "invalid_records": "invalid",
            "sums": None,
            "complete": True,
        },
        "metrika_ergasias": {"test_summary": {"status": "unknown", "passed": None}},
        "epeisodia_ergasias": {
            "katastasi": "malformed",
            "paratiriseis": [None, {"katastasi": "not-a-real-status"}],
        },
    }
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 390, "height": 844}, reduced_motion="reduce"
        )
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator("#explore-tab").click()
        page.locator('.category-tab[data-view="activity"]').click()
        native = page.locator(".codex-native-panel")
        expect(native).to_contain_text("Recognized records")
        expect(native).to_contain_text("Not recorded")
        expect(native.locator(".codex-native-token-row").last).to_contain_text(
            "Not recorded"
        )
        assert native.locator(".codex-native-token-row").count() == 6
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator('.category-tab[data-view="growth"]').click()
        expect(
            page.locator(".native-outcomes-panel [data-status=unknown]")
        ).to_be_visible()
        assert not errors
        browser.close()


def test_browser_story_explore_kai_epistrofi(tmp_path: Path) -> None:
    """Rendered story navigation, detail focus and source filters stay functional."""
    selida = apothikefse_anafora(fortose_deigma(), tmp_path)
    martyria = Path("artifacts")
    martyria.mkdir(exist_ok=True)
    sfalmata: list[str] = []
    diktyo: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        plaisio = browser.new_context(
            viewport={"width": 1440, "height": 1000},
            record_video_dir=str(martyria / "video"),
        )
        page = plaisio.new_page()
        page.on("pageerror", lambda sfalma: sfalmata.append(str(sfalma)))
        page.on(
            "request",
            lambda aitima: (
                diktyo.append(aitima.url)
                if aitima.url.startswith(("http://", "https://"))
                else None
            ),
        )
        page.goto(selida.as_uri(), wait_until="networkidle")
        expect(page.locator("#demo-banner")).to_be_visible()
        expect(page.locator("#scene-content")).not_to_be_empty()
        grammata = page.evaluate(
            """async () => {
              const families = ["Inter", "Space Grotesk", "JetBrains Mono"];
              await Promise.all(families.map((family) =>
                document.fonts.load(`16px "${family}"`)));
              return Object.fromEntries(families.map((family) => [
                family,
                {
                  loaded: document.fonts.check(`16px "${family}"`),
                  count: [...document.fonts].filter((font) =>
                    font.family.replaceAll('"', '') === family &&
                    font.status === "loaded").length,
                },
              ]));
            }"""
        )
        assert all(font["loaded"] and font["count"] for font in grammata.values())
        assert page.locator(".scene-title em").evaluate(
            "el => getComputedStyle(el).color"
        ) not in ("transparent", "rgba(0, 0, 0, 0)")
        page.screenshot(path=str(martyria / "desktop-story.png"), full_page=True)
        arxiko = page.locator("#scene-content").inner_text()
        page.locator("#next-scene").click()
        expect(page.locator("#scene-content")).not_to_have_text(
            arxiko, use_inner_text=True
        )
        page.wait_for_timeout(1000)
        prin = page.locator("#scene-content").inner_text()
        page.locator("#scene-detail").click()
        expect(page.locator("#detail-dialog")).to_be_visible()
        expect(page.locator("#detail-dialog")).to_have_accessible_name(re.compile(".+"))
        page.locator("#close-dialog").click()
        expect(page.locator("#detail-dialog")).not_to_be_visible()
        assert page.locator("#scene-content").inner_text() == prin
        expect(page.locator("#scene-detail")).to_be_focused()
        page.locator("#replay-scene").click()
        page.locator("#play-story").click()
        expect(page.locator("#play-story")).to_have_attribute(
            "aria-label", "Pause story"
        )
        page.locator("#play-story").click()
        page.locator("#explore-tab").click()
        expect(page.locator("#explore-view")).to_be_visible()
        expect(page.locator("#story-view")).not_to_be_visible()
        page.locator('.category-tab[data-view="tools"]').click()
        expect(page.locator("#explore-cards")).to_contain_text("Claude")
        expect(page.locator(".metric-value").first).to_be_visible()
        assert (
            page.locator(".metric-value").first.evaluate(
                "el => parseFloat(getComputedStyle(el).fontSize)"
            )
            >= 36
        )
        epiloges = page.locator("#source-filter option").all_text_contents()
        assert len(epiloges) > 1
        page.locator("#source-filter").select_option(index=1)
        expect(page.locator("#explore-cards")).not_to_be_empty()
        karta = page.locator(".metric-card").first
        expect(karta).to_be_visible()
        assert karta.evaluate("el => parseFloat(getComputedStyle(el).borderRadius)") > 0
        karta.click()
        expect(page.locator("#detail-dialog")).to_be_visible()
        page.locator("#close-dialog").click()
        page.screenshot(path=str(martyria / "desktop-explore.png"), full_page=True)
        page.locator("#share-card").click()
        with page.expect_download() as lipsi:
            page.locator("#save-share").click()
        lipsi.value.save_as(str(martyria / "browser-share.svg"))
        karta_share = (martyria / "browser-share.svg").read_text(encoding="utf-8")
        assert "SYNTHETIC DEMO DATA" in karta_share
        assert "2026-10-12" not in karta_share
        assert "2026-10-23" not in karta_share
        assert not sfalmata, sfalmata
        assert not diktyo, diktyo
        plaisio.close()
        browser.close()


def test_browser_asfales_keimeno_kai_idiotiko_share(tmp_path: Path) -> None:
    """Untrusted labels stay text and the browser share exports aggregates only."""
    dedomena = fortose_deigma()
    dedomena["leitourgia"] = "live"
    epithesi = "<img src=https://example.invalid/PRIVATE_CANARY onerror=alert(1)>"
    dedomena["ergaleia"] = [
        {"onoma": epithesi, "synedries": 1, "prompts": 2, "tokens": None}
    ]
    dedomena["projects"] = [{"onoma": "PRIVATE_CANARY", "commits": 1, "arxeia": 1}]
    selida = apothikefse_anafora(dedomena, tmp_path)
    diktyo: list[str] = []
    dialogoi: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on(
            "request",
            lambda aitima: (
                diktyo.append(aitima.url)
                if aitima.url.startswith(("https://", "http://"))
                else None
            ),
        )
        page.on("dialog", lambda dialogos: dialogoi.append(dialogos.message))
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator('.nav-item[data-view="tools"]').click()
        expect(page.locator("#explore-cards")).to_contain_text(epithesi)
        assert page.locator("#explore-cards img").count() == 0
        page.locator("#share-card").click()
        with page.expect_download() as lipsi:
            page.locator("#save-share").click()
        teliko = tmp_path / "private-share.svg"
        lipsi.value.save_as(str(teliko))
        karta_share = teliko.read_text(encoding="utf-8")
        for aporrito in ("PRIVATE_CANARY", "2026-10-12", "2026-10-23", epithesi):
            assert aporrito not in karta_share
        assert "SYNTHETIC DEMO DATA" not in karta_share
        assert not diktyo
        assert not dialogoi
        browser.close()


def test_browser_kinito_kai_ligotero_motion(tmp_path: Path) -> None:
    """Mobile and reduced motion preserve navigation and readable data."""
    selida = apothikefse_anafora(fortose_deigma(), tmp_path)
    martyria = Path("artifacts")
    martyria.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            reduced_motion="reduce",
        )
        page.goto(selida.as_uri(), wait_until="networkidle")
        expect(page.locator("#next-scene")).to_be_visible()
        page.locator("#next-scene").click()
        expect(page.locator("#scene-content")).not_to_be_empty()
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth"
        )
        page.screenshot(path=str(martyria / "mobile-story.png"), full_page=True)
        page.locator("#explore-tab").click()
        expect(page.locator("#explore-view")).to_be_visible()
        expect(page.locator("#story-view")).not_to_be_visible()
        page.screenshot(path=str(martyria / "mobile-explore.png"), full_page=True)
        browser.close()


def test_browser_ola_ta_kefalaia_kai_pliktrologio(tmp_path: Path) -> None:
    """Every chapter is reachable and autoplay pauses without losing position."""
    from devrar.cli import kyria

    assert kyria(["wrap", "--demo", "--output", str(tmp_path)]) == 0
    selida = next(tmp_path.glob("run-*/index.html"))
    martyria = Path("artifacts")
    martyria.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        plaisio = browser.new_context(
            viewport={"width": 1440, "height": 1000},
            record_video_dir=str(martyria / "video"),
        )
        page = plaisio.new_page()
        page.goto(selida.as_uri(), wait_until="networkidle")
        arithmos_kefalaion = page.locator(".progress-step").count()
        assert arithmos_kefalaion >= 8
        titloi: set[str] = set()
        for deiktis in range(arithmos_kefalaion):
            page.locator(".progress-step").nth(deiktis).click()
            titlos = page.locator(".scene-title").inner_text()
            assert titlos not in titloi
            titloi.add(titlos)
            expect(page.locator("#scene-detail")).to_be_visible()
            if deiktis == 6:
                expect(page.locator(".recognition-badge")).to_have_count(3)
                diakritiko = page.locator(".recognition-badge").first
                diakritiko.click()
                expect(page.locator("#detail-dialog")).to_be_visible()
                page.locator("#close-dialog").click()
                expect(diakritiko).to_be_focused()
            page.screenshot(path=str(martyria / f"chapter-{deiktis + 1}.png"))
        page.locator(".progress-step").first.click()
        arxiko = page.locator(".scene-title").inner_text()
        page.keyboard.press("ArrowRight")
        expect(page.locator(".scene-title")).not_to_have_text(
            arxiko, use_inner_text=True
        )
        page.keyboard.press("ArrowLeft")
        expect(page.locator(".scene-title")).to_have_text(arxiko, use_inner_text=True)
        page.locator("#play-story").click()
        expect(page.locator(".scene-title")).not_to_have_text(
            arxiko, timeout=9000, use_inner_text=True
        )
        page.locator("#play-story").click()
        prin = page.locator(".scene-title").inner_text()
        page.wait_for_timeout(700)
        assert page.locator(".scene-title").inner_text() == prin
        page.locator('.nav-item[data-view="growth"]').click()
        expect(page.locator("#explore-subtitle")).to_contain_text("all authors")
        expect(page.locator(".dimension-card")).to_have_count(5)
        page.locator(".dimension-card").nth(1).click()
        expect(page.locator("#dialog-body")).to_contain_text(
            "Handoff: keep the engineering score unavailable"
        )
        expect(page.locator("#dialog-body")).not_to_contain_text(
            "Evidence excerpt unavailable."
        )
        page.locator("#close-dialog").click()
        expect(page.locator(".evidence-card").first).to_contain_text("Recorded event")
        page.locator(".evidence-card").first.click()
        expect(page.locator("#dialog-body")).to_contain_text("demo-session-alpha#1")
        expect(page.locator("#dialog-body")).to_contain_text("demo-session-alpha")
        page.locator("#close-dialog").click()
        page.evaluate("window.scrollTo(0, 0)")
        page.screenshot(path=str(martyria / "desktop-growth.png"), full_page=True)
        plaisio.close()
        browser.close()


def test_browser_print_psisimo_kai_apotyxia_analisis(tmp_path: Path) -> None:
    """Printing preserves readable data, opt-in humour and honest failure state."""
    dedomena = fortose_deigma()
    dedomena["analysi"] = {
        "methodos": "local",
        "katastasi": "failed",
        "aitia": "Synthetic model validation failed",
        "modelo": "synthetic-model",
    }
    selida = apothikefse_anafora(dedomena, tmp_path, roast=True)
    martyria = Path("artifacts")
    martyria.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(selida.as_uri(), wait_until="networkidle")
        expect(page.locator("#roast-note")).to_be_visible()
        expect(page.locator("#roast-note")).to_contain_text("1,074")
        expect(page.locator("#coverage-alert")).to_contain_text("Synthetic model")
        page.locator('.nav-item[data-view="growth"]').click()
        expect(page.locator(".assessment-score")).to_contain_text("—")
        page.emulate_media(media="print")
        expect(page.locator(".sidebar")).not_to_be_visible()
        expect(page.locator("#story-view")).not_to_be_visible()
        expect(page.locator("#explore-view")).to_be_visible()
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth"
        )
        page.screenshot(path=str(martyria / "print-layout.png"), full_page=True)
        page.pdf(path=str(martyria / "print-demo.pdf"), format="A4")
        page.emulate_media(media="screen")
        expect(page.locator(".sidebar")).to_be_visible()
        expect(page.locator("#explore-title")).to_contain_text("Strengths")
        browser.close()


def test_browser_kinisi_epanekkinisi_pafsi_kai_metrisi(tmp_path: Path) -> None:
    """Scene reveals restart, pause freezes ambience, and stats count up accessibly."""
    selida = apothikefse_anafora(fortose_deigma(), tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(reduced_motion="no-preference")
        page.goto(selida.as_uri(), wait_until="networkidle")

        reveal = page.locator("#scene-content")
        reveal.evaluate("el => el.getAnimations()[0].finished")
        page.wait_for_timeout(650)
        assert reveal.evaluate("el => el.getAnimations()[0].playState") == "finished"
        page.locator("#next-scene").click()
        assert reveal.evaluate("el => el.getAnimations()[0].playState") == "running"
        page.wait_for_timeout(650)
        page.locator("#replay-scene").click()
        assert reveal.evaluate("el => el.getAnimations()[0].playState") == "running"
        for _ in range(3):
            page.locator("#next-scene").click()
        expect(page.locator(".progress-step").nth(4)).to_have_attribute(
            "aria-current", "step"
        )

        orbit = page.locator(".orbit-two")
        page.locator("#play-story").click()
        page.wait_for_timeout(180)
        page.locator("#play-story").click()
        katastasi_pafsis_prin = orbit.evaluate(
            """async el => {
              const kinisi = el.getAnimations()[0];
              await kinisi.ready;
              return { playState: kinisi.playState, pending: kinisi.pending };
            }"""
        )
        assert katastasi_pafsis_prin == {"playState": "paused", "pending": False}
        clock_before = orbit.evaluate("el => el.getAnimations()[0].currentTime")
        page.wait_for_timeout(180)
        katastasi_pafsis_meta = orbit.evaluate(
            """async el => {
              const kinisi = el.getAnimations()[0];
              await kinisi.ready;
              return { playState: kinisi.playState, pending: kinisi.pending };
            }"""
        )
        assert katastasi_pafsis_meta == {"playState": "paused", "pending": False}
        clock_after = orbit.evaluate("el => el.getAnimations()[0].currentTime")
        assert clock_after == clock_before
        star = page.locator(".starburst")
        if star.count():
            assert star.evaluate("el => el.getAnimations()[0].playState") == "paused"

        page.locator(".progress-step").nth(2).click()
        stat = page.locator(".scene-stat")
        assert stat.get_attribute("aria-label") == "1,074 USER PROMPTS"
        expect(
            page.get_by_role("img", name="1,074 USER PROMPTS", exact=True)
        ).to_be_visible()
        assert (
            float(stat.locator(".scene-stat-value").inner_text().replace(",", ""))
            < 1074
        )
        page.wait_for_timeout(1100)
        assert stat.locator(".scene-stat-value").inner_text().strip() == "1,074"

        page.locator("#play-story").click()
        page.evaluate(
            "Object.defineProperty(document, 'hidden', "
            "{ configurable: true, value: true })"
        )
        page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
        expect(page.locator("#play-story")).to_have_attribute(
            "aria-label", "Play story"
        )
        browser.close()


def test_browser_ligoteri_kinisi_amesa_metrika_kai_agnosta(
    tmp_path: Path,
) -> None:
    """Reduced motion exposes final measured values while unknown stats stay unknown."""
    dedomena = fortose_deigma()
    dedomena["synola"]["minimata_xristi"] = None
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(reduced_motion="reduce")
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator(".progress-step").nth(1).click()
        metrimeno = page.locator(".scene-stat")
        megisto = max(grammi["prompts"] for grammi in dedomena["ergaleia"])
        assert metrimeno.get_attribute("aria-label") == (
            f"{megisto:,} RECORDED PROMPTS"
        )
        assert metrimeno.locator(".scene-stat-value").inner_text() == f"{megisto:,}"
        page.locator(".progress-step").nth(2).click()
        stat = page.locator(".scene-stat")
        assert stat.inner_text().strip().startswith("Not recorded")
        assert stat.get_attribute("aria-label") == "Not recorded USER PROMPTS"
        browser.close()


def test_browser_grafima_drastiriotitas_katholiko_kai_agnosta(
    tmp_path: Path,
) -> None:
    """Source filters leave dated activity report-wide without charting null as zero."""
    dedomena = fortose_deigma()
    drastiriotita = dedomena["drastiriotita"]
    assert isinstance(drastiriotita, list) and len(drastiriotita) > 1
    drastiriotita[0]["prompts"] = None
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator("#explore-tab").click()
        chart = page.locator(".chart-line")
        simeiaArxika = chart.get_attribute("points")
        assert simeiaArxika
        assert len(simeiaArxika.split()) == len(drastiriotita) - 1
        page.locator("#source-filter").select_option(index=1)
        assert chart.get_attribute("points") == simeiaArxika
        browser.close()


def test_browser_activity_calendar_hours_and_interval_estimate(tmp_path: Path) -> None:
    """New work metrics render a truthful calendar, hour chart, and evidence summary."""
    dedomena = fortose_deigma()
    ora = [{"ora": ora_n, "prompts": 0} for ora_n in range(24)]
    ora[9]["prompts"] = 12
    ora[13]["prompts"] = 5
    ora[3]["prompts"] = None
    dedomena["metrika_ergasias"] = {
        "zoni": "Europe/Athens",
        "ora": ora,
        "imeres": [
            {"imerominia": "2026-10-12", "prompts": 4},
            {"imerominia": "2026-10-13", "prompts": 0},
            {"imerominia": "bad-date", "prompts": 900},
            None,
        ],
        "timestamps_unknown": 1,
        "events": 24,
        "interval_estimate_minutes": 133,
        "interval_estimate_status": "observed_pairs_only",
        "sources": [
            {
                "pigi": "Claude Code",
                "events": 24,
                "tool_results": 3,
                "tests_passed": 5,
                "tests_failed": 1,
                "tests_skipped": 2,
            }
        ],
        "test_summary": {
            "status": "observed",
            "passed": 5,
            "failed": 1,
            "skipped": 2,
            "todo": 3,
        },
        "epeisodia": [{"exit_success": 2, "exit_failure": 1}],
        "episodes_included": 1,
        "episodes_eligible": 2,
        "episodes_truncated": True,
    }
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator('.nav-item[data-view="activity"]').click()
        assert page.locator(".work-metrics-panel").is_visible()
        assert (
            page.locator(".activity-day[data-date='2026-10-12']").get_attribute(
                "aria-label"
            )
            == "2026-10-12: 4 recorded prompts"
        )
        assert (
            page.locator(".activity-day[data-date='2026-10-13']").get_attribute(
                "aria-label"
            )
            == "2026-10-13: 0 recorded prompts"
        )
        expect(page.locator(".activity-legend")).to_contain_text(
            "Fewer → more recorded prompts"
        )
        assert page.locator(".activity-hour").count() == 23
        expect(page.locator(".activity-peak")).to_contain_text("09:00")
        span = page.locator(".activity-span")
        expect(span).to_contain_text("2h 13m")
        expect(span).to_contain_text("estimated")
        expect(span).to_contain_text("not human PC time")
        expect(page.locator(".activity-test-summary")).to_contain_text(
            "5 passed · 1 failed · 2 skipped · 3 TODO"
        )
        expect(page.locator(".activity-test-summary")).to_contain_text(
            "Tool output is evidence, not proof of overall completion"
        )
        expect(page.locator(".activity-test-definition")).to_contain_text(
            "Command exit counts require explicit exit records"
        )
        expect(page.locator(".activity-tool-results")).to_contain_text(
            "3 recorded tool results"
        )
        expect(page.locator(".activity-exits")).to_contain_text(
            "Observed command exits: 2 success · 1 failure. "
            "Only 1 of 2 included episode summaries are counted."
        )
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator("#source-filter").select_option(index=1)
        assert page.locator(".activity-hour").count() == 23
        browser.close()

        palio_deigma = fortose_deigma()
        for kleidi in ("metrika_ergasias", "epeisodia_ergasias", "sygkrisi"):
            palio_deigma.pop(kleidi, None)
        legacy = apothikefse_anafora(palio_deigma, tmp_path / "legacy")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(legacy.as_uri(), wait_until="networkidle")
        page.locator('.nav-item[data-view="activity"]').click()
        assert page.locator(".work-metrics-panel").count() == 0
        assert page.locator(".chart-line").count() == 1
        page.locator('.nav-item[data-view="growth"]').click()
        assert page.locator(".outcomes-panel").count() == 0
        assert page.locator(".comparison-panel").count() == 0
        browser.close()


def test_browser_activity_unknown_and_malformed_payload_stays_unknown(
    tmp_path: Path,
) -> None:
    """Malformed buckets and unbounded timestamps never become invented zeros."""
    dedomena = fortose_deigma()
    dedomena["metrika_ergasias"] = {
        "zoni": "Europe/Athens",
        "ora": [
            {"ora": 24, "prompts": 8},
            {"ora": 1, "prompts": None},
            {"ora": "02", "prompts": 5},
        ],
        "imeres": [
            {"imerominia": "2026-02-30", "prompts": 12},
            {"imerominia": "2026-10-14", "prompts": "unknown"},
            None,
        ],
        "interval_estimate_minutes": 999,
        "interval_estimate_status": "no_bounded_pairs",
        "sources": [],
        "test_summary": {
            "status": "no_observed_tests",
            "passed": None,
            "failed": None,
            "skipped": None,
        },
        "epeisodia": [None, {"exit_success": "4", "exit_failure": None}],
    }
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator('.nav-item[data-view="activity"]').click()
        expect(page.locator(".activity-hourly-card")).to_contain_text(
            "Hourly prompt counts were not recorded"
        )
        expect(page.locator(".activity-calendar-card")).to_contain_text(
            "No valid dated prompt aggregates were recorded"
        )
        expect(page.locator(".activity-test-counts")).to_contain_text(
            "Test results not recorded"
        )
        expect(page.locator(".activity-tool-results")).to_have_text(
            "Tool results: not recorded · separate from test summaries."
        )
        expect(page.locator(".activity-span")).to_contain_text(
            "Not recorded; timestamps do not bound"
        )
        expect(page.locator(".activity-span")).not_to_contain_text("999")
        expect(page.locator(".activity-exits")).to_contain_text("Not recorded")
        browser.close()


def test_browser_supplied_time_and_cost_preserve_scope_precision_and_privacy(
    tmp_path: Path,
) -> None:
    """Optional imported watcher and ledger data stay scoped and exact."""
    dedomena = fortose_deigma()
    dedomena["energos_xronos"] = {
        "status": "partial",
        "source": "ActivityWatch",
        "scope": "Supplied intervals only; not a complete PC-time record.",
        "note": "WATCHER_PRIVATE_CANARY · uncovered periods remain unknown.",
        "active_seconds": 3661.5,
        "afk_seconds": 901.25,
        "coverage": {
            "events_total": 8,
            "events_used": 6,
            "events_ignored": 2,
            "unknown_intervals": 1,
            "partial": True,
        },
        "by_day": [
            {"date": "2026-10-12", "active_seconds": 3600, "afk_seconds": 600},
            {"date": "bad-date", "active_seconds": 999999, "afk_seconds": 0},
        ],
    }
    dedomena["kostos"] = {
        "status": "partial",
        "source": "COST_PRIVATE_CANARY ledger",
        "note": "One row was ignored.",
        "coverage": {"rows_total": 4, "rows_used": 3, "rows_ignored": 1},
        "totals": [
            {"currency": "USD", "kind": "billed", "amount": "0.300000000000000004"},
            {"currency": "USD", "kind": "estimated", "amount": "1.2500"},
            {"currency": "EUR", "kind": "billed", "amount": "2.75"},
            {"currency": "USD", "kind": "estimated", "amount": "1e6"},
        ],
    }
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator('.nav-item[data-view="activity"]').click()
        watcher = page.locator(".supplied-time-panel")
        assert watcher.is_visible()
        expect(watcher).to_contain_text("Supplied intervals only")
        expect(watcher).to_contain_text("Partial")
        expect(watcher).to_contain_text("1h 1m 1.5s")
        expect(watcher).to_contain_text("15m 1.25s")
        expect(watcher).to_contain_text("2026-10-12")
        assert watcher.locator('[data-date="bad-date"]').count() == 0

        cost = page.locator(".supplied-cost-panel")
        assert cost.is_visible()
        expect(cost).to_contain_text("Partial")
        expect(cost).to_contain_text("0.300000000000000004 USD · Billed")
        expect(cost).to_contain_text("1.2500 USD · Estimated")
        expect(cost).to_contain_text("2.75 EUR · Billed")
        assert cost.locator(".cost-total").count() == 3
        assert "1e6" not in cost.inner_text()
        page.locator("#story-tab").click()
        page.locator(".progress-step").nth(8).click()
        page.locator("#scene-detail").click()
        preview = page.locator(".share-preview")
        assert "WATCHER_PRIVATE_CANARY" not in preview.text_content()
        assert "COST_PRIVATE_CANARY" not in preview.text_content()
        assert "0.300000000000000004" not in preview.text_content()
        page.locator("#cancel-share").click()
        page.locator("#scene-detail").click()
        with page.expect_download() as lipsi:
            page.locator("#save-share").click()
        share_file = tmp_path / "imported-data-share.svg"
        lipsi.value.save_as(str(share_file))
        svg = share_file.read_text(encoding="utf-8")
        assert "WATCHER_PRIVATE_CANARY" not in svg
        assert "COST_PRIVATE_CANARY" not in svg
        assert "0.300000000000000004" not in svg
        browser.close()


def test_browser_git_first_parent_changes_show_scope_and_partial_coverage(
    tmp_path: Path,
) -> None:
    """First-parent numstat deltas are distinct from existing HEAD counters."""
    dedomena = fortose_deigma()
    dedomena["git_diafores"] = {
        "adapter": "git-numstat-first-parent-v1",
        "katastasi": "partial",
        "periodos": {"apo": "2026-10-01", "eos": "2026-10-27", "zoni": "Europe/Athens"},
        "filtro": {"author": None},
        "semantics": {
            "history": "first-parent only; non-first-parent-only commits are omitted",
            "merge": "included against first parent; counted separately",
            "renames": "disabled; a rename is recorded as deletion and addition",
            "binary": (
                "binary numstat rows count as binary file changes; "
                "line counts exclude them"
            ),
            "limit_commits_per_repository": 10000,
        },
        "apothikies": [
            {
                "onoma": "PRIVATE_GIT_CANARY",
                "commits": 3,
                "merge_commits": 1,
                "additions": 12,
                "deletions": 4,
                "file_changes": 6,
                "binary_file_changes": 1,
                "arxeia_tracked_HEAD": 20,
            },
            {
                "onoma": "unreadable",
                "commits": None,
                "merge_commits": None,
                "additions": None,
                "deletions": None,
                "file_changes": None,
                "binary_file_changes": None,
                "arxeia_tracked_HEAD": None,
            },
        ],
        "synola": {
            "merge_commits": 1,
            "additions": 12,
            "deletions": 4,
            "file_changes": 6,
            "binary_file_changes": 1,
            "unique_commits": 3,
            "arxeia_tracked_HEAD": 20,
        },
        "kalypsi": {
            "apothikies": 2,
            "epityxeis": 1,
            "sfalmata": 1,
            "agnostes_imerominies": 0,
            "perikopi": True,
            "katastasi": "partial",
            "simeioseis": ["History was capped at 10000 commits per repository."],
        },
    }
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator("#explore-tab").click()
        page.locator('.category-tab[data-view="projects"]').click()
        panel = page.locator(".git-changes-panel")
        assert panel.is_visible()
        expect(panel).to_contain_text("Git changes in first-parent history")
        expect(panel).to_contain_text("Partial")
        expect(panel).to_contain_text("Author filter: all authors")
        expect(panel).to_contain_text("12 additions")
        expect(panel).to_contain_text("4 deletions")
        expect(panel).to_contain_text("6 file changes")
        expect(panel).to_contain_text("1 binary file changes")
        expect(panel).to_contain_text(
            "Merge commits are compared with their first parent"
        )
        expect(panel).to_contain_text("renames are disabled")
        expect(panel).to_contain_text("10,000 commit limit per repository")
        expect(panel).to_contain_text("1 of 2 repositories readable")
        assert "PRIVATE_GIT_CANARY" in panel.inner_text()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator("#story-tab").click()
        page.locator(".progress-step").nth(8).click()
        page.locator("#scene-detail").click()
        assert "PRIVATE_GIT_CANARY" not in page.locator(".share-preview").text_content()
        page.locator("#cancel-share").click()
        browser.close()

        missing = fortose_deigma()
        missing["git_diafores"] = {
            "katastasi": "missing",
            "apothikies": [],
            "synola": {
                "additions": None,
                "deletions": None,
                "file_changes": None,
                "binary_file_changes": None,
            },
            "kalypsi": {
                "apothikies": 0,
                "epityxeis": 0,
                "sfalmata": 0,
                "perikopi": False,
                "katastasi": "missing",
                "simeioseis": ["No Git repositories were selected."],
            },
        }
        missing_page = apothikefse_anafora(missing, tmp_path / "missing-git")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(missing_page.as_uri(), wait_until="networkidle")
        page.locator("#explore-tab").click()
        page.locator('.category-tab[data-view="projects"]').click()
        expect(page.locator(".git-changes-panel")).to_contain_text("Not available")
        expect(page.locator(".git-changes-panel")).to_contain_text("Not recorded")
        browser.close()

        missing = fortose_deigma()
        missing["energos_xronos"] = {
            "status": "missing",
            "source": "ActivityWatch",
            "scope": "Supplied intervals only; not a complete PC-time record.",
            "note": "No source file was supplied.",
            "active_seconds": None,
            "afk_seconds": None,
            "coverage": {"partial": True},
            "by_day": [],
        }
        missing["kostos"] = {
            "status": "missing",
            "source": "recorded ledger",
            "note": "No source file was supplied.",
            "coverage": {"partial": True},
            "totals": None,
        }
        missing_page = apothikefse_anafora(missing, tmp_path / "missing")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(missing_page.as_uri(), wait_until="networkidle")
        page.locator('.nav-item[data-view="activity"]').click()
        expect(page.locator(".supplied-time-panel")).to_contain_text("Not available")
        expect(page.locator(".supplied-time-panel")).not_to_contain_text("0s")
        expect(page.locator(".supplied-cost-panel")).to_contain_text("Not available")
        assert page.locator(".cost-total").count() == 0
        browser.close()


def test_browser_outcome_cards_show_citations_and_unknowns_without_blame(
    tmp_path: Path,
) -> None:
    """Growth shows observed, mixed and unknown work outcomes with exact citations."""
    dedomena = fortose_deigma()
    dedomena["epeisodia_ergasias"] = {
        "ekdosi": "0.1",
        "katastasi": "partial",
        "kalypsi": {"diathesima": 3, "analysimena": 3, "perikopi": False},
        "paratiriseis": [
            {
                "id": "W0001",
                "pigi": "Claude Code",
                "synedria": "session-alpha",
                "katastasi": "observed_success",
                "apotelesma": "Tool or test output records a successful check.",
                "metrisi": {"tests_passed": 2, "tests_failed": 0, "tests_skipped": 0},
                "tekmiria": [
                    {
                        "pigi": "Claude Code",
                        "synedria": "session-alpha",
                        "locator": "session-alpha.jsonl:8",
                        "apospasma": "2 passed in 0.4s",
                    }
                ],
                "kalypsi_tekmirion": {"included": 1, "eligible": 1, "truncated": False},
            },
            {
                "id": "W0002",
                "pigi": "Codex",
                "synedria": "session-beta",
                "katastasi": "mixed",
                "apotelesma": (
                    "Recorded checks include both successful and failed results."
                ),
                "metrisi": {"tests_passed": 1, "tests_failed": 1, "tests_skipped": 0},
                "tekmiria": [
                    {
                        "pigi": "Codex",
                        "synedria": "session-beta",
                        "locator": "run-17/tool-result",
                        "apospasma": "<img src=x onerror=alert(1)> exit 1",
                        "kodikos_exodou": "1",
                    }
                ],
                "kalypsi_tekmirion": {"included": 1, "eligible": 5, "truncated": True},
            },
            {
                "id": "W0003",
                "pigi": "Claude Code",
                "synedria": "session-gamma",
                "katastasi": "unknown",
                "apotelesma": (
                    "Outcome is unknown from the available tool and exit evidence."
                ),
                "metrisi": {
                    "tests_passed": None,
                    "tests_failed": None,
                    "tests_skipped": None,
                },
                "tekmiria": [],
                "kalypsi_tekmirion": {"included": 0, "eligible": 0, "truncated": False},
            },
        ],
        "dynata_simeia": [],
        "proteraiotites": [],
        "vathmologisi_energi": False,
        "periorismoi": ["Recorded outcomes do not establish overall task quality."],
    }
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        sfalmata: list[str] = []
        page.on("pageerror", lambda sfalma: sfalmata.append(str(sfalma)))
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator('.nav-item[data-view="growth"]').click()
        outcomes = page.locator(".outcome-card")
        assert outcomes.count() == 3
        assert page.locator(
            '.outcome-card[data-status="observed_success"]'
        ).is_visible()
        assert page.locator('.outcome-card[data-status="mixed"]').is_visible()
        unknown = page.locator('.outcome-card[data-status="unknown"]')
        expect(unknown).to_contain_text("Outcome unknown")
        expect(outcomes.nth(0)).to_contain_text("session-alpha")
        expect(outcomes.nth(0)).to_contain_text("session-alpha.jsonl:8")
        expect(outcomes.nth(0)).to_contain_text("2 passed in 0.4s")
        expect(outcomes.nth(1)).to_contain_text("Codex")
        expect(outcomes.nth(1)).to_contain_text("run-17/tool-result")
        expect(outcomes.nth(1)).to_contain_text("exit code 1")
        expect(outcomes.nth(1)).to_contain_text("citations are truncated")
        assert page.locator(".outcome-card img").count() == 0
        assert "alert(1)" in outcomes.nth(1).inner_text()
        expect(page.locator(".outcomes-limit")).to_contain_text(
            "do not establish task completion or code quality"
        )
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert not sfalmata, sfalmata
        browser.close()


def test_browser_progress_comparison_handles_compatibility_and_null_deltas(
    tmp_path: Path,
) -> None:
    """Progress cards expose compatibility, zero baselines and overlap limits."""
    dedomena = fortose_deigma()
    dedomena["sygkrisi"] = {
        "ekdosi": "0.1",
        "katastasi": "compatible",
        "symvatotita": {
            "periodos": {"katastasi": "compatible", "aitia": "Periods do not overlap."},
            "piges": {"katastasi": "compatible", "aitia": "Sources match."},
        },
        "metrika": {
            "synola.minimata_xristi": {
                "katastasi": "compatible",
                "trexousa": 12,
                "proigoumeni": 10,
                "delta": 2,
                "pososto": 20,
                "aitia": "Recorded totals are comparable.",
            },
            "episodia.tests_passed": {
                "katastasi": "compatible",
                "trexousa": 4,
                "proigoumeni": 0,
                "delta": 4,
                "pososto": None,
                "aitia": (
                    "PRIVATE_COMPARE_CANARY: zero baseline "
                    "has no defined percent change."
                ),
            },
            "synola.commits": {
                "katastasi": "missing",
                "trexousa": None,
                "proigoumeni": 5,
                "delta": None,
                "pososto": None,
                "aitia": "One or both values are unknown.",
            },
        },
        "periorismoi": ["Activity volume does not establish skill or causality."],
    }
    selida = apothikefse_anafora(dedomena, tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator('.nav-item[data-view="growth"]').click()
        panel = page.locator(".comparison-panel")
        assert panel.is_visible()
        expect(page.locator(".comparison-status")).to_contain_text("Compatible")
        prompts = page.locator('.comparison-card[data-metric="synola.minimata_xristi"]')
        expect(prompts).to_contain_text("+2")
        expect(prompts).to_contain_text("+20%")
        zero_baseline = page.locator(
            '.comparison-card[data-metric="episodia.tests_passed"]'
        )
        expect(zero_baseline).to_contain_text("+4")
        expect(zero_baseline).to_contain_text("Percent change unavailable")
        missing = page.locator('.comparison-card[data-metric="synola.commits"]')
        expect(missing).to_contain_text("Not recorded")
        expect(missing).to_contain_text("Delta unavailable")
        assert "PRIVATE_COMPARE_CANARY" in panel.inner_text()
        page.locator("#story-tab").click()
        page.locator(".progress-step").nth(8).click()
        page.locator("#scene-detail").click()
        assert (
            "PRIVATE_COMPARE_CANARY"
            not in page.locator(".share-preview").text_content()
        )
        page.locator("#cancel-share").click()
        page.locator("#scene-detail").click()
        with page.expect_download() as lipsi:
            page.locator("#save-share").click()
        share_file = tmp_path / "comparison-share.svg"
        lipsi.value.save_as(str(share_file))
        assert "PRIVATE_COMPARE_CANARY" not in share_file.read_text(encoding="utf-8")
        browser.close()

        overlap = fortose_deigma()
        overlap["sygkrisi"] = {
            "ekdosi": "0.1",
            "katastasi": "overlapping",
            "symvatotita": {
                "periodos": {
                    "katastasi": "overlapping",
                    "aitia": (
                        "The report periods overlap, so deltas "
                        "could double-count activity."
                    ),
                }
            },
            "metrika": {
                "synola.minimata_xristi": {
                    "katastasi": "compatible",
                    "trexousa": 12,
                    "proigoumeni": 10,
                    "delta": 2,
                    "pososto": 20,
                    "aitia": (
                        "Malformed per-metric status must not "
                        "override the global period overlap."
                    ),
                }
            },
            "periorismoi": [],
        }
        selida_overlap = apothikefse_anafora(overlap, tmp_path / "overlap")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(selida_overlap.as_uri(), wait_until="networkidle")
        page.locator('.nav-item[data-view="growth"]').click()
        expect(page.locator(".comparison-caveat")).to_contain_text("periods overlap")
        expect(
            page.locator('.comparison-card[data-metric="synola.minimata_xristi"]')
        ).to_contain_text("Delta unavailable")
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        browser.close()


def test_browser_theme_keyboard_switch_preserves_story_and_share_allowlist(
    tmp_path: Path,
) -> None:
    """Blue hour changes the report frame while Original restores its appearance."""
    selida = apothikefse_anafora(fortose_deigma(), tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(selida.as_uri(), wait_until="networkidle")
        appearance = page.locator("#appearance-select")
        expect(appearance).to_be_visible()
        expect(appearance).to_have_value("original")
        expect(page.locator("body")).to_have_attribute("data-theme", "original")
        original_background = page.locator("body").evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )
        page.locator(".progress-step").nth(6).click()
        page.wait_for_timeout(650)
        story_colors = page.locator(".story-stage").evaluate(
            """el => ({
              background: getComputedStyle(el).backgroundColor,
              color: getComputedStyle(el).color,
              title: getComputedStyle(el.querySelector('.scene-title')).color,
            })"""
        )
        page.locator("#explore-tab").click()
        page.locator('.category-tab[data-view="overview"]').click()
        recognition = page.locator(".recognition-panel").inner_text()
        counts = page.locator(".metric-value").all_text_contents()
        page.locator("#appearance-select").focus()
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        expect(appearance).to_have_value("blue-hour")
        expect(page.locator("body")).to_have_attribute("data-theme", "blue-hour")
        blue_background = page.locator("body").evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )
        assert blue_background != original_background
        assert page.locator(".recognition-panel").inner_text() == recognition
        assert page.locator(".metric-value").all_text_contents() == counts
        assert (
            page.locator(".story-stage").evaluate(
                """el => ({
              background: getComputedStyle(el).backgroundColor,
              color: getComputedStyle(el).color,
              title: getComputedStyle(el.querySelector('.scene-title')).color,
            })"""
            )
            == story_colors
        )
        page.locator("#appearance-select").focus()
        page.keyboard.press("ArrowUp")
        page.keyboard.press("Enter")
        expect(appearance).to_have_value("original")
        expect(page.locator("body")).to_have_attribute("data-theme", "original")
        assert (
            page.locator("body").evaluate("el => getComputedStyle(el).backgroundColor")
            == original_background
        )

        share_text_by_theme = []
        for theme in ("original", "blue-hour"):
            if theme == "blue-hour":
                appearance.focus()
                page.keyboard.press("ArrowDown")
                page.keyboard.press("Enter")
            page.locator("#share-card").click()
            share_text_by_theme.append(
                page.locator(".share-preview text").all_text_contents()
            )
            page.locator("#cancel-share").click()
            expect(page.locator("#share-card")).to_be_focused()
        assert share_text_by_theme[0] == share_text_by_theme[1]
        browser.close()


def test_browser_blue_hour_activity_growth_mobile_and_reduced_motion(
    tmp_path: Path,
) -> None:
    """Blue hour keeps activity and growth readable at mobile and reduced motion."""
    selida = apothikefse_anafora(fortose_deigma(), tmp_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            reduced_motion="reduce",
        )
        page = context.new_page()
        page.goto(selida.as_uri(), wait_until="networkidle")
        page.locator("#appearance-select").focus()
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        expect(page.locator("body")).to_have_attribute("data-theme", "blue-hour")
        page.locator("#explore-tab").click()
        page.locator('.category-tab[data-view="activity"]').click()
        expect(page.locator(".activity-calendar-card")).to_be_visible()
        expect(page.locator(".activity-hourly-card")).to_be_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator('.category-tab[data-view="growth"]').click()
        expect(page.locator(".outcomes-panel")).to_be_visible()
        expect(page.locator(".comparison-panel")).to_be_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator("#story-tab").click()
        page.locator(".progress-step").nth(6).click()
        expect(page.locator('.progress-step[aria-current="step"]')).to_have_attribute(
            "aria-label", "Go to chapter 7"
        )
        page.wait_for_timeout(20)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert page.evaluate(
            """() => ['replay-scene','play-story','next-scene','scene-detail']
            .every(id => {
              const el = document.getElementById(id), rect = el.getBoundingClientRect();
              return rect.width > 0 && rect.left >= 0 && rect.right <= innerWidth;
            })"""
        )
        assert page.locator("#scene-content").evaluate(
            "el => parseFloat(getComputedStyle(el).animationDuration) <= 0.001"
        )
        browser.close()
