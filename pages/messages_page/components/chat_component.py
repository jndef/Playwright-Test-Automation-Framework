import re
import allure
from playwright.sync_api import Page, Locator
from base.base_component import BaseComponent
from config.urls import Links
from pages.messages_page.components.publish_message_component import PublishMessageComponent


class ChatComponent(BaseComponent):
    _PAGE_URL = Links.FEED_URL

    def __init__(self, page: Page):
        """
        Init ChatComponent, that requires page locator object
        :param page: Playwright Page object
        """
        super().__init__(page)
        self.chat_url = self._PAGE_URL

    @property
    def _get_all_messages_list(self) -> Locator:
        """Internal method. Return all messages as Locator"""
        return self.page.get_by_test_id(re.compile("message-[^-]+$"))

    @property
    def _get_own_messages_list(self) -> Locator:
        """Internal method. Return all OWN messages as Locator"""
        return self.page.get_by_test_id(re.compile("message-[^-]+$")).locator(".justify-end")

    @property
    def _get_recipients_messages_list(self) -> Locator:
        """Method that return all NOT OWN messages as Locator"""
        return self.page.get_by_test_id(re.compile("message-[^-]+$")).locator(".justify-start")

    def _get_message_by_text(self, text_info: str) -> Locator:
        """Internal method. Return message (Locator) from messages list, filtered by text message"""
        return self._get_all_messages_list.filter(has_text=text_info)

    def _get_message_by_index(self, index_message: int):
        """Internal method. Return message (Locator) picked by index message from messages list"""
        return self._get_all_messages_list.nth(index_message - 1)

    @allure.step("Create message at chat")
    def create_message_with_check(self, message_text: str):
        """
        Method that create message at chat. Includes check of corresponding request
        :param message_text: Message text (optional). If it isn't specified, method will generate a random message
        :return:
        """
        with self.page.expect_response(
                lambda response: "/message" in response.url and response.request.method == "POST", timeout=10000
        ) as response_info:
            PublishMessageComponent(self.page) \
                .fill_message_input(message_text if message_text else self.get_rand_data.generate_text(30)) \
                .click_publish_message_button()

            response = response_info.value
            request = response.request

            # Get json from response
            response_body = response.json()
            # (Optional) Get request body
            request_body = request.post_data_json
            assert response_body["content"] == message_text
            assert request_body["content"] == message_text
            # print(
            #     f"✅ Success request. {response.request.method} {response.url} - {response.status}\nRequest payload: {request_body}\nResponse payload: {response_body}")
