import os
from dotenv import load_dotenv
from base.base_page import BasePage
load_dotenv()


class Links(BasePage):
    HOST = os.getenv("HOST", "http://localhost")
    FE_URL= f"{HOST}:3000"

    LOGIN_URL = f"{FE_URL}/login"
    HOME_PAGE = f"{FE_URL}/home"
    MESSAGES_URL = f"{FE_URL}/messages"
    FEED_URL = f"{FE_URL}"
    REGISTER_URL = f"{FE_URL}/register"
    BOOKMARK_URL = f"{FE_URL}/bookmarks"
    NOTIFICATIONS_URL = f"{FE_URL}/notifications"
    SEARCH_URL = f"{FE_URL}/search"
    EXPLORE_URL = f"{FE_URL}/explore"
    PROFILE_URL = f"{FE_URL}/profile"
    ADMIN_URL = f"{FE_URL}/admin"
