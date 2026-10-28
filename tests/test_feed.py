import re
import allure
import pytest
from allure_commons.types import Severity
from playwright.sync_api import expect

from base.base_test import BaseTest
from conftest import AuthenticatedUser
from helpers.api_helper import ApiHelper
from pages.feed_page.components.post_component import PostComponent
from pages.feed_page.components.publish_post_component import PublishPostComponent
from pages.feed_page.page import FeedPage


@allure.epic("Feed")
@allure.feature("Posts")
@allure.parent_suite("Posts")
@allure.title("Tests Feed")
@pytest.mark.feed
class TestFeed(BaseTest):

    @allure.story("Create a new post")
    @allure.testcase("Create a new post")
    @allure.id("TC-POST-001")
    @allure.title("Create a new post")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("post_body", [None])
    @pytest.mark.smoke
    @pytest.mark.post
    def test_create_new_post(self, user: AuthenticatedUser, post_body):
        used_post_body = post_body or self.get_rand_data.generate_text()
        feed_page = self.feed_page(user.page)
        feed_page.create_post_with_check(used_post_body)

        created_post = feed_page.get_post_by_text(used_post_body)
        expect(created_post.post_locator).to_be_visible()
        expect(created_post.post_locator).to_contain_text(used_post_body, use_inner_text=True)

    @allure.story("Get existed post")
    @allure.testcase("404 on non-existent resource")
    @allure.id("TC-EDGE-006")
    @allure.title("404 on non-existent resource")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("post_url", ["/post/00000000-0000-0000-0000-000000000999"])
    @pytest.mark.smoke
    @pytest.mark.post
    def test_navigate_to_not_existed_post(self, user: AuthenticatedUser, post_url):
        feed_page = self.feed_page(user.page)
        chosen_post_url = post_url or "/post/10000000-0000-0000-0000-000000000999"
        feed_page.navigate_to_post_with_certain_url(chosen_post_url)
        expect(feed_page.get_post_empty_state).to_be_visible()
        expect(feed_page.get_post_empty_state).to_have_text("Not found")

    @allure.story("Create a new post")
    @allure.testcase("Post at max length (2000 chars)")
    @allure.id("TC-POST-007")
    @allure.title("Post at max length (2000 chars)")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("max_post_body_length", [2000])
    @pytest.mark.regression
    @pytest.mark.post
    def test_create_new_post_with_max_body(self, user: AuthenticatedUser, max_post_body_length):
        max_length: int = max_post_body_length or 2001
        post_body = "A" * max_length
        feed_page = self.feed_page(user.page)
        create_post = feed_page.create_body_form()
        create_post.add_post_body(post_body)
        create_post_counter = create_post.get_post_body_letter_counter()
        assert create_post_counter == max_length
        create_post.click_publish()
        new_post = feed_page.get_post_by_text(post_body)
        expect(new_post.post_locator.first).to_be_visible()

    @allure.story("Create a new post")
    @allure.testcase("Create a new post with tag")
    @allure.id("TC-POST-001")
    @allure.title("Create a new post with tag")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("searched_tag", ["automation"])
    @pytest.mark.smoke
    @pytest.mark.post
    def test_create_new_post_with_hashtag(self, user: AuthenticatedUser, searched_tag):
        used_tag = searched_tag or "automation"
        expected_tag = re.escape(used_tag)
        pattern = re.compile(fr"/explore\?hashtag={expected_tag}$")

        post_body = self.get_rand_data.generate_text() + f"\n#{used_tag}"
        feed_page = self.feed_page(user.page)
        feed_page.create_post_with_check(post_body)

        created_post = feed_page.get_post_by_text(post_body)
        post_hashtags = created_post.get_post_tags_list()
        expect(created_post.post_locator).to_be_visible()
        expect(post_hashtags).to_have_attribute("href", value=pattern)

        post_hashtags.click()
        expect(feed_page.page).to_have_url(pattern)

    @allure.story("Add comment to post")
    @allure.testcase("Add comment to post")
    @allure.id("TC-COM-001")
    @allure.title("Add comment to post")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.comment
    @pytest.mark.parametrize("user", ["admin"], indirect=True)
    @pytest.mark.parametrize("used_comment_body", [None])
    def test_create_new_comment(self, user: AuthenticatedUser, used_comment_body: str):
        feed_page: FeedPage = self.feed_page(user.page)
        random_comment_body = used_comment_body or self.get_rand_data.generate_text()

        post = feed_page.get_post_by_index(index=1)
        post.open_post()

        post.create_comment(random_comment_body)
        created_comment = post.get_comment_by_text(random_comment_body)

        expect(created_comment.comment_locator).to_be_visible()
        expect(created_comment.comment_locator).to_contain_text(random_comment_body, use_inner_text=True)

    @allure.story("Like and unlike a post")
    @allure.testcase("Like and unlike a post")
    @allure.id("TC-POST-003")
    @allure.title("Like and unlike a post")
    @allure.severity(Severity.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.post
    @pytest.mark.flaky(reruns=1)
    @pytest.mark.like
    def test_like_unlike_post(self, user: AuthenticatedUser):
        feed_page: FeedPage = self.feed_page(user.page)
        index_ind: int = feed_page.get_random_post_index
        picked_post: PostComponent = feed_page.get_posts_with_comments(certain_index=index_ind)
        picked_post.like_unlike_post()

    @allure.story("Delete own post")
    @allure.testcase("Delete own post")
    @allure.id("TC-POST-005")
    @allure.title("Delete own post")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.regression
    @pytest.mark.post
    def test_delete_own_post(self, user: AuthenticatedUser):
        api: ApiHelper = self.get_api_helper
        api_created_post_before = api.create_post(
            token=user.token,
            post_text=self.get_rand_data.generate_text()
        )

        feed_page: FeedPage = self.feed_page(user.page)
        feed_page.page.reload()
        created_post = feed_page.get_post_by_text(api_created_post_before.content)
        expect(created_post.post_locator).to_be_visible()
        created_post.click_on_post_actions_menu().delete_post()
        expect(created_post.post_locator).not_to_be_visible()

    @allure.story("Upload image and attach to post")
    @allure.testcase("Upload image and attach to post")
    @allure.id("TC-POST-011")
    @allure.title("Upload image and attach to post")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("attachment_files_list", [["sampleFile.jpeg"]])
    @pytest.mark.regression
    @pytest.mark.post
    def test_create_new_post_with_image(self, user: AuthenticatedUser, attachment_files_list: list[str]):
        feed_page: FeedPage = self.feed_page(user.page)
        post_body: str = self.get_rand_data.generate_text()
        attachment_file_names: list[str] = attachment_files_list or ["sampleFile.jpeg"]

        feed_page.create_post_with_check(post_body, attachment_file_names=attachment_file_names)

        published_post = feed_page.get_post_by_text(post_body)

        expect(published_post.post_locator).to_be_visible()
        with allure.step("Check that created post contains image"):
            expect(published_post.post_locator.locator("img")).to_be_visible()
            expect(published_post.post_locator).to_be_visible()
            expect(published_post.post_locator).to_contain_text(post_body, use_inner_text=True)

    @allure.story("Upload image and attach to post")
    @allure.testcase("Upload oversized image (>5MB)")
    @allure.id("TC-EDGE-007")
    @allure.title("Upload oversized image (>5MB)")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("attachment_files_list", [["meze.jpg"]])
    @pytest.mark.regression
    @pytest.mark.post
    def test_create_new_post_too_large_image(self, user: AuthenticatedUser, attachment_files_list: list[str]):
        feed_page: FeedPage = self.feed_page(user.page)
        create_post = PublishPostComponent(user.page)
        attachment_file_names: list[str] = attachment_files_list or ["meze.jpg"]

        create_post.add_attachment_to_post(file_name=attachment_file_names, success_case=False)

        with allure.step("Check that app does not allows to attach images (>5 mb)"):
            expect(feed_page.page.get_by_role("status")).to_be_visible()
            expect(feed_page.page.get_by_role("status")).to_have_text("File size exceeds 5MB limit")

    @allure.story("Upload image and attach to post")
    @allure.testcase("Upload non-image file")
    @allure.id("TC-EDGE-008")
    @allure.title("Upload non-image file")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("attachment_files_list", [["test.txt"]])
    @pytest.mark.regression
    @pytest.mark.post
    def test_create_new_post_incorrect_file(self, user: AuthenticatedUser, attachment_files_list: list[str]):
        feed_page: FeedPage = self.feed_page(user.page)
        create_post = PublishPostComponent(user.page)
        attachment_file_names: list[str] = attachment_files_list or ["test.txt"]

        create_post.add_attachment_to_post(file_name=attachment_file_names, success_case=False)

        with allure.step("Check that app does not allows to attach non-image file"):
            expect(feed_page.page.get_by_role("status")).to_be_visible()
            expect(feed_page.page.get_by_role("status")).to_have_text("Only JPEG, PNG, GIF, WebP images are allowed")

    @allure.story("Reply to a comment (nested)")
    @allure.testcase("Reply to a comment (nested)")
    @allure.id("TC-COM-002")
    @allure.title("Reply to a comment (nested)")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.parametrize("reply_body", ["Test reply"])
    @pytest.mark.regression
    @pytest.mark.comment
    @pytest.mark.dependency(name="test_create_reply")
    def test_create_reply_to_comment(self, user: AuthenticatedUser, reply_body):
        used_reply_body: str = self.get_rand_data.generate_text(20) if reply_body is None else reply_body + str(
            self.get_rand_data.generate_number(0, 100))
        feed_page = self.feed_page(user.page)
        used_post = feed_page.get_posts_with_comments()
        used_post.open_post()

        used_comment = used_post.get_comment_by_index(1)
        used_comment.click_reply_btn()
        used_comment.create_reply(used_reply_body)

        created_reply = used_comment.get_reply_by_text(used_reply_body)
        another_used_reply_body: str = self.get_rand_data.generate_text(20) if reply_body is None else reply_body + str(
            self.get_rand_data.generate_number(0, 100))

        expect(created_reply.comment_locator).to_be_visible()
        expect(created_reply.comment_locator).to_contain_text(used_reply_body, use_inner_text=True)
        used_comment.click_reply_btn()
        used_comment.create_reply(another_used_reply_body)

    @allure.story("Bookmark and view bookmarks")
    @allure.testcase("Bookmark and view bookmarks")
    @allure.id("TC-POST-004")
    @allure.title("Bookmark and view bookmarks")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.flaky(reruns=1)
    @pytest.mark.regression
    @pytest.mark.post
    def test_bookmark_post(self, user: AuthenticatedUser):
        feed_page = self.feed_page(user.page)
        used_post = feed_page.get_post_by_index(1)
        used_post_body = used_post.get_certain_post_body()
        bookmark_status_before: bool = used_post.is_post_bookmarked()
        used_post.bookmark_post()
        sidebar = self.get_sidebar(user.page)
        sidebar.navigate_to("bookmarks")
        bookmark_page = self.bookmark_page(user.page)
        if bookmark_status_before:
            expect(bookmark_page.get_bookmarked_post_by_text(used_post_body).post_locator).not_to_be_visible()
        else:
            expect(bookmark_page.get_bookmarked_post_by_text(used_post_body).post_locator).to_be_visible()

    @allure.story("Like a comment")
    @allure.testcase("Like a comment")
    @allure.id("TC-POST-003")
    @allure.title("Like a comment")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.regression
    @pytest.mark.comment
    @pytest.mark.like
    def test_like_unlike_comment(self, user: AuthenticatedUser):
        feed_page = self.feed_page(user.page)
        used_post = feed_page.get_posts_with_comments(certain_index=1)
        used_post.open_post()
        used_comment = used_post.get_comment_by_index(1)
        used_comment.click_like_comment()

    @allure.story("Expand nested replies")
    @allure.testcase("Expand nested replies")
    @allure.id("TC-COM-003")
    @allure.title("Expand nested replies")
    @allure.severity(Severity.NORMAL)
    @pytest.mark.parametrize("user", ["user_bob"], indirect=True)
    @pytest.mark.regression
    @pytest.mark.comment
    @pytest.mark.flaky(reruns=3, max_reruns=3)
    @pytest.mark.dependency(depends=["test_create_reply"])
    @pytest.mark.order(-1)
    def test_expand_nested_replies(self, user: AuthenticatedUser, get_body_of_post_with_replies):
        feed_page = self.feed_page(user.page)
        post_body_with_replies = get_body_of_post_with_replies
        post_with_replies = feed_page.get_post_by_text_with_load_previous_posts(post_body_with_replies)
        post_with_replies.open_post()
        used_comment = post_with_replies.get_comment_with_replies()

        used_comment.click_load_more_replies()
