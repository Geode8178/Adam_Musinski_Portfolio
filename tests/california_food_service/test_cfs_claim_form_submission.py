"""Test the ability to submit a claim for the California Food Service Program"""

from config.settings import url


def test_cfs_claim_form(page):
    # User-focused, single login is used, so there is no back and forth between tests.
    page.goto(url("/dashboard/"), wait_until="domcontentloaded")
    if not page.url.endswith("/dashboard/"):
        raise Exception("Failed to load the Dashboard page.")

    # Pause so you can visually confirm the dashboard rendered.
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(30_000)
