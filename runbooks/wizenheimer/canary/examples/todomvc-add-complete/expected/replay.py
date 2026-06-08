#!/usr/bin/env python3
"""
Canary QA replay script — TodoMVC flow.
Reproduces the QA flow headless; exits non-zero if any assertion fails.
Run: python replay.py
"""
from playwright.sync_api import sync_playwright, expect


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # 1. Open the app
        page.goto("https://demo.playwright.dev/todomvc", wait_until="domcontentloaded")
        assert page.url.startswith("https://demo.playwright.dev/todomvc"), "navigation failed"

        # 2. Add todo "Buy milk"
        page.fill("input.new-todo", "Buy milk")
        page.press("input.new-todo", "Enter")
        page.wait_for_timeout(400)

        # 3. Add todo "Walk the dog"
        page.fill("input.new-todo", "Walk the dog")
        page.press("input.new-todo", "Enter")
        page.wait_for_timeout(400)

        # 4. Assert counter shows "2 items left"
        counter_text = page.locator(".todo-count").inner_text().strip()
        assert counter_text.startswith("2"), f"expected counter '2 items left', got '{counter_text}'"

        # 5. Mark "Buy milk" completed via its checkbox
        page.locator(".todo-list li").filter(has_text="Buy milk").locator("input.toggle").check()
        page.wait_for_timeout(400)

        # 6. Assert counter shows "1 item left"
        counter_text = page.locator(".todo-count").inner_text().strip()
        assert counter_text.startswith("1"), f"expected counter '1 item left', got '{counter_text}'"

        # 7. Assert "Buy milk" item has 'completed' class
        buy_milk_class = page.locator(".todo-list li").filter(has_text="Buy milk").get_attribute("class") or ""
        assert "completed" in buy_milk_class, f"expected Buy milk to be completed, class='{buy_milk_class}'"

        context.close()
        browser.close()
        print("All assertions passed — flow PASS")


if __name__ == "__main__":
    main()
