import allure
from playwright.sync_api import Page
from playwright.sync_api import expect

from base.base_page import BasePage
from config.urls import Links
from pages.login_page.registration_page import RegisterPage


class LoginPage(BasePage):
    _PAGE_URL = Links.LOGIN_URL

    def __init__(self, page: Page):
        """
        Init LoginPage object, that accepted playwright page object
        :param page: playwright page object
        """
        super().__init__(page)
        self.email_input = page.get_by_test_id("auth-email-input")
        self.password_input = page.get_by_test_id("auth-password-input")
        self.submit_button = page.get_by_test_id("auth-login-btn")
        self.success_prompt = page.get_by_role("status")
        self.error_info = self.page.get_by_test_id("auth-error-message")

    @allure.step("Enter email at input field")
    def fill_email_input(self, login: str = None):
        """
        Method to fill email input
        :param login: provided email (str)
        :return:
        """
        self.email_input.fill(login)
        return self

    @allure.step("Enter password at input field")
    def fill_password_input(self, password: str = None):
        """
        Method to fill password input
        :param password: provided password (str)
        :return:
        """
        self.password_input.fill(password)
        return self

    @allure.step("Click submit button")
    def click_submit_button(self):
        """
        Method to click submit button
        :return:
        """
        self.submit_button.click()
        return self

    def go_to_register_page(self):
        """
        Method to go to register page
        :return: RegisterPage object
        """
        expected_url = Links.REGISTER_URL
        self.page.locator("a").filter(has_text="Sign up").click()
        expect(self.page).to_have_url(expected_url)
        return RegisterPage(self.page)

    def login(self, email: str, password: str):
        """
        Method to login to your account with all required steps (fluent)
        :param email: provided email (str)
        :param password: provided password (str)
        :return:
        """
        with allure.step(f"Login to your account {email}"):
            self.fill_email_input(email).fill_password_input(password).click_submit_button()
