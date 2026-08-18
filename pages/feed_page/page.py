import random
import re
import allure
from playwright.sync_api import Page, Locator, expect
from base.base_page import BasePage
from config.urls import Links
from pages.feed_page.components.post_component import PostComponent
from pages.feed_page.components.publish_post_component import PublishPostComponent


class FeedPage(BasePage):
    _PAGE_URL = Links.FEED_URL

    def __init__(self, page: Page):
        """
        Init FeedPage object, that accepted playwright page object
        :param page: playwright page object
        """
        super().__init__(page)

    @property
    def get_posts_at_page(self) -> Locator:
        """
        Method to get posts at the page
        :return:
        """
        locator = self.page.locator("article")
        expect(locator.first).to_be_visible()
        return locator

    @property
    def get_post_empty_state(self) -> Locator:
        """
        Method to get empty state (corresponding locator) of the post page (when post doesn't exist)
        :return: Locator
        """
        return self.page.locator("main div.text-center")

    def navigate_to_post_with_certain_url(self, post_url: str):
        """
        Method to navigate to specified post url
        :param post_url: provided post url
        :return:
        """
        self.page.goto(self._PAGE_URL + post_url)

    def get_post_by_index(self, index: int) -> PostComponent:
        """
        Method returns post (as PostComponent) with specified index from list of the posts at the page
        :param index: number in the list of the posts at the page
        :return: PostComponent with root locator of picked post
        """
        return PostComponent(self.page, self.get_posts_at_page.nth(index - 1))

    def get_post_by_text(self, post_text: str) -> PostComponent:
        """
        Method returns post (as PostComponent) from list of the posts at the page, filtered by provided post_text
        :param post_text: text of the post, used in filtration (has_text) (str)
        :return: PostComponent with root locator of picked post
        """
        return PostComponent(self.page, self.get_posts_at_page.filter(has_text=post_text))


    def _filter_posts_with_comments(self) -> list:
        """
        Internal method. Iterate existed posts and collect only posts with comments
        :return: list with posts (locator) with comments
        """
        posts: Locator = self.get_posts_at_page
        posts_with_comments = []
        for index in range(0, posts.count()):
            if int(posts.nth(index).get_by_test_id(re.compile(r"^post-comments-count-[^-]+$")).text_content()) > 0:
                posts_with_comments.append(posts.nth(index))
        return posts_with_comments

    def get_post_by_text_with_load_previous_posts(self, post_text):
        """
        Internal method. Iterate existed posts and collect only posts with certain body
        :return: post (locator) with certain body
        """
        first_match= None
        max_page = 8
        current_page = 1
        load_more_btn = self.page.get_by_role("button", name="Load more")
        while first_match is None and current_page <= max_page:
            first_match = self.get_post_by_text(post_text) if self.get_post_by_text(post_text).post_locator.is_visible() else None
            if first_match is not None:
                return first_match
            if load_more_btn.is_visible():
                load_more_btn.click()
                current_page += 1
            else:
                break
        raise ValueError(f"Searched post with text '{post_text}' not found")

    def _get_post_with_comments_load(self):
        """
        Internal method, that loaded new posts until at least one has comments
        :return:
        """
        posts_with_comments = self._filter_posts_with_comments()
        len_posts_with_comments: int = len(posts_with_comments)
        while len_posts_with_comments == 0:
            self.page.get_by_role("button", name="Load more").click()
            posts_with_comments = self._filter_posts_with_comments()
            len_posts_with_comments: int = len(posts_with_comments)
        return posts_with_comments

    def get_posts_with_comments(self, certain_index: int = None) -> PostComponent:
        """
        Method returns post as PostComponent from posts (have comments) lists, picked by index
        :param certain_index: (Optional) post index at the corresponding list of the posts (have comments)
        :return: PostComment with root locator of picked post
        """
        posts_with_comments = self._get_post_with_comments_load()
        if certain_index is not None:
            if certain_index > len(posts_with_comments):
                certain_index = len(posts_with_comments)
            return PostComponent(self.page, posts_with_comments[certain_index-1])
        return PostComponent(self.page, random.choice(posts_with_comments))

    @property
    def get_random_post_index(self) -> int:
        """
        Method to get random post index depending on list of the posts at the page
        :return: random post index (int)
        """
        posts_len = self.get_posts_at_page.count() - 1
        rand_post_index = self.get_rand_data.generate_number(0, posts_len)
        return rand_post_index

    def create_body_form(self):
        """
        Method, that returns Create Post component
        :return: PublishPostComponent
        """
        return PublishPostComponent(self.page)

    @allure.step("Create post")
    def create_post_with_check(self, post_text: str = None, attachment_file_names: list[str] = None):
        """
        Method to create post with specified text and attachment (optional). Includes check of corresponding request
        :param post_text: (optional) text of a new post. If it isn't specified, method will generate a random post body
        :param attachment_file_names: (optional) specified file name will attach image to post while creation
        :return:
        """
        if post_text is None:
            post_text = self.get_rand_data.generate_text(30)
        with self.page.expect_response(
                lambda response: "/posts" in response.url and response.request.method == "POST"
        ) as response_info:
            if attachment_file_names is None:
                PublishPostComponent(self.page) \
                    .add_post_body(post_text) \
                    .click_publish()
            else:
                PublishPostComponent(self.page) \
                    .add_post_body(post_text) \
                    .add_attachment_to_post(attachment_file_names) \
                    .click_publish()
            response = response_info.value
            request = response.request

            # Get JSON from response
            response_body = response.json()
            # (Optional) Get request body
            request_body = request.post_data_json
            assert response_body["content"] == post_text
            assert request_body["content"] == post_text
            if attachment_file_names is not None:
                assert "/uploads/images" in response_body["image_url"], f"Actual {response_body['image_url']}"
                assert "/uploads/images" in request_body["image_url"], f"Actual{request_body['image_url']}"
            # print(
            #     f"✅ Success request. {response.request.method} {response.url} - {response.status}\nRequest payload: {request_body}\nResponse payload: {response_body}")
