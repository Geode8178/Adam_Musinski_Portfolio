from __future__ import annotations

from datetime import datetime, date
from typing import Optional

import pytest
from playwright.sync_api import Page, Locator

from config.settings import url


# ---------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------

# Helper to log messages for this specific test
def _log(msg: str) -> None:
    print(f"[RSP][Invoice Date Field] {msg}")


# Helper to visually highlight elements during debug runs
def _highlight(
    page: Page,
    el: Locator,
    *,
    color: str = "#0a84ff",
    wait_ms: int = 400,
) -> None:
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


def parse_invoice_date(text: str) -> date:
    """
    Parse an invoice date string from the grid into a datetime.date.

    Supports formats like:
      - YYYY-MM-DD
      - MM/DD/YYYY
      - Abbrev month with a period: 'Oct. 30, 2025'
      - Abbrev month without a period: 'Oct 30, 2025'
      - Full month name: 'October 30, 2025'
    """
    text = text.strip()

    POTENTIAL_DATE_FORMATS = [
        "%Y-%m-%d",      # 2025-10-30
        "%m/%d/%Y",      # 10/30/2025
        "%m/%d/%y",      # 10/30/25
        "%b. %d, %Y",    # Oct. 30, 2025
        "%b %d, %Y",     # Oct 30, 2025
        "%B %d, %Y",     # October 30, 2025
    ]

    for fmt in POTENTIAL_DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass

    raise AssertionError(
        f"Unrecognized Invoice Date format: {text!r}. "
        "Supported formats include: YYYY-MM-DD, MM/DD/YYYY, "
        "and 'Oct. 30, 2025' style month formats."
    )


def find_invoice_date_header(page: Page) -> Locator:
    """
    Robustly target ONLY the sortable Invoice Date column header link.
    """
    # First: look for an ascending sort link
    header = page.locator("th >> a[href*='sort=invoice_date']")
    if header.count() == 0:
        # Sometimes descending sort uses sort=-invoice_date
        header = page.locator("th >> a[href*='sort=-invoice_date']")

    assert header.count() == 1, (
        "Could not find the Invoice Date sortable column header "
        "(expected <th><a href*='sort=invoice_date'>...</a></th>)."
    )

    header.first.wait_for(state="visible", timeout=30_000)
    return header.first


def get_first_invoice_date_cell(page: Page) -> Locator:
    """
    Return Locator for the first-row Invoice Date cell.
    Adjust selectors if necessary to match your table structure.
    """
    cell = page.locator("td.invoice_date, td.invoice-date, td.invoiceDate").first
    cell.wait_for(state="visible", timeout=30_000)
    return cell


def sort_invoice_date_desc(page: Page) -> None:
    """
    Ensure the Invoice Date column is sorted in descending order.

    Implementation: click the sortable Invoice Date header exactly 2 times,
    re-locating it each time to handle href changes (sort=invoice_date vs -invoice_date).
    Assumes:
      - Initial state is unsorted or ascending.
      - First click => ascending, second click => descending.
    """
    for i in range(2):
        header = find_invoice_date_header(page)
        _log(f"Clicking Invoice Date header to move toward descending sort (attempt {i + 1}/2).")
        _highlight(page, header)
        header.click()


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

