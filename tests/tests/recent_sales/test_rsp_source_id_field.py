from __future__ import annotations

import re

import pytest
from playwright.sync_api import Locator, Page

from config.settings import url


# Helper to log messages for this specific test
def _log(msg: str) -> None:
    print(f"[RSP][Source ID Field] {msg}")


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

    # Correct regex: \s for whitespace, (\d+) for digits
    match = re.search(r"Total Record Count\s+(\d+)", text)
    assert match, (
        "Could not parse Total Record Count from text: "
        f"{text!r}. Expected format like 'Total Record Count 123'."
    )
    count = int(match.group(1))
    _log(f"Parsed Total Record Count = {count} from: {text!r}")
    return count


def search_by_source_id(page: Page, *, value: str) -> int:
    """
    Fill the Source ID field, click Search, wait for results, return record count.
    """
    _log(f"Searching with Source ID field = {value!r}.")

    source_input = page.locator("#id_source_id")
    assert source_input.count() == 1, "Expected a single Source ID input (#id_source_id)."
    source_input.wait_for(state="visible", timeout=30_000)
    _highlight(page, source_input, color="#0a84ff")

    source_input.fill("")
    if value:
        source_input.type(value)

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
    first_source_cell_locator = page.locator(
        "td.source_id, td.source-id, td.iris_source_id, td.iris-source-id"
    ).first

    _log("Waiting for either a Source ID row or 'Total Record Count 0'.")
    try:
        first_source_cell_locator.wait_for(state="visible", timeout=10_000)
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
                "No Source ID result row was found and the empty-state 'Total Record Count 0' "
                "was not visible. The page may not have rendered results correctly."
            )

    # Regardless of whether there are rows or 0 rows, parse the count deterministically
    return get_total_record_count(page)


def build_alternating_case_prefix(base: str, length: int) -> str:
    """
    Build a prefix of `base` (up to `length`) where alphabetical characters
    alternate between lower/upper case, in order of alphabetic characters.

    Non-alphabetical chars (spaces, dashes, digits) are preserved as-is.
    """
    prefix = base[:length]
    result_chars = []
    alpha_index = 0

    for ch in prefix:
        if ch.isalpha():
            if alpha_index % 2 == 0:
                result_chars.append(ch.lower())
            else:
                result_chars.append(ch.upper())
            alpha_index += 1
        else:
            result_chars.append(ch)

    transformed = "".join(result_chars)
    _log(f"Alternating-case prefix for base={base!r}, length={length}: {transformed!r}")
    return transformed


