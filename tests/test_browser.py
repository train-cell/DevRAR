"""Exercise generated local HTML in an isolated headless Chromium context."""

import os
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
        assert page.locator(".scene-title em").evaluate(
            "el => getComputedStyle(el).color"
        ) not in ("transparent", "rgba(0, 0, 0, 0)")
        page.screenshot(path=str(martyria / "desktop-story.png"), full_page=True)
        arxiko = page.locator("#scene-content").inner_text()
        page.locator("#next-scene").click()
        expect(page.locator("#scene-content")).not_to_have_text(
            arxiko, use_inner_text=True
        )
        prin = page.locator("#scene-content").inner_text()
        page.locator("#scene-detail").click()
        expect(page.locator("#detail-dialog")).to_be_visible()
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
        with page.expect_download() as lipsi:
            page.locator("#share-card").click()
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
        with page.expect_download() as lipsi:
            page.locator("#share-card").click()
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
