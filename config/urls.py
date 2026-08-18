import os
from dotenv import load_dotenv
from base.base_page import BasePage
load_dotenv()


class Links(BasePage):
    HOST = os.getenv("HOST") or 'http://localhost:3000'

    LOGIN_URL = f"{HOST}/login"
    HOME_PAGE = f"{HOST}/home"
    MESSAGES_URL = f"{HOST}/messages"
    FEED_URL = f"{HOST}"
    REGISTER_URL = f"{HOST}/register"
    BOOKMARK_URL = f"{HOST}/bookmarks"
    NOTIFICATIONS_URL = f"{HOST}/notifications"
    SEARCH_URL = f"{HOST}/search"
    EXPLORE_URL = f"{HOST}/explore"
    PROFILE_URL = f"{HOST}/profile"
    ADMIN_URL = f"{HOST}/admin"
