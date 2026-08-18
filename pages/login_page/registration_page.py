from playwright.sync_api import Page, Locator
from playwright.sync_api import expect
from base.base_page import BasePage
from config.urls import Links


class RegisterPage(BasePage):
    _PAGE_URL = Links.LOGIN_URL

    def __init__(self, page: Page):
        """
        Init RegisterPage object, that accepted playwright page object
        :param page: playwright page object
        """
        super().__init__(page)
        self.error_message: Locator = self.page.get_by_test_id("auth-error-message")

    def fill_display_name_input(self, display_name: str):
        """
        Method to fill display name input with given display name
        :param display_name: provided display name (str)
        :return:
        """
        display_name_input = self.page.get_by_test_id("auth-display-name-input")
        display_name_input.fill(display_name)
        expect(display_name_input).to_have_value(display_name)
        return self

    def fill_username_input(self, user_name: str):
        """
        Method to fill username input with given username
        :param user_name: provided username (str)
        :return:
        """
        username_input = self.page.get_by_test_id("auth-username-input")
        username_input.fill(user_name)
        expect(username_input).to_have_value(user_name)
        return self

    def fill_email_input(self, email: str):
        """
        Method to fill email input with given email
        :param email: provided email (str)
        :return:
        """
        email_input = self.page.get_by_test_id("auth-email-input")
        email_input.fill(email)
        expect(email_input).to_have_value(email)
        return self

    def fill_password_input(self, password: str = None):
        """
        Method to fill password input with given password
        :param password:
        :return:
        """
        if password is None:
            password = self.get_rand_data.generate_password()
        password_input = self.page.get_by_test_id("auth-password-input")
        password_input.fill(password)
        expect(password_input).to_have_value(password)
        return self

    def click_on_submit_button(self):
        """
        Method to click on submit button
        :return:
        """
        self.page.get_by_test_id("auth-register-btn").click()
        return self
