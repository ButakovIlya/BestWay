from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIRECTORY = Path(__file__).parents[2]


class DBSettings(BaseModel):
    name: str = "bestway"
    host: str = "localhost"
    port: int = 5432
    user: str = "bestway"
    password: str = "root"
    dialect: str = "postgresql+asyncpg"
    pool_size: int = 2
    max_overflow: int = 4
    echo: bool = False

    @property
    def dsn(self) -> str:
        print(f"{self.dialect}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}")
        return f"{self.dialect}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        # print(f"{self.dialect}://root:root@localhost:5432/bestway")
        # return f"{self.dialect}://root:root@localhost:5432/bestway"


class AppSettings(BaseModel):
    title: str = "BestWay"
    debug: bool = False
    version: str = "0.1.0"

    base_url: str = "http://localhost:8002"


class UptraceSettings(BaseModel):
    enabled: bool = False
    dsn: str | None = None


class ApiSettings(BaseModel):
    prefix: str = "/api"
    admin: str = "/admin"
    public: str = "/public"

    docs_endpoint: str = "/docs"
    openapi_endpoint: str = "/openapi.json"

    @property
    def docs_url(self) -> str:
        return f"{self.prefix}{self.docs_endpoint}"

    @property
    def openapi_url(self) -> str:
        return f"{self.prefix}{self.openapi_endpoint}"

    @property
    def admin_prefix(self) -> str:
        return f"{self.prefix}{self.admin}"

    @property
    def public_prefix(self) -> str:
        return f"{self.prefix}{self.public}"


class JWTSettings(BaseModel):
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 600000
    refresh_token_expire_days: int = 600000


class CentrifugoSettings(BaseModel):
    host: str = "http://localhost:8001"
    api_key: str = "secret"
    publish_endpoint: str = "/api/publish"

    @property
    def headers(self) -> dict:
        return {"Content-type": "application/json", "X-API-Key": self.api_key}


class RedisSettings(BaseModel):
    host: str = "redis://localhost:6379/2"
    # host: str = "redis://redis:6379/2"
    password: str = ""


class TaskSettings(BaseModel):
    app_name: str = "bestway"
    broker_url: str = "redis://localhost:6379/0"
    result_url: str = "redis://localhost:6379/1"

    # broker_url: str = "redis://redis:6379/0"
    # result_url: str = "redis://redis:6379/1"


class SmsSettings(BaseSettings):
    service_url: str = ""
    api_key: str = ""
    cache_timeout: int = 300  # По умолчанию 5 минут

    class Config:
        env_prefix = "SMS__"
        env_nested_delimiter = ("__",)


class StorageSettings(BaseModel):
    storage_directory: str = "storage"
    media_directory: str = "media"
    max_file_size_mb: int = 10

    @property
    def storage_path(self) -> Path:
        return BASE_DIRECTORY / self.storage_directory

    @property
    def media_path(self) -> Path:
        return self.storage_path / self.media_directory


class ProxySettings(BaseSettings):
    host: str = "127.0.0.1"
    http_port: int = 62566
    socks5_port: int = 62567
    username: str = "username"
    password: str = "password"


class ChatGPTSettings(BaseSettings):
    service_url: str = "https://api.openai.com/v1/chat/completions"
    api_key: str = "secret"
    model: str = "gpt-4o-mini"
    max_responses_per_day: int = 100
    request_delay: int = 1  # в секундах
    max_request_retries: int = 3
    chatgpt_request_timeout: int = 60


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    task: TaskSettings = TaskSettings()
    uptrace: UptraceSettings = UptraceSettings()
    db: DBSettings = DBSettings()
    storage: StorageSettings = StorageSettings()
    redis: RedisSettings = RedisSettings()
    api: ApiSettings = ApiSettings()
    jwt: JWTSettings = JWTSettings()
    centrifugo: CentrifugoSettings = CentrifugoSettings()

    chatgpt: ChatGPTSettings = ChatGPTSettings()
    proxy: ProxySettings = ProxySettings()

    sms: SmsSettings = SmsSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )
