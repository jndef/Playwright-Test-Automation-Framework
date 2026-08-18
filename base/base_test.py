from base.base_components.sidebar_component import SideBarComponent
from config.credentials import Credentials
from helpers.api_helper import ApiHelper
from helpers.data_generator import Generators
from helpers.interceptor_helper import InterceptorHelper
from pages.admin_page.admin_page import AdminPage
from pages.bookmark_page.page import BookmarkPage
from pages.feed_page.page import FeedPage
from pages.login_page.login_page import LoginPage
from pages.messages_page.page import MessagesPage
from pages.notification_page.notifications_page import NotificationsPage
from pages.search_page.search_page import SearchPage


class BaseTest:

    @property
    def feed_page(self):
        """
        Get feed page object
        :return: FeedPage()
        """
        feed_page = lambda p: FeedPage(p)
        return feed_page

    @property
    def admin_page(self):
        """
        Get admin page object
        :return: AdminPage()
        """
        admin_page = lambda p: AdminPage(p)
        return admin_page

    @property
    def bookmark_page(self):
        """
        Get bookmark page object
        :return: BookmarkPage()
        """
        bookmark_page = lambda p: BookmarkPage(p)
        return bookmark_page

    @property
    def messages_page(self):
        """
        Get messages page object
        :return: MessagesPage()
        """
        messages_page = lambda p: MessagesPage(p)
        return messages_page

    @property
    def notifications_page(self):
        """
        Get notifications page object
        :return: NotificationsPage()
        """
        notifications_page = lambda p: NotificationsPage(p)
        return notifications_page

    @property
    def search_page(self):
        """
        Get search page object
        :return: SearchPage()
        """
        search_page = lambda p: SearchPage(p)
        return search_page

    @property
    def login_page(self):
        """
        Get login page object
        :return: LoginPage()
        """
        login_page = lambda p: LoginPage(p)
        return login_page

    @property
    def credentials(self):
        """
        Get credentials config helper
        :return: Credentials()
        """
        credentials = Credentials()
        return credentials

    @property
    def get_rand_data(self):
        """
        Get rand data helper
        :return: Generators()
        """
        rand_data = Generators()
        return rand_data

    @property
    def get_api_helper(self):
        """
        Get api helper object
        :return: ApiHelper()
        """
        api_helper = ApiHelper()
        return api_helper

    @property
    def get_interceptor(self):
        """
        Get interceptor helper object
        :return: InterceptorHelper()
        """
        return lambda p: InterceptorHelper(p)

    @property
    def get_sidebar(self):
        """
        Get general sidebar component
        :return: SideBarComponent()
        """
        sidebar = lambda p: SideBarComponent(p)
        return sidebar
