from __future__ import annotations

import re
from datetime import datetime, timedelta, date

import pytest
from playwright.sync_api import Locator, Page

from config.settings import url


# Helper to log messages for this specific test
def _log(msg: str) -> None:
    print(f"[RSP][Invoice Date Field] {msg}")


# Helper to visually highlight elements during debug runs
def _highlight(page: Page, el: Locator, *, color: str = "#0a84ff", wait_ms: int = 400) -> None:
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


def get_total_record_count(page: Page) -> int:
    """
    Parse and return the total record count from the page.

    Expects text like: "Total Record Count 123" inside a <p> element.
    """
    total_p = page.locator("p:has-text('Total Record Count')").first
    total_p.wait_for(state="visible", timeout=30_000)
    text = total_p.inner_text().strip()

    match = re.search(r"Total Record Count\s+(\d+)", text)
    assert match, (
        "Could not parse Total Record Count from text: "
        f"{text!r}. Expected format like 'Total Record Count 123'."
    )
    count = int(match.group(1))
    _log(f"Parsed Total Record Count = {count} from: {text!r}")
    return count


def parse_invoice_date(text: str) -> date:
    """
    Parse an invoice date string from the grid into a datetime.date.

    Supports formats like:
      - YYYY-MM-DD
      - MM/DD/YYYY
      - Abbrev month with period: 'Oct. 30, 2025'
      - Abbrev month without period: 'Oct 30, 2025'
      - Full month name: 'October 30, 2025'
    """
    text = text.strip()

    POSSIBLE_FORMATS = [
        "%Y-%m-%d",      # 2025-10-30
        "%m/%d/%Y",      # 10/30/2025
        "%m/%d/%y",      # 10/30/25
        "%b. %d, %Y",    # Oct. 30, 2025
        "%b %d, %Y",     # Oct 30, 2025
        "%B %d, %Y",     # October 30, 2025
    ]

    for fmt in POSSIBLE_FORMATS:
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
    # First: look for ascending/descending sort link
    header = page.locator("th >> a[href*='sort=invoice_date']")
    if header.count() == 0:
        # Sometimes desc sort uses sort=-invoice_date
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


def verify_first_date_within_days(page: Page, *, max_days: int) -> None:
    """
    Read the first-row Invoice Date cell, parse it, and assert that it falls
    within [today - max_days, today].
    """
    cell = get_first_invoice_date_cell(page)
    _highlight(page, cell, color="#ff9f0a")
    raw_text = cell.inner_text().strip()
    assert raw_text, "Expected non-empty Invoice Date cell text."
    inv_date = parse_invoice_date(raw_text)

    today = date.today()
    min_date = today - timedelta(days=max_days)

    _log(
        f"Verifying Invoice Date {inv_date.isoformat()} is within "
        f"[{min_date.isoformat()}, {today.isoformat()}] for Last {max_days} Days."
    )

    assert min_date <= inv_date <= today, (
        f"Invoice Date {inv_date.isoformat()} is not within the "
        f"last {max_days} days (expected between {min_date.isoformat()} and "
        f"{today.isoformat()}). Raw cell text: {raw_text!r}"
    )


