import allure
from playwright.sync_api import Page, Locator, expect

from base.base_component import BaseComponent
from helpers.download_upload_helper import UploadDownloadHelper


class PublishPostComponent(BaseComponent):
    def __init__(self, page: Page):
        """
        Init PublishPostComponent, allows to perform post publishing
        """
        super().__init__(page)
        self._post_text_area: Locator = page.get_by_role("textbox")
        self._publish_post_button: Locator = page.get_by_test_id("post-composer-submit")
        self._published_post_preview: Locator = page.get_by_test_id("post-composer-preview")
        self._post_image_preview: Locator = page.get_by_test_id("post-composer-image-preview")
        self._remove_attachment_button: Locator = page.get_by_test_id("post-composer-image-remove")
        self._post_attachments_input: Locator = page.get_by_test_id("post-composer-file-input")
        self._post_body_counter: Locator = page.get_by_test_id('post-composer').locator("span")

    @allure.step("Enter text at post body input")
    def add_post_body(self, text_data: str = None):
        """
        Method to add text at post body input
        :param text_data: (Optional) Text to be added. If it's skipped, the method will generate a random post body
        :return:
        """
        if text_data is None:
            text_data = self.get_rand_data.generate_text()
        self._post_text_area.fill(text_data)
        return self

    @allure.step("Submit post publishing")
    def click_publish(self):
        """
        Method to submit post publishing
        :return:
        """
        self._publish_post_button.click()
        self.is_completed()
        return self

    @allure.step("Attach image")
    def add_attachment_to_post(self, file_name: list[str], download_folder: str = "data", success_case: bool = True):
        """
        Method to attach image to post while publishing
        :param file_name: name of the file to be attached
        :param download_folder: folder, where attached images is stored
        :param success_case: (Optional, default - True). If False - the app skips visibility expectation
        :return:
        """
        download_helper = UploadDownloadHelper(self.page, self._post_attachments_input)
        download_helper.upload_files(file_names=file_name, download_folder=download_folder)
        if success_case:
            expect(self._post_image_preview).to_be_visible()
        return self

    def get_post_body_letter_counter(self) -> int:
        """
        Method to get post body letter counter
        :return: post body letter counter as integer
        """
        return int(self._post_body_counter.inner_text().split('/')[0])
