import re
import allure
from playwright.sync_api import Page, Locator, expect
from base.base_page import BasePage
from pages.admin_page.components.moderate_user_component import ModerateUserComponent


class UserManagementPage(BasePage):

    def __init__(self, page: Page):
        """
        Init UserManagementPage object with provided page
        :param page: playwright page object
        """
        super().__init__(page)

    @allure.step("Fill admin search user input")
    def admin_fill_search_user_input(self, user_name: str):
        """
        Method to fill admin search user input
        :param user_name: searched username
        :return:
        """
        self.page.get_by_test_id("admin-search-input").fill(user_name)
        expect(self.page.get_by_test_id("admin-search-input")).to_have_value(user_name)
        return self

    @allure.step("Submit admin search input")
    def admin_submit_search(self, track_search_criteria: str):
        """
        Method (admin only) to submit search using Enter key. Includes check of corresponding request
        :param track_search_criteria: provided searched info
        :return:
        """
        with self.page.expect_response(
                lambda response: f"/admin/users?search={track_search_criteria}" in response.url and response.request.method == "GET"
        ) as response_info:
            self.page.get_by_test_id("admin-search-input").press("Enter")
            response = response_info.value
            assert response.ok, f"Error. Search user request has status code {response.status}\nResponse: {response.text}"
            response_body = response.json()
            first_response_item: dict = response_body["items"][0]
            assert track_search_criteria in first_response_item["username"] or track_search_criteria in \
                   first_response_item[
                       "display_name"], f"{track_search_criteria} not found at 1st item or response is empty"
            return self

    @property
    def _admin_get_users_list(self) -> Locator:
        """
        Internal method (admin only) to get user list
        :return: Locator with users list
        """
        return self.page.get_by_test_id(re.compile(r"^admin-user-row-[^-]+$"))

    def admin_get_user_by_index(self, user_number_in_list: int) -> ModerateUserComponent:
        """
        Internal method (admin only) to get user by index from user list Locator
        :param user_number_in_list:
        :return: component of moderate user component (ModerateUserComponent)
        """
        return ModerateUserComponent(self.page, self._admin_get_users_list.nth(user_number_in_list - 1))

    def admin_get_user_by_text(self, user_text_info: str) -> ModerateUserComponent:
        """
        Internal method (admin only) to get user from user list Locator, filtered by user text info
        :param user_text_info: user's text info, used in filtration (has_text)
        :return: component of moderate user component (ModerateUserComponent)
        """
        return ModerateUserComponent(self.page, self._admin_get_users_list.filter(has_text=user_text_info))
