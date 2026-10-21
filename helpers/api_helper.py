import os
from abc import ABC, abstractmethod
from collections import namedtuple
from unittest import skip
from dotenv import load_dotenv

import requests
load_dotenv()

from config.credentials import Credentials

STAGE = os.getenv("STAGE", "http://localhost")
API_URL = f"{STAGE}:8000"

API_AUTH = API_URL + "/api/auth"
API_POST = API_URL + "/api/posts"
API_USERS = API_URL + "/api/users"
API_COMMENTS = API_URL + "/api/comments"
API_MESSAGES = API_URL + "/api/messages"
API_CONVERSATIONS = API_URL + "/api/conversations"

credentials = Credentials()


class ApiHelper:
    def __init__(self):
        self.request_data = {}
        self.request_timeout = 10.0
        self._cache = {}

    def _set_headers(self, headers):
        """
        Method to set headers for request builder
        :param headers:
        :return: self
        """
        self.request_data["headers"] = headers
        return self

    def _set_url(self, url: str):
        """
        Method to set request url for request builder
        :param url:
        :return: self
        """
        self.request_data["url"] = url
        return self

    def _set_request_body(self, json):
        """
        Method to set request body (json) for request builder if required
        :param json:
        :return: self
        """
        self.request_data["json"] = json
        return self

    def _set_query_params(self, **kwargs):
        """
        Method to set request query params for request builder if required
        :param kwargs: query and value params
        :return: self
        """
        self.request_data["params"] = {}
        for key, value in kwargs.items():
            self.request_data["params"][key] = value
        return self

    def _send_request(self, method: str):
        """
        Request builder depending request method
        :param method:
        :return:
        """
        method = method.upper().strip()
        assert method.upper().strip() in ["GET", "POST", "PUT", "PATCH", "DELETE"], "Invalid method"
        if method == "GET":
            return requests.get(**self.request_data, timeout=self.request_timeout)
        elif method == "POST":
            return requests.post(**self.request_data, timeout=self.request_timeout)
        elif method == "PUT":
            return requests.put(**self.request_data, timeout=self.request_timeout)
        elif method == "PATCH":
            return requests.patch(**self.request_data, timeout=self.request_timeout)
        else:
            return requests.delete(**self.request_data, timeout=self.request_timeout)

    def refresh_token(self, r_token: str, role: str):
        """
        POST. Update access token using valid refresh token, depending on specified user (role)
        :param r_token:str - provided valid refresh  token
        :param role:str - specified role used for Credentials helper
        :return:
        """
        UserData = namedtuple("_", ["access_token", "refresh_token"])
        request = self \
            ._set_url(API_AUTH + "/refresh") \
            ._set_headers({"Content-Type": "application/json"}) \
            ._set_request_body({"refresh_token": r_token}) \
            ._send_request(method="POST")

        if request.status_code == 200:
            response = request.json()
            self._cache[role] = response
            return UserData(access_token=response["access_token"], refresh_token=response["refresh_token"])
        raise ValueError(
            f"API error while refresh ({request.status_code})\nMessage: {request.text}\nUsed data:{request.request.body}")

    def login_to_account(self, role: str, force: bool = False):
        """
        POST. Request to get actual access and refresh token of user with specified alias(role)
        :param role:str - alias used in credentials helper
        :param force:bool (Optional) - If True, the app will perform login via UI. Default - False
        :return:
        """
        UserData = namedtuple("_", ["access_token", "refresh_token"])
        creds = credentials.get_user(role)
        email, password = creds.email, creds.password
        if not force and role in self._cache:
            return UserData(access_token=self._cache[role]["access_token"],
                            refresh_token=self._cache[role]["refresh_token"])
        request = self \
            ._set_url(API_AUTH + "/login") \
            ._set_headers({"Content-Type": "application/json"}) \
            ._set_request_body({"email": email, "password": password}) \
            ._send_request(method="POST")
        if request.status_code == 200:
            response = request.json()
            self._cache[role] = response
            return UserData(access_token=response["access_token"], refresh_token=response["refresh_token"])
        raise ValueError(f"API error while login ({request.status_code})\nMessage: {request.text}")

    def create_post(self, token: str, post_text: str):
        """
        POST. Request to create post using provided text and users access token
        :param token:str - provided valid access token
        :param post_text:str - post body info (content)
        :return:
        """
        PostData = namedtuple("_", ["display_name", "content"])

        request = self \
            ._set_url(API_POST) \
            ._set_headers({"Content-Type": "application/json", "Authorization": f"Bearer {token}"}) \
            ._set_request_body({"content": f"{post_text}"}) \
            ._send_request(method="POST")

        if request.status_code == 201:
            response = request.json()
            return PostData(display_name=response["author"]["display_name"], content=response["content"])
        raise ValueError(
            f"API error ({request.status_code}) while post creation!\n{request.text}\n{request.request.headers['Authorization']}\n")

    def unfollow_user(self, token: str, user_name: str):
        """
        POST. Request to unfollow user by provided user_name and access token
        :param token:str - provided valid access token
        :param user_name:str - post body info (content)
        :return:
        """
        request = self \
            ._set_url(f"{API_USERS}/{user_name}/follow") \
            ._set_headers({"Content-Type": "application/json", "Authorization": f"Bearer {token}"}) \
            ._send_request(method="DELETE")
        if request.status_code not in [204, 404]:
            raise ValueError(
                f"API error ({request.status_code}) while unfollowing!\n{request.text}\n{request.request.headers['Authorization']}\n")

    def follow_user(self, token: str, user_name: str):
        """
        POST. Request to follow user by provided user_name and access token
        :param token:str - provided valid access token
        :param user_name:str - post body info (content)
        :return:
        """
        request = self \
            ._set_url(f"{API_USERS}/{user_name}/follow") \
            ._set_headers({"Content-Type": "application/json", "Authorization": f"Bearer {token}"}) \
            ._send_request(method="POST")
        if request.status_code not in [204, 409]:
            raise ValueError(
                f"API error ({request.status_code}) while following!\n{request.text}\n{request.request.headers['Authorization']}\n")
