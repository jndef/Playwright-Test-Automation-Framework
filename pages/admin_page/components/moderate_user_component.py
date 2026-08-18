import re
import allure
from playwright.sync_api import Page, Locator, expect
from base.base_component import BaseComponent


class ModerateUserComponent(BaseComponent):

    def __init__(self, page: Page, root: Locator):
        """
        Init ModerateUserComponent. Required playwright page object and locator of certain user at page
        :param page: Playwright page object
        :param root: Locator of user at the page
        """
        super().__init__(page)
        self.user_root_component: Locator = root

    @allure.step("Click on verify button")
    def admin_click_on_verify_button(self):
        """
        Method to click on verify button (for admin). Performed verification/undo verification request for certain user and check corresponding API request + check changes in UI
        :return:
        """
        verify_button = self.user_root_component.get_by_test_id(re.compile(r"^admin-verify-btn-[^-]+$"))
        verify_button_text: str = verify_button.text_content()

        with self.page.expect_response(
                lambda response: "/admin/users" in response.url and response.request.method == "PATCH"
        ) as response_info:
            verify_button.click()
            response = response_info.value
            request = response.request
            # Get JSON from response
            response_body = response.json()
            # (Optional) Get request body
            request_body = request.post_data_json
            assert response.ok, f"Error. Verify user request has status code {response.status}\nResponse: {response.text}"
            self.is_completed()
        if verify_button_text == "Verify":
            with allure.step("Check. Verify users status at request"):
                assert request_body["is_verified"] == True
            with allure.step("Check. Verify users status at response"):
                assert response_body["is_verified"] == True
            with allure.step("Check. Button text has been updated"):
                expect(verify_button).to_have_text("Verified")
            with allure.step("Check. Verify label has been added"):
                expect(self.user_root_component.locator("span.text-brand-500")).to_be_visible()
        elif verify_button_text == "Verified":
            with allure.step("Check verified users status at request"):
                assert request_body[
                           "is_verified"] == False, f"Error, request. ER: False. AR: {request_body['is_verified']}"
            with allure.step("Check verified users status at response"):
                assert response_body[
                           "is_verified"] == False, f"Error, response. ER: False. AR: {response_body['is_verified']}"
            with allure.step("Check. Button text has been updated"):
                expect(verify_button).to_have_text("Verify")
            with allure.step("Check. Verify label has been removed"):
                expect(self.user_root_component.locator("span.text-brand-500")).not_to_be_visible()

    @allure.step("Click on ban button")
    def admin_click_on_ban_button(self):
        """
        Click on ban button (for admin). Performed ban request for certain user + check corresponding API request + check changes in UI
        :return:
        """
        ban_button = self.user_root_component.get_by_test_id(re.compile(r"^admin-ban-btn-[^-]+$"))
        ban_button_text: str = ban_button.text_content()
        with self.page.expect_response(
                lambda response: "/admin/users" in response.url and response.request.method == "PATCH"
        ) as response_info:
            ban_button.click()
            response = response_info.value
            request = response.request
            # Get JSON from response
            response_body = response.json()
            # (Optional) Get request body
            request_body = request.post_data_json

            assert response.ok, f"Error. Ban user request has status code {response.status}\nResponse: {response.text}"
            self.is_completed()
        if ban_button_text == "Ban":
            with allure.step("Check. Ban status value at request"):
                assert request_body["is_active"] == False
            with allure.step("Check. Ban status value at response"):
                assert response_body["is_active"] == False
            with allure.step("Check. Ban text label is visible"):
                expect(self.user_root_component.locator("span.text-red-500")).to_be_visible()
            with allure.step("Check. Ban text label has expected text"):
                expect(self.user_root_component.locator("span.text-red-500")).to_have_text("[BANNED]")
            with allure.step("Check. Button text has been updated"):
                expect(ban_button).to_have_text("Unban")

        elif ban_button_text == "Unban":
            with allure.step("Check. Ban status value at request"):
                assert request_body["is_active"] == True
            with allure.step("Check. Ban status value at response"):
                assert response_body["is_active"] == True
            with allure.step("Check. Button text has been updated"):
                expect(ban_button).to_have_text("Ban")
            with allure.step("Ban text label is not visible"):
                expect(self.user_root_component.locator("span.text-red-500")).not_to_be_visible()

    @allure.step("Update user's role")
    def admin_select_new_users_role(self, new_role: str):
        """
        Select new role for certain user (for admin). Performed ban request for certain user + check corresponding API request + check changes in UI
        :return:
        """
        if new_role not in ["admin", "moderator", "user"]:
            raise ValueError("Invalid role")
        select_role = self.user_root_component.get_by_test_id(re.compile(r"^admin-role-select-[^-]+$"))
        with self.page.expect_response(
                lambda response: "/admin/users" in response.url and response.request.method == "PATCH"
        ) as response_info:
            select_role.click()
            select_role.select_option(new_role.lower())
            response = response_info.value
            request = response.request
            # Get JSON from response
            response_body = response.json()
            # (Optional) Get request body
            request_body = request.post_data_json
            with allure.step("Check changed role"):
                assert response.ok, f"Error. Change user's role request has status code {response.status}\nResponse: {response.text}"
            self.is_completed()
            with allure.step("Check. New user's role value at request"):
                assert request_body["role"] == new_role.lower()
            with allure.step("Check. New user's role value at response"):
                assert response_body["role"] == new_role.lower()
