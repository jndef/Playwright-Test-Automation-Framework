import re
import allure
from playwright.sync_api import Locator, Page

from base.base_page import BasePage
from config.urls import Links
from pages.messages_page.components.chat_component import ChatComponent
from pages.messages_page.components.start_conversation_component import StartConversationComponent


class MessagesPage(BasePage):
    _PAGE_URL = Links.MESSAGES_URL

    def __init__(self, page: Page):
        """
        Init MessagesPage object, that accepted playwright page object
        :param page: playwright page object
        """
        super().__init__(page)

    @property
    def get_conversations_list(self) -> Locator:
        """
        Method returns locator with chats (existed conversations)
        :return: Locator
        """
        return self.page.get_by_test_id(re.compile(r"^conversation-[^-]+$"))

    @allure.step("Get conversation by recipient name")
    def get_conversation_by_name_or_last_message(self, text_filter: str) -> Locator:
        """
        Method is used to get conversation from list, filtered by name or last message
        :param text_filter: text, used for filtration
        :return: Locator
        """
        return self.get_conversations_list.filter(has_text=text_filter)

    def search_conversation_flow(self, recipient_name: str) -> ChatComponent:
        """
        Method performed search flow with all necessary steps, includes StartConversationComponent init
        :param recipient_name: name of the recipient used for conversation filter
        :return: StartConversationComponent object with found user
        """
        with allure.step(f"Start conversation with {recipient_name}"):
            return StartConversationComponent(self.page) \
                .click_new_message_button() \
                .fill_search_conversation_input(recipient_name) \
                .submit_search_conversation() \
                .open_and_get_conversation_from_list_by_text(recipient_name)

    @staticmethod
    def get_conversation_unread_count(chat_locator: Locator) -> int:
        """
        Method returns count of unread messages of certain conversation
        :param chat_locator: provided locator of conversation
        :return: count of unread messages (int)
        """
        return int(chat_locator.locator("span.rounded-full").inner_text())
