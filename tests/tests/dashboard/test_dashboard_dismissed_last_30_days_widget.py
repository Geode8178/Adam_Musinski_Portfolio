"""Test the sales summary section of a Market Actor card found on the Incentive Connect
   dashboard. This will test the Dismissed Last 30 Days widget."""

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

    # Find the "Dismissed Last 30 Days" widget in the Sales Records Summary section.
    dismissed_last_30_days = first_market_actor_card.locator(
        "span.me-2.card-link.text-400",
        has_text="Dismissed Last 30 Days",
    ).first
    dismissed_last_30_days.wait_for(state="visible", timeout=30_000)

    assert dismissed_last_30_days.inner_text().strip() == "Dismissed Last 30 Days"
    print("Found widget: Dismissed Last 30 Days")

    dismissed_last_30_days.scroll_into_view_if_needed()

    # Highlight the "Dismissed Last 30 Days" label so the user can clearly see it during the run.
    dismissed_last_30_days.evaluate(
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
    dismissed_last_30_days_row = dismissed_last_30_days.locator(
        "xpath=ancestor::div[contains(@class,'d-flex') and contains(@class,'flex-row')][1]"
    ).first
    dismissed_last_30_days_row.wait_for(state="visible", timeout=30_000)

    dismissed_last_30_days_info_icon = dismissed_last_30_days_row.locator(
        'span[data-bs-toggle="tooltip"] i.bi.bi-info-circle'
    ).first
    dismissed_last_30_days_info_icon.wait_for(state="visible", timeout=30_000)

    # Optional: verify the tooltip text on the host <span>.
    tooltip_host_span = dismissed_last_30_days_info_icon.locator("xpath=ancestor::span[1]").first
    tooltip_text = (tooltip_host_span.get_attribute("data-bs-title") or "").strip()
    assert tooltip_text == "Records that have been archived because they can’t be completed or exported."

    # Hover to display the tooltip in the browser during the run.
    tooltip_host_span.hover()
    page.wait_for_timeout(750)

    # Find the "Dismissed Last 30 Days" counter (hyperlink) and record its value.
    # Scope the counter-link to the widget container instead of filtering by link text.
    dismissed_last_30_days_widget = first_market_actor_card.locator(
        "div:has(span.me-2.card-link.text-400:has-text('Dismissed Last 30 Days'))"
        ":has(a[href*='status=DISMISSED'][href*='dismissed_date=30'])"
    ).first
    dismissed_last_30_days_widget.wait_for(state="visible", timeout=30_000)

    dismissed_last_30_days_counter_link = dismissed_last_30_days_widget.locator(
        "a[href*='status=DISMISSED'][href*='dismissed_date=30']"
    ).first
    dismissed_last_30_days_counter_link.wait_for(state="visible", timeout=30_000)

    dismissed_last_30_days_counter = dismissed_last_30_days_counter_link.inner_text().strip()
    assert dismissed_last_30_days_counter.isdigit(), (
        "Dismissed Last 30 Days counter should be a non-negative integer string, "
        f"but was {dismissed_last_30_days_counter!r}"
    )
    print(f"Dismissed Last 30 Days counter: {dismissed_last_30_days_counter}")

    # Click the counter-link and verify the destination URL.
    dismissed_last_30_days_counter_link.click()

    expected_url = (
        "https://ic-staging.staging.aws.incentiveconnect.com/"
        "salesdata/?status=DISMISSED&dismissed_date=30&market_actor=0"
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

    # Verify the Status field is set to "Dismissed".
    status_dropdown = page.locator("#id_status").first
    status_dropdown.wait_for(state="visible", timeout=30_000)

    selected_status = (
        status_dropdown.locator("option:checked").first.inner_text().strip()
    )
    assert selected_status == "Dismissed", (
        f"Status field should be 'Dismissed', but was {selected_status!r}"
    )

    # Verify the Dismissed Date field is set to "Last 30 Days".
    dismissed_date_dropdown = page.locator("#id_dismissed_date").first
    dismissed_date_dropdown.wait_for(state="visible", timeout=30_000)

    selected_dismissed_date = (
        dismissed_date_dropdown.locator("option:checked").first.inner_text().strip()
    )
    assert selected_dismissed_date == "Last 30 Days", (
        f"Dismissed Date field should be 'Last 30 Days', but was {selected_dismissed_date!r}"
    )

    # Find the Total Record Count and compare it to exported_last_30_days_counter.
    total_record_count_el = page.locator('p:has-text("Total Record Count")').first
    total_record_count_el.wait_for(state="visible", timeout=30_000)

    total_record_count_text = total_record_count_el.inner_text().strip()
    assert total_record_count_text.startswith("Total Record Count"), (
        f"Unexpected Total Record Count text: {total_record_count_text!r}"
    )

    total_record_count = total_record_count_text.replace(
        "Total Record Count", ""
    ).strip()
    assert total_record_count.isdigit(), (
        f"Total Record Count should end with an integer, but was {total_record_count_text!r}"
    )

    assert int(total_record_count) == int(dismissed_last_30_days_counter), (
        "Total Record Count should match Dismissed Last 30 Days counter, "
        f"but Total Record Count was {total_record_count} and Dismissed Last 30 Days was {dismissed_last_30_days_counter}"
    )

    print(f"PASSED: Total Record Count: {total_record_count}, Dismissed Last 30 Days: {dismissed_last_30_days_counter}")







