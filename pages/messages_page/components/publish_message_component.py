import allure
from playwright.sync_api import Page
from base.base_component import BaseComponent


class PublishMessageComponent(BaseComponent):
    def __init__(self, page: Page):
        """
        Init PublishMessageComponent, that requires page locator object
        :param page: Playwright Page object
        """
        super().__init__(page)

    @allure.step("Publish message to chat")
    def click_publish_message_button(self, send_via_enter=False):
        """
        Method to send message to chat
        :param send_via_enter: (optional) send via enter if True. Default False
        :return:
        """
        if send_via_enter:
            self.page.get_by_test_id("message-input").press(key="enter")
        else:
            self.page.get_by_test_id("message-send-btn").click()

    def fill_message_input(self, message_text: str=None):
        """
        Method to fill message input field.
        :param message_text: provide message text. If it isn't specified, method will generate random text
        :return:
        """
        self.page.get_by_test_id("message-input").fill(message_text or self.get_rand_data.generate_text(15))
        return self
