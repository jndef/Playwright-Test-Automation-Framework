import json
from dotenv import load_dotenv
from playwright.sync_api import Route, Response

load_dotenv()


class InterceptorHelper:
    def __init__(self, page):
        self.page = page

    @staticmethod
    def replace_url(start_url, replaced_request_path):
        """Method to replace real request url by rewritten one"""
        request_url_before: str = start_url
        list_url = request_url_before.split(sep=f"/api/")
        list_url[1] = replaced_request_path
        request_url_after = "/api".join(list_url)
        return request_url_after

    def requests_monitoring(self):
        """
        Print all performed requests
        :return:
        """
        def log_requests(route: Route):
            # Retrieve request from route object
            request = route.request
            print(f"→ {request.method} {request.url}")
            route.continue_()

        return self.page.route("**/*", log_requests)

    def response_monitoring(self):
        """
        Print all responses of performed requests
        :return:
        """
        def check_response(response: Response):
            if "/api/" in response.url and response.ok:
                try:
                    data = response.json()
                    print(f"✅ API responses: {response.url}\nData: {data}")
                except:
                    pass

        return self.page.on("response", check_response)

    def response_monitoring_with_filters(self, filter_method: str, filter_key_url: str):
        """
        Interceptor requests. Print performed requests with ability to filter by method and request url
        :param filter_method: specify to filter requests by method
        :param filter_key_url: specify to filter requests by url
        :return:
        """
        def check_response(response: Response):
            if filter_key_url in response.url and response.ok and response.request.method == filter_method.upper():
                try:
                    data = response.json()
                    print(
                        f"✅ Request {response.request.method} {response.url}. Status: {response.status}\nData: {data}\n---")
                except:
                    pass

        return self.page.on("response", check_response)

    def block_images_requests(self):
        """Block image requests for playwright browser"""
        def block_images(route):
            # Retrieve request from object route
            request = route.request

            if request.resource_type == "image":
                print(f"🚫 Block imaged: {request.url}")
                route.abort()  # Sync version, API called directly
            else:
                route.continue_()  # API called directly

        return self.page.route("**/*", block_images)

    def modify_request(self, filter_method: str, filter_key_url: str, modify_method: str = None,
                       modify_payload: dict = None,
                       modify_header: dict = None, modify_request_path: str = None):
        """
        Interceptor method. Catch request with specified filter (method, url) and modify it (method, headers, request path,
        request payload)
        :param filter_method: specify interceptor filter by request method
        :param filter_key_url: specify interceptor filter by certain url
        :param modify_method: replace real request method by rewritten one
        :param modify_payload: replace real request payload by rewritten one
        :param modify_header: replace real request header by rewritten one
        :param modify_request_path: replace real request path by rewritten one
        :return:
        """

        target_method = filter_method.upper()

        def modify(route):
            request = route.request

            if request.method == target_method and filter_key_url in request.url:
                # 1. Define new headers
                new_headers = {**request.headers}  # Create copy of dict
                if modify_header:
                    new_headers.update(modify_header)

                # 2.  Define request body (transform dict to JSON-row)
                new_post_data = json.dumps(modify_payload) if modify_payload is not None else request.post_data

                # 3. Define request path
                new_url = self.replace_url(request.url, modify_request_path) if modify_request_path else request.url

                # 2. Define request method
                new_method = modify_method if modify_method else request.method

                # Modify and send request
                route.continue_(
                    method=new_method,
                    post_data=new_post_data,
                    headers=new_headers,
                    url=new_url
                )
                print(f"🔄 Request is modified: {new_method} -> {new_url}")
            else:
                # Skip rest requests
                route.continue_()

        # Set up interceptor
        self.page.route(f"**/{filter_key_url}", modify)

    def modify_response_mock(self, filter_method: str, filter_key_url: str, modify_status_code: int = 200,
                             modify_body: dict = None, modify_content_type: str = "application/json"):
        """
        Interceptor method. Replace real request specified filter (method, url)
        by modified mock (body, content-type, status code)
        :param filter_method: specify method to filter requests for mock response
        :param filter_key_url: specify url to filter requests for mock response
        :param modify_status_code: set mock status code for intercepted request
        :param modify_body: set mock response body for intercepted request
        :param modify_content_type: set mock content type for intercepted request
        :return:
        """
        target_method = filter_method.upper()

        def mock_api(route):  # Only one argument route
            request = route.request

            if request.method == target_method and filter_key_url in request.url:
                # Modify dict to json row
                body_str = json.dumps(modify_body) if modify_body is not None else request.post_data

                # Return fake response without requests to real BE
                route.fulfill(
                    status=modify_status_code,
                    body=body_str,
                    content_type=modify_content_type
                )
                print(f"✅ API Response is replaced by mock: {request.url}")
            else:
                route.continue_()

        # Filter url
        self.page.route(f"**/*{filter_key_url}*", mock_api)

    def modify_real_response(self, filter_method: str, filter_key_url: str, modify_status_code: int = None,
                             modify_body: dict = None, modify_content_type: str = None):
        """
        Intercept request. Modify response (status code, body, content type) with certain request filter (method, url)
        :param filter_method: modify request with specific method
        :param filter_key_url: modify request with specific url
        :param modify_status_code: specify 'new' status code
        :param modify_body: specify 'new' request body
        :param modify_content_type: specify 'new' request content type
        :return:
        """
        target_method = filter_method.upper()

        def intercept_api(route):
            request = route.request

            if request.method == target_method and filter_key_url in request.url:
                # 1. Perform real request to server, await for response
                response = route.fetch()

                # 2. Define status code Определяем статус-код
                status = modify_status_code if modify_status_code is not None else response.status

                # 3. Define content type (modify or keep existed)
                content_type = modify_content_type if modify_content_type else response.headers.get("content-type",
                                                                                                    "application/json")
                # 4. Define response body (modify or keep existed)
                body_str = json.dumps(modify_body) if modify_body is not None else response.text()

                # 5. Return 'changed' response to client (playwright browser)
                route.fulfill(
                    response=response,  # Send original response as base
                    status=status,
                    body=body_str,
                    headers={**response.headers, "content-type": content_type}
                )
                print(f"🔄 Real server response is intercepted and modified: {request.url}")
            else:
                route.continue_()

        self.page.route(f"**/*{filter_key_url}*", intercept_api)
