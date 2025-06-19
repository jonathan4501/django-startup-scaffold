from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_scaffold.settings')

app = Celery('startup_scaffold')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()



app.conf.beat_schedule = {
    'mark-expired-jobs-every-hour': {
        'task': 'jobs.tasks.mark_expired_jobs',
        'schedule': crontab(minute=0, hour='*'),  # every hour
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
