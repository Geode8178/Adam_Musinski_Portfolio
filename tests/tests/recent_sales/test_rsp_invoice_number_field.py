from __future__ import annotations

import re

import pytest
from playwright.sync_api import Locator, Page

from config.settings import url


# Helper to log messages for this specific test
def _log(msg: str) -> None:
    print(f"[RSP][Invoice Number Field] {msg}")


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


def search_by_invoice_number(page: Page, *, value: str) -> int:
    """
    Fill the Invoice Number field, click Search, wait for results, return record count.
    """
    _log(f"Searching with Invoice Number field = {value!r}.")

    invoice_input = page.locator("#id_invoice_number")
    assert invoice_input.count() == 1, "Expected a single Invoice Number input (#id_invoice_number)."
    invoice_input.wait_for(state="visible", timeout=30_000)
    _highlight(page, invoice_input, color="#0a84ff")

    invoice_input.fill("")
    if value:
        invoice_input.type(value)

    search_button = page.locator(
        "button[type='submit'].btn.btn-primary",
        has_text="Search",
    )
    assert search_button.count() == 1, "Expected a single primary 'Search' submit button."
    search_button.wait_for(state="visible", timeout=30_000)
    _highlight(page, search_button, color="#34c759")
    search_button.click()

    # Wait for either some results or the empty-state Total Record Count 0
    total_0 = page.locator("p:has-text('Total Record Count 0')").first
    first_invoice_cell_locator = page.locator("td.invoice_number, td.invoice-number").first

    _log("Waiting for either an Invoice Number row or 'Total Record Count 0'.")
    try:
        first_invoice_cell_locator.wait_for(state="visible", timeout=10_000)
        has_rows = True
    except Exception:
        has_rows = False

    if not has_rows:
        try:
            total_0.wait_for(state="visible", timeout=5_000)
            _highlight(page, total_0, color="#ff9f0a")
            _log("Detected 'Total Record Count 0' after search.")
        except Exception:
            raise Exception(
                "No Invoice Number result row was found and the empty-state 'Total Record Count 0' "
                "was not visible. The page may not have rendered results correctly."
            )

    # Regardless of whether there are rows or 0 rows, parse the count deterministically
    return get_total_record_count(page)


@pytest.mark.rsp
@pytest.mark.ui
@pytest.mark.invoice_number
def test_rsp_invoice_number_field(page: Page) -> None:
    """
    Verify the incremental narrowing behavior of the Invoice Number filter on Recent Sales.

    Steps:
      1. Navigate to /salesdata/.
      2. Verify Market Actor = "All".
      3. Verifies Status = "All".
      4. Verify Invoice Date = "All".
      5. Perform an initial search with NO Invoice Number (blank).
      6. Record Total Record Count and first-row Invoice Number.
      7. Iteratively search using partial prefixes of that Invoice Number, verifying that
         each additional digit narrows the result set and that the final search (full
         Invoice Number) yields exactly one record.
    """

    # Navigate to Recent Sales page
    _log("Navigating to Recent Sales page (/salesdata/).")
    page.goto(url("/salesdata/"), wait_until="domcontentloaded")
    page.wait_for_url("**/salesdata/**", timeout=30_000)
    _log(f"Arrived on: {page.url}")

    # 1–3. Verify default filters: Market Actor, Status, Invoice Date = "All"
    _log('Verifying Market Actor, Status, and Invoice Date are set to "All".')

    # Market Actor (#id_market_actor) = All
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

    # Status (#id_status) = All
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

    # Invoice Date (#id_invoice_date) = All
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
        "Expected Invoice Date selection to be 'All', "
        f"got {selected_invoice_date!r}."
    )
    _log(f"Invoice Date confirmed: {selected_invoice_date!r}")

    # 5. Initial search with NO Invoice Number (blank field)
    _log("Performing initial search with blank Invoice Number field.")
    total_record_count = search_by_invoice_number(page, value="")
    if total_record_count == 0:
        pytest.skip(
            "No records found for initial search with blank Invoice Number (Total Record Count 0)."
        )
    _log(f"Initial Total Record Count (blank Invoice Number): {total_record_count}.")

    # 8. Locate the Invoice Number column header (for completeness / stability)
    _log("Locating Invoice Number column header link (sort control).")
    invoice_header_link = page.get_by_role("link", name="Invoice number", exact=True)
    if invoice_header_link.count() == 0:
        invoice_header_link = page.locator("a[href*='sort=-invoice_number']")

    assert invoice_header_link.count() >= 1, (
        "Could not find the Invoice Number column header link "
        "(by role name 'Invoice number' or href*='sort=-invoice_number')."
    )
    invoice_header_link = invoice_header_link.first
    invoice_header_link.wait_for(state="visible", timeout=30_000)
    _highlight(page, invoice_header_link, color="#0a84ff")

    # 6 & 9. Get first-row Invoice Number after unfiltered search
    _log("Locating first-row Invoice Number cell after blank search.")
    first_invoice_cell = page.locator("td.invoice_number, td.invoice-number").first
    try:
        first_invoice_cell.wait_for(state="visible", timeout=30_000)
    except Exception:
        raise AssertionError(
            "Expected at least one Invoice Number cell (td.invoice_number or td.invoice-number) "
            "to be visible after initial (blank) search, but none was found."
        )

    _highlight(page, first_invoice_cell, color="#ff9f0a")
    full_invoice_number = first_invoice_cell.inner_text().strip()
    assert full_invoice_number, (
        "First Invoice Number cell is empty; cannot proceed with digit iteration test."
    )
    _log(f"First-row full Invoice Number value: {full_invoice_number!r}")

    # 10. Iteratively filter by each digit of the first Invoice Number
    #     (blank -> first digit -> first 2 digits -> ... -> full number)
    assert total_record_count > 0, "Expected initial Total Record Count to be > 0."

    for i in range(1, len(full_invoice_number) + 1):
        partial_value = full_invoice_number[:i]
        _log(
            f"Iteration {i}/{len(full_invoice_number)}: searching with partial Invoice Number "
            f"prefix {partial_value!r}."
        )

        updated_record_count = search_by_invoice_number(page, value=partial_value)

        # Strict decrease for all iterations EXCEPT the final one
        if i < len(full_invoice_number):
            assert (
                    updated_record_count < total_record_count
            ), (
                f"Expected updated_record_count < total_record_count for partial prefix "
                f"{partial_value!r}, but got updated_record_count={updated_record_count}, "
                f"total_record_count={total_record_count}."
            )
        else:
            # FINAL ITERATION: full invoice number must yield EXACTLY ONE record
            assert updated_record_count == 1, (
                f"Expected Total Record Count to be 1 after final prefix "
                f"{partial_value!r}, but got {updated_record_count}."
            )

        total_record_count = updated_record_count

    # 10n. On the last iteration (full invoice number), verify the final count == 1
    assert total_record_count == 1, (
        "Expected Total Record Count to be 1 after filtering by the full Invoice Number "
        f"{full_invoice_number!r}, but got {total_record_count}."
    )
    _log(
        "PASSED: Invoice Number filter progressively narrowed results for each digit of the "
        f"first-row Invoice Number ({full_invoice_number!r}) and the final Total Record Count was 1."
    )