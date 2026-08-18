import re
import allure
from playwright.sync_api import Page, Locator
from base.base_components.alert_component import AlertComponent
from base.base_page import BasePage


class ContentModerationPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def _moderation_get_posts_lists(self) -> Locator:
        """
        Internal method (admin only). Returns list of posts lists
        :return: Locator with existed posts lists
        """
        return self.page.locator("div.card")

    def moderation_get_post_by_index(self, index: int) -> Locator:
        """
        Method (admin only) to return certain Locator from post list by index
        :param index: number of certain Locator to return
        :return: Specified locator from list (Locator)
        """
        return self._moderation_get_posts_lists.nth(index - 1)

    def moderation_get_post_by_text(self, post_text: str) -> Locator:
        """
        Method (admin only) to return certain Locator from post list by post text (body, author name)
        :param post_text: text used in filtration (has text)
        :return: Specified locator from list (Locator) by post text (body and author name)
        """
        return self._moderation_get_posts_lists.filter(has_text=post_text)

    @property
    def _moderation_get_posts_active_lists(self) -> Locator:
        """
        Internal method (admin only). Returns list of posts lists (not deleted)
        :return: Locator with existed posts lists (Locator)
        """
        return self._moderation_get_posts_lists.filter(has_not_text="[DELETED]")

    def moderation_get_post_active_by_index(self, index: int) -> Locator:
        """
        Method (admin only) to return certain Locator from active post list by index
        :param index: number of certain Locator to return
        :return: Locator from active posts list (Locator) with certain index
        """
        return self._moderation_get_posts_active_lists.nth(index - 1)

    def moderation_get_post_active_by_text(self, post_text: str):
        """
        Method (admin only) to return certain Locator from active post list filtered by provided post text (post body)
        :param post_text: text used in filtration (has text)
        :return: Locator from active posts list (Locator) filtered by provided post text (post body)
        """
        return self._moderation_get_posts_active_lists.filter(has_text=post_text)

    @allure.step("Click on delete post action menu and confirm")
    def moderation_delete_post(self, chosen_post: Locator):
        """
        Method (admin only) to delete post action menu and confirm and check corresponding API request
        :param chosen_post: provided locator of the post, to be deleted (Locator)
        :return:
        """
        remove_button: Locator = chosen_post.get_by_test_id(re.compile(r"admin-delete-post-btn-[-a-f0-9]+$"))
        random_index = self.get_rand_data.generate_number()
        alert = AlertComponent(self.page)
        with self.page.expect_response(
                lambda response: "/admin/posts" in response.url and response.request.method == "DELETE"
        ) as response_info:
            remove_button.click()
            alert.click_and_accept_prompt(remove_button, f"reason number {random_index}")
            response = response_info.value
            assert response.ok
