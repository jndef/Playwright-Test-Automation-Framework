import allure
from playwright.sync_api import Locator, Page
from base.base_component import BaseComponent


class SideBarComponent(BaseComponent):
    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def get_messages_badge(self) -> Locator:
        """Get messages badge locator from sidebar"""
        return self.page.get_by_test_id("nav-messages-badge")


    def get_notifications_badge(self) -> Locator:
        """Get notification badge locator from sidebar"""
        return self.page.get_by_test_id("nav-notifications-badge")

    def _get_navigation_locator(self, navigate_to: str) -> Locator:
        """Sidebar navigation builder (locator) depending on tab name
        :param navigate_to:str - name of the tab to navigate to
        :return: Locator
        """
        sources = ['feed', 'explore', 'search', 'messages', 'notifications', 'bookmarks', 'profile', 'settings',
                   'admin']
        navigate_to = navigate_to.strip().lower()
        if navigate_to not in sources:
            raise KeyError(f"Page '{navigate_to}' not found")
        return self.page.get_by_test_id(f"nav-{navigate_to}")

    def navigate_to(self, navigate_to: str):
        """
        Action - navigate to specified tab
        :param navigate_to:str - name of the tab to navigate to
        :return:
        """
        with allure.step(f"Open page at sidebar: {navigate_to}"):
            locator_navigate_to: Locator = self._get_navigation_locator(navigate_to)
            locator_navigate_to.click()
