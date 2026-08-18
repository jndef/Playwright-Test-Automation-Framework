import os
from playwright.sync_api import expect, Locator, Page


class UploadDownloadHelper:
    def __init__(self, page: Page, download_upload_locator: Locator):
        """
        Class used to initialize the UploadDownloadHelper
        :param page:page - playwright.page.Page object
        :param download_upload_locator:Locator - provided selector, used for uploading/download purposes in UI
        """
        self.page = page
        self.attachments_folder = "data"
        self.download_upload_locator = download_upload_locator

    def upload_files(self, file_names: list[str], download_folder: str = "data"):
        """
        Method performed to upload files from local folder to server
        :param file_names: list[str] -  of file names to upload
        :param download_folder:str - folder of files used for download/upload purposes
        :return:
        """
        files = [os.path.join(os.getcwd(), download_folder, filename) for filename in file_names]
        self.download_upload_locator.set_input_files(files=[*files])

    def download_file(self):
        """
        Method performed to download files from server to local folder
        :return:
        """
        with self.page.expect_download() as download_info:
            self.download_upload_locator.click()
            # self.page.locator("//button[contains(@onclick, 'txt')]").click()
        download = download_info.value
        # # filename = download.suggested_filename
        # # save_dir = os.path.abspath("downloads")
        # # os.makedirs(save_dir, exist_ok=True)
        # # save_path = os.path.join(save_dir, filename)
        # # download.save_as(save_path)
        download.save_as(os.path.join(os.getcwd(), self.attachments_folder, download.suggested_filename))

    def download_track_expect(self, class_name:str="hidden"):
        """
        Method to track download/upload locator visibility by specified class
        :return:
        """
        expect(self.download_upload_locator).not_to_have_class(class_name)

    def track_indicator_progress(self, track_attribute: str, track_value: str):
        """
        Method to track download/upload progress by specified attribute name and value of download/upload locator
        Method performed to track
        :param track_attribute: name of attribute to track
        :param track_value: value of attribute to track
        :return:
        """
        expect(self.download_upload_locator).to_have_attribute(track_attribute, track_value)
