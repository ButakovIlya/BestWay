from celery import Task, shared_task


@shared_task(bind=True, name="bestway.tasks.default.chatgpt_process_route_task")
def chatgpt_process_route_task(self: Task) -> None:
    print("Задачка запущена")
    return "Success"
