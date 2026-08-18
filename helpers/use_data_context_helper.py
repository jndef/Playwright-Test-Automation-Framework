import json
import os
import platform
from datetime import datetime, timedelta
from helpers.api_helper import ApiHelper



class DataContextManager:
    """
     # Object initialization requires accept api helper object and folder, where files are placed
    """
    def __init__(self,
                 api:ApiHelper, context_data_folder='data', ):
        self.context_data_path = os.path.join(os.getcwd(), context_data_folder)
        self.context_data_file = os.path.join(self.context_data_path)
        self.api = api

    @staticmethod
    def get_path_to_file(file_name: str = None, folders: str = None):
        """
        Method, that prepared path to specified file name and folders.
        :param file_name: prepared name, required to build file path
        :param folders: prepared folder name, if file is placed in certain folder
        :return:
        """
        if folders is not None:
            os_name = platform.system()
            if os_name == "Darwin":
                folders = folders.replace("\\", "/")
            elif os_name == "Windows":
                folders = folders.replace("/", "\\")
            return os.path.join(os.getcwd(), f"{folders}", f"{file_name}")
        return os.path.join(os.getcwd(), f"{file_name}")

    @staticmethod
    def _extract_token_from_storage(storage_data: dict, token_key: str) -> str:
        """ Internal method. Parse storage_state file, Playwright."""
        return next(
            (
                item["value"] for origin in storage_data.get("origins", [])
                for item in origin.get("localStorage", [])  if str(item.get("name")).lower() == token_key.lower()
            ),
            ""
        )

    @staticmethod
    def _update_tokens_in_storage_dict(storage_data: dict, tokens_data) -> dict:
        """
        Internal method. to update values at provided dict storage file.
        :param storage_data: provided storage file
        :param tokens_data: key, value to be rewritten
        :return: dict
        """

        for origin in storage_data.get("origins", []):
            for item in origin.get("localStorage", []):
                if item["name"] == "access_token":
                    item["value"] = tokens_data.access_token
                if item["name"] == "refresh_token":
                    item["value"] = tokens_data.refresh_token
        return storage_data

    def _set_file_path(self, role):
        """Internal method.  generate file path based on file name (and context_data_path)"""
        filename = f"storage_{role}.json"
        self.context_data_file = os.path.join(self.context_data_path, filename)

    def get_storage_access_token(self, role:str) -> str:
        """
        Method to get access token from storage file of user with provided role (alias).
        :param role: provided alias of user (str)
        :return: token value (str)
        """
        self._set_file_path(role)
        storage_file = self._get_storage_dict(role)
        token = self._extract_token_from_storage(storage_file, "access_token")
        return token

    def storage_file_handler(self, role: str):
        """
        Method that managed storage file depending on its edit time based on certain user alias
        :param role: provided user alias (str)
        :return:
        """
        state_file: str = self.get_path_to_file(folders="data", file_name=f"storage_{role}.json")
        if os.path.exists(state_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(state_file))
            file_life_time = datetime.now() - file_time
            # file_life_time = timedelta(minutes=35)
            if timedelta(minutes=30) < file_life_time < timedelta(minutes=40):
                try:
                    self.refresh_session(role)
                except ValueError:
                    self.refresh_session(role, force_login=True)
            elif file_life_time > timedelta(minutes=40):
                self.refresh_session(role, force_login=True)
            return state_file
        else:
            return None

    def refresh_session(self, role, force_login: bool = False):
        """
        Method to refresh session based on user role (alias) with ability to repeat API login when refresh token expired
        :param role: provided user alias (str)
        :param force_login: Optional parameter, allowed to perform API login to account. Default - False
        :return:
        """
        # send request refresh token
        if force_login:
            tokens_data = self.api.login_to_account(role, force=True)
        else:
            tokens_data = self._refresh_tokens(role)
        self._rewrite_storage(role, tokens_data=tokens_data)

    def _refresh_tokens(self, used_role: str) -> dict:
        """
        Internal method. Method that performed refresh token via API for certain user
        :param used_role: provided user alias (str)
        :return: dict
        """
        self._set_file_path(used_role)
        storage_data: dict = self._get_storage_dict(used_role)
        ref_token: str = self._extract_token_from_storage(storage_data, token_key="refresh_token")
        tokens_data = self.api.refresh_token(r_token=ref_token, role=used_role)
        return tokens_data

    def _get_storage_dict(self, role: str) -> dict:
        """
        Internal method. Return storage file of certain user
        :param role: provided user alias (str)
        :return: dict
        """
        self._set_file_path(role)
        storage_data: dict
        if not os.path.exists(self.context_data_file):
            # If file doesn't exist, print the message
            raise Exception(f"File {self.context_data_file} doesn't exist.")
        else:
            try:
                with open(self.context_data_file, "r+") as file:
                    storage_data = json.load(file)  # Load data from JSON-file
            except (OSError, IOError) as e:
                # Error handle while file rewriting
                print(f"Error handle while file rewriting: {e}")
        return storage_data

    def _rewrite_storage(self, rewrite_for_role: str, tokens_data: dict):
        """
        Internal method. Rewrite storage file of certain user using provided tokens data
        :param rewrite_for_role: provided user alias (str)
        :param tokens_data: provided tokens data (dict)
        :return:
        """
        self._set_file_path(rewrite_for_role)
        if not os.path.exists(self.context_data_file):
            # If file doesn't exist, print the message
            raise Exception(f"File {self.context_data_file} doesn't exist")
        else:
            storage_data = self._get_storage_dict(rewrite_for_role)
            changed_file: dict = self._update_tokens_in_storage_dict(storage_data, tokens_data)
            try:
                with open(self.context_data_file, "w") as file:
                    json.dump(changed_file, file)  # Запись данных в JSON-файл
            except (OSError, IOError) as e:
                # Error handling while recording to file
                print(f"Error while Local Storage saving: {e}")
