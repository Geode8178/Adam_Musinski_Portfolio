"""Test the sales summary section of a Market Actor card found on the Incentive Connect
dashboard. This will test the Last Ingest widget."""

from config.settings import url

def test_last_ingest_widget(page):

    # User-focused, single login is used, so there is no back and forth between tests.
    page.goto(url("/dashboard/"), wait_until="domcontentloaded")
    if not page.url.endswith("/dashboard/"):
        raise Exception("Failed to load the Dashboard page.")

    # Locate the first available Market Actor card.
    first_market_actor_card = page.locator("div.card:has(h2.card-title)").first
    first_market_actor_card.wait_for(state="visible", timeout=30_000)

    # Find the "Sales Records Summary" title INSIDE the first Market Actor card.
    sales_records_summary_title = first_market_actor_card.locator(
        "h3.card-title.rose-primary-text",
        has_text="Sales Records Summary",
    ).first
    sales_records_summary_title.wait_for(state="visible", timeout=30_000)

    # Optional: assert the exact text we found (helps debugging if there are similar headings).
    assert sales_records_summary_title.inner_text().strip() == "Sales Records Summary"
    print("Found section: Sales Records Summary")

    # Find the "Last Ingest" widget/link INSIDE the Sales Records Summary section.
    last_ingest = first_market_actor_card.locator(
        "span.me-2.card-link.text-400",
        has_text="Last Ingest",
    ).first
    last_ingest.wait_for(state="visible", timeout=30_000)

    assert last_ingest.inner_text().strip() == "Last Ingest"
    print("Found widget: Last Ingest")

    # Highlight the "Last Ingest" label so the user can clearly see it during the run.
    last_ingest.scroll_into_view_if_needed()
    last_ingest.evaluate(
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

    # Find the widget container by walking UP from the "Last Ingest" label to the nearest container
    # that includes the "Ingested on" line. This avoids accidentally selecting a larger section container.
    last_ingest_widget = last_ingest.locator(
        "xpath=ancestor::*[self::div or self::li]"
        "[.//p[contains(@class,'card-text') and contains(., 'Ingested on')]][1]"
    ).first
    last_ingest_widget.wait_for(state="visible", timeout=30_000)

    # Verify an integer is displayed for the Last Ingest widget value (e.g., <h3>10335</h3>)
    # and that the integer is NOT negative.
    last_ingest_value = last_ingest_widget.locator("h3:not(.card-title)").first
    last_ingest_value.wait_for(state="visible", timeout=30_000)

    last_ingest_value_text = last_ingest_value.inner_text().strip()
    assert last_ingest_value_text.isdigit(), (
        "Last Ingest value should be a non-negative integer string, "
        f"but was {last_ingest_value_text!r}"
    )

    last_ingest_value_int = int(last_ingest_value_text)
    assert last_ingest_value_int >= 0, (
        f"Last Ingest value should be >= 0, but was {last_ingest_value_int}"
    )
    print(f"Last Ingest value: {last_ingest_value_int}")

    # Verify "Ingested on: <mm/dd/yyyy>" exists and a date format is mm/dd/yyyy.
    ingested_on_p = last_ingest_widget.locator(
        'p.card-text:has-text("Ingested on")'
    ).first
    ingested_on_p.wait_for(state="visible", timeout=30_000)

    ingested_on_date_span = ingested_on_p.locator("span").first
    ingested_on_date_span.wait_for(state="visible", timeout=30_000)

    ingested_on_date_text = ingested_on_date_span.inner_text().strip()

    import re
    assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", ingested_on_date_text), (
        "Ingested on date should be formatted as mm/dd/yyyy, "
        f"but was {ingested_on_date_text!r}"
    )
    print(f"Ingested on date: {ingested_on_date_text}")


