import httpx

from config.settings import Settings


class ProxyClient:
    settings = Settings()

    CHATGPT_REQUEST_TIMEOUT = settings.chatgpt.chatgpt_request_timeout

    def __init__(
        self,
        proxy_host: str,
        proxy_http_port: int,
        proxy_username: str,
        proxy_password: str,
    ):
        self.proxy_host = proxy_host
        self.proxy_http_port = proxy_http_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password

        proxy_url = (
            f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_host}:{self.proxy_http_port}"
        )
        transport = httpx.HTTPTransport(proxy=proxy_url)

        self.client = httpx.Client(transport=transport)

    def post(self, url: str, json: dict, headers: dict):
        response = self.client.post(url, json=json, headers=headers, timeout=self.CHATGPT_REQUEST_TIMEOUT)
        response.raise_for_status()
        # logger.info(f"Response headers: {response.headers}")

        return response.json()
