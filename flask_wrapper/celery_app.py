from celery import Celery

# Setting up celery
redis_url = '127.0.0.1:6379'
celery_app = Celery(__name__, broker=f'redis://{redis_url}/0', backend=f'redis://{redis_url}/0')
