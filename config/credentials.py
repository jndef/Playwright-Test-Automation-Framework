import json
import os
from dataclasses import dataclass

import allure
from dotenv import load_dotenv

load_dotenv()

roles = json.loads(os.getenv("ROLES", "[]"))


@dataclass
class UserProfile:
    alias: str
    user_id: str
    email: str
    password: str


class Credentials:

    @staticmethod
    def _role_checker(update_role=None):
        """
        Method cheks if provided role is valid and in allowed list and returns back the role
        :param update_role: specified role, used in Credentials helper
        :return:str
        """
        role = os.getenv("role")
        if update_role is not None:
            role = update_role
        if not isinstance(role, str):
            raise Exception("Invalid role - not str")
        if role not in roles:
            raise Exception(f"Invalid role: {role}. Not in allowed list {roles}")
        return role


    def get_user(self, alias: str) -> UserProfile:
        """
        Method gets users credentials and id using provided alias from env file
        :param alias: provided alias of user
        :return: object of UserProfile dataclass
        """
        with allure.step(f"Setup - Get credentials data from .env for user: {alias}"):
            alias = self._role_checker(alias)
            # stage = "LOCAL" if os.getenv("STAGE") == "local_docker" else os.getenv("STAGE").upper()
            role = alias.upper()
            return UserProfile(
                alias=alias,
                user_id=os.getenv(f"{role}_ID"),
                email=os.getenv(f"{role}_LOGIN"),
                password=os.getenv(f"{role}_PASSWORD"),
            )
