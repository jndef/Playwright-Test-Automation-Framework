from playwright.sync_api import Page, expect
from helpers.data_generator import Generators


class UIMain:
    def __init__(self, page: Page):
        self.page = page
        self.get_rand_data = Generators()
        self.token: str = ''

    def is_completed(self):
        """Expect that toast (success/fail) is shown after action"""
        loc_toast = self.page.get_by_role("status")
        for index in range(loc_toast.count()):
            expect(loc_toast.nth(index)).to_be_visible()
