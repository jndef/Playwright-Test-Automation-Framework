import allure
from playwright.sync_api import Page, expect, Locator

from base.base_page import BasePage
from config.urls import Links


class ProfilePage(BasePage):
    _PAGE_URL = Links.PROFILE_URL

    def __init__(self, page: Page, profile_url=None):
        """
        Initialization of ProfilePage, that accepted playwright page object and profile url
        :param page: playwright page object
        :param profile_url: provided profile url
        """

        super().__init__(page)
        self.profile_url: str = profile_url or self._PAGE_URL
        self._message_button: Locator = self.page.get_by_test_id("profile-message-btn")
        self.follow_mark: Locator = self.page.locator("div span.rounded-full.text-gray-500")
        self._follow_button: Locator = self.page.get_by_test_id("profile-follow-btn")


    @property
    def _get_followers_count(self) -> Locator:
        """
        Internal method to get the number of followers
        :return:
        """
        return self.page.get_by_test_id("profile-followers-count")

    @allure.step("Click on Follow button")
    def _click_follow_button(self):
        """
        Internal method to click on Follow button
        :return:
        """
        self._follow_button.click()

    @allure.step("Follow/unfollow flow")
    def follow_unfollow_user(self):
        """
        Method, performed to follow/unfollow user. Includes check of corresponding request and UI check after
        :return:
        """
        followers_count = int(self._get_followers_count.text_content())
        is_follower_before: bool = self.is_follower()
        if is_follower_before:
            with allure.step("Unfollow the user, check result"):
                with self.page.expect_response(
                        lambda response: "/follow" in response.url and response.request.method == "DELETE"
                ) as response_info:
                    self._click_follow_button()
                    self.is_completed()
                self.page.reload()
                expect(self._get_followers_count).to_have_text(str(followers_count - 1))
                expect(self._follow_button).to_have_class("btn-primary")
                response = response_info.value
                assert response.ok
        else:
            with allure.step("Follow the user, check result"):
                with self.page.expect_response(
                        lambda response: "/follow" in response.url and response.request.method == "POST"
                ) as response_info:
                    self._click_follow_button()
                    self.is_completed()
                self.page.reload()
                expect(self._get_followers_count).to_have_text(str(followers_count + 1))
                expect(self._follow_button).to_contain_class("btn-secondary")
                response = response_info.value
                assert response.ok

    @allure.step("Check following state")
    def is_follower(self) -> bool:
        """
        Method to check if user is follower or not
        :return:
        """
        follow_button = self.page.get_by_test_id("profile-follow-btn")
        follow_button_class = follow_button.get_attribute("class")
        if "primary" in follow_button_class:
            return False
        elif "secondary" in follow_button_class:
            return True
        raise BaseException(f"Can't define follower state by provided class: {follow_button_class}")

    @allure.step("Click 'Message' button at profile page")
    def click_message_button(self):
        """
        Method to click message button at profile page
        :return:
        """
        self._message_button.click()

    @property
    def get_total_following(self) -> Locator:
        """
        Method to get the total number of following
        :return: Locator
        """
        return self.page.get_by_test_id("profile-following-count")

    def get_total_follower(self) -> Locator:
        """
        Method to get the total number of follower
        :return: Locator
        """
        return self._get_followers_count

    @allure.step("Open the page with list of following users")
    def open_profile_following_page(self):
        """
        Method to open the page with list of following users
        :return:
        """
        new_url = self.page.url + "/following"
        self.get_total_following.click()
        expect(self.page).to_have_url(new_url)

    @allure.step("Open the page with list of followers")
    def open_profile_followers_page(self):
        """
        Method to open the page with list of followers
        :return:
        """
        new_url = self.page.url + "/followers"
        self._get_followers_count.click()
        expect(self.page).to_have_url(new_url)

    @allure.step("Get count of users at following/followers page")
    def get_users_list_count_at_page(self) -> int:
        """
        Method to get the count of users at the page
        :return: count of users at the page (int)
        """
        locator = self.page.locator("div a.card")
        expect(locator.last).to_be_visible()
        return self.page.locator("div a.card").count()
