#!/usr/bin/env python3
"""
Canary QA replay script — login flow for https://the-internet.herokuapp.com/login
Generated 2026-06-07. Re-runnable in CI with zero agent cost.
Exit 0 on pass, non-zero on any assertion failure.
"""
import sys
from playwright.sync_api import sync_playwright, expect


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Step 1: Open login page
        page.goto("https://the-internet.herokuapp.com/login", wait_until="domcontentloaded")
        expect(page.locator("#username")).to_be_visible()

        # Step 2: Fill username
        page.fill("#username", "tomsmith")

        # Step 3: Fill password
        page.fill("#password", "SuperSecretPassword!")

        # Step 4: Submit login form
        page.click("button[type='submit']")
        page.wait_for_load_state("domcontentloaded")

        # Step 5: Assert green success flash banner contains expected text
        flash = page.locator("#flash")
        expect(flash).to_be_visible()
        expect(flash).to_contain_text("You logged into a secure area")

        # Step 6: Click Logout
        page.click("a[href='/logout']")
        page.wait_for_load_state("domcontentloaded")

        # Step 7: Assert login form is visible again
        expect(page.locator("#username")).to_be_visible()
        expect(page.locator("#password")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()

        context.close()
        browser.close()

    print("All assertions passed — flow complete.")


if __name__ == "__main__":
    main()
