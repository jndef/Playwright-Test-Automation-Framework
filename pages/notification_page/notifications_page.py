import allure
from playwright.sync_api import Locator, Page

from base.base_page import BasePage
from config.urls import Links
from pages.feed_page.components.post_component import PostComponent
from pages.messages_page.page import MessagesPage
from pages.profile_page.profile_page import ProfilePage


class NotificationsPage(BasePage):
    _PAGE_URL = Links.NOTIFICATIONS_URL

    def __init__(self, page: Page):
        """
        Init NotificationsPage object, that accepted playwright page object
        :param page: playwright page object
        """
        super().__init__(page)
        self.picked_notification: Locator
        self.picked_notification_url: str = ""

    @property
    def _get_notifications_list(self) -> Locator:
        """
        Internal method. Get notifications list as Locator
        :return:
        """
        return self.page.locator("main a")

    def get_notification_by_index(self, order_number: int):
        """
        Method to get notification from list, picked by provided index  (Locator) and set it up as picked notification
        :param order_number: provided number of notification in the list
        :return:
        """
        self.picked_notification = self._get_notifications_list.nth(order_number - 1)
        return self

    @allure.step("Get notification source")
    def go_to_notification_target(self):
        """
        Method to navigate to notification target (factory) depending on notification url
        :return:
        """
        self.click_on_notification()
        if "/post/" in self.page.url:
            return PostComponent(self.page, self.page.get_by_role("article"))
        elif "/profile/" in self.page.url:
            return ProfilePage(self.page, self.page.url)
        elif "/messages/" in self.page.url:
            return MessagesPage(self.page)
        raise ValueError(f"Unrecognized notification target: {self.page.url}")

    def get_notification_url(self):
        """
        Method gets notification url and set it up as picked notification url
        :return:
        """
        self.picked_notification_url = self.picked_notification.get_attribute("href")
        return self

    @allure.step("Click on notification")
    def click_on_notification(self):
        """
        Method to click on picked notification (Locator)
        :return:
        """
        self.picked_notification.click()
        return self

    def is_unread_all(self) -> bool:
        """
        Method to check if all notifications from the list are read or not
        :return: boolean
        """
        notifications = self._get_notifications_list.locator("div[data-testid]")
        count = notifications.count()
        if all(self.is_read(notifications.nth(index)) is False for index in range(count)):
            return True
        return False

    @staticmethod
    def is_read(notification: Locator = None) -> bool:
        """Method to check if notification is read or not
        :param notification: provided notification locator
        :return: boolean
        """
        if "bg-brand-50/50" not in notification.get_attribute("class"):
            return True
        return False

    def get_total_unread_badge(self) -> Locator:
        """
        Method to get total unread badge (Locator)
        :return:
        """
        return self.page.get_by_test_id("notifications-unread-badge")

    def get_total_unread_count(self) -> int:
        """
        Get total unread count value (int)
        :return: unread count value (int)
        """
        badge = self.page.get_by_test_id("notifications-unread-badge")
        return int(badge.text_content()) if badge.text_content() else 0

    @allure.step("Click and read all notifications")
    def read_all_notification_with_check(self):
        """
        Method to read all notification. Includes check corresponding request
        :return:
        """
        with self.page.expect_response(
                lambda response: "/read-all" in response.url and response.request.method == "POST"
        ) as response_info:
            self.page.get_by_test_id("notifications-mark-all-btn").click()
            response = response_info.value
            assert response.ok

    def filter_show_only_unread(self):
        """
        Method to filter unread notifications (unread only) and check corresponding request
        :return:
        """
        with self.page.expect_response(
                lambda response: "/notifications?is_read=false" in response.url and response.request.method == "GET"
        ) as response_info:
            self.page.get_by_test_id("notifications-filter-unread").click()
            response = response_info.value
            assert response.ok

    def filter_show_all(self):
        """
        Method to filter unread notifications (all) and check corresponding request
        :return:
        """
        with self.page.expect_response(
                lambda response: "/notifications" in response.url and response.request.method == "GET"
        ) as response_info:
            self.page.get_by_test_id("notifications-filter-all").click()
            response = response_info.value
            assert response.ok
