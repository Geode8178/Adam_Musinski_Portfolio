"""Validates that the visible Market Actor cards on the dashboard are defaulted open.
The program will then close them, validating UI requirements."""

from config.settings import url
from playwright.sync_api import expect

def test_dashboard_ma_card_accordion(page):

    # User-focused, single login is used, so there is no back and forth between tests.
    page.goto(url("/dashboard/"), wait_until="domcontentloaded")
    if not page.url.endswith("/dashboard/"):
        raise Exception("Failed to load the Dashboard page.")

    # Validate UI Requirements: Market Actor cards should be defaulted open on the dashboard.
    cards = page.locator("div.card:has(h2.card-title)")
    cards.first.wait_for(state="visible", timeout=30_000)

    market_actor_cards_collapsed = []
    market_actor_cards_not_collapsed = []

    def _card_panel(ma_card):
        # Prefer explicit collapse/accordion containers; fall back to card-body.
        ma_panel = ma_card.locator(".accordion-collapse, .collapse, .card-body").first
        return ma_panel

    # First Pass: Verify Market Actor card is in an expanded state (panel visible).
    for i in range(cards.count()):
        card = cards.nth(i)
        title = card.locator("h2.card-title").first
        name = title.inner_text().strip()
        if not name:
            continue

        panel = _card_panel(card)

        # If this fails, it means our "panel" selector is wrong for your DOM.
        expect(panel, f"Card '{name}' should have a collapsible/visible content panel.").to_have_count(1)

        try:
            expect(panel, f"Card '{name}' should be expanded (content visible) when the dashboard loads.").to_be_visible(
                timeout=10_000
            )
        except AssertionError:
            market_actor_cards_collapsed.append(name)

    if market_actor_cards_collapsed:
        raise Exception(
            "The following Market Actor cards are collapsed when the dashboard loaded: "
            f"{market_actor_cards_collapsed}"
        )

    # Second Pass: Collapse each Market Actor card and verify it is collapsed.
    for i in range(cards.count()):
        card = cards.nth(i)
        title = card.locator("h2.card-title").first
        name = title.inner_text().strip()
        if not name:
            continue

        panel = _card_panel(card)

        # Click a reliable target inside the header area: the title itself tends to be stable.
        title.scroll_into_view_if_needed()
        title.click()

        try:
            expect(panel, f"Card '{name}' should be collapsed (content hidden) when clicked on.").to_be_hidden(
                timeout=10_000
            )
        except AssertionError:
            market_actor_cards_not_collapsed.append(name)

    if market_actor_cards_not_collapsed:
        raise Exception(
            "The following Market Actor cards are not collapsed when clicked on: "
            f"{market_actor_cards_not_collapsed}"
        )


