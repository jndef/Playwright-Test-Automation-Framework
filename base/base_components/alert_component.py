from playwright.sync_api import Page, Locator
from base.base_component import BaseComponent


class AlertComponent(BaseComponent):
    def __init__(self, page: Page):
        super().__init__(page)

    def click_and_accept_alert(self, click_locator: Locator):
        """Click  at locator and accept prompt - 'ОК'"""
        self.page.once("dialog", lambda dialog: dialog.accept())
        click_locator.click()

    def click_and_accept_prompt(self, click_locator: Locator, input_value: str):
        """Click by locator, fill in the input at prompt and accept it - 'ОК'"""
        self.page.once("dialog", lambda dialog: dialog.accept(input_value))
        click_locator.click()

    def click_and_dismiss_dialog(self, click_locator: Locator):
        """Click  at locator and accept deny prompt - 'DISMISS'"""
        self.page.once("dialog", lambda dialog: dialog.dismiss())
        click_locator.click()
