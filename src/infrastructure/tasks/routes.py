import asyncio

from celery import Task, shared_task

from application.use_cases.routes.enums import RouteGenerationMode as Mode


@shared_task(bind=True, name="bestway.tasks.default.route_generate_gpt_task")
def route_generate_gpt_task(self: Task, user_id: int, survey_id: int, mode: str = Mode.FULL.name) -> None:
    loop = asyncio.get_event_loop()
    use_case = self.app.container.route_chatgpt_generate_use_case()
    loop.run_until_complete(use_case.execute(user_id, survey_id, mode))
