import re
import allure
import pytest
from allure_commons.types import Severity
from playwright.sync_api import expect, Locator

from base.base_test import BaseTest
from conftest import AuthenticatedUser
from pages.messages_page.components.chat_component import ChatComponent
from pages.profile_page.profile_page import ProfilePage


@allure.epic("Messages")
@allure.feature("Send message")
@allure.parent_suite("Messages")
@pytest.mark.messages
class TestMessages(BaseTest):

    @allure.story("Start new DM conversation")
    @allure.id("TC-MSG-001")
    @allure.testcase("Start new DM conversation")
    @allure.title("Start new DM conversation")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("chat_between", [
        ['user_bob', 'user_alice']
    ])
    @pytest.mark.smoke
    @pytest.mark.flaky(reruns=1)
    def test_start_new_dm_conversation(self, cleanup_conversation_between_users, user: AuthenticatedUser, chat_between):

        cleanup_conversation_between_users(chat_between[0], chat_between[1])

        sidebar = self.get_sidebar(user.page)
        sidebar.navigate_to("messages")
        messages_page = self.messages_page(user.page)

        recipient_name = chat_between[1].split("_")[1]
        messages_page.search_conversation_flow(recipient_name)
        sidebar.navigate_to("messages")

        expect(messages_page.get_conversation_by_name_or_last_message(recipient_name)).to_be_visible()

    @allure.story("Send a message")
    @allure.id("TC-MSG-002")
    @allure.testcase("Send a message")
    @allure.title("Send a message")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("message_text", [None])
    @pytest.mark.parametrize("chat_between", [
        ['user_bob', 'user_alice']
    ])
    @pytest.mark.smoke
    def test_send_message(self, user, chat_between, message_text):
        used_message_text = message_text or self.get_rand_data.generate_text(25)
        sidebar = self.get_sidebar(user.page)
        sidebar.navigate_to("messages")
        messages_page = self.messages_page(user.page)

        recipient_name = chat_between[1].split("_")[1]
        chat_between_users = messages_page.search_conversation_flow(recipient_name)

        chat_between_users.create_message_with_check(used_message_text)
        expect(chat_between_users._get_message_by_text(used_message_text)).to_be_visible()
        chat_between_users.page.go_back()
        messages_page = self.messages_page(user.page)

        expect(messages_page.get_conversation_by_name_or_last_message(used_message_text)).to_be_visible()

    @allure.story("Start DM from user profile")
    @allure.id("TC-MSG-006")
    @allure.testcase("Start DM from user profile")
    @allure.title("Start DM from user profile")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("chat_between", [
        ['user_bob', 'user_alice']
    ])
    @pytest.mark.regression
    def test_start_chat_on_profile_page(self, user: AuthenticatedUser, chat_between,
                                        cleanup_conversation_between_users):
        cleanup_conversation_between_users(chat_between[0], chat_between[1])

        searched_profile_name: str = chat_between[1].split("_")[1]
        sidebar = self.get_sidebar(user.page)
        sidebar.navigate_to("search")

        search_page = self.search_page(user.page)
        search_page.open()
        with allure.step("Search by name and open result"):
            searched_user: ProfilePage = search_page.search_area_set(search_by="Users") \
                .fill_search_input(searched_profile_name) \
                .submit_search() \
                .get_search_result_by_text(searched_profile_name)
            search_page.set_expected_result_url(searched_user)
            used_profile_page = search_page.click_on_chosen_result(searched_user)
        with allure.step(f"Check, that profile url contains '{searched_profile_name}'"):
            expected_url = search_page.chosen_result_url
            expect(used_profile_page.page).to_have_url(expected_url)

        used_profile_page.click_message_button()
        chat = ChatComponent(user.page)
        random_message: str = self.get_rand_data.generate_text(25)

        expect(chat.page).to_have_url(re.compile(".*messages"))
        chat.create_message_with_check(random_message)
        expect(chat._get_message_by_text(random_message)).to_be_visible()

    @allure.story("Unread messages badge")
    @allure.id("TC-MSG-003")
    @allure.testcase("Unread messages badge")
    @allure.title("Unread messages badge")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.regression
    def test_unread_messages_badge(self, user):
        sidebar = self.get_sidebar(user.page)
        expect(sidebar.get_notifications_badge()).to_be_visible()
        assert int(sidebar.get_notifications_badge().inner_text()) > 0

    @allure.story("Send a message")
    @allure.id("TC-MSG-004")
    @allure.testcase("Opening conversation marks as read")
    @allure.title("Opening conversation marks as read")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("another_user", ["user_alice"], indirect=True)
    @pytest.mark.parametrize("chat_with", [['user_bob','user_alice']])
    @pytest.mark.regression
    def test_auto_read_chat_after_opening(self, user, chat_with, another_user):
        random_message = self.get_rand_data.generate_text(25)
        sidebar = self.get_sidebar(user.page)
        sidebar.navigate_to("messages")
        messages_page = self.messages_page(user.page)

        recipient_name = chat_with[1].split("_")[1]
        chat_between_users = messages_page.search_conversation_flow(recipient_name)

        chat_between_users.create_message_with_check(random_message)
        chat_between_users.page.reload()
        expect(chat_between_users._get_message_by_text(random_message)).to_be_visible()

        user2_sidebar = self.get_sidebar(another_user.page)
        user2_sidebar.page.reload()
        total_message_unread_count = int(user2_sidebar.get_messages_badge().inner_text())
        user2_sidebar.navigate_to("messages")
        user2_messages_page = self.messages_page(another_user.page)

        user_2_chat_with_user_1: Locator = user2_messages_page.get_conversation_by_name_or_last_message(random_message)
        user_2_chat_unread_count:int = user2_messages_page.get_conversation_unread_count(user_2_chat_with_user_1)
        user_2_chat_with_user_1.click()

        if 1 <= total_message_unread_count and 1 <= user_2_chat_unread_count:
            new_total_unread_count = str(total_message_unread_count - user_2_chat_unread_count)
            expect(user2_sidebar.get_messages_badge()).to_have_text(new_total_unread_count)
        else:
            expect(user2_sidebar.get_messages_badge()).not_to_be_visible()
