import os
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from auth.incentive_connect_login import login_via_entra_sso  # adjust if needed


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Store the test result on the node so fixtures can read it.
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def _load_env_file(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@pytest.fixture(scope="session", autouse=True)
def _env() -> None:
    _load_env_file(".env")


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=1000,  # <-- requested: slow_mo @ 1000
        )
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def storage_state_path(tmp_path_factory) -> Path:
    # Stored in pytest's temp area; you can change this to a project folder if you prefer.
    return tmp_path_factory.mktemp("auth") / "storage_state.json"


@pytest.fixture(scope="session", autouse=True)
def _login_once_and_save_state(browser, storage_state_path: Path) -> None:
    # Only create it once per session.
    if storage_state_path.exists():
        return

    context = browser.new_context()
    page = context.new_page()

    login_via_entra_sso(page)

    # Save cookies/localStorage/session to reuse without logging in again.
    context.storage_state(path=str(storage_state_path))

    page.close()
    context.close()


@pytest.fixture
def context(request, browser, storage_state_path: Path):
    # New isolated context per test, but already authenticated.
    context = browser.new_context(storage_state=str(storage_state_path))

    # ---- Trace setup (Option C: collect trace and save only on failure) ----
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    # Ensure artifacts folder exists.
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Save trace only when the test failed.
    failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    if failed:
        safe_nodeid = request.node.nodeid.replace("/", "_").replace("\\", "_").replace("::", "__")
        trace_path = artifacts_dir / f"trace_{safe_nodeid}.zip"
        context.tracing.stop(path=str(trace_path))
        print(f"[trace] saved to: {trace_path}")
    else:
        context.tracing.stop()

    context.close()


@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()
