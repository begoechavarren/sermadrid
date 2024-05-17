from celery import Celery

app = Celery("app", broker="redis://redis:6379/0")

app.conf.update(
    result_backend="redis://redis:6379/0",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

app.autodiscover_tasks(["app.app.worker.v1.tasks"])


if __name__ == "__main__":
    app.start()
