import random
import re

import allure
from playwright.sync_api import Page, Locator, expect

from base.base_components.alert_component import AlertComponent
from base.base_component import BaseComponent
from config.urls import Links
from pages.feed_page.components.comment_component import CommentComponent
from pages.feed_page.components.publish_comment_component import PublishCommentComponent


class PostComponent(BaseComponent):
    _PAGE_URL = Links.FEED_URL

    def __init__(self, page: Page, root: Locator = None):
        """
        Init PostComponent, that requires page locator object and locator of the post as root
        :param page: Playwright Page object
        :param root: Locator of the post component
        """
        super().__init__(page)
        self.post_locator: Locator = root
        self.post_url = self._PAGE_URL

        self._body = self.post_locator.get_by_test_id(re.compile(r"^post-content-[^-]+$"))

        self._like_button = self.post_locator.get_by_test_id(re.compile(r"^post-like-btn-[^-]+$"))

        self._like_count = self.post_locator.get_by_test_id(re.compile(r"^post-likes-count-[^-]+$"))

        self._comment_button = self.post_locator.get_by_test_id(re.compile(r"^post-comment-btn-[^-]+$"))
        self._repost_button = self.post_locator.get_by_test_id(re.compile(r"^post-repost-btn-[^-]+$"))
        self._repost_count = self.post_locator.locator(".//span")

        self._post_image = self.post_locator.get_by_test_id("post-composer-image-preview").get_by_role("img")
        self._post_published_image = self.post_locator.get_by_alt_text("Post image")

        self._delete_post_action_button = self.post_locator.get_by_test_id(re.compile(r"^post-delete-btn-[^-]+$"))

        self._bookmark_button = self.post_locator.get_by_test_id(re.compile(r"^post-bookmark-btn-[^-]+$"))
        self._action_menu_button = self.post_locator.get_by_test_id(re.compile(r"^post-menu-btn-[^-]+$"))

    def open_post(self):
        """
        Method open post page
        :return:
        """
        with allure.step(f"Open the post {self._PAGE_URL}"):
            self._define_current_post_url()
            self._comment_button.click()
            self.page.wait_for_url(self.post_url)
            # print(f"Navigate to post page {self.post_url}")
            self.page.wait_for_load_state("networkidle")
            return self

    @allure.step("Click on post action menu")
    def click_on_post_actions_menu(self):
        """
        Method performed click on post action menu
        :return:
        """
        self._action_menu_button.click()
        return self

    def _get_post_link(self) -> str:
        """
        Internal method. Returns link to post page, placed at comment button locator
        :return: link to post (str)
        """
        return self._comment_button.get_attribute("href")

    def _define_current_post_url(self):
        """
        Internal method. Define current post url
        :return:
        """
        self.post_url = self._PAGE_URL + self._get_post_link()

    def _is_liked_state_post(self) -> bool:
        """
        Internal method. Returns true if post is liked, false otherwise
        :return: boolean
        """
        like_button: Locator = self._like_button
        post_like_property = like_button.get_attribute("class")
        if "text-gray-500" in post_like_property:
            return False
        return True

    def _get_post_likes_count(self) -> int:
        """
        Internal method. Get post likes count value (int)
        :return: count of likes (int)
        """
        return int(self._like_count.inner_text())

    def like_unlike_post(self):
        """
        Method, performed like/remove like post depending on initials state. Includes check of corresponding request and like count after
        :return:
        """
        post_likes_count_before: int = self._get_post_likes_count()
        post_is_liked_before: bool = self._is_liked_state_post()

        like_button: Locator = self._like_button

        if post_is_liked_before:
            with allure.step("Unlike post"):
                with self.page.expect_response(
                        lambda response: "/like" in response.url and response.request.method == "DELETE"
                ) as response_info:
                    like_button.click()
                    expect(self._like_button).to_have_text(str(post_likes_count_before - 1))

        else:
            with allure.step("Like post"):
                with self.page.expect_response(
                        lambda response: "/like" in response.url and response.request.method == "POST"
                ) as response_info:
                    like_button.click()
                expect(self._like_button).to_have_text(str(post_likes_count_before + 1))
        response = response_info.value
        assert response.ok

        assert post_is_liked_before != self._is_liked_state_post()

    @allure.step("Click on delete post action menu and confirm")
    def delete_post(self):
        """
        Method, performed post deletion. Includes check of corresponding request
        :return:
        """
        with self.page.expect_response(
                lambda response: "/post" in response.url and response.request.method == "DELETE"
        ) as response_info:
            alert = AlertComponent(self.page)
            alert.click_and_accept_alert(self._delete_post_action_button)
        response = response_info.value
        assert response.ok

    def is_post_bookmarked(self) -> bool:
        """
        Method checked if post bookmarked or not (True/False)
        :return: boolean value
        """
        bookmark_button_class: str = self._bookmark_button.get_attribute("class")
        if "text-brand-600 bg-brand-50" in bookmark_button_class:
            return True
        else:
            return False

    def bookmark_post(self):
        """
        Method, performed click on bookmark button. Includes check of corresponding request depends on bookmark case
        :return:
        """
        bookmark_post_status:bool = self.is_post_bookmarked()
        if bookmark_post_status:
            with allure.step("Unbookmark post"):
                with self.page.expect_response(
                        lambda response: "/bookmark" in response.url and response.request.method == "DELETE"
                ) as response_info:
                    self._bookmark_button.click()
                response = response_info.value
                assert response.ok
        else:
            with allure.step("Bookmark post"):
                with self.page.expect_response(
                        lambda response: "/bookmark" in response.url and response.request.method == "POST"
                ) as response_info:
                    self._bookmark_button.click()
                response = response_info.value
                # Get JSON response from request
                response_body = response.json()
                # (Optional) Get request body
                assert response_body["status"] == "bookmarked"

    @allure.step("Get post body text")
    def get_certain_post_body(self) -> str:
        """
        Get post body text (based on post root locator)
        :return: post body text (str)
        """
        return self._body.text_content().strip()

    @allure.step("Create comment")
    def create_comment(self, comment_text: str = None):
        """
        Method, performed create comment. Includes check of corresponding request
        :param comment_text: provided comment text (Optional). If it isn't specified, method will generate a random comment text
        :return:
        """
        if comment_text is None:
            comment_text = self.get_rand_data.generate_text(30)
        with self.page.expect_response(
                lambda response: "/comment" in response.url and response.request.method == "POST"
        ) as response_info:
            PublishCommentComponent(self.page) \
                .fill_comment_input(comment_text) \
                .publish_comment()
            response = response_info.value
            request = response.request

            # Get JSON response from request
            response_body = response.json()
            # (Optional) Get request body
            request_body = request.post_data_json
            assert response_body["content"] == comment_text
            assert request_body["content"] == comment_text
            # print(
            #     f"✅ Success request\n {response.request.method} {response.url} - {response.status}\nRequest payload: {request_body}\nResponse payload: {response_body}")

    @property
    def _get_comments_list(self) -> Locator:
        """
        Internal method. Returns list of comments as Locator
        :return: Comments list as Locator
        """
        locator = self.page.locator(".card[data-testid^='comment-']:visible")
        expect(locator.first).to_be_visible()
        # expect(self.page.get_by_test_id(re.compile(r"^comment-[^-]+$")).last).to_be_visible()
        return self.page.locator(".card[data-testid^='comment-']:visible")

    @allure.step("Get comment by index")
    def get_comment_by_index(self, index: int) -> CommentComponent:
        """
        Get comment by specified index from comments list as CommentComponent
        :param index: specified comment index
        :return: CommentComponent
        """
        return CommentComponent(self.page, self._get_comments_list.nth(index - 1))

    @allure.step("Get comment by text")
    def get_comment_by_text(self, comment_text: str) -> CommentComponent:
        """
        Get comment from comments list, filtered by provided comment_text (CommentComponent)
        :param comment_text: text of comment, used in filter (str)
        :return: CommentComponent of filtered comment by provided text
        """
        return CommentComponent(self.page, self._get_comments_list.filter(has_text=comment_text))

    def get_post_tags_list(self) -> Locator:
        """
        Get list of tags for certain post (depends on root post locator)
        :return: Locator with tags of certain post
        """
        return self.post_locator.locator("a.rounded-full")

    def get_comment_with_replies(self, certain_index: int = None) -> CommentComponent:
        """
        Method, returned comment with replies as CommentComponent
        :param certain_index: index of the comment in corresponding list (Optional). If it isn't specified, method will get random comment
        :return: CommentComponent
        """
        comments: Locator = self._get_comments_list
        comments_with_replies: list[Locator] = []
        for index in range(0, comments.count()):
            if comments.nth(index).get_by_role("button").nth(2).is_visible():
                comments_with_replies.append(comments.nth(index))
        if len(comments_with_replies) == 0:
            raise ValueError("Comment with replies were not found")
        if certain_index is not None:
            if certain_index > len(comments_with_replies):
                certain_index = len(comments_with_replies)
            return CommentComponent(self.page, comments_with_replies[certain_index - 1])

        return CommentComponent(self.page, random.choice(comments_with_replies))
