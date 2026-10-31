"""Capture README screenshots from the running stack (headless Chromium).

    uv run --with playwright python scripts/screenshots.py
Needs `docker compose up` with the producer running for ~30 s.
"""

import html
import os
import subprocess

from playwright.sync_api import sync_playwright

OUT = "docs/screenshots"
APP = os.getenv("APP_URL", "http://localhost:3000")
API = os.getenv("API_URL", "http://localhost:8000")
FUNCTIONS = os.getenv("FUNCTIONS_URL", "http://localhost:7071")
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
    # The real Azure Functions host (Python v2 app): landing page + its own execution log.
    page.goto(FUNCTIONS)
    page.wait_for_timeout(1000)
    page.screenshot(path=f"{OUT}/functions-host.png")
    logs = subprocess.run(["docker", "compose", "logs", "--no-log-prefix", "--tail", "4000", "functions"],
                          capture_output=True, text=True).stdout.splitlines()
    run = [ln for ln in logs if "Executed 'Functions." in ln]
    keep = [ln for ln in run if "TriggerTweetsToBlobAndEventHub" in ln][-8:] + \
        [ln for ln in run if "EventHubTriggerTweetsToCosmosDB" in ln][-12:]
    page.set_content("<body style='margin:0;background:#0d1117'><pre style='color:#c9d1d9;font:13px/1.5 Menlo,monospace;"
                     "padding:16px'>$ docker compose logs functions | grep Executed\n"
                     + html.escape("\n".join(k.strip() for k in keep)) + "</pre></body>")
    page.set_viewport_size({"width": 1440, "height": 520})
    page.screenshot(path=f"{OUT}/functions-executions.png", full_page=True)
    browser.close()
