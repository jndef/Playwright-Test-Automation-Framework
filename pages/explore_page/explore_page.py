import allure
from playwright.sync_api import Locator, Page, expect
from base.base_page import BasePage
from config.urls import Links
from pages.feed_page.page import FeedPage


class ExplorePage(BasePage):
    _PAGE_URL = Links.EXPLORE_URL

    def __init__(self, page: Page):
        super().__init__(page)

    def _get_trending_tags_list(self) -> Locator:
        """
        Internal method to get Locator with trending tags list
        :return: Locator with trending tags list at the page
        """
        return self.page.locator("div.card a.rounded-full")

    def get_certain_tag_by_text(self, tag_name: str) -> Locator:
        """
        Method to get Locator from trending tags list, filtered by tag name (has_text)
        :param tag_name: tag name, used in filtration
        :return: Locator from trending tags list, filtered by tag name
        """
        return self._get_trending_tags_list().get_by_text(tag_name, exact=True)

    def get_certain_tag_by_index(self, tag_number: int) -> Locator:
        """
        Method to get Locator from trending tag lists, filtered by tag number in the list
        :param tag_number: number of tag at trending tag list
        :return: Locator from trending tag lists, filtered by tag number
        """
        return self._get_trending_tags_list().nth(tag_number - 1)

    def get_trending_page_title_locator(self) -> Locator:
        """
        Method to get Locator of page title from trending page
        :return: Locator of corresponding block at the page
        """
        return self.page.locator("main h1")

    @allure.step("Click on trending tag")
    def open_trending_tag(self, trending_tag_name: str) -> FeedPage:
        """
        Method to click on trending tag and open page (Feed page object). Includes check GET request, contained corresponding tag name
        :param trending_tag_name: trending tag, to be clicked and opened
        :return: Feed page object with posts, contained corresponding trending tag at body
        """
        trending_tag: Locator = self.get_certain_tag_by_text(trending_tag_name)
        expected_url: str = trending_tag.get_attribute("href")

        with self.page.expect_response(
                lambda response: f"/posts?hashtag={trending_tag_name}&sort_by=likes_count&sort_order=desc" in response.url and response.request.method == "GET"
        ) as response_info:
            trending_tag.click()
            response = response_info.value
            request = response.request
            assert trending_tag_name in request.url and response.ok
        expect(self.page).to_have_url(expected_url)
        expect(self.get_trending_page_title_locator()).to_have_text(trending_tag_name)
        return FeedPage(self.page)
