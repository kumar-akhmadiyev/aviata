from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, signals


app = Celery('celery_aviata',
				backend='redis://localhost:6379/0',
				broker='pyamqp://guest@localhost//',
				include=['tasks.tasks'])
