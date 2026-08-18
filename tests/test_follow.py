import allure
import pytest
from allure_commons.types import Severity
from playwright.sync_api import expect

from base.base_test import BaseTest
from helpers.api_helper import ApiHelper


@allure.epic("Follows")
@allure.feature("Follows")
@allure.parent_suite("Follows")
class TestFollow(BaseTest):

    @allure.story("Follow/unfollow a public user")
    @allure.testcase("Follow a public user")
    @allure.id("TC-FOL-001")
    @allure.title("Follow a public user")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.smoke
    @pytest.mark.parametrize("follow_user", ['alice_dev'])
    @pytest.mark.flaky(reruns=2)
    def test_follow_public_user(self, user, follow_user):
        api: ApiHelper = self.get_api_helper
        api.unfollow_user(
            token=user.token,
            user_name=follow_user
        )

        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("search")

        search_page = self.search_page(user.page)
        user_page = search_page.search_flow("users", follow_user)
        user_page.follow_unfollow_user()

        # with user_page.page.expect_response(
        #         lambda response: f"{follow_user}/follow" in response.url and response.request.method == "POST"
        # ) as response_info:
        #     response = response_info.value
        #     assert response.ok

    @allure.story("Follow/unfollow a public user")
    @allure.testcase("Unfollow a user")
    @allure.id("TC-FOL-003")
    @allure.title("Unfollow a user")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.regression
    @pytest.mark.parametrize("unfollow_user", ['alice_dev'])
    @pytest.mark.flaky(reruns=2)
    def test_unfollow_public_user(self, user, unfollow_user):
        api: ApiHelper = self.get_api_helper
        api.follow_user(
            token=user.token,
            user_name=unfollow_user
        )

        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("search")

        search_page = self.search_page(user.page)
        user_page = search_page.search_flow("users", unfollow_user)
        user_page.follow_unfollow_user()

        # with user_page.page.expect_response(
        #         lambda response: f"{unfollow_user}/follow" in response.url and response.request.method == "DELETE"
        # ) as response_info:
        #     response = response_info.value
        #     assert response.ok

    @allure.story("'Follows you' indicator")
    @allure.testcase("'Follows you' indicator")
    @allure.id("TC-FOL-004")
    @allure.title("'Follows you' indicator")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("follower", [['alice', 'bob']])
    @pytest.mark.parametrize("user", ["user_alice"], indirect=True)
    @pytest.mark.parametrize("another_user", ["user_bob"], indirect=True)
    @pytest.mark.regression
    def test_follow_you_indicator(self, user, another_user, follower):
        # session 1
        user1_side_bar = self.get_sidebar(user.page)
        user1_side_bar.navigate_to("search")
        user1_search_page = self.search_page(user.page)
        user1_profile_of_user2 = user1_search_page.search_flow("users", follower[1])
        if not user1_profile_of_user2.follow_mark.is_visible():
            # session 2
            user2_side_bar = self.get_sidebar(another_user.page)
            user2_side_bar.navigate_to("search")
            user2_search_page = self.search_page(another_user.page)
            user2_profile_of_user1 = user2_search_page.search_flow("users", follower[0])
            user2_profile_of_user1.follow_unfollow_user()
            user1_profile_of_user2.page.reload(wait_until="networkidle")
        expect(user1_profile_of_user2.follow_mark).to_be_visible()

    @allure.story("Follow/unfollow a public user")
    @allure.testcase("Followers and following lists")
    @allure.id("TC-FOL-005")
    @allure.title("Followers and following lists")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.regression
    @pytest.mark.parametrize("follow_user", ['alice_dev'])
    @pytest.mark.flaky(reruns=2)
    def test_check_follower_followers_stats(self, user, follow_user):
        side_bar = self.get_sidebar(user.page)
        side_bar.navigate_to("search")

        search_page = self.search_page(user.page)
        user_page = search_page.search_flow("users", follow_user)

        user_page.open_profile_following_page()
        following_count_at_page: int = user_page.get_users_list_count_at_page()
        user_page.page.go_back()
        expect(user_page.get_total_following).to_have_text(str(following_count_at_page))

        user_page.open_profile_followers_page()
        followers_count_at_page: int = user_page.get_users_list_count_at_page()
        user_page.page.go_back()
        expect(user_page.get_total_follower()).to_have_text(str(followers_count_at_page))
