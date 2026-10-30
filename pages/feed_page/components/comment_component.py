from __future__ import annotations
import random
import re
import allure
from playwright.sync_api import Page, Locator, expect
from base.base_component import BaseComponent
from pages.feed_page.components.publish_comment_component import PublishCommentComponent


class CommentComponent(BaseComponent):

    def __init__(self, page: Page, root: Locator):
        """
        Init CommentComponent, that required page locator object and locator of the comment as root
        :param page: Playwright Page object
        :param root: Locator of the comment component
        """
        super().__init__(page)
        self.comment_locator: Locator = root
        self._comment_body = self.comment_locator.locator("//p")
        self._like_button = self.comment_locator.locator("[data-testid^='comment-like-btn-']")
        # self._like_button = self.comment_locator.get_by_test_id(re.compile(r"^comment-like-btn-[^-]+$"))
        self._reply_button = self.comment_locator.get_by_test_id(re.compile(r"^comment-reply-btn-[^-]+$"))
        self._reply_wrappers = self.comment_locator.locator(
            "xpath=following-sibling::div[contains(@class,'ml-8')]"
        )
        self._direct_replies = self._reply_wrappers.locator("> div[data-testid^='comment-']")

    @allure.step("Create reply to comment")
    def create_reply(self, reply_text: str = None):
        """
        Method, that create reply to comment using PublishCommentComponent inside (not required to specify it)/. Included check of corresponding API request
        :param reply_text: provided text of a new reply (Optional). If param isn't provided, method will generate random
        :return:
        """
        if reply_text is None:
            reply_text = self.get_rand_data.generate_text(30)
        with self.page.expect_response(
                lambda response: "/replies" in response.url and response.request.method == "POST"
        ) as response_info:
            PublishCommentComponent(self.page) \
                .fill_comment_input(reply_text) \
                .publish_comment()
        response = response_info.value
        request = response.request

        # Get JSON from response
        response_body = response.json()
        # (Optional). Get request body
        request_body = request.post_data_json
        assert response_body["content"] == reply_text
        assert request_body["content"] == reply_text
        # print(
        #     f"✅ Success request\n {response.request.method} {response.url} - {response.status}\nRequest payload: {request_body}\nResponse payload: {response_body}")

    def is_liked_state_comment(self) -> bool:
        """
        Method, that check if comment is liked or not depends on certain class of the comment locator (uses root comment locator)
        :return: boolean
        """
        like_button = self._like_button
        post_like_property = like_button.get_attribute("class")
        if "text-gray-400 hover:text-red-500" not in post_like_property:
            return True
        return False

    def like_comment_count(self) -> str:
        """
        Method, that returns if likes count of the comment (uses root comment locator)
        :return: count of likes (str)
        """
        return self.comment_locator.get_by_test_id(re.compile(r"^comment-like-btn-[^-]+$")).inner_text()
        # return int(self._like_button.inner_text())

    def click_like_comment(self):
        """
        Method performed like/remove like comment (uses root comment locator). Includes API request check depends on case (like/remove like) and like count after in UI
        :return:
        """
        like_button = self.comment_locator.get_by_test_id(re.compile(r"^comment-like-btn-[^-]+$"))
        old_count: int = int(like_button.inner_text())
        comment_is_liked_before: bool = self.is_liked_state_comment()
        if not comment_is_liked_before:
            with self.page.expect_response(
                    lambda response: "/like" in response.url and response.request.method == "POST"
            ) as response_info:
                like_button.click()
                response = response_info.value
                assert response.ok
                with allure.step("Like comment"):
                    expect(self._like_button).to_have_text(str(old_count + 1), use_inner_text=True)
        else:
            with self.page.expect_response(
                    lambda response: "/like" in response.url and response.request.method == "DELETE"
            ) as response_info:
                like_button.click()
                response = response_info.value
                assert response.ok
            with allure.step("Remove like from comment"):
                self.comment_locator.hover()
                expect(self._like_button).to_have_text(str(old_count - 1), use_inner_text=True)

    def get_comment_with_replies(self, certain_index: int = None) -> CommentComponent | None:
        """
        Method, that returns comment with replies list (Locator)
        :param certain_index: (Optional) Allows to specify number of the comment in corresponding list
        :return: return certain comment as CommentComponent
        """
        comments: Locator = self._direct_replies
        comments_with_replies: list[Locator] = []
        for index in range(comments.count()):
            if comments.nth(index).get_by_role("button").nth(2).is_visible():
                comments_with_replies.append(comments.nth(index))
        if len(comments_with_replies) == 0:
            return None
        if certain_index is not None:
            if certain_index > len(comments_with_replies):
                certain_index = len(comments_with_replies)
            return CommentComponent(self.page, comments_with_replies[certain_index - 1].locator("div"))
        return CommentComponent(self.page, random.choice(comments_with_replies).locator("div"))

    @allure.step("Click reply comment button")
    def click_reply_btn(self):
        """
        Method performed click on the button to start adding a new reply
        :return:
        """
        self._reply_button.click()

    @allure.step("Click load replies button")
    def click_load_more_replies(self):
        """
        Method performed click on the button to load more replies to certain comment (root comment locator)
        :return:
        """
        self.comment_locator.locator("//button[contains(@class,'hover:underline')]").click()

    @allure.step("Get reply by index")
    def get_reply_by_index(self, index: int) -> CommentComponent:
        """
        Method performed get reply by index from list (Locator)
        :param index: number of the reply
        :return: certain comment as CommentComponent
        """
        return CommentComponent(self.page, self._direct_replies.nth(index - 1))

    @allure.step("Get reply by text")
    def get_reply_by_text(self, comment_text: str) -> CommentComponent:
        """
        Method performed get reply by text from list (Locator)
        :param comment_text: text of reply used in filtration (has_text)
        :return: certain comment as CommentComponent
        """
        return CommentComponent(self.page, self._direct_replies.filter(has_text=comment_text))
