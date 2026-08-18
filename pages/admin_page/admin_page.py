import allure
from playwright.sync_api import Page, Locator

from base.base_page import BasePage
from config.urls import Links
from pages.admin_page.content_moderation_page import ContentModerationPage
from pages.admin_page.user_managent_page import UserManagementPage


class AdminPage(BasePage):
    # Url
    _PAGE_URL = Links.ADMIN_URL

    def __init__(self, page: Page):
        super().__init__(page)

    def get_metric_block(self, metric_name: str) -> Locator:
        """
        Method (for admin), worked as factory: returned metric block (Locator) based on metric_name
        :param metric_name: provided metric name (str)
        :return: Metric block (Locator)
        """
        metric_name = metric_name.lower().strip()
        if metric_name == "users":
            return self.page.get_by_test_id('admin-stats-users-count')
        elif metric_name == "posts":
            return self.page.get_by_test_id('admin-stats-posts-count')
        elif metric_name == "comments":
            return self.page.locator("div.card").nth(2)
        elif metric_name == "messages":
            return self.page.locator("div.card").nth(3)
        raise ValueError("Incorrect metric name")

    def get_stat_count(self, metric_name: str) -> Locator:
        """
        Method (for admin), that returns Locator with value of certain metric block
        :param metric_name: provided metric name (str)
        :return: value of metric block (Locator)
        """
        stat_count: Locator = self.get_metric_block(metric_name)
        return stat_count.locator("p.text-2xl.font-bold")

    @allure.step("Navigate to content moderation page")
    def open_content_moderation_page(self) -> ContentModerationPage:
        """
        Method (for admin) for navigation to content moderation page
        :return: object of content moderation page ContentModerationPage
        """
        content_moderation = self.page.locator("a.card").filter(has_text="Content Moderation")
        content_moderation.click()
        return ContentModerationPage(self.page)

    @allure.step("Navigate to user management page")
    def open_user_management_page(self) -> UserManagementPage:
        """
        Method (for admin) for navigation to user management page
        :return: object of user management page UserManagementPage
        """
        user_management = self.page.locator("a.card").filter(has_text="User Management")
        user_management.click()
        return UserManagementPage(self.page)
