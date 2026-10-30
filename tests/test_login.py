import allure
import pytest
from allure_commons.types import Severity
from playwright.sync_api import expect

from base.base_test import BaseTest
from config.urls import Links


@allure.epic("Registration/Login")
@allure.feature("Registration/Login")
@allure.parent_suite("Registration/Login")
@pytest.mark.auth
class TestLoginFeed(BaseTest):

    @allure.story("Login as existed user")
    @allure.testcase("Login as existed user")
    @allure.id("TC-AUTH-001")
    @allure.title("Successful login")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user_to_ui_login", ["admin"])
    @pytest.mark.smoke
    @pytest.mark.login
    def test_login_to_account(self, default_page, user_to_ui_login):
        login_page = self.login_page(default_page)
        login_page.open()
        email, password = self.credentials.get_user(user_to_ui_login).email, self.credentials.get_user(
            user_to_ui_login).password
        login_page.login(email, password)
        expect(login_page.success_prompt).to_be_visible()

    @allure.story("Login as existed user")
    @allure.testcase("Login with wrong password")
    @allure.id("TC-AUTH-002")
    @allure.title("Login with wrong password")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("users_creds_to_login", ["user_bob"])
    @pytest.mark.regression
    @pytest.mark.login
    def test_incorrect_login_to_account(self, default_page, users_creds_to_login):
        login_page = self.login_page(default_page)
        login_page.open()
        email, password = self.credentials.get_user(users_creds_to_login).email, "123"
        login_page.login(email, password)
        expect(login_page.error_info).to_be_visible()
        expect(login_page.error_info).to_have_text("Invalid email or password")
        expect(login_page.page).not_to_have_url(Links.FEED_URL)

    @allure.story("Register account")
    @allure.testcase("Register with duplicate email")
    @allure.id("TC-AUTH-005")
    @allure.title("Register with duplicate email")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("existed_user_to_register", ["user_bob"])
    @pytest.mark.regression
    @pytest.mark.register
    def test_register_existed_account(self, default_page, existed_user_to_register):
        rand_register_data = self.get_rand_data.get_register_rand_data_object()
        login_page = self.login_page(default_page)
        login_page.open()
        register_page = login_page.go_to_register_page()
        register_page.fill_display_name_input(rand_register_data.display_name) \
            .fill_username_input(rand_register_data.username) \
            .fill_email_input(self.credentials.get_user(existed_user_to_register).email) \
            .fill_password_input(rand_register_data.password) \
            .click_on_submit_button()
        expect(register_page.error_message).to_be_visible()
        expect(login_page.page).not_to_have_url(Links.FEED_URL)

    @allure.story("Register account")
    @allure.testcase("Username validation rejects spaces")
    @allure.id("TC-AUTH-008")
    @allure.title("Username validation rejects spaces")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.register
    def test_register_with_invalid_data_spaces(self, default_page):
        rand_register_data = self.get_rand_data.get_register_rand_data_object()
        login_page = self.login_page(default_page)
        login_page.open()
        register_page = login_page.go_to_register_page()
        register_page.fill_display_name_input(rand_register_data.display_name) \
            .fill_username_input(f"  {rand_register_data.username}  ") \
            .fill_email_input(rand_register_data.email) \
            .fill_password_input(rand_register_data.password) \
            .click_on_submit_button()
        expect(login_page.page).not_to_have_url(Links.FEED_URL)

    @allure.story("Ban/unban user")
    @allure.testcase("Regular user blocked from admin")
    @allure.id("TC-AUTH-003")
    @allure.title("Regular user blocked from admin")
    @allure.severity(Severity.BLOCKER)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("banned_user_to_login", ["user_eve"])
    @pytest.mark.regression
    def test_attempt_to_login_as_banned_user(self, user, default_page, banned_user_to_login):
        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("admin")
        admin_page = self.admin_page(user.page)

        banned_user_login_page = self.login_page(default_page)
        banned_user_login_page.open()

        user_management_page = admin_page.open_user_management_page()
        for_moderated_user = user_management_page.admin_fill_search_user_input(banned_user_to_login.split("_")[1]) \
            .admin_submit_search(track_search_criteria=banned_user_to_login.split("_")[1]) \
            .admin_get_user_by_index(1)
        for_moderated_user.admin_click_on_ban_button()

        creds = self.credentials.get_user(banned_user_to_login)
        email, password = creds.email, creds.password
        banned_user_login_page.login(email, password)
        expect(banned_user_login_page.error_info).to_be_visible()
        expect(banned_user_login_page.error_info).to_have_text("Account is deactivated")

        # after
        for_moderated_user.admin_click_on_ban_button()
