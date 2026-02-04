"""Validate UI Requirements: Program Widget features are correct for internal users.
Internal Users views are all the same in this context.
"""

import re
from config.settings import url

def test_dashboard_program_widget_features(page):

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

    # Find the first program widget INSIDE that card.
    first_program_widget = first_market_actor_card.locator("h5.rose-primary-text").first
    first_program_widget.wait_for(state="visible", timeout=30_000)

    # Capture the program name from the selected program widget.
    program_widget_name = first_program_widget.inner_text().strip()
    assert program_widget_name, (
        "Expected the first Market Actor card to have at least one program widget."
    )
    print(f"Selected Program Widget: {program_widget_name}")

    first_program_widget_name = first_program_widget.inner_text().strip()
    assert first_program_widget_name, (
        "Expected the first Market Actor card to have at least one program widget."
    )
    print(
        f"First program widget (first Market Actor card): {first_program_widget_name}"
    )

    # Verify the program name is visible in the selected program widget.
    first_market_actor_card.locator(
        "h5.rose-primary-text",
        has_text=first_program_widget_name,
    ).first.wait_for(state="visible", timeout=30_000)

    def _assert_row_tooltip_and_value(
        label_text: str,
        expected_tooltip: str | None,
        *,
        expect_numeric: bool,
        expected_tooltips: tuple[str, ...] = (),
    ) -> str:
        row = first_market_actor_card.locator(
            f'li.list-group-item:has-text("{label_text}")'
        ).first
        row.wait_for(state="visible", timeout=30_000)

        info_icon = row.locator(
            'span[data-bs-toggle="tooltip"] i.bi.bi-info-circle'
        ).first
        info_icon.wait_for(state="visible", timeout=30_000)

        tooltip_host_span = info_icon.locator("xpath=ancestor::span[1]").first
        tooltip_text = (tooltip_host_span.get_attribute("data-bs-title") or "").strip()

        acceptable_tooltips = tuple(t.strip() for t in expected_tooltips if t and t.strip())
        if expected_tooltip and expected_tooltip.strip():
            acceptable_tooltips = (expected_tooltip.strip(),) + acceptable_tooltips

        assert tooltip_text in acceptable_tooltips, (
            f"Unexpected tooltip text for {label_text!r}: {tooltip_text!r}. "
            f"Expected one of: {acceptable_tooltips!r}"
        )

        tooltip_host_span.hover()

        if expect_numeric:
            value_el = row.locator("p.ms-auto.mb-0.rose-primary-text").first
            value_el.wait_for(state="visible", timeout=30_000)
            value_text = value_el.inner_text().strip()
            assert value_text.isdigit(), (
                f"{label_text} value should be a non-negative integer string, but was {value_text!r}"
            )
            return value_text

        # Date-style value (e.g., Last Exported Date) uses a span, not a p.
        value_el = row.locator("span.fw-bold.ms-auto").first
        value_el.wait_for(state="visible", timeout=30_000)
        value_text = value_el.inner_text().strip()

        assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", value_text), (
            f"{label_text} value should be a date in mm/dd/yyyy format, but was {value_text!r}"
        )
        return value_text

    # Store STRING values for later comparisons in this test/file.
    program_widget_rfe_counter = _assert_row_tooltip_and_value(
        "Ready For Export",
        "Records that are complete and ready to batch.",
        expect_numeric=True,
    )

    program_widget_incomplete_counter = _assert_row_tooltip_and_value(
        "Incomplete Records",
        "Records that are missing program-required data.",
        expect_numeric=True,
    )

    program_widget_expired_counter = _assert_row_tooltip_and_value(
        "Expired Records",
        None,
        expect_numeric=True,
        expected_tooltips=(
            "The sale does not match an active program's eligibility parameters, e.g., sales date, equipment/product type, and/or location.",
            "The sales does not match an active program's eligibility parameters, e.g., sales date, equipment/product type, and/or location.",
        ),
    )

    program_widget_last_export_date = _assert_row_tooltip_and_value(
        "Last Exported Date",
        "Records that have been previously batched.",
        expect_numeric=False,
    )

    # Verify program_widget_last_export_date is formatted as mm/dd/yyyy.
    assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", program_widget_last_export_date), (
        "program_widget_last_export_date should be formatted as mm/dd/yyyy, "
        f"but was {program_widget_last_export_date!r}"
    )

    # Click on the Recent Sales Page Link in the side panel menu.
    recent_sales_link = page.locator('a.nav-link.ps-4[href="/salesdata/"]').first
    recent_sales_link.wait_for(state="visible", timeout=30_000)
    recent_sales_link.click()

    # Verify the program_widget_rfe_counter is equal to the number of records displayed.
    # Set the Market Actor dropdown equal to the market_actor_name.
    market_actor_dropdown = page.locator("#id_market_actor").first
    market_actor_dropdown.wait_for(state="visible", timeout=30_000)
    market_actor_dropdown.select_option(label=market_actor_name)

    # Verify the dropdown actually selected the right Market Actor.
    selected_market_actor = (
        market_actor_dropdown.locator("option:checked").inner_text().strip()
    )
    assert selected_market_actor == market_actor_name, (
        f"Market Actor dropdown should be set to {market_actor_name!r}, but was {selected_market_actor!r}"
    )

    # Set the Status dropdown to 'Ready'.
    status_dropdown = page.locator("#id_status").first
    status_dropdown.wait_for(state="visible", timeout=30_000)
    status_dropdown.select_option(label="Ready")

    # Verify the dropdown actually selected 'Ready'.
    selected_status = status_dropdown.locator("option:checked").inner_text().strip()
    assert selected_status == "Ready", (
        f"Status dropdown should be set to 'Ready', but was {selected_status!r}"
    )

    # Set the Assigned Program dropdown to the program_widget_name.
    assigned_program_dropdown = page.locator("#id_program").first
    assigned_program_dropdown.wait_for(state="visible", timeout=30_000)
    assigned_program_dropdown.select_option(label=program_widget_name)

    # Verify the dropdown actually selected the right program.
    selected_program = (
        assigned_program_dropdown.locator("option:checked").inner_text().strip()
    )
    assert selected_program == program_widget_name, (
        f"Assigned Program dropdown should be set to {program_widget_name!r}, but was {selected_program!r}"
    )

    # Verify the counter for the Ready For Export data point is equal to the number of sales records listed.
    # Click Search button.
    search_button = page.locator('button.btn.btn-primary:has-text("Search")').first
    search_button.wait_for(state="visible", timeout=30_000)
    search_button.click()

    # Record the Total Record Count.
    total_record_count_el = page.locator('p:has-text("Total Record Count")').first
    total_record_count_el.wait_for(state="visible", timeout=30_000)

    total_record_count_text = total_record_count_el.inner_text().strip()
    match = re.search(r"Total Record Count\s+(\d+)", total_record_count_text)
    assert match, (
        f"Could not parse Total Record Count from: {total_record_count_text!r}"
    )

    total_record_counter = int(match.group(1))

    assert total_record_counter == int(program_widget_rfe_counter), (
        f"Total Record Count should be {program_widget_rfe_counter}, but was {total_record_counter}"
    )

    # Verify the program_widget_incomplete_counter is equal to the number of records displayed.
        # Set the Status dropdown to 'Incomplete Requirements'.
    status_dropdown = page.locator("#id_status").first
    status_dropdown.wait_for(state="visible", timeout=30_000)
    status_dropdown.select_option(label="Incomplete Requirements")

    # Verify the counter for the Incomplete Records data point is equal to the number of sales records listed.
        # Click Search button.
    search_button = page.locator('button.btn.btn-primary:has-text("Search")').first
    search_button.wait_for(state="visible", timeout=30_000)
    search_button.click()

    # Record the Total Record Count.
    total_record_count_el = page.locator('p:has-text("Total Record Count")').first
    total_record_count_el.wait_for(state="visible", timeout=30_000)

    total_record_count_text = total_record_count_el.inner_text().strip()
    match = re.search(r"Total Record Count\s+(\d+)", total_record_count_text)
    assert match, (
        f"Could not parse Total Record Count from: {total_record_count_text!r}"
    )

    total_record_counter = int(match.group(1))

    assert total_record_counter == int(program_widget_incomplete_counter), (
        f"Total Record Count should be {program_widget_incomplete_counter}, but was {total_record_counter}"
    )

    # Verify the program_widget_expired_counter is equal to the number of records displayed.
        # Set the Status dropdown to 'Expired'.
    status_dropdown = page.locator("#id_status").first
    status_dropdown.wait_for(state="visible", timeout=30_000)
    status_dropdown.select_option(label="Expired")

        # Click Search button.
    search_button = page.locator('button.btn.btn-primary:has-text("Search")').first
    search_button.wait_for(state="visible", timeout=30_000)
    search_button.click()

        # Record the Total Record Count.
    total_record_count_el = page.locator('p:has-text("Total Record Count")').first
    total_record_count_el.wait_for(state="visible", timeout=30_000)

    total_record_count_text = total_record_count_el.inner_text().strip()
    match = re.search(r"Total Record Count\s+(\d+)", total_record_count_text)
    assert match, (
        f"Could not parse Total Record Count from: {total_record_count_text!r}"
    )

    total_record_counter = int(match.group(1))

    assert total_record_counter == int(program_widget_expired_counter), (
        f"Total Record Count should be {program_widget_expired_counter}, but was {total_record_counter}"
    )

