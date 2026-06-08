"""
Replay script — reproduces the saucedemo QA flow headless.
Runs in CI with zero agent cost. Exits non-zero if any assertion fails.

Usage:
    python replay.py
"""
from playwright.sync_api import sync_playwright, expect


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # 1. Open the app
        page.goto("https://www.saucedemo.com", wait_until="domcontentloaded")
        expect(page.locator("[data-test='login-button']")).to_be_visible()

        # 2. Enter credentials
        page.fill("[data-test='username']", "standard_user")
        page.fill("[data-test='password']", "secret_sauce")

        # 3. Submit login
        page.click("[data-test='login-button']")

        # 4. Assert inventory page loaded (URL contains "inventory")
        page.wait_for_url("**/inventory**", timeout=5000)
        assert "inventory" in page.url, f"Expected inventory URL, got: {page.url}"

        # 5. Add Sauce Labs Backpack to cart
        page.click("[data-test='add-to-cart-sauce-labs-backpack']")

        # 6. Assert cart badge shows "1"
        badge = page.locator("[data-test='shopping-cart-badge']")
        expect(badge).to_be_visible()
        expect(badge).to_have_text("1")

        browser.close()
        print("All assertions passed — flow: PASS")


if __name__ == "__main__":
    main()
