from fixtures.db_fixtures import *
import os
from dataclasses import dataclass

import allure
import pytest

from config.credentials import Credentials
from config.urls import Links
from playwright.sync_api import Page, expect, Browser

from helpers.api_helper import ApiHelper
from helpers.use_data_context_helper import DataContextManager

BROWSER_CONTEXT_OPTS = {
    "viewport": {"width": 1520, "height": 710},
}
GLOBAL_TIMEOUT = 15000

@pytest.fixture(scope="session")
def api_helper() -> ApiHelper:
    api_helper = ApiHelper()
    return api_helper


@pytest.fixture(scope="session")
def auth_helper(api_helper) -> DataContextManager:
    auth_helper = DataContextManager(api=api_helper)
    return auth_helper


def login_to_account(page: Page, role: str):
    credentials = Credentials()
    email, password = credentials.get_user(role).email, credentials.get_user(role).password
    page.goto(Links.LOGIN_URL)
    page.get_by_test_id('auth-email-input').fill(email)
    page.get_by_test_id('auth-password-input').fill(password)
    page.get_by_test_id("auth-login-btn").click()
    expect(page.get_by_role("status")).to_be_visible()


def go_to_main_page(page: Page):
    page.goto(Links.FEED_URL)


def _context_page_for_role(role: str, browser: Browser, auth_helper):
    state_file = auth_helper.get_path_to_file(folders="data", file_name=f"storage_{role}.json")
    auth_helper.storage_file_handler(role)
    print(f"Storage file mtime: {os.path.getmtime(state_file) if os.path.exists(state_file) else 'missing'}")
    if not os.path.exists(state_file):
        context = browser.new_context(**BROWSER_CONTEXT_OPTS)
        context.set_default_timeout(GLOBAL_TIMEOUT)
        page = context.new_page()
        login_to_account(page, role)
        context.storage_state(path=str(state_file))
    else:
        context = browser.new_context(storage_state=str(state_file), **BROWSER_CONTEXT_OPTS)
        context.set_default_timeout(GLOBAL_TIMEOUT)
        page = context.new_page()
        go_to_main_page(page)
        print(f"URL after navigation: {page.url}")
        print(f"Storage file: {state_file}")
        print(f"Storage file exists: {os.path.exists(state_file)}")

    return context, page


@pytest.fixture(scope="session")
def browser_type_launch_args():
    return {
        # "headless": os.path.exists('/.dockerenv'),
        "headless": True
        # "slow_mo": 1700,

    }


@dataclass
class AuthenticatedUser:
    page: Page
    token: str = None


def _authenticated_user(browser: Browser, request, auth_helper: DataContextManager):
    role = request.param
    context, page = _context_page_for_role(role, browser, auth_helper)
    token = auth_helper.get_storage_access_token(role)
    return context, AuthenticatedUser(page=page, token=token)


@pytest.fixture
def user(browser, request, auth_helper):
    context, au = _authenticated_user(browser, request, auth_helper)
    yield au
    au.page.close()
    context.close()


@pytest.fixture
def another_user(browser, request, auth_helper):
    context, au = _authenticated_user(browser, request, auth_helper)
    yield au
    au.page.close()
    context.close()


@pytest.fixture
def default_page(browser: Browser):
    context = browser.new_context(**BROWSER_CONTEXT_OPTS)
    context.set_default_timeout(GLOBAL_TIMEOUT)
    page = context.new_page()
    yield page
    page.close()
    context.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Called only when test is failed ("call" stage)
    if rep.when == "call" and rep.failed:
        page = None

        # Dynamically iterate all args, passed(moved) to the test (fixtures)
        for fixture_value in item.funcargs.values():
            # If fixture value is Playwright Page object
            if isinstance(fixture_value, Page):
                page = fixture_value
                break  # We have found the page of the current test, break cycle
            if isinstance(fixture_value, AuthenticatedUser):
                page = fixture_value.page
                break
        # If page is found
        if page:
            try:
                # Check error type, if it is necessary
                exc_info = call.excinfo.value if call.excinfo else None

                # Capture page screen
                screenshot_bytes = page.screenshot(full_page=True)

                allure.attach(
                    screenshot_bytes,
                    name="Screen after failed test",
                    attachment_type=allure.attachment_type.PNG
                )

                # Log current URL
                allure.attach(
                    page.url,
                    name="Page URL at fail moment",
                    attachment_type=allure.attachment_type.TEXT
                )

            except Exception as e:
                print(f"Failed to attach artefacts to Allure: {e}")
