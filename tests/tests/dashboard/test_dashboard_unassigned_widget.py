"""Test the sales summary section of a Market Actor card found on the Incentive Connect
dashboard. This will test the Unassigned widget."""

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

    # Find the "Unassigned" widget in the Sales Records Summary section.
    unassigned = first_market_actor_card.locator(
        "span.me-2.card-link.text-400",
        has_text="Unassigned",
    ).first
    unassigned.wait_for(state="visible", timeout=30_000)

    assert unassigned.inner_text().strip() == "Unassigned"
    print("Found widget: Unassigned")

    unassigned.scroll_into_view_if_needed()

    # Highlight the "Unassigned" label so the user can clearly see it during the run.
    unassigned.evaluate(
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

    # Row container for "Unassigned"
    unassigned_row = first_market_actor_card.locator(
        "div.d-flex.flex-row:has(span.me-2.card-link.text-400:has-text('Unassigned'))"
    ).first
    unassigned_row.wait_for(state="visible", timeout=30_000)
    unassigned_row.scroll_into_view_if_needed()

    # Tooltip host <span> (the element that actually owns data-bs-title)
    tooltip_host_span = unassigned_row.locator(
        "span[data-bs-toggle='tooltip']"
        "[data-bs-title='Records that did not match a program.']"
    ).first
    tooltip_host_span.wait_for(state="attached", timeout=30_000)
    tooltip_host_span.wait_for(state="visible", timeout=30_000)

    # Sanity: confirm the icon is there too
    unassigned_info_icon = tooltip_host_span.locator("i.bi.bi-info-circle").first
    unassigned_info_icon.wait_for(state="visible", timeout=30_000)

    # Verify tooltip text
    tooltip_text = (tooltip_host_span.get_attribute("data-bs-title") or "").strip()
    assert tooltip_text == "Records that did not match a program."

    # Hover to display the tooltip during the run
    tooltip_host_span.hover()
    page.wait_for_timeout(750)

    # Find the "Unassigned" counter (hyperlink) and record its value.
    # Scope the counter-link to the widget container instead of filtering by link text.
    unassigned_widget = first_market_actor_card.locator(
        "div:has(span.me-2.card-link.text-400:has-text('Unassigned'))"
        ":has(a[href*='status=UNASSIGNED'])"
    ).first
    unassigned_widget.wait_for(state="visible", timeout=30_000)

    unassigned_counter_link = unassigned_widget.locator(
        "a[href*='status=UNASSIGNED']"
    ).first
    unassigned_counter_link.wait_for(state="visible", timeout=30_000)

    unassigned_counter = unassigned_counter_link.inner_text().strip()
    assert unassigned_counter.isdigit(), (
        "Unassigned counter should be a non-negative integer string, "
        f"but was {unassigned_counter!r}"
    )
    print(f"Unassigned counter: {unassigned_counter}")

    # Click the counter-link.
    unassigned_counter_link.click()

    expected_url = (
        "https://ic-staging.staging.aws.incentiveconnect.com/"
        "salesdata/?status=UNASSIGNED&market_actor=0"
    )
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

    # Verify the Status field is set to "Unassigned".
    status_dropdown = page.locator("#id_status").first
    status_dropdown.wait_for(state="visible", timeout=30_000)

    selected_status = (
        status_dropdown.locator("option:checked").first.inner_text().strip()
    )
    assert selected_status == "Unassigned", (
        f"Status field should be 'Unassigned', but was {selected_status!r}"
    )

    selected_status_value = (
        status_dropdown.locator("option:checked").first.get_attribute("value") or ""
    ).strip()
    assert selected_status_value == "UNASSIGNED", (
        f"Status value should be 'UNASSIGNED', but was {selected_status_value!r}"
    )

    # Verify the Invoice Date field is set to "All".
    invoice_date_dropdown = page.locator("#id_invoice_date").first
    invoice_date_dropdown.wait_for(state="visible", timeout=30_000)

    selected_invoice_date = (
        invoice_date_dropdown.locator("option:checked").first.inner_text().strip()
    )
    assert selected_invoice_date == "All", (
        f"Invoice Date field should be 'All', but was {selected_invoice_date!r}"
    )

    # Find the Total Record Count and compare it to unassigned_counter.
    total_record_count_el = page.locator('p:has-text("Total Record Count")').first
    total_record_count_el.wait_for(state="visible", timeout=30_000)

    total_record_count_text = total_record_count_el.inner_text().strip()
    assert total_record_count_text.startswith("Total Record Count"), (
        f"Unexpected Total Record Count text: {total_record_count_text!r}"
    )

    total_record_count = total_record_count_text.replace("Total Record Count", "").strip()
    assert total_record_count.isdigit(), (
        f"Total Record Count should end with an integer, but was {total_record_count_text!r}"
    )

    assert int(total_record_count) == int(unassigned_counter), (
        "Total Record Count should match Unassigned counter, "
        f"but Total Record Count was {total_record_count} and Unassigned was {unassigned_counter}"
    )

    # ... existing code ...