@pytest.mark.rsp
@pytest.mark.ui
@pytest.mark.invoice_date
def test_rsp_invoice_date_field(page: Page) -> None:
    """
    Verify the behavior of the Invoice Date filter (All, Last 90/60/30 Days)
    with Market Actor and Status left as 'All'.

    Steps:
      1. Verify Invoice Date = 'All'.
      2. Click Search.
      3. Verify Total Record Count != 0.
      4. For each of: Last 90 Days, Last 60 Days, Last 30 Days:
         a. Set Invoice Date to that option.
         b. Click Search.
         c. Verify Total Record Count != 0 (or skip if 0).
         d. Click Invoice Date column header to sort Asc -> check first date within window.
         e. Click Invoice Date column header to sort Desc -> check first date within window.
    """

    # ------------------------------------------------------------------
    # Navigate to Recent Sales page
    # ------------------------------------------------------------------
    _log("Navigating to Recent Sales page (/salesdata/).")
    page.goto(url("/salesdata/"), wait_until="domcontentloaded")
    page.wait_for_url("**/salesdata/**", timeout=30_000)
    _log(f"Arrived on: {page.url}")

    # ------------------------------------------------------------------
    # Verify default filters: Market Actor, Status = All
    # ------------------------------------------------------------------
    _log('Verifying Market Actor and Status are set to "All".')

    # Market Actor (#id_market_actor)
    market_actor_dropdown = page.locator("#id_market_actor")
    assert market_actor_dropdown.count() == 1, (
        "Expected a single Market Actor select (#id_market_actor)."
    )
    market_actor_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(page, market_actor_dropdown, color="#0a84ff")
    selected_market_actor = (
        market_actor_dropdown.locator("option:checked").inner_text().strip()
    )
    assert selected_market_actor == "All", (
        "Expected Market Actor selection to be 'All', "
        f"got {selected_market_actor!r}."
    )
    _log(f"Market Actor confirmed: {selected_market_actor!r}")

    # Status (#id_status)
    status_dropdown = page.locator("#id_status")
    assert status_dropdown.count() == 1, "Expected a single Status select (#id_status)."
    status_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(page, status_dropdown, color="#0a84ff")
    selected_status = status_dropdown.locator("option:checked").inner_text().strip()
    assert selected_status == "All", (
        "Expected Status selection to be 'All', "
        f"got {selected_status!r}."
    )
    _log(f"Status confirmed: {selected_status!r}")

    # ------------------------------------------------------------------
    # 1. Verify Invoice Date = 'All'
    # ------------------------------------------------------------------
    invoice_date_dropdown = page.locator("#id_invoice_date")
    assert invoice_date_dropdown.count() == 1, (
        "Expected a single Invoice Date select (#id_invoice_date)."
    )
    invoice_date_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(page, invoice_date_dropdown, color="#0a84ff")

    selected_invoice_date = (
        invoice_date_dropdown.locator("option:checked").inner_text().strip()
    )
    assert selected_invoice_date == "All", (
        "Expected Invoice Date selection to be 'All' by default, "
        f"got {selected_invoice_date!r}."
    )

    # ------------------------------------------------------------------
    # 2–3. Click Search, verify Total Record Count != 0 for 'All'
    # ------------------------------------------------------------------
    _log('Clicking "Search" with Invoice Date = All.')
    search_button = page.locator(
        "button[type='submit'].btn.btn-primary",
        has_text="Search",
    )
    assert search_button.count() == 1, "Expected a single primary 'Search' submit button."
    search_button.wait_for(state="visible", timeout=30_000)
    _highlight(page, search_button, color="#34c759")
    search_button.click()

    total_record_count = get_total_record_count(page)
    assert total_record_count != 0, (
        "Expected non-zero Total Record Count when Invoice Date = 'All', "
        f"but got {total_record_count}."
    )
    _log(f"Total Record Count with Invoice Date='All': {total_record_count}.")

    # ------------------------------------------------------------------
    # Inner helper: exercise one Invoice Date option (90, 60, 30 days)
    # ------------------------------------------------------------------
    def _exercise_invoice_date_option(label: str, max_days: int) -> None:
        nonlocal total_record_count

        _log(f"--- Testing Invoice Date option: {label!r} (Last {max_days} Days) ---")

        # 4. Set Invoice Date to desired label (Last 90/60/30 Days)
        _log(f"Setting Invoice Date = {label!r}.")
        invoice_date_dropdown.select_option(label=label)

        selected_label = (
            invoice_date_dropdown.locator("option:checked").inner_text().strip()
        )
        assert selected_label == label, (
            f"Expected Invoice Date selection to be {label!r}, "
            f"got {selected_label!r}."
        )
        _log(f"Invoice Date confirmed: {selected_label!r}")

        # 5. Click Search
        _log('Clicking "Search" after changing Invoice Date.')
        search_button.wait_for(state="visible", timeout=30_000)
        _highlight(page, search_button, color="#34c759")
        search_button.click()

        # 6. Verify Total Record Count != 0 (otherwise skip)
        total_record_count = get_total_record_count(page)
        if total_record_count == 0:
            pytest.skip(
                f"No records found for Invoice Date={label!r} "
                "(Total Record Count 0)."
            )
        _log(
            f"Total Record Count with Invoice Date={label!r}: {total_record_count}."
        )

        # If there's only one record, sorting is moot; just verify date in range.
        if total_record_count == 1:
            _log(
                "Only one record found for this Invoice Date option; "
                "skipping sort checks and verifying the single Invoice Date is within range."
            )
            verify_first_date_within_days(page, max_days=max_days)
            return

        # 7. Sort Asc
        _log("Sorting Invoice Date Asc (click header #1).")
        invoice_date_header = find_invoice_date_header(page)
        _highlight(page, invoice_date_header, color="#0a84ff")
        invoice_date_header.click()

        # 8. Verify first position (Asc) is within the Last N Days
        verify_first_date_within_days(page, max_days=max_days)

        # 9. Sort Desc
        _log("Sorting Invoice Date Desc (click header #2).")
        invoice_date_header = find_invoice_date_header(page)
        _highlight(page, invoice_date_header, color="#0a84ff")
        invoice_date_header.click()

        # 10. Verify first position (Desc) is also within the Last N Days
        verify_first_date_within_days(page, max_days=max_days)

        _log(
            f"PASSED for Invoice Date={label!r}: first-row dates after Asc/Desc sort "
            f"are within the last {max_days} days."
        )

    # ------------------------------------------------------------------
    # Exercise Last 90 Days, Last 60 Days, Last 30 Days
    # ------------------------------------------------------------------
    _exercise_invoice_date_option("Last 90 Days", max_days=90)
    _exercise_invoice_date_option("Last 60 Days", max_days=60)
    _exercise_invoice_date_option("Last 30 Days", max_days=30)

    _log(
        "PASSED: Invoice Date filter for All, Last 90/60/30 Days behaved correctly "
        "with sorting and date-window validation."
    )
