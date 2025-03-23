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
        print(
            f"{self.dialect}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        )
        return f"{self.dialect}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        # print(f"{self.dialect}://root:root@localhost:5432/bestway")
        # return f"{self.dialect}://root:root@localhost:5432/bestway"


class AppSettings(BaseModel):
    title: str = "BestWay"
    debug: bool = False
    version: str = "0.1.0"
    cross_validation_tasks_count: int = 5
    reset_validation_field_tasks_count: int = 5


class UptraceSettings(BaseModel):
    enabled: bool = False
    dsn: str | None = None


class ApiSettings(BaseModel):
    prefix: str = "/api"
    docs_endpoint: str = "/docs"
    openapi_endpoint: str = "/openapi.json"

    @property
    def docs_url(self) -> str:
        return f"{self.prefix}{self.docs_endpoint}"

    @property
    def openapi_url(self) -> str:
        return f"{self.prefix}{self.openapi_endpoint}"


class StorageSettings(BaseModel):
    storage_directory: str = "storage"
    resource_directory: str = "resources"
    results_directory: str = "results"
    actual_data_directory: str = "actual_data"
    upload_resource_file_log_directory: str = "logs"
    cross_validation_file_log_directory: str = "cross_validation"

    @property
    def storage_path(self) -> Path:
        return BASE_DIRECTORY / self.storage_directory

    @property
    def resource_path(self) -> Path:
        return self.storage_path / self.resource_directory

    @property
    def results_path(self) -> Path:
        return self.storage_path / self.results_directory

    @property
    def actual_data_path(self) -> Path:
        return self.storage_path / self.actual_data_directory

    @property
    def upload_resource_file_log_path(self) -> Path:
        return self.storage_path / self.upload_resource_file_log_directory

    @property
    def cross_validation_file_log_path(self) -> Path:
        return self.storage_path / self.cross_validation_file_log_directory


class JWTSettings(BaseModel):
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30


class CentrifugoSettings(BaseModel):
    host: str = "http://localhost:8000"
    api_key: str = "key"
    publish_endpoint: str = "/api/publish"

    @property
    def headers(self) -> dict:
        return {"Content-type": "application/json", "X-API-Key": self.api_key}


class RedisSettings(BaseModel):
    host: str = "redis://localhost:6379/2"
    password: str = ""


class TaskSettings(BaseModel):
    app_name: str = "bestway"
    broker_url: str = "redis://localhost:6379/0"
    result_url: str = "redis://localhost:6379/1"


class SmsSettings(BaseSettings):
    service_url: str
    api_key: str
    cache_timeout: int = 300  # По умолчанию 5 минут

    class Config:
        env_prefix = "SMS__"
        env_nested_delimiter="__",


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    task: TaskSettings = TaskSettings()
    uptrace: UptraceSettings = UptraceSettings()
    db: DBSettings = DBSettings()
    redis: RedisSettings = RedisSettings()
    api: ApiSettings = ApiSettings()
    jwt: JWTSettings = JWTSettings()

    sms: SmsSettings = SmsSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )
