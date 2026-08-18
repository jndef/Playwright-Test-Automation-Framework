import allure
from playwright.sync_api import Page, Locator
from base.base_component import BaseComponent


class PublishCommentComponent(BaseComponent):

    def __init__(self, page: Page):
        super().__init__(page)
        """
        Init PublishCommentComponent, allows to perform comment publishing
        """
        self._comment_input: Locator = self.page.get_by_test_id("comment-input")
        self._publish_button: Locator = self.page.get_by_test_id("comment-submit-btn")

    @allure.step("Enter text at comment input")
    def fill_comment_input(self, text_data: str = None):
        """
        Fill comment input with text data
        :param text_data: text to fill at comment input. If not specified, method will generate a random text
        :return:
        """
        if text_data is None:
            text_data = self.get_rand_data.generate_text()
        self._comment_input.type(text_data)
        return self

    @allure.step("Submit comment publishing")
    def publish_comment(self):
        """
        Method to submit comment publishing
        :return:
        """
        self._publish_button.click()
        self.is_completed()
        return self
