import re
import allure
from playwright.sync_api import Locator, Page, expect

from base.base_page import BasePage
from config.urls import Links
from pages.feed_page.components.post_component import PostComponent
from pages.profile_page.profile_page import ProfilePage


class SearchPage(BasePage):
    _PAGE_URL = Links.SEARCH_URL

    def __init__(self, page: Page):
        """
        Initialization of SearchPage, that accepted playwright page object
        :param page: playwright page object
        """

        super().__init__(page)
        self.chosen_search_area: str = "users"
        self.chosen_result_url: str

    @allure.step("Define search area")
    def search_area_set(self, search_by: str):
        """
        Method to specify search area
        :param search_by: specified search area
        :return:
        """
        self.chosen_search_area = search_by.lower()
        self.page.get_by_role("button", name=f"{search_by.capitalize()}").click()
        return self

    @property
    def get_empty_state_info(self) -> Locator:
        """Method to return locator with empty state info"""
        return self.page.locator("main p")

    @property
    @allure.step("Collect all search results")
    def get_search_results(self) -> Locator:
        """
        Method to return locator with search results list depending on actual search area
        :return: Locator with search results list
        """
        if self.chosen_search_area == "posts":
            return self.page.get_by_test_id(re.compile(r"^post-card-[^-]+$"))
        return self.page.locator("main a")

    @allure.step("Get search result by text")
    def get_search_result_by_text(self, text_at_result: str) -> Locator:
        """
        Method to get search result from list, filtered using provided text_at_result param
        :param text_at_result: provided text used in filtration
        :return: Locator from list with results
        """
        return self.get_search_results.filter(has_text=text_at_result)

    @allure.step("Get search result by index")
    def get_search_result_by_index(self, index: int):
        """
        Method to get search result from list, picked using provided index
        :param index: number of result in list
        :return: Locator of picked result
        """
        return self.get_search_results.nth(index - 1)

    @allure.step("Set expected search results list")
    def set_expected_result_url(self, chosen_result):
        """
        Method to set expected result url depending on provided result (locator)
        :param chosen_result: Locator of expected result
        :return:
        """
        if self.chosen_search_area in ["users", "hashtags"]:
            self.chosen_result_url = Links.HOST + chosen_result.get_attribute("href")
        elif self.chosen_search_area == "posts":
            post_url = chosen_result.get_by_test_id(re.compile(r"^post-comment-btn-[^-]+$")).get_attribute("href")
            self.chosen_result_url = Links.HOST + post_url
        return self

    @allure.step(f"Fill search input")
    def fill_search_input(self, search_text: str):
        """
        Method to fill search input
        :param search_text: text to fill search input
        :return:
        """
        self.page.get_by_test_id("nav-search-input").fill(search_text)
        return self

    @allure.step(f"Submit search")
    def submit_search(self):
        """
        Method to submit search clicking on corresponding button
        :return:
        """
        self.page.get_by_role("button", name="Search").click()
        return self

    @allure.step(f"Click on search result")
    def click_on_chosen_result(self, searched_element: Locator):
        """
        Method to click on chosen search result and return corresponding page object
        :param searched_element: Locator of chosen search result
        :return:
        """
        if self.chosen_search_area == "posts":
            searched_element.get_by_test_id(re.compile(r"^post-comment-btn-[^-]+$")).click()
            expect(self.page).to_have_url(self.chosen_result_url)
            return PostComponent(self.page, searched_element)
        searched_element.click()
        return ProfilePage(self.page, profile_url=self.chosen_result_url)

    def search_flow(self, search_area: str, search_criteria: str):
        with allure.step(f"Search '{search_criteria}' at '{search_area}' area"):
            search_result = self.search_area_set(search_by=search_area) \
                .fill_search_input(search_criteria) \
                .submit_search() \
                .get_search_result_by_index(1)
            self.set_expected_result_url(search_result)
            result = self.click_on_chosen_result(search_result)
        return result
