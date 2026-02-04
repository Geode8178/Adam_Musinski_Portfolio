"""Test the sales summary section of a Market Actor card found on the Incentive Connect
dashboard. This will test the Latest Invoice Date widget."""
from urllib.parse import parse_qs, urlparse

from config.settings import url

def test_dashboard_sales_summary_section(page):

    # User-focused, single login is used, so there is no back and forth between tests.
    page.goto(url("/dashboard/"), wait_until="domcontentloaded")
    if not page.url.endswith("/dashboard/"):
        raise Exception("Failed to load the Dashboard page.")

    # Locate the first available Market Actor card.
    first_market_actor_card = page.locator("div.card:has(h2.card-title)").first
    first_market_actor_card.wait_for(state="visible", timeout=30_000)

    # Capture the first Market Actor name.
    market_actor_name = (
        first_market_actor_card.locator("h2.card-title").first.inner_text().strip()
    )
    assert market_actor_name, (
        "Expected the first Market Actor card to have a visible name."
    )
    print(f"Selected Market Actor: {market_actor_name}")

    # Find the "Sales Records Summary" title INSIDE the first Market Actor card.
    sales_records_summary_title = first_market_actor_card.locator(
        "h3.card-title.rose-primary-text",
        has_text="Sales Records Summary",
    ).first
    sales_records_summary_title.wait_for(state="visible", timeout=30_000)

    # Optional: assert the exact text we found (helps debugging if there are similar headings).
    assert sales_records_summary_title.inner_text().strip() == "Sales Records Summary"
    print("Found section: Sales Records Summary")

    # Find the "Latest Invoice Date" widget in the Sales Records Summary section.
    latest_invoice_date_label = first_market_actor_card.locator(
        "span.me-2.card-link.text-400",
        has_text="Latest Invoice Date",
    ).first
    latest_invoice_date_label.wait_for(state="visible", timeout=30_000)

    assert latest_invoice_date_label.inner_text().strip() == "Latest Invoice Date"
    print("Found widget: Latest Invoice Date")

    latest_invoice_date_label.scroll_into_view_if_needed()

    # Highlight the "Latest Invoice Date" label so the user can clearly see it during the run.
    latest_invoice_date_label.evaluate(
        """
        (el) => {
          el.style.outline = '3px solid #ff3b30';
          el.style.outlineOffset = '3px';
          el.style.background = 'rgba(255, 59, 48, 0.15)';
          el.style.borderRadius = '4px';
        }
        """
    )
    page.wait_for_timeout(1200)

    # Find the info-circle icon (tooltip trigger) in the same flex row as the label.
    latest_invoice_date_row = latest_invoice_date_label.locator(
        "xpath=ancestor::div[contains(@class,'d-flex') and contains(@class,'flex-row')][1]"
    ).first
    latest_invoice_date_row.wait_for(state="visible", timeout=30_000)

    latest_invoice_date_info_icon = latest_invoice_date_row.locator(
        'span[data-bs-toggle="tooltip"] i.bi.bi-info-circle'
    ).first
    latest_invoice_date_info_icon.wait_for(state="visible", timeout=30_000)

    # Optional: verify the tooltip text on the host <span>.
    tooltip_host_span = latest_invoice_date_info_icon.locator(
        "xpath=ancestor::span[1]"
    ).first
    tooltip_text = (tooltip_host_span.get_attribute("data-bs-title") or "").strip()
    assert tooltip_text == "Date of latest sale received from N/A."

    # Hover to display the tooltip in the browser during the run.
    tooltip_host_span.hover()
    page.wait_for_timeout(750)

    # Find the "Latest Invoice Date" hyperlink and record its displayed date.
    latest_invoice_date_widget = first_market_actor_card.locator(
        "div:has(span.me-2.card-link.text-400:has-text('Latest Invoice Date'))"
        ":has(a[href^='/salesdata/'][href*='enable_date_range=on'])"
    ).first
    latest_invoice_date_widget.wait_for(state="visible", timeout=30_000)

    latest_invoice_date_link = latest_invoice_date_widget.locator(
        "a[href^='/salesdata/']"
        "[href*='enable_date_range=on']"
        "[href*='invoice_start_date=']"
        "[href*='invoice_end_date=']"
        "[href*='market_actor=0']"
    ).first
    latest_invoice_date_link.wait_for(state="visible", timeout=30_000)

    latest_invoice_date = latest_invoice_date_link.inner_text().strip()
    assert latest_invoice_date, "Latest Invoice Date link should display a date string."
    print(f"Latest Invoice Date: {latest_invoice_date}")

    # Derive expected destination from href BEFORE clicking (avoid stale locator after navigation).
    href = (latest_invoice_date_link.get_attribute("href") or "").strip()
    assert href, "Latest Invoice Date link should have a non-empty href."

    expected_url = url(href)
    print(f"Expecting navigation to: {expected_url}")

    # Click once, then wait for navigation.
    latest_invoice_date_link.click()
    page.wait_for_url(expected_url, timeout=30_000)
    assert page.url == expected_url, (
        f"Expected URL {expected_url!r}, but was {page.url!r}"
    )

    # Verify the Market Actor field is == to market_actor_name.
    market_actor_dropdown = page.locator("#id_market_actor").first
    market_actor_dropdown.wait_for(state="visible", timeout=30_000)

    selected_market_actor_name = (
        market_actor_dropdown.locator("option:checked").first.inner_text().strip()
    )
    assert selected_market_actor_name == market_actor_name, (
        f"Market Actor field should be {market_actor_name!r}, but was {selected_market_actor_name!r}"
    )

    # Verify the Status field is set to "All".
    status_dropdown = page.locator("#id_status").first
    status_dropdown.wait_for(state="visible", timeout=30_000)

    selected_status = (
        status_dropdown.locator("option:checked").first.inner_text().strip()
    )
    assert selected_status == "All", (
        f"Status field should be 'All', but was {selected_status!r}"
    )

    # Verify the "Select specific date range" boolean is checked.
    enable_date_range_checkbox = page.locator("#enable-date-range-invoice").first
    enable_date_range_checkbox.wait_for(state="visible", timeout=30_000)
    assert enable_date_range_checkbox.is_checked(), (
        "Expected 'Select specific date range' to be checked for Invoice Date range."
    )

    # ... existing code ...

    qs = parse_qs(urlparse(page.url).query)
    expected_invoice_start_date = (qs.get("invoice_start_date") or [""])[0]
    expected_invoice_end_date = (qs.get("invoice_end_date") or [""])[0]
    assert expected_invoice_start_date, "Expected invoice_start_date to be present in the URL query string."
    assert expected_invoice_end_date, "Expected invoice_end_date to be present in the URL query string."

    # Verify Invoice Start Date field == expected (and matches latest_invoice_date).
    invoice_start_date_input = page.locator("#invoice_start_date").first
    invoice_start_date_input.wait_for(state="visible", timeout=30_000)
    invoice_start_date_value = invoice_start_date_input.input_value().strip()
    assert invoice_start_date_value == expected_invoice_start_date, (
        f"Invoice Start Date should be {expected_invoice_start_date!r}, but was {invoice_start_date_value!r}"
    )
    assert invoice_start_date_value == expected_invoice_end_date, (
        f"Invoice Start Date should match Invoice End Date, but was {invoice_start_date_value!r} vs {expected_invoice_end_date!r}"
    )

    # Verify Invoice End Date field == expected (and matches latest_invoice_date).
    invoice_end_date_input = page.locator("#invoice_end_date").first
    invoice_end_date_input.wait_for(state="visible", timeout=30_000)
    invoice_end_date_value = invoice_end_date_input.input_value().strip()
    assert invoice_end_date_value == expected_invoice_end_date, (
        f"Invoice End Date should be {expected_invoice_end_date!r}, but was {invoice_end_date_value!r}"
    )

    # Verify the input fields match the date we captured from the widget link.
    # NOTE: latest_invoice_date is the dashboard link text; it may be formatted differently than YYYY-MM-DD.
    # If it is already YYYY-MM-DD, this will pass; otherwise, we rely on the URL-driven assertions above.
    if latest_invoice_date == expected_invoice_start_date:
        assert invoice_start_date_value == latest_invoice_date
        assert invoice_end_date_value == latest_invoice_date

    # Move to the Invoice Date column and click once to sort.
    invoice_date_sort_link = page.locator("a:has-text('Invoice date')").first
    invoice_date_sort_link.wait_for(state="visible", timeout=30_000)
    invoice_date_sort_link.click()

    # Validate the invoice date from the first record row found matches the expected date.
    first_invoice_date_cell = page.locator("td.invoice_date").first
    first_invoice_date_cell.wait_for(state="visible", timeout=30_000)

    first_invoice_date_text = first_invoice_date_cell.inner_text().strip()
    assert first_invoice_date_text, "Expected the first row to have a visible invoice date."

    from datetime import datetime

    # Example UI text: "Nov. 26, 2025" (note the dot after the month).
    normalized = first_invoice_date_text.replace(".", "")
    parsed = datetime.strptime(normalized, "%b %d, %Y").date()
    first_invoice_date_iso = parsed.isoformat()

    assert first_invoice_date_iso == expected_invoice_start_date, (
        "First row invoice date should match the selected invoice date range, "
        f"but was {first_invoice_date_iso!r} and expected {expected_invoice_start_date!r}"
    )









