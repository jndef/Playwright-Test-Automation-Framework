import random

from psycopg2.extras import RealDictCursor

from mysql import connector
import psycopg2
import sqlite3
from mysql.connector.cursor import MySQLCursor

from config.credentials import Credentials


class DataBaseHandler:

    def __init__(self, config):
        self.db_name = config.db_name
        self.config = config
        self.connection = None
        self.cursor: MySQLCursor = None
        # self.sslmode = None

    def _get_connection_params(self) -> dict:
        """
        Method to get connection parameters
        :return: dict
        """
        if self.db_name in ['local_db']:
            return {
                'host': self.config.server,
                'database': self.config.database,
                'user': self.config.user,
                'password': self.config.password,
                'port': self.config.port
            }

        else:
            raise ValueError("Поддерживаются только local_db")

    def connect(self):
        """
        Method to connect to database
        :return:
        """
        params = self._get_connection_params()
        if self.db_name == 'mysql':
            self.connection = connector.connect(**params)
        elif self.db_name in ['postgres', 'local_db']:
            self.connection = psycopg2.connect(**params)
        elif self.db_name == 'sqlite':
            self.connection = sqlite3.connect(params["database"])
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    def commit(self):
        """
         Method to commit changes in DB
         :return:
         """
        self.connection.commit()

    def rollback(self):
        """
         Method to revert changes in DB
         :return:
         """
        self.connection.rollback()

    def close_connection(self):
        """
         Method to close connection with DB
         :return:
         """
        self.connection.close()

    @staticmethod
    def _table_name_verification(table_name):
        """
        Method to verify table name used in helpers
        :param table_name:str - provided table name to check
        :return:
        """
        existed_tables = ['users', 'refresh_tokens', 'follows', 'posts', 'hashtags', 'post_hashtags', 'comments',
                          'likes', 'bookmarks', 'conversations', 'conversation_participants', 'messages',
                          'notifications']
        if table_name not in existed_tables:
            raise Exception(f"Table {table_name} does not exist")

    def get_posts_with_comments_and_replies(self, used_table: str = "comments"):
        """
        Query to DB to get user by provided name (alias)
        :param used_table:str - provided table to use in query
        :return: result of DB query
        """
        self._table_name_verification(used_table)
        query = f"""
            SELECT count(id), post_id, parent_comment_id 
            FROM comments 
            WHERE parent_comment_id is not null
            GROUP BY parent_comment_id, post_id
            HAVING count(id) > 1
            ORDER BY post_id, count(id) ASC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_post_content_by_id(self, post_id: str, used_table: str = "comments"):
        """
        Query to DB to get user by provided name (alias)
        :param used_table:str - provided table to use in query
        :param post_id:str - provided table to use in query
        :return: result of DB query
        """
        self._table_name_verification(used_table)
        query = f"""
            SELECT content 
            FROM posts
            WHERE id = %s
        """
        self.cursor.execute(query, (post_id,))
        return self.cursor.fetchone()["content"]

    def get_user_by_name(self, user_alias: str = None, used_table: str = "users"):
        """
        Query to DB to get user by provided name (alias)
        :param user_alias:str - users alias used in framework for user's credentials
        :param used_table:str - provided table to use in query
        :return: result of DB query
        """
        creds = Credentials()

        self._table_name_verification(used_table)
        user_id: str = creds.get_user(alias=user_alias).user_id
        query = f"""
            SELECT username 
            FROM users
            WHERE id = %s
        """
        self.cursor.execute(query, (user_id,))

        return self.cursor.fetchone()["username"]

    def get_conversation_id_between_users(self, user_alias1: str, user_alias2: str,
                                          used_table: str = "conversation_participants"):
        """
        Method to get conversation id between two users
        :param user_alias1: alias of 1st user
        :param user_alias2: alias of 2nd user
        :param used_table: str - provided table name used in query
        :return:
        """
        creds = Credentials()

        user_id1, user_id2 = creds.get_user(user_alias1).user_id, creds.get_user(user_alias2).user_id
        query = f"""
            SELECT cp.conversation_id 
            FROM {used_table} cp
            INNER JOIN conversations c ON c.id = cp.conversation_id
            WHERE cp.user_id IN (%s, %s) AND c.is_group is FALSE
            GROUP BY 1
            HAVING COUNT(*) = 2
        """
        self._table_name_verification(used_table)
        self.cursor.execute(
            query, (user_id1, user_id2)
        )
        if self.cursor.rowcount > 0:
            return self.cursor.fetchone()["conversation_id"]
        return None

    def check_conversation_by_id(self, conversation_id: str, used_table: str = "conversations"):
        """
        Check conversation count in DB using provided id
        :param conversation_id: conversation id (uuid format)
        :param used_table: str - provided table name used in query
        :return:
        """
        self._table_name_verification(used_table)
        query = f"""
            SELECT id 
            FROM {used_table}
            WHERE id = %s
        """
        self.cursor.execute(query, (conversation_id,))
        return self.cursor.rowcount

    def update_mark_all_notifications_unread(self, for_user: str = "Admin", used_table: str = "notifications"):
        """
        Make all notifications unread for user with specified user (alias)
        :param for_user: user's alias, used to get correct user id for DB query
        :param used_table:str - provided table to use in query
        :return:
        """
        query = f"""
            UPDATE {used_table}
            SET is_read = false 
            WHERE user_id IN (SELECT id from users WHERE display_name = %s)
        """
        self.cursor.execute(query, (for_user,))
        # self.commit()

    def delete_conversation(self, conversation_id: str, used_table: str = "conversations"):
        """
        Make all notifications unread for user with specified user (alias)
        :param conversation_id: conversation id (uuid format)
        :param used_table:str - provided table to use in query
        :return:
        """
        self._table_name_verification(used_table)
        query = f"DELETE FROM {used_table} WHERE id = %s"
        self.cursor.execute(query, (conversation_id,))
        # self.commit()
