from playwright.sync_api import Locator
from config.status_ui_spec_definitions import STATUS_UI_SPECS

def assert_status_cell_matches_spec(cell: Locator, *, status_key: str) -> None:
    spec = STATUS_UI_SPECS[status_key]

    # Validate required icons
    for sel in spec.required_icon_selectors:
        assert cell.locator(sel).count() >= 1, (
            f"Expected status cell to contain icon {sel!r} for status {status_key!r}."
        )

    # Validate required text fragments (search within whole cell text)
    cell_text = cell.inner_text().strip()
    for expected in spec.must_contain:
        assert expected in cell_text, (
            f"Expected status cell to contain {expected!r} for status {status_key!r}, "
            f"but cell text was: {cell_text!r}"
        )

from config.settings import url


def test_rsp_status_field_unassigned(page):
    def _log(msg: str) -> None:
        print(f"[RSP][Status=Unassigned] {msg}")

    def _highlight(el, *, color: str = "#0a84ff", wait_ms: int = 400) -> None:
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

    # User stays logged in and navigates to the Sales Data page.
    _log("Navigating to Recent Sales page (/salesdata/).")
    page.goto(url("/salesdata/"), wait_until="domcontentloaded")
    page.wait_for_url("**/salesdata/**", timeout=30_000)
    _log(f"Arrived on: {page.url}")

    # Market Actor: set to "AF Supply" (#id_market_actor)
    _log('Setting Market Actor = "AF Supply".')
    market_actor_dropdown = page.locator("#id_market_actor")
    assert market_actor_dropdown.count() == 1, (
        "Expected a single Market Actor select (#id_market_actor)."
    )
    market_actor_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(market_actor_dropdown, color="#0a84ff")
    market_actor_dropdown.select_option(label="AF Supply")

    selected_market_actor = (
        market_actor_dropdown.locator("option:checked").inner_text().strip()
    )
    assert selected_market_actor == "AF Supply", (
        f"Expected Market Actor selection to be 'AF Supply', got {selected_market_actor!r}"
    )
    _log(f"Market Actor confirmed: {selected_market_actor!r}")

    # Status: set to "Unassigned" (#id_status)
    _log('Setting Status = "Unassigned".')
    status_dropdown = page.locator("#id_status")
    assert status_dropdown.count() == 1, "Expected a single Status select (#id_status)."
    status_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(status_dropdown, color="#0a84ff")
    status_dropdown.select_option(label="Unassigned")

    selected_status = status_dropdown.locator("option:checked").inner_text().strip()
    assert selected_status == "Unassigned", (
        f"Expected Status selection to be 'Unassigned', got {selected_status!r}"
    )
    _log(f"Status confirmed: {selected_status!r}")

    # Invoice Date: ensure it is "All" (#id_invoice_date)
    _log('Ensuring Invoice Date = "All".')
    invoice_date_dropdown = page.locator("#id_invoice_date")
    assert invoice_date_dropdown.count() == 1, (
        "Expected a single Invoice Date select (#id_invoice_date)."
    )
    invoice_date_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(invoice_date_dropdown, color="#0a84ff")
    invoice_date_dropdown.select_option(label="All")

    selected_invoice_date = (
        invoice_date_dropdown.locator("option:checked").inner_text().strip()
    )
    assert selected_invoice_date == "All", (
        f"Expected Invoice Date selection to be 'All', got {selected_invoice_date!r}"
    )
    _log(f"Invoice Date confirmed: {selected_invoice_date!r}")

    # Click the "Search" button.
    _log('Clicking "Search".')
    search_button = page.locator(
        "button[type='submit'].btn.btn-primary",
        has_text="Search",
    )
    assert search_button.count() == 1, (
        "Expected a single primary 'Search' submit button."
    )
    search_button.wait_for(state="visible", timeout=30_000)
    _highlight(search_button, color="#34c759")
    search_button.click()

    # Instead of relying only on networkidle (can be flaky if the page polls),
    # wait for the first Status cell to exist/appear.
    def first_status_cell():
        cell = page.locator("td.status").first
        cell.wait_for(state="visible", timeout=30_000)
        return cell

    _log("Waiting for results table to show Status column cells.")
    first_cell = first_status_cell()
    _highlight(first_cell, color="#ff9f0a")
    _log("Results loaded (first Status cell is visible).")

    def verify_status_cell(cell, *, stage: str) -> None:
        _log(f"Verifying first-row Status cell ({stage}).")
        _highlight(cell, color="#ff9f0a")

        icon = cell.locator("i.bi.fs-4.bi-exclamation.text-danger")
        assert icon.count() >= 1, (
            "Expected exclamation icon with .text-danger in Status cell."
        )

        cell_text = cell.inner_text().strip()
        assert "Incomplete" in cell_text, (
            f"Expected 'Incomplete' in Status cell text, got: {cell_text!r}"
        )

        help_text = cell.locator("span.help-text")
        assert help_text.count() >= 1, (
            "Expected <span class='help-text'> inside Status cell."
        )
        help_text_text = help_text.first.inner_text().strip()
        assert "Unassigned" in help_text_text, (
            f"Expected 'Unassigned' in help-text, got: {help_text_text!r}"
        )

        _log("Status cell OK: has red icon, contains 'Incomplete', help-text contains 'Unassigned'.")

    # Find the Status column header (sort link).
    _log("Locating Status column header link (sort control).")
    status_header_link = page.get_by_role("link", name="Status", exact=True)
    if status_header_link.count() == 0:
        status_header_link = page.locator('a[href*="sort=status"]')

    assert status_header_link.count() >= 1, "Could not find the Status column header link."
    status_header_link.first.wait_for(state="visible", timeout=30_000)
    status_header_link.first.scroll_into_view_if_needed()
    status_header_link.first.focus()
    _highlight(status_header_link.first, color="#0a84ff")

    # Verify the baseline (after search).
    verify_status_cell(first_cell, stage="baseline")

    # Click to sort Asc.
    _log("Sorting by Status (click #1).")
    status_header_link.first.click()
    first_cell_asc = first_status_cell()
    verify_status_cell(first_cell_asc, stage="after sort #1")

    # Click to sort Desc.
    _log("Sorting by Status (click #2).")
    status_header_link.first.click()
    first_cell_desc = first_status_cell()
    verify_status_cell(first_cell_desc, stage="after sort #2")

    _log(
        "PASSED: filters applied, search executed, first-row Status cell validated, sort toggled twice and re-validated."
    )
