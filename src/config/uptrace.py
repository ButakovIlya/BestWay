import uptrace
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from config.settings import Settings


def config_uptrace(app: FastAPI) -> None:
    settings = Settings()
    if not settings.uptrace.enabled:
        return

    uptrace.configure_opentelemetry(
        dsn=settings.uptrace.dsn,
        service_name=settings.app.title,
        service_version=settings.app.version,
    )
    FastAPIInstrumentor.instrument_app(app)
