"""SSO Login Test For Incentive Connect."""
from config.settings import url

def test_entra_sso_login(page):
    # User-focused, single login is used, so there is no back and forth between tests.
    page.goto(url("/dashboard/"), wait_until="domcontentloaded")
    if not page.url.endswith("/dashboard/"):
        raise Exception("Failed to load the Dashboard page.")
