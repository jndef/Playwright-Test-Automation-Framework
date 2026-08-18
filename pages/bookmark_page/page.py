from playwright.sync_api import Page, Locator, expect
from base.base_page import BasePage
from config.urls import Links
from pages.feed_page.components.post_component import PostComponent


class BookmarkPage(BasePage):
    _PAGE_URL = Links.BOOKMARK_URL

    def __init__(self, page: Page):
        super().__init__(page)


    @property
    def get_bookmarked_posts_at_page(self) -> Locator:
        """
        Method to get posts at the page
        :return:
        """
        locator = self.page.locator("article")
        expect(locator.first).to_be_visible()
        return locator

    def get_bookmarked_post_by_text(self, post_text: str) -> PostComponent:
        """
        Method returns post (as PostComponent) from list of the posts at the page, filtered by provided post_text
        :param post_text: text of the post, used in filtration (has_text) (str)
        :return: PostComponent with root locator of picked post
        """
        return PostComponent(self.page, self.get_bookmarked_posts_at_page.filter(has_text=post_text))