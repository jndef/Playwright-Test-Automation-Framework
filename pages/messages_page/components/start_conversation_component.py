import re
import allure
from playwright.sync_api import Locator, Page, expect
from base.base_component import BaseComponent
from pages.messages_page.components.chat_component import ChatComponent


class StartConversationComponent(BaseComponent):
    def __init__(self, page: Page):
        super().__init__(page)
        """
        Init StartConversationComponent, that requires page locator object
        :param page: Playwright Page object
        """

    @allure.step("fill in search conversation input")
    def fill_search_conversation_input(self, name: str):
        """
        Method to fill search conversation input
        :param name: Name(str) of user for conversation
        :return: None
        """
        with allure.step(f"Fill in search conversation input by text: {name}"):
            self.page.get_by_test_id("new-conversation-search").fill(name)
        return self

    @allure.step("Submit search conversation")
    def submit_search_conversation(self):
        """
        Method initiated search conversation by user via certain button
        :return:
        """
        self.page.get_by_role("button", name="Search").click()
        return self

    @allure.step("Click 'New message' button")
    def click_new_message_button(self):
        """
        Method initiated search conversation by user via certain button
        :return:
        """
        self.page.get_by_test_id("new-conversation-btn").click()
        return self

    @property
    @allure.step("Get search conversation results list")
    def _get_search_conversations_results_list(self) -> Locator:
        """
        Method to get search conversation results list
        :return: Locator with search conversation results list
        """
        return self.page.get_by_test_id(re.compile(r"^new-conversation-user-[^-]+$"))

    def open_and_get_conversation_from_list_by_index(self, index: int) -> ChatComponent:
        """
        Method to get certain search conversation result by specified index
        :param index:
        :return: ChatComponent
        """
        conversation: Locator = self._get_search_conversations_results_list.nth(index - 1)
        conversation.click()
        return ChatComponent(self.page)

    def open_and_get_conversation_from_list_by_text(self, recipient_info: str) -> ChatComponent:
        """
        Method to get certain search conversation result by specified index
        :param recipient_info:str
        :return: ChatComponent
        """
        current_url = self.page.url
        conversation: Locator = self._get_search_conversations_results_list.filter(has_text=recipient_info)
        conversation.click()
        expect(self.page).not_to_have_url(current_url)
        return ChatComponent(self.page)
