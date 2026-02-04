"""Validate UI Requirements: Program widgets should match Market Actor cards on the dashboard."""

from config.settings import url
import re

def test_dashboard_program_widgets_match_market_actor(page):

    # User-focused, single login is used, so there is no back and forth between tests.
    page.goto(url("/dashboard/"), wait_until="domcontentloaded")
    if not page.url.endswith("/dashboard/"):
        raise Exception("Failed to load the Dashboard page.")

    # Locate the first available Market Actor card and capture its name.
    market_actor_title = page.locator("h2.card-title").first
    market_actor_title.wait_for(state="visible", timeout=30_000)
    market_actor_name = market_actor_title.inner_text()

    # Capture all program widgets on the first Market Actor card.
    first_market_actor_card = page.locator("div.card:has(h2.card-title)").first
    first_market_actor_card.wait_for(state="visible", timeout=30_000)

    program_widgets = first_market_actor_card.locator("h5.rose-primary-text")

    first_ma_card_program_names: list[str] = []  # type: ignore[annotation-unchecked]
    for i in range(program_widgets.count()):
        first_ma_card_program_names.append(program_widgets.nth(i).inner_text())

    # Click the Recent Sales link in the side panel menu.
    recent_sales_link = page.locator('a.nav-link.ps-4[href="/salesdata/"]').first
    recent_sales_link.wait_for(state="visible", timeout=30_000)
    recent_sales_link.click()

    if not page.url.endswith("/salesdata/"):
        raise Exception("Failed to load the Recent Sales page.")

    # Select the Market Actor on the Recent Sales page.
    market_actor_dropdown = page.locator("#id_market_actor").first
    market_actor_dropdown.wait_for(state="visible", timeout=30_000)
    market_actor_dropdown.select_option(label=market_actor_name)

    # Verify Status is 'All' (if not, set it to 'All').
    status_dropdown = page.locator("#id_status").first
    status_dropdown.wait_for(state="visible", timeout=30_000)

    selected_status = status_dropdown.locator("option:checked").inner_text()
    if selected_status != "All":
        status_dropdown.select_option(label="All")
        selected_status = status_dropdown.locator("option:checked").inner_text()

    assert selected_status == "All", f"Status dropdown should be 'All' but was '{selected_status}'."

    # Verify Invoice Date is 'All' (if not, set it to 'All').
    invoice_date_dropdown = page.locator("#id_invoice_date").first
    invoice_date_dropdown.wait_for(state="visible", timeout=30_000)

    selected_invoice_date = invoice_date_dropdown.locator("option:checked").inner_text()
    if selected_invoice_date != "All":
        invoice_date_dropdown.select_option(label="All")
        selected_invoice_date = invoice_date_dropdown.locator("option:checked").inner_text()

    assert selected_invoice_date == "All", f"Invoice Date dropdown should be 'All' but was '{selected_invoice_date}'."

    # Step 9: Iterate Assigned Program options -> Search -> validate results ↔ widget visibility.
    assigned_program_dropdown = page.locator("#id_program").first
    assigned_program_dropdown.wait_for(state="visible", timeout=30_000)

    search_button = page.locator('button.btn.btn-primary:has-text("Search")').first
    search_button.wait_for(state="visible", timeout=30_000)

    # Collect all selectable program labels from the dropdown (skip placeholder + Unassigned).
    program_option_labels = assigned_program_dropdown.locator("option").all_inner_texts()
    program_option_labels = [t for t in program_option_labels if t not in ("---------", "Unassigned")]

    def _record_id_links():
        # e.g. <a href="/salesdata/24517/">24517</a>
        return page.locator('a[href^="/salesdata/"]').filter(has_text=re.compile(r"^\d+$"))

    def _has_sales_records() -> bool:
        return _record_id_links().count() > 0

    def _wait_for_results_to_render(timeout_ms: int = 15_000) -> None:
        """
        Deterministic wait after clicking Search:
        waits until either
          - at least one record link appears (record id), OR
          - the "Total Record Count 0" empty state appears.
        """
        page.wait_for_load_state("domcontentloaded")

        empty_state_total_0 = page.locator('p:has-text("Total Record Count 0")').first

        # records exist
        try:
            _record_id_links().first.wait_for(state="visible", timeout=timeout_ms)
            return
        except Exception:
            pass

        # empty state
        empty_state_total_0.wait_for(state="visible", timeout=timeout_ms)

    # A) Reverse check: any program that returns records MUST be a widget on the Market Actor card.
    programs_with_records_not_in_widgets: list[str] = []

    for program_label in program_option_labels:
        assigned_program_dropdown.select_option(label=program_label)
        search_button.click()
        _wait_for_results_to_render()

        if _has_sales_records() and program_label not in first_ma_card_program_names:
            programs_with_records_not_in_widgets.append(program_label)

    if programs_with_records_not_in_widgets:
        raise Exception(
            "Found sales records for program(s) that are NOT shown as dashboard widgets for "
            f"Market Actor '{market_actor_name}': {programs_with_records_not_in_widgets}. "
            f"Dashboard widgets were: {first_ma_card_program_names}"
        )

    # B) Forward check: every widget program SHOULD have at least one record when filtered.
    widget_programs_with_no_records: list[str] = []

    for widget_program in first_ma_card_program_names:
        assigned_program_dropdown.select_option(label=widget_program)
        search_button.click()
        _wait_for_results_to_render()

        if not _has_sales_records():
            widget_programs_with_no_records.append(widget_program)

    if widget_programs_with_no_records:
        raise Exception(
            "The following dashboard widget program(s) have NO sales records when filtered by "
            f"Market Actor '{market_actor_name}' with Status='All' and Invoice Date='All': "
            f"{widget_programs_with_no_records}"
        )
