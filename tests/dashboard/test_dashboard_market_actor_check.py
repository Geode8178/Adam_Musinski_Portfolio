"""Validates the correct market actor cards visible on the dashboard."""

from config.settings import url

def test_dashboard_market_actor_check(page):

    # User-focused, single login is used, so there is no back and forth between tests.
    page.goto(url("/dashboard/"), wait_until="domcontentloaded")
    if not page.url.endswith("/dashboard/"):
        raise Exception("Failed to load the Dashboard page.")

    # Capture the Market Actor card names in a list.
    ma_card_name_selector = "h2.card-title"
    ma_card_name_locator = page.locator(ma_card_name_selector)

    # Capture the Market Actor card names in a list (Infinite Scroll).
    ma_card_name_locator.first.wait_for(state="visible", timeout=10_000)

    dashboard_ma_names: set[str] = set()  # type: ignore[annotation-unchecked]
    stable_rounds = 0
    stable_rounds_to_stop = 2  # Expected number of rounds to ensure stability.
    max_rounds = 10  # Safety Cap.

    for _ in range(max_rounds):
        dashboard_market_actor_names = [
            t.strip() for t in ma_card_name_locator.all_inner_texts() if t and t.strip()
        ]

        before = len(dashboard_ma_names)
        dashboard_ma_names.update(dashboard_market_actor_names)
        after = len(dashboard_ma_names)

        if before == after:
            stable_rounds += 1
        else:
            stable_rounds = 0

        if stable_rounds >= stable_rounds_to_stop:
            break

        # Scroll to trigger lazy loading of more Market Actor cards.
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(1000)

        # Open the Recent Sales page.
        recent_sales_button = page.get_by_role("link", name="Recent Sales")
        recent_sales_button.click()
        if not page.url.endswith("/salesdata/"):
            raise Exception("Failed to load the Recent Sales page.")

        # Find and select the Market Actor combobox.
        market_actor_dropdown = page.get_by_role("combobox", name="Market Actor")
        options = market_actor_dropdown.locator("option").all_text_contents()
        active_market_actor_names = [o.strip() for o in options if o and o.strip() and o.strip() != "All"]

        # Run a comparison between the Market Actor names on the dashboard and the Recent Sales page.
        assert dashboard_ma_names == set(active_market_actor_names)
        if dashboard_ma_names != set(active_market_actor_names):
            raise Exception("Market Actor names on the dashboard do not match the Recent Sales page.")
        else:
            return



