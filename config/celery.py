import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.update(imports=['scan.peers'])


@app.task(bind=True, ignore_result=True)
def peer_cmd_task(self):
    from scan.peers import peer_cmd
    peer_cmd()


app.conf.beat_schedule = {
    "task_cmd": {
        "task": "scan.tasks.task_cmd",
        "schedule": 60.0
    },
    "peer_cmd": {
        "task": "scan.peers.peer_cmd",
        "schedule": 300.0
    },
    "add_new_pools": {
        "task": "scan.views.pools.add_new_pools",
        "schedule": 10.0
    },
}
