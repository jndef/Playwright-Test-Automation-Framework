import random

from faker import Faker

fake = Faker()
import pytest

from config.credentials import Credentials
from config.db_config import MyLocalDBConfig
from helpers.db_helper import DataBaseHandler

creds = Credentials()


@pytest.fixture(name="db_connect", scope="session")
def connect_database():
    """
    Fixture to connect to database (session scope) and close it after test session
    :return:
    """
    data_base = DataBaseHandler(MyLocalDBConfig)

    data_base.connect()

    # connection = sqlite3.connect("pytest_allure/test.db")
    print("\n▶️ DB connected")
    yield data_base
    data_base.close_connection()
    print("\n⏹️ DB disconnected")


@pytest.fixture()
def cleanup_conversation_between_users(db_connect):
    """
    Fixture, clean conversation between user1 and user2 using DB after test. Accepted commit_cleanup (bool)
    :param db_connect:
    :return:
    """

    def _cleanup(user_a, user_b, commit_cleanup: bool = True):
        conversation_id = db_connect.get_conversation_id_between_users(user_a, user_b)

        if conversation_id and conversation_id is not None:
            db_connect.delete_conversation(conversation_id)
            if commit_cleanup:
                db_connect.commit()
            count = db_connect.check_conversation_by_id(conversation_id)
            assert count == 0 if commit_cleanup else count == 1

    return _cleanup


@pytest.fixture()
def get_conversation(request, db_connect):
    """
    Fixture to get conversation between user1 and user2 using DB after test
    :param request: case info, retrieved from test
    :param db_connect: db connection from fixture
    :return:
    """
    case_info = request.param
    conversation_id = db_connect.get_conversation_id_between_users(user_alias1=case_info["user1"],
                                                                   user_alias2=case_info["user2"])
    if conversation_id is not None:
        yield conversation_id


@pytest.fixture()
def get_posts_with_replies(db_connect):
    """
    Fixture to get posts with replies using DB before test
    :param db_connect: db connection from fixture
    :return: id of the post with replies
    """
    posts_id = db_connect.get_posts_with_comments_and_replies()
    yield random.choice(posts_id)["post_id"]


@pytest.fixture()
def get_body_of_post_with_replies(db_connect, get_posts_with_replies):
    """
    Fixture to get body of picked post with replies using DB before test
    :param db_connect: db connection from fixture
    :param get_posts_with_replies:
    :return:
    """
    content = db_connect.get_post_content_by_id(post_id=get_posts_with_replies)
    yield content


@pytest.fixture(name="mark_unread_all")
def mark_all_notifications_as_unred(db_connect, request, commit: bool = True):
    """
    Fixture to mark all unread notifications as unread using DB
    :param request: case info, retrieved from test
    :param db_connect: db connection from fixture
    :param commit: submit changes at DB
    :return:
    """
    mark_unread = request.param
    db_connect.update_mark_all_notifications_unread(for_user=mark_unread)
    if commit:
        db_connect.commit()
    yield
