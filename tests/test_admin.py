import re
import allure
import pytest
from allure_commons.types import Severity
from playwright.sync_api import expect, Locator
from base.base_test import BaseTest


@allure.epic("Admin")
@allure.feature("Admin")
@allure.parent_suite("Admin")
@pytest.mark.admin
class TestAdmin(BaseTest):

    @allure.story("Change role")
    @allure.testcase("Change role - user to admin")
    @allure.id("TC-ADM-003")
    @allure.title("Change role - user to admin")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("another_user", ["user_eve"], indirect=True)
    @pytest.mark.parametrize("change_role", [['eve', 'admin']])
    @pytest.mark.smoke
    def test_change_role(self, user, change_role, another_user):
        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("admin")
        admin_page = self.admin_page(user.page)
        user_management_page = admin_page.open_user_management_page()
        chosen_user_management = user_management_page.admin_fill_search_user_input(change_role[0]) \
            .admin_submit_search(track_search_criteria=change_role[0]) \
            .admin_get_user_by_index(1)
        chosen_user_management.admin_select_new_users_role(change_role[1])
        user2_side_bar = self.get_sidebar(another_user.page)
        user2_side_bar.page.reload()
        user2_side_bar.navigate_to("admin")

        # after
        chosen_user_management.admin_select_new_users_role("user")

    @allure.story("Ban/unban user")
    @allure.testcase("Ban user")
    @allure.id("TC-ADM-002")
    @allure.title("Ban user")
    @allure.severity(Severity.BLOCKER)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("ban_user", ['eve'])
    @pytest.mark.smoke
    def test_ban_user(self, user, ban_user):
        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("admin")
        admin_page = self.admin_page(user.page)
        user_management_page = admin_page.open_user_management_page()
        chosen_user_management = user_management_page.admin_fill_search_user_input(ban_user) \
            .admin_submit_search(track_search_criteria=ban_user) \
            .admin_get_user_by_index(1)
        chosen_user_management.admin_click_on_ban_button()

        # after - unban
        chosen_user_management.admin_click_on_ban_button()

    @allure.story("Ban/unban user")
    @allure.testcase("UnBan user")
    @allure.id("TC-ADM-011")
    @allure.title("UnBan user")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("unban_user", ['frank'])
    @pytest.mark.smoke
    def test_unban_user(self, user, unban_user):
        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("admin")
        admin_page = self.admin_page(user.page)
        user_management_page = admin_page.open_user_management_page()
        chosen_user_management = user_management_page.admin_fill_search_user_input(unban_user) \
            .admin_submit_search(track_search_criteria=unban_user) \
            .admin_get_user_by_index(1)
        chosen_user_management.admin_click_on_ban_button()

        # after - ban again
        chosen_user_management.admin_click_on_ban_button()

    @allure.story("Verify/unverify user")
    @allure.testcase("Verify user")
    @allure.id("TC-ADM-012")
    @allure.title("Verify user")
    @allure.severity(Severity.BLOCKER)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("verify_user", ['bob'])
    @pytest.mark.smoke
    def test_verify_user(self, user, verify_user):
        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("admin")
        admin_page = self.admin_page(user.page)
        user_management_page = admin_page.open_user_management_page()
        chosen_user_management = user_management_page.admin_fill_search_user_input(verify_user) \
            .admin_submit_search(track_search_criteria=verify_user) \
            .admin_get_user_by_index(1)
        chosen_user_management.admin_click_on_verify_button()

        # after
        chosen_user_management.admin_click_on_verify_button()

    @allure.story("Verify/unverify user")
    @allure.testcase("UnVerify user")
    @allure.id("TC-ADM-012")
    @allure.title("UnVerify user")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("unverify_user", ['alice'])
    @pytest.mark.smoke
    def test_unverify_user(self, user, unverify_user):
        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("admin")
        admin_page = self.admin_page(user.page)
        user_management_page = admin_page.open_user_management_page()
        chosen_user_management = user_management_page.admin_fill_search_user_input(unverify_user) \
            .admin_submit_search(track_search_criteria=unverify_user) \
            .admin_get_user_by_index(1)
        chosen_user_management.admin_click_on_verify_button()

        # after
        chosen_user_management.admin_click_on_verify_button()

    @allure.story("Admin/moderator can moderate posts content")
    @allure.testcase("Moderator soft-deletes post")
    @allure.id("TC-POST-006")
    @allure.title("Moderator soft-deletes post")
    @allure.severity(Severity.CRITICAL)
    @allure.epic("Feed")
    @allure.feature("Posts")
    @allure.parent_suite("Posts")
    @pytest.mark.parametrize("user", ["moderator"], indirect=True)
    @pytest.mark.regression
    @pytest.mark.post
    @pytest.mark.moderation
    def test_delete_post_at_moderation_page(self, user):
        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("admin")
        admin_page = self.admin_page(user.page)
        content_management_page = admin_page.open_content_moderation_page()
        expect(content_management_page.page).to_have_url(re.compile(r".*/admin/content"))
        moderated_post: Locator = content_management_page.moderation_get_post_active_by_index(1)
        content_management_page.moderation_delete_post(moderated_post)
        content_management_page.is_completed()

    @allure.story("Admin/moderator can moderate posts content")
    @allure.testcase("Dashboard shows stats")
    @allure.id("TC-ADM-001")
    @allure.title("Dashboard shows stats")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.smoke
    def test_check_dashboard_stats(self, user):
        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("admin")
        admin_page = self.admin_page(user.page)

        expect(admin_page.get_metric_block("posts")).to_be_visible()
        expect(admin_page.get_metric_block("comments")).to_be_visible()
        expect(admin_page.get_metric_block("messages")).to_be_visible()
        expect(admin_page.get_metric_block("users")).to_be_visible()
