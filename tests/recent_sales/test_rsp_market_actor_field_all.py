"""This test verifies that the Market Actor field is displayed correctly on the Recent Sales Page.
It will run a search and validate that sales records can be pulled using "All" market
actors by manipulating the Market Actor column in the sales record list view. It will
validate that the first market actor and last market actors are visible.
"""

from config.settings import url


def test_rsp_market_actor_field(page):
    def _log(msg: str) -> None:
        print(f"[RSP][MarketActor=All] {msg}")

    def _highlight(el, *, color: str = "#0a84ff", wait_ms: int = 350) -> None:
        el.scroll_into_view_if_needed()
        el.evaluate(
            f"""
            (node) => {{
              node.style.outline = '3px solid {color}';
              node.style.outlineOffset = '3px';
              node.style.background = 'rgba(10, 132, 255, 0.10)';
              node.style.borderRadius = '4px';
            }}
            """
        )
        page.wait_for_timeout(wait_ms)

    _log("Navigating to Recent Sales page (/salesdata/).")
    page.goto(url("/salesdata/"), wait_until="domcontentloaded")
    page.wait_for_url("**/salesdata/**", timeout=30_000)
    _log(f"Arrived on: {page.url}")

    # Verify Market Actor field is set to "All".
    _log("Validating Market Actor default selection is 'All'.")
    market_actor_dropdown = page.locator("#id_market_actor")
    assert market_actor_dropdown.count() == 1, "Expected a single Market Actor select (#id_market_actor)."
    market_actor_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(market_actor_dropdown)

    selected_label = market_actor_dropdown.locator("option:checked").inner_text().strip()
    assert selected_label == "All", (
        f"Expected Market Actor default selection to be 'All', got {selected_label!r}"
    )
    _log("Market Actor default confirmed: 'All'.")

    market_actor_options = [t.strip() for t in market_actor_dropdown.locator("option").all_text_contents()]
    market_actor_names = [t for t in market_actor_options if t and t != "All"]
    assert market_actor_names, "Expected at least one Market Actor option besides 'All'."

    first_market_actor = market_actor_names[0]
    last_market_actor = market_actor_names[-1]
    _log(f"Captured first_market_actor={first_market_actor!r}, last_market_actor={last_market_actor!r}")

    # Verify Status field is set to "All".
    _log("Validating Status default selection is 'All'.")
    status_dropdown = page.locator("#id_status")
    assert status_dropdown.count() == 1, "Expected a single Status select (#id_status)."
    status_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(status_dropdown)

    selected_status_label = status_dropdown.locator("option:checked").inner_text().strip()
    assert selected_status_label == "All", (
        f"Expected Status default selection to be 'All', got {selected_status_label!r}"
    )
    _log("Status default confirmed: 'All'.")

    # Verify Invoice Date is defaulted to "All".
    _log("Validating Invoice Date default selection is 'All'.")
    invoice_date_dropdown = page.locator("#id_invoice_date")
    assert invoice_date_dropdown.count() == 1, "Expected a single Invoice Date select (#id_invoice_date)."
    invoice_date_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(invoice_date_dropdown)

    selected_invoice_date_label = invoice_date_dropdown.locator("option:checked").inner_text().strip()
    assert selected_invoice_date_label == "All", (
        f"Expected Invoice Date default selection to be 'All', got {selected_invoice_date_label!r}"
    )
    _log("Invoice Date default confirmed: 'All'.")

    # Click the Search Button (submit button).
    _log('Clicking "Search".')
    search_button = page.locator("button[type='submit'].btn.btn-primary", has_text="Search")
    assert search_button.count() == 1, "Expected a single primary submit Search button."
    search_button.wait_for(state="visible", timeout=30_000)
    _highlight(search_button, color="#34c759")
    search_button.click()

    # Prefer deterministic UI wait over networkidle.
    first_market_actor_cell = page.locator("td.market_actor").first
    first_market_actor_cell.wait_for(state="visible", timeout=30_000)
    _highlight(first_market_actor_cell, color="#ff9f0a")
    _log("Results loaded (first Market Actor cell is visible).")

    first_market_actor_in_table = first_market_actor_cell.inner_text().strip()
    assert first_market_actor_in_table == first_market_actor, (
        f"Expected first Market Actor row to be {first_market_actor!r}, but was {first_market_actor_in_table!r}"
    )
    _log(f"Ascending check OK: first row Market Actor == {first_market_actor!r}")

    # Sort by Market actor.
    market_actor_header_link = page.get_by_role("link", name="Market actor", exact=True)
    market_actor_header_link.wait_for(state="visible", timeout=30_000)
    market_actor_header_link.scroll_into_view_if_needed()
    market_actor_header_link.focus()
    _highlight(market_actor_header_link, color="#0a84ff")

    _log("Sorting Market Actor (click #1).")
    market_actor_header_link.click()
    first_market_actor_cell.wait_for(state="visible", timeout=30_000)

    _log("Sorting Market Actor (click #2) to reach descending order.")
    market_actor_header_link.click()
    first_market_actor_cell.wait_for(state="visible", timeout=30_000)

    first_market_actor_in_table_desc = first_market_actor_cell.inner_text().strip()
    assert first_market_actor_in_table_desc == last_market_actor, (
        f"Expected first Market Actor row (descending) to be {last_market_actor!r}, "
        f"but was {first_market_actor_in_table_desc!r}"
    )
    _log(f"Descending check OK: first row Market Actor == {last_market_actor!r}")

    _log("PASSED: defaults validated, search executed, Market Actor sort verified asc/desc.")
