from playwright.sync_api import Locator, Page
from base.ui_main import UIMain


class BaseComponent(UIMain):

    def __init__(self, page: Page, root: Locator = None):
        super().__init__(page)
        self.root = root or page