@pytest.mark.rsp
@pytest.mark.ui
@pytest.mark.source_id
def test_rsp_source_id_field(page: Page) -> None:
    """
    Verify incremental narrowing behavior and case-insensitive handling of the
    Iris Source ID filter on Recent Sales.

    Behavior matches the Model test:
      1. Navigate to /salesdata/.
      2. Verify Market Actor = "All".
      3. Verify Status = "All".
      4. Verify Invoice Date = "All".
      5. Perform initial search with NO Source ID (blank).
      6. Record Total Record Count and first-row Iris Source ID value.
      7. Iteratively search using alternating-case prefixes of that value, verifying that:
           - Total Record Count never increases as the prefix grows.
           - After the full value is entered:
               * If Total Record Count <= 25, all rows' Iris Source ID values match the
                 first-row value (case-insensitive).
               * If Total Record Count > 25, we still pass based on monotonic narrowing
                 and demonstrated case-insensitive behavior.
    """

    # ------------------------------------------------------------------
    # Navigate to Recent Sales page
    # ------------------------------------------------------------------
    _log("Navigating to Recent Sales page (/salesdata/).")
    page.goto(url("/salesdata/"), wait_until="domcontentloaded")
    page.wait_for_url("**/salesdata/**", timeout=30_000)
    _log(f"Arrived on: {page.url}")

    # ------------------------------------------------------------------
    # Verify default filters: Market Actor, Status, Invoice Date = "All"
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Initial search with NO Source ID (blank field)
    # ------------------------------------------------------------------
    _log("Performing initial search with blank Source ID field.")
    total_record_count = search_by_source_id(page, value="")
    if total_record_count == 0:
        pytest.skip(
            "No records found for initial search with blank Source ID (Total Record Count 0)."
        )
    _log(f"Initial Total Record Count (blank Source ID): {total_record_count}.")

    # ------------------------------------------------------------------
    # Locate Iris Source ID column header (for stability / visibility)
    # ------------------------------------------------------------------
    _log("Locating Iris Source ID column header link (sort control).")
    source_header_link = page.get_by_role("link", name="Iris Source ID", exact=True)
    if source_header_link.count() == 0:
        source_header_link = page.locator("a[href*='sort=source_id']")

    assert source_header_link.count() >= 1, (
        "Could not find the Iris Source ID column header link "
        "(by role name 'Iris Source ID' or href*='sort=source_id')."
    )
    source_header_link = source_header_link.first
    source_header_link.wait_for(state="visible", timeout=30_000)
    _highlight(page, source_header_link, color="#0a84ff")

    # ------------------------------------------------------------------
    # Get first-row Source ID after unfiltered search
    # ------------------------------------------------------------------
    _log("Locating first-row Source ID cell after blank search.")
    first_source_cell = page.locator(
        "td.source_id, td.source-id, td.iris_source_id, td.iris-source-id"
    ).first
    try:
        first_source_cell.wait_for(state="visible", timeout=30_000)
    except Exception:
        raise AssertionError(
            "Expected at least one Source ID cell (td.source_id/source-id or td.iris_source_id/iris-source-id) "
            "to be visible after initial (blank) search, but none was found."
        )

    _highlight(page, first_source_cell, color="#ff9f0a")
    full_source_id_value = first_source_cell.inner_text().strip()
    assert full_source_id_value, (
        "First Source ID cell is empty; cannot proceed with prefix iteration test."
    )
    _log(f"First-row full Source ID value: {full_source_id_value!r}")

    # ------------------------------------------------------------------
    # Iteratively filter by each (alternating-case) prefix of Source ID
    # ------------------------------------------------------------------
    assert total_record_count > 0, "Expected initial Total Record Count to be > 0."

    for i in range(1, len(full_source_id_value) + 1):
        partial_value = build_alternating_case_prefix(full_source_id_value, i)
        _log(
            f"Iteration {i}/{len(full_source_id_value)}: searching with "
            f"alternating-case Source ID prefix {partial_value!r}."
        )

        updated_record_count = search_by_source_id(page, value=partial_value)

        # We expect the result set to never grow as the prefix becomes more specific
        assert (
            updated_record_count <= total_record_count
        ), (
            "Expected updated_record_count to be <= previous total_record_count "
            f"for prefix {partial_value!r}, but got "
            f"updated_record_count={updated_record_count}, total_record_count={total_record_count}."
        )

        _log(
            f"After prefix {partial_value!r}: Total Record Count = {updated_record_count} "
            f"(previously {total_record_count})."
        )
        total_record_count = updated_record_count

    # ------------------------------------------------------------------
    # Final validation:
    # - Always require at least one result
    # - If Total Record Count <= 25, verify all Source ID values match first-row Source ID
    #   (case-insensitive).
    # - If Total Record Count > 25, pass based on monotonic narrowing and
    #   case-insensitive behavior without asserting per-row equality.
    # ------------------------------------------------------------------
    assert total_record_count > 0, (
        "Expected at least one result for full Source ID value "
        f"{full_source_id_value!r}, but got Total Record Count 0."
    )

    if total_record_count <= 25:
        _log(
            f"Final Total Record Count for full Source ID (alt-case) is {total_record_count} "
            "(<= 25) – verifying all Source ID cells match first-row Source ID."
        )

        all_source_cells = page.locator(
            "td.source_id, td.source-id, td.iris_source_id, td.iris-source-id"
        )
        visible_count = all_source_cells.count()
        assert visible_count >= total_record_count, (
            "Expected at least as many Source ID cells on the page as the Total Record Count "
            f"(visible_count={visible_count}, total_record_count={total_record_count})."
        )

        normalized_expected = full_source_id_value.casefold()

        for idx in range(total_record_count):
            cell = all_source_cells.nth(idx)
            cell.wait_for(state="visible", timeout=30_000)
            text = cell.inner_text().strip()
            assert text, f"Expected non-empty Source ID cell text at row {idx}, got {text!r}."
            assert text.casefold() == normalized_expected, (
                f"Expected Source ID at row {idx} to match first-row Source ID "
                f"{full_source_id_value!r} (case-insensitive), but got {text!r}."
            )

        _log(
            "All Source ID cells in the final result set (<= 25 rows) match the first-row "
            f"Source ID value {full_source_id_value!r} (case-insensitive)."
        )
    else:
        _log(
            "Final Total Record Count is > 25; skipping exhaustive per-row Source ID equality "
            "checks. Test passes based on monotonic narrowing and demonstrated "
            "case-insensitive behavior during prefix iterations."
        )

    _log(
        "PASSED: Source ID filter handled alternating-case prefixes correctly, "
        "monotonically narrowed (or preserved) the result set, and the final result "
        "set satisfied the size/equality rules for Iris Source ID."
    )
