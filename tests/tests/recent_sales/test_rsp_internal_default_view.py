from config.settings import url


def test_rsp_internal_default_view(page):
    def _log(msg: str) -> None:
        print(f"[RSP][DefaultView] {msg}")

    def _highlight(el, *, color="#ff3b30", wait_ms: int = 250) -> None:
        el.scroll_into_view_if_needed()
        el.evaluate(
            f"""
            (node) => {{
              node.style.outline = '3px solid {color}';
              node.style.outlineOffset = '3px';
              node.style.background = 'rgba(255, 59, 48, 0.12)';
              node.style.borderRadius = '4px';
            }}
            """
        )
        page.wait_for_timeout(wait_ms)

    # Navigate to Recent Sales page.
    _log("Navigating to Recent Sales page (/salesdata/).")
    page.goto(url("/salesdata/"), wait_until="domcontentloaded")
    page.wait_for_url("**/salesdata/**", timeout=30_000)
    _log(f"Arrived on: {page.url}")

    # Verify the Market Actor field is set to "All".
    _log("Checking defaults: Market Actor = 'All'.")
    market_actor_dropdown = page.locator("#id_market_actor").first
    market_actor_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(market_actor_dropdown, color="#0a84ff")

    selected_market_actor_name = (
        market_actor_dropdown.locator("option:checked").first.inner_text().strip()
    )
    assert selected_market_actor_name == "All", (
        f"Market Actor field should be 'All', but was {selected_market_actor_name!r}"
    )
    _log("Market Actor default OK.")

    # Verify the Status field is set to "All".
    _log("Checking defaults: Status = 'All'.")
    status_dropdown = page.locator("#id_status").first
    status_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(status_dropdown, color="#0a84ff")

    selected_status = status_dropdown.locator("option:checked").first.inner_text().strip()
    assert selected_status == "All", (
        f"Status field should be 'All', but was {selected_status!r}"
    )
    _log("Status default OK.")

    # Verify the Assigned Program field is set to "---------".
    _log("Checking defaults: Assigned Program = '---------'.")
    assigned_program_dropdown = page.locator("#id_program").first
    assigned_program_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(assigned_program_dropdown, color="#0a84ff")

    selected_program = (
        assigned_program_dropdown.locator("option:checked").first.inner_text().strip()
    )
    assert selected_program == "---------", (
        f"Assigned Program field should be '---------', but was {selected_program!r}"
    )
    _log("Assigned Program default OK.")

    # Verify the Invoice Number field is a text field and is defaulted blank.
    _log("Checking defaults: Invoice Number type=text and blank.")
    invoice_number_input = page.locator("#id_invoice_number").first
    invoice_number_input.wait_for(state="visible", timeout=30_000)
    _highlight(invoice_number_input, color="#0a84ff")

    invoice_number_type = (invoice_number_input.get_attribute("type") or "").strip()
    assert invoice_number_type == "text", (
        f"Invoice Number field type should be 'text', but was {invoice_number_type!r}"
    )

    invoice_number_value = invoice_number_input.input_value()
    assert invoice_number_value == "", (
        f"Invoice Number field should be blank, but was {invoice_number_value!r}"
    )
    _log("Invoice Number defaults OK.")

    # Verify the Product Type field can be selected and deselected for each option.
    _log("Validating Product Type options can be selected and cleared.")
    product_type_select = page.locator("select:has(option[value='QA Test Item'])").first
    product_type_select.wait_for(state="visible", timeout=30_000)
    _highlight(product_type_select, color="#0a84ff")

    option_values = product_type_select.locator("option").evaluate_all(
        """
        (opts) => opts
          .map(o => (o.value || "").trim())
          .filter(v => v.length > 0)
        """
    )

    has_empty_option = product_type_select.locator("option[value='']").count() > 0
    _log(f"Product Type options found: {len(option_values)}; has_empty_option={has_empty_option}")

    for option_value in option_values:
        _highlight(product_type_select, color="#ff9f0a", wait_ms=150)
        product_type_select.select_option(value=option_value)

        selected_value = product_type_select.input_value().strip()
        assert selected_value == option_value, (
            f"Product Type should be set to {option_value!r}, but was {selected_value!r}"
        )

        if has_empty_option:
            product_type_select.select_option(value="")
            assert product_type_select.input_value().strip() == "", (
                "Product Type should be cleared back to blank, but it was not."
            )
        else:
            product_type_select.evaluate(
                """
                (sel) => {
                  sel.value = "";
                  sel.dispatchEvent(new Event("input", { bubbles: true }));
                  sel.dispatchEvent(new Event("change", { bubbles: true }));
                }
                """
            )
            assert product_type_select.input_value().strip() == "", (
                "Product Type should be cleared back to blank, but it was not."
            )
    _log("Product Type select/clear loop OK.")

    # Verify the Manufacturer field is a text field and is defaulted blank.
    _log("Checking defaults: Manufacturer type=text and blank.")
    manufacturer_input = page.locator("#id_manufacturer").first
    manufacturer_input.wait_for(state="attached", timeout=30_000)
    _highlight(manufacturer_input, color="#0a84ff")

    manufacturer_type = (manufacturer_input.get_attribute("type") or "").strip()
    assert manufacturer_type == "text", (
        f"Manufacturer field type should be 'text', but was {manufacturer_type!r}"
    )

    manufacturer_value = manufacturer_input.input_value()
    assert manufacturer_value == "", (
        f"Manufacturer field should be blank, but was {manufacturer_value!r}"
    )
    _log("Manufacturer defaults OK.")

    # Verify the Model field is a text field and is defaulted blank.
    _log("Checking defaults: Model type=text and blank.")
    model_input = page.locator("#id_model").first
    model_input.wait_for(state="attached", timeout=30_000)
    _highlight(model_input, color="#0a84ff")

    model_type = (model_input.get_attribute("type") or "").strip()
    assert model_type == "text", (
        f"Model field type should be 'text', but was {model_type!r}"
    )

    model_value = model_input.input_value()
    assert model_value == "", (
        f"Model field should be blank, but was {model_value!r}"
    )
    _log("Model defaults OK.")

    # Verify the Source ID field is a text field and is defaulted blank.
    _log("Checking defaults: Source ID type=text and blank.")
    source_id_input = page.locator("#id_source_id").first
    source_id_input.wait_for(state="attached", timeout=30_000)
    _highlight(source_id_input, color="#0a84ff")

    source_id_type = (source_id_input.get_attribute("type") or "").strip()
    assert source_id_type == "text", (
        f"Source ID field type should be 'text', but was {source_id_type!r}"
    )

    source_id_value = source_id_input.input_value()
    assert source_id_value == "", (
        f"Source ID field should be blank, but was {source_id_value!r}"
    )
    _log("Source ID defaults OK.")

    # Verify the Invoice Date field is set to "All" and select each option once.
    _log("Checking defaults: Invoice Date = 'All', then cycling options.")
    invoice_date_dropdown = page.locator("#id_invoice_date").first
    invoice_date_dropdown.wait_for(state="visible", timeout=30_000)
    _highlight(invoice_date_dropdown, color="#0a84ff")

    selected_invoice_date = (
        invoice_date_dropdown.locator("option:checked").first.inner_text().strip()
    )
    assert selected_invoice_date == "All", (
        f"Invoice Date field should be 'All', but was {selected_invoice_date!r}"
    )

    invoice_date_option_values = invoice_date_dropdown.locator("option").evaluate_all(
        """
        (opts) => opts
          .map(o => (o.value || "").trim())
          .filter(v => v.length > 0)
        """
    )
    _log(f"Invoice Date option values found: {invoice_date_option_values!r}")

    for option_value in invoice_date_option_values:
        _highlight(invoice_date_dropdown, color="#ff9f0a", wait_ms=150)
        invoice_date_dropdown.select_option(value=option_value)
        selected_text = (
            invoice_date_dropdown.locator("option:checked").first.inner_text().strip()
        )
        assert selected_text in ("Last 30 Days", "Last 60 Days", "Last 90 Days"), (
            f"Unexpected Invoice Date selection text after choosing {option_value!r}: {selected_text!r}"
        )

    invoice_date_dropdown.select_option(value="")
    selected_invoice_date = (
        invoice_date_dropdown.locator("option:checked").first.inner_text().strip()
    )
    assert selected_invoice_date == "All", (
        f"Invoice Date field should be 'All' after reset, but was {selected_invoice_date!r}"
    )
    _log("Invoice Date cycle/reset OK.")

    # Verify "Select specific date range" is NOT checked.
    _log("Checking: 'Select specific date range' is unchecked by default.")
    enable_date_range_checkbox = page.locator("#enable-date-range-invoice").first
    enable_date_range_checkbox.wait_for(state="visible", timeout=30_000)
    _highlight(enable_date_range_checkbox, color="#0a84ff")

    assert not enable_date_range_checkbox.is_checked(), (
        "Expected 'Select specific date range' to be unchecked by default."
    )

    # Select the boolean and verify Invoice Start/End Date fields are visible and blank.
    _log("Checking date-range toggle ON shows blank start/end fields.")
    enable_date_range_checkbox.check()
    _highlight(enable_date_range_checkbox, color="#ff9f0a", wait_ms=150)

    invoice_start_date_input = page.locator("#invoice_start_date").first
    invoice_start_date_input.wait_for(state="visible", timeout=30_000)
    _highlight(invoice_start_date_input, color="#0a84ff")

    invoice_start_date_value = invoice_start_date_input.input_value().strip()
    assert invoice_start_date_value == "", (
        f"Invoice Start Date should be blank, but was {invoice_start_date_value!r}"
    )

    invoice_end_date_input = page.locator("#invoice_end_date").first
    invoice_end_date_input.wait_for(state="visible", timeout=30_000)
    _highlight(invoice_end_date_input, color="#0a84ff")

    invoice_end_date_value = invoice_end_date_input.input_value().strip()
    assert invoice_end_date_value == "", (
        f"Invoice End Date should be blank, but was {invoice_end_date_value!r}"
    )

    # Deselect the "Select specific date range" checkbox.
    _log("Checking date-range toggle OFF returns to unchecked.")
    enable_date_range_checkbox.uncheck()
    _highlight(enable_date_range_checkbox, color="#ff9f0a", wait_ms=150)

    assert not enable_date_range_checkbox.is_checked(), (
        "Expected 'Select specific date range' to be unchecked after uncheck()."
    )
    _log("Date range toggle OK.")

    # Verify Advanced Search toggle exists and is expanded (observe current behavior).
    _log("Checking Advanced Search toggle text + expanded state.")
    advanced_search_toggle = page.locator(
        "span.d-inline-flex.align-items-center"
        "[data-bs-toggle='collapse']"
        "[href='#advanced_search_form']"
        "[aria-controls='advanced_search_form']"
    ).first
    advanced_search_toggle.wait_for(state="visible", timeout=30_000)
    _highlight(advanced_search_toggle, color="#0a84ff")

    advanced_search_text = (
        advanced_search_toggle.locator("span.text-decoration-underline").first.inner_text().strip()
    )
    assert advanced_search_text == "Advanced Search", (
        f"Expected Advanced Search toggle text to be 'Advanced Search', but was {advanced_search_text!r}"
    )

    aria_expanded = (advanced_search_toggle.get_attribute("aria-expanded") or "").strip()
    assert aria_expanded == "true", (
        f"Advanced Search should be expanded (aria-expanded='true'), but was {aria_expanded!r}"
    )
    _log("Advanced Search toggle OK.")

    # Find the Search button, verify it is visible, and highlight it.
    _log("Checking Search and Clear controls are visible.")
    search_button = page.locator('button.btn.btn-primary:has-text("Search")').first
    search_button.wait_for(state="visible", timeout=30_000)
    _highlight(search_button, color="#34c759")

    clear_button = page.locator('a#clear-filters-btn.btn.btn-secondary[href="/salesdata/"]').first
    clear_button.wait_for(state="visible", timeout=30_000)
    _highlight(clear_button, color="#0a84ff")
    _log("Search/Clear controls OK.")

    # Verify the warning message is visible and styled as danger (red).
    _log("Checking warning alert and styling.")
    warning_alert = (
        page.locator("div.alert.alert-danger")
        .filter(has_text="Run a search to load relevant sales.")
        .first
    )
    warning_alert.wait_for(state="visible", timeout=30_000)
    _highlight(warning_alert, color="#ff3b30")

    warning_text = warning_alert.inner_text().strip()
    assert warning_text == "Run a search to load relevant sales.", (
        f"Unexpected warning text: {warning_text!r}"
    )

    warning_classes = (warning_alert.get_attribute("class") or "").strip()
    assert "alert-danger" in warning_classes.split(), (
        f"Warning alert should include 'alert-danger' class, but classes were: {warning_classes!r}"
    )
    _log("Warning alert OK.")

    # Verify the Total Record Count is visible at the bottom of the page and is set to 0.
    _log("Checking Total Record Count shows 0 before searching.")
    total_record_count_el = page.locator('p:has-text("Total Record Count 0")').first
    total_record_count_el.wait_for(state="visible", timeout=30_000)
    _highlight(total_record_count_el, color="#ff9f0a")

    total_record_count_text = total_record_count_el.inner_text().strip()
    assert total_record_count_text == "Total Record Count 0", (
        f"Unexpected Total Record Count text: {total_record_count_text!r}"
    )
    _log("Total Record Count default OK. PASSED.")


