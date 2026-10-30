import re

import allure
import pytest
from allure_commons.types import Severity
from playwright.sync_api import expect

from base.base_test import BaseTest


@allure.epic("Notifications")
@allure.feature("Notifications")
@allure.parent_suite("Notifications")
@pytest.mark.notifications
class TestNotifications(BaseTest):

    @allure.story("Unread badge in sidebar")
    @allure.testcase("Unread badge in sidebar")
    @allure.id("TC-NOT-001")
    @allure.title("Unread badge in sidebar")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.smoke
    def test_check_notifications_badge(self, user):
        notification_badge_element = self.get_sidebar(user.page).get_notifications_badge()
        expect(notification_badge_element).to_be_visible()

    @allure.story("Mark all as read")
    @allure.testcase("Mark all as read")
    @allure.id("TC-NOT-002")
    @allure.title("Mark all as read")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("mark_unread_all", ["user_bob"], indirect=True)
    @pytest.mark.regression

    def test_read_all_notifications(self, mark_unread_all, user):
        sidebar = self.get_sidebar(user.page)

        sidebar.navigate_to("notifications")
        notification_page = self.notifications_page(user.page)

        expect(notification_page.get_total_unread_badge()).to_be_visible()
        expect(sidebar.get_notifications_badge()).to_be_visible()

        notification_page.read_all_notification_with_check()
        expect(notification_page.get_total_unread_badge()).not_to_be_visible()
        expect(sidebar.get_notifications_badge()).not_to_be_visible()
        assert not notification_page.is_unread_all()

    @allure.story("Filter unread only")
    @allure.testcase("Filter unread only")
    @allure.id("TC-NOT-003")
    @allure.title("Filter unread only")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("mark_unread_all", ["Admin"], indirect=True)
    @pytest.mark.regression
    def test_show_only_unread_notifications(self, mark_unread_all, user):
        sidebar = self.get_sidebar(user.page)

        sidebar.navigate_to("notifications")
        notification_page = self.notifications_page(user.page)
        notification_page.filter_show_only_unread()
        assert notification_page.is_unread_all()
        notification_page.filter_show_all()

    @allure.story("Click notification navigates")
    @allure.testcase("Click notification navigates")
    @allure.id("TC-NOT-004")
    @allure.title("Click notification navigates")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("mark_unread_all", ["Admin"], indirect=True)
    @pytest.mark.smoke
    def test_click_notification_navigates(self, mark_unread_all, user):
        # Precondition - Get Login as alice_dev who has unread notifications (seed data).
        sidebar = self.get_sidebar(user.page)
        sidebar.navigate_to("notifications")

        notification_page = self.notifications_page(user.page)

        post_page = notification_page.get_notification_by_index(1) \
            .get_notification_url() \
            .go_to_notification_target()

        expect(post_page.page).to_have_url(re.compile(rf".*{notification_page.picked_notification_url}"))

    @allure.story("Click notification navigates")
    @allure.testcase("Click notification navigates")
    @allure.id("TC-NOT-004")
    @allure.title("Click notification navigates")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("another_user", ["user_alice"], indirect=True)
    @pytest.mark.parametrize("post_author", ["bob"])
    @pytest.mark.parametrize("mark_unread_all", ["user_bob"], indirect=True)
    @pytest.mark.smoke
    @pytest.mark.like
    @pytest.mark.flaky(reruns=2)
    def test_get_notification_on_post_like(self, user, another_user, post_author, mark_unread_all):
        rand_post_body: str = self.get_rand_data.generate_text(45)

        user1_sidebar = self.get_sidebar(user.page)

        user1_notification_badge = user1_sidebar.get_notifications_badge()
        user1_notification_count = int(user1_notification_badge.inner_text())
        user1_feed_page = self.feed_page(user.page)
        user1_feed_page.create_post_with_check(post_text=rand_post_body)

        user2_sidebar = self.get_sidebar(another_user.page)
        user2_sidebar.navigate_to("search")
        user2_search_page = self.search_page(another_user.page)
        founded_post = user2_search_page.search_flow(search_area="posts", search_criteria=rand_post_body)
        founded_post.like_unlike_post()

        # user1_sidebar.navigate_to("notifications")
        user1_feed_page.page.reload()
        expect(user1_sidebar.get_notifications_badge()).to_be_visible()
        expect(user1_sidebar.get_notifications_badge()).to_have_text(str(user1_notification_count + 1))
