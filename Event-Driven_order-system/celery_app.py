from celery import Celery

celery_app = Celery(
    "worker",
    broker="pyamqp://guest@localhost//",
    backend="rpc://"
)

import tasks.stock_tasks