import allure
import pytest
from allure_commons.types import Severity
from playwright.sync_api import expect

from base.base_test import BaseTest
from pages.feed_page.components.post_component import PostComponent


@allure.epic("Search")
@allure.feature("Search")
@allure.parent_suite("Search")
@pytest.mark.search
class TestSearch(BaseTest):


    @allure.story("Search user by name")
    @allure.testcase("Search user by name")
    @allure.id("TC-SRC-001")
    @allure.title("Search user by name")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("data_for_search", [["users", "alice_dev"]])
    @pytest.mark.regression
    def test_search_by_name(self, user, data_for_search):
        search_by, search_criteria = data_for_search[0], data_for_search[1]

        sidebar = self.get_sidebar(user.page)
        sidebar.navigate_to("search")

        search_page = self.search_page(user.page)
        used_profile_page = search_page.search_flow(search_by, search_criteria)
        with allure.step(f"Check, that profile url contains '{search_criteria}'"):
            expected_url = search_page.chosen_result_url
            expect(used_profile_page.page).to_have_url(expected_url)




    @allure.story("Search user by post content")
    @allure.testcase("Search user by post content")
    @allure.id("TC-SRC-002")
    @allure.title("Search user by post content")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_eve"], indirect=True)
    @pytest.mark.parametrize("data_for_search", [["posts", "Writing good documentation is an art form"]])
    @pytest.mark.regression
    def test_search_by_posts(self, user, data_for_search):
        search_by, searched_post_text = data_for_search[0], data_for_search[1]

        sidebar = self.get_sidebar(user.page)
        sidebar.navigate_to("search")

        search_page = self.search_page(user.page)
        post_page:PostComponent = search_page.search_flow(search_by, searched_post_text)
        with allure.step(f"Check, that post url is expected '{searched_post_text}'"):
            expected_url = search_page.chosen_result_url
            expect(post_page.page).to_have_url(expected_url)


    @allure.story("Search hashtags")
    @allure.testcase("Search hashtags")
    @allure.id("TC-SRC-003")
    @allure.title("Search hashtags")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("data_for_search", [["hashtags", "coding"]])
    @pytest.mark.regression
    def test_search_by_hashtags(self, user, data_for_search):
        search_by, searched_tag = data_for_search[0], data_for_search[1]

        sidebar = self.get_sidebar(user.page)
        sidebar.navigate_to("search")

        search_page = self.search_page(user.page)

        hashtags_page:PostComponent = search_page.search_flow(search_by, searched_tag)
        with allure.step(f"Check, that page has  expected url'"):
            expected_url = search_page.chosen_result_url
            expect(hashtags_page.page).to_have_url(expected_url)




    @allure.story("Search user by post content")
    @allure.testcase("Empty search results")
    @allure.id("TC-SRC-004")
    @allure.title("Empty search results")
    @allure.severity(Severity.MINOR)
    @pytest.mark.parametrize("user", ["user_eve"], indirect=True)
    @pytest.mark.parametrize("data_for_search", [[["users", "posts", "hashtags"], "zzzznonexistent"]])
    @pytest.mark.regression
    def test_search_no_results_state(self, user, data_for_search):
        search_by, searched_text = data_for_search[0], data_for_search[1]
        sidebar = self.get_sidebar(user.page)
        sidebar.navigate_to("search")

        search_page = self.search_page(user.page)
        search_page.fill_search_input(searched_text)\
            .submit_search()

        for search_area in search_by:
            search_page.search_area_set(search_area)
            expect(search_page.get_empty_state_info).to_have_text(f"No {search_area} found")