@pytest.mark.rsp
@pytest.mark.ui
@pytest.mark.invoice_date
@pytest.mark.invoice_date_range
def test_rsp_invoice_date_specific_range(page: Page) -> None:
    """
    Verify the behavior of the 'Select specific date range' Invoice Date filter.

    Flow:
      1. Start on the Recent Sales page.
      2. Verify Market Actor is 'All'.
      3. Verify Status is 'All'.
      4. Enable a specific date range checkbox.
      5. Verify Invoice Start/End Date fields are visible.
      6. Set Invoice End Date = today.
      7. Click Search.
      8. Sort Invoice Date descending.
      9. Take first-row Invoice Date as 'latest_date' and verify it is <= today.
     10. Find the next row with a different Invoice Date and use that as Invoice Start Date.
     11. Set Invoice Start Date = that date.
     12. Click Search.
     13. Verify the first-row Invoice Date is >= start date.
     14. Sort Invoice Date descending again.
     15. Verify the first-row Invoice Date is <= end date (today).
    """

    # ------------------------------------------------------------------
    # 1. Navigate to Recent Sales page
    # ------------------------------------------------------------------
    _log("Navigating to Recent Sales page (/salesdata/) for specific-date-range test.")
    page.goto(url("/salesdata/"), wait_until="domcontentloaded")
    page.wait_for_url("**/salesdata/**", timeout=30_000)
    _log(f"Arrived on: {page.url}")

    # ------------------------------------------------------------------
    # 2. Verify Market Actor is set to 'All'
    # ------------------------------------------------------------------
    _log('Verifying Market Actor is set to "All".')
    market_actor_dropdown = page.locator("#id_market_actor")
    assert market_actor_dropdown.count() == 1, (
        "Expected a single Market Actor select (#id_market_actor)."
    )
    market_actor_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(page, market_actor_dropdown)
    selected_market_actor = (
        market_actor_dropdown.locator("option:checked").inner_text().strip()
    )
    assert selected_market_actor == "All", (
        "Expected Market Actor selection to be 'All', "
        f"got {selected_market_actor!r}."
    )
    _log(f"Market Actor confirmed: {selected_market_actor!r}")

    # ------------------------------------------------------------------
    # 3. Verify Status is set to 'All'
    # ------------------------------------------------------------------
    _log('Verifying Status is set to "All".')
    status_dropdown = page.locator("#id_status")
    assert status_dropdown.count() == 1, "Expected a single Status select (#id_status)."
    status_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(page, status_dropdown)
    selected_status = status_dropdown.locator("option:checked").inner_text().strip()
    assert selected_status == "All", (
        "Expected Status selection to be 'All', "
        f"got {selected_status!r}."
    )
    _log(f"Status confirmed: {selected_status!r}")

    # ------------------------------------------------------------------
    # 4. Click the 'Select specific date range' checkbox
    #    <input type="checkbox" id="enable-date-range-invoice" name="enable_date_range">
    # ------------------------------------------------------------------
    _log('Enabling "Select specific date range" checkbox.')
    specific_range_checkbox = page.locator("#enable-date-range-invoice")
    assert specific_range_checkbox.count() == 1, (
        "Expected a single specific-date-range checkbox "
        "(#enable-date-range-invoice)."
    )
    specific_range_checkbox.wait_for(state="visible", timeout=30_000)
    _highlight(page, specific_range_checkbox)
    specific_range_checkbox.check()

    # ------------------------------------------------------------------
    # 5. Verify 'Invoice Start Date' and 'Invoice End Date' fields are visible
    #    Start: <input type="date" id="invoice_start_date" ...>
    #    End: <input type="date" id="invoice_end_date" ...>
    # ------------------------------------------------------------------
    _log("Verifying Invoice Start Date and End Date fields are visible.")
    invoice_start_input = page.locator("#invoice_start_date")
    invoice_end_input = page.locator("#invoice_end_date")

    assert invoice_start_input.count() == 1, (
        "Expected a single Invoice Start Date input (#invoice_start_date)."
    )
    assert invoice_end_input.count() == 1, (
        "Expected a single Invoice End Date input (#invoice_end_date)."
    )

    invoice_start_input.wait_for(state="visible", timeout=30_000)
    invoice_end_input.wait_for(state="visible", timeout=30_000)
    _highlight(page, invoice_start_input)
    _highlight(page, invoice_end_input)

    # ------------------------------------------------------------------
    # 6. Enter today's date into the 'Invoice End Date' field.
    #    Assuming native <input type="date"> expects YYYY-MM-DD.
    # ------------------------------------------------------------------
    today = date.today()
    today_str = today.isoformat()  # 'YYYY-MM-DD'
    _log(f"Setting Invoice End Date to today: {today_str}.")
    invoice_end_input.fill(today_str)

    # ------------------------------------------------------------------
    # 7. Click the 'Search' button
    # ------------------------------------------------------------------
    _log('Clicking "Search" after setting Invoice End Date.')
    search_button = page.locator(
        "button[type='submit'].btn.btn-primary",
        has_text="Search",
    )
    assert search_button.count() == 1, "Expected a single primary 'Search' submit button."
    search_button.wait_for(state="visible", timeout=30_000)
    _highlight(page, search_button)
    search_button.click()

    # ------------------------------------------------------------------
    # 8–11. Sort desc, get top Invoice Date, verify <= today,
    #        and capture next different date as start date.
    # ------------------------------------------------------------------
    _log("Sorting Invoice Date column to descending using helper (2 clicks).")
    sort_invoice_date_desc(page)

    # Helper to read invoice date from a row index (0-based)
    def _get_invoice_date_from_row(row_index: int) -> date:
        # Target the specific row first
        row = page.locator("tbody tr").nth(row_index)
        if row.count() == 0:
            pytest.skip(f"No table row at index {row_index} when reading Invoice Date.")

        # Then target the invoice date cell within that row
        row_cell = row.locator("td.invoice_date, td.invoice-date, td.invoiceDate").first
        row_cell.wait_for(state="visible", timeout=30_000)
        _highlight(page, row_cell, color="#ff9f0a")
        raw = row_cell.inner_text().strip()
        assert raw, f"Expected non-empty Invoice Date cell text in row {row_index}."
        return parse_invoice_date(raw)

    # First position (row 0)
    latest_date = _get_invoice_date_from_row(0)
    _log(f"Top Invoice Date after descending sort: {latest_date.isoformat()}.")

    # Verify the date found is inclusive to today's date (<= today)
    assert latest_date <= today, (
        "Expected top Invoice Date to be on or before today "
        f"({today.isoformat()}), got {latest_date.isoformat()}."
    )

    # Find the next position down where the date != first position date.
    _log("Searching for the next row with a different Invoice Date.")
    different_date: Optional[date] = None
    for idx in range(1, 50):  # arbitrary upper bound to avoid infinite loop
        row = page.locator("tbody tr").nth(idx)
        if row.count() == 0:
            break

        try:
            row_date = _get_invoice_date_from_row(idx)
        except AssertionError:
            continue  # skip malformed rows, if any

        if row_date != latest_date:
            different_date = row_date
            _log(
                f"Found different Invoice Date at row {idx}: "
                f"{different_date.isoformat()} (first row was {latest_date.isoformat()})."
            )
            break

    assert different_date is not None, (
        "Could not find a second row with a different Invoice Date. "
        "Need this to set the Invoice Start Date."
    )

    # ------------------------------------------------------------------
    # 13. Enter that date into the 'Invoice Start Date' field.
    # ------------------------------------------------------------------
    start_date = different_date
    start_str = start_date.isoformat()
    _log(f"Setting Invoice Start Date to: {start_str}.")
    invoice_start_input.fill(start_str)

    # ------------------------------------------------------------------
    # 14. Click the 'Search' button again.
    # ------------------------------------------------------------------
    _log('Clicking "Search" after setting Invoice Start Date.')
    search_button.wait_for(state="visible", timeout=30_000)
    _highlight(page, search_button)
    search_button.click()

    # ------------------------------------------------------------------
    # 15–16. Verify the first-row date is >= start date.
    # ------------------------------------------------------------------
    _log("Verifying first Invoice Date after search is >= start date.")
    first_after_start = _get_invoice_date_from_row(0)
    assert first_after_start >= start_date, (
        "Expected first Invoice Date after search to be on or after "
        f"start date {start_date.isoformat()}, got {first_after_start.isoformat()}."
    )

    # ------------------------------------------------------------------
    # 17. Sort Invoice Date header to descending again.
    # ------------------------------------------------------------------
    _log("Sorting Invoice Date to descending again via helper (2 clicks).")
    sort_invoice_date_desc(page)

    # ------------------------------------------------------------------
    # 18. Verify first position date is <= end date (today).
    # ------------------------------------------------------------------
    _log("Verifying top Invoice Date is <= end date (today).")
    first_after_desc = _get_invoice_date_from_row(0)
    assert first_after_desc <= today, (
        "Expected first Invoice Date after descending sort to be on or "
        f"before end date {today.isoformat()}, got {first_after_desc.isoformat()}."
    )

    _log(
        "PASSED: Specific Invoice Date range filter behaved correctly with "
        "start/end dates and descending sort validation."
    )


