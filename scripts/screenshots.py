"""Capture README screenshots from the running stack (headless Chromium).

    uv run --with playwright python scripts/screenshots.py
Needs `docker compose up` with the producer running for ~30 s.
"""

import os

from playwright.sync_api import sync_playwright

OUT = "docs/screenshots"
APP = os.getenv("APP_URL", "http://localhost:3000")
API = os.getenv("API_URL", "http://localhost:8000")
COSMOS_EXPLORER = os.getenv("COSMOS_EXPLORER_URL", "http://localhost:1234")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)

    page.goto(APP)
    page.wait_for_selector("text=SSE connected")
    page.wait_for_selector(".feed img")
    page.wait_for_timeout(6000)
    page.screenshot(path=f"{OUT}/live-view.png", full_page=True)

    page.click("text=Send invalid tweet")
    page.wait_for_selector("text=rejected")
    page.wait_for_timeout(2500)
    page.locator(".grid .panel").first.screenshot(path=f"{OUT}/live-view-rejection.png")

    page.goto(COSMOS_EXPLORER)
    page.wait_for_timeout(5000)
    page.click("text=Explorer")
    page.wait_for_timeout(8000)
    page.screenshot(path=f"{OUT}/cosmos-data-explorer.png")

    page.goto(f"{API}/docs")
    page.wait_for_selector(".opblock-summary-path")
    page.wait_for_timeout(500)
    page.screenshot(path=f"{OUT}/api-docs.png")
    browser.close()
