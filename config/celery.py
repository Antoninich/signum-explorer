import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def peer_cmd_task(self):
    from scan.peers import peer_cmd
    peer_cmd()


app.conf.beat_schedule = {
    "task_cmd": {
        "task": "scan.tasks.task_cmd",
        "schedule": 60.0
    },
    "peer_cmd_task": {
        "task": "config.celery.peer_cmd_task",
        "schedule": 300.0
    },
    "add_new_pools": {
        "task": "scan.views.pools.add_new_pools",
        "schedule": 120.0
    },
}
