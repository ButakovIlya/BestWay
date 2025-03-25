from config.containers import Container
from config.loggers import config_loggers
from config.settings import Settings

from celery import Celery

settings = Settings()
TASKS_PACKAGES = ["infrastructure.tasks"]


def create_app() -> Celery:
    app = Celery(
        settings.task.app_name,
        broker=settings.task.broker_url,
        backend=settings.task.result_url,
    )
    app.autodiscover_tasks(TASKS_PACKAGES, related_name="__init__")
    container = Container()
    container.wire(modules=[
        "api.public.profile",
    ])
    container.wire(packages=["infrastructure"])
    app.container = container
    config_loggers()
    return app


app = create_app()
