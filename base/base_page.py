import allure
from base.ui_main import UIMain


class BasePage(UIMain):

    _PAGE_URL: str = ""

    @allure.step(f"Open page {_PAGE_URL}")
    def open(self):
        """Open page depending on page url"""
        self.page.goto(self._PAGE_URL)
        self.page.wait_for_load_state("networkidle")


