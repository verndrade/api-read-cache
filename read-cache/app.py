from flask import Flask, Response
from celery import Celery, Task, signals
from celery.signals import celeryd_init

from cache import redis_client
from utils import CACHED_PATHS, GITHUB_API_PATH, AUTH_HEADERS, paginated_request, timestamp_to_iso

from datetime import datetime
import json
import requests
import tasks

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()

    app.extensions["celery"] = celery_app
    return celery_app

app = Flask(__name__)

app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        beat_schedule={
            "refresh-every-60-seconds": {
                "task": "tasks.periodic_refresh",
                "schedule": 60,
             }
         },
    ),
)
celery_app = celery_init_app(app)

@celeryd_init.connect
def startup_refresh(sender=None, conf=None, **kwargs):
    tasks.periodic_refresh.delay()

@app.route("/healthcheck")
def healthcheck():
    try:
        redis_client.ping()
    except:
        return "Redis connection error", 503

    if redis_client.exists("forks") == 0 or redis_client.exists("last_updated") == 0 or redis_client.exists("open_issues") == 0 or redis_client.exists("stars") == 0:
        return "Views still being created, check back soon!", 503 

    response = requests.get(GITHUB_API_PATH, headers=AUTH_HEADERS )

    if response.status_code != 200:
        return "Unhealthy!", 503

    return "Healthy!"

@app.route("/view/bottom/<int:N>/forks")
def forks(N):
    if N < 1:
        return "[]"

    res = redis_client.zrange("forks", 0, N-1, withscores=True, score_cast_func=int)

    if res == []:
        return "View is still being created, check back soon!", 503

    res.sort(key=lambda x: x[1], reverse=True)

    return res

@app.route("/view/bottom/<int:N>/last_updated")
def last_updated(N):
    if N < 1:
        return "[]"

    res = redis_client.zrange("last_updated", 0, N-1, withscores=True, score_cast_func=timestamp_to_iso)

    if res == []:
        return "View is still being created, check back soon!", 503

    res.sort(key=lambda x: x[1], reverse=True)

    return res

@app.route("/view/bottom/<int:N>/open_issues")
def open_issues(N):
    if N < 1:
        return "[]"

    res = redis_client.zrange("open_issues", 0, N-1, withscores=True, score_cast_func=int)

    if res == []:
        return "View is still being created, check back soon!", 503

    res.sort(key=lambda x: x[1], reverse=True)

    return res

@app.route("/view/bottom/<int:N>/stars")
def stars(N):
    if N < 1:
        return "[]"

    res = redis_client.zrange("stars", 0, N-1, withscores=True, score_cast_func=int)

    if res == []:
        return "View is still being created, check back soon!", 503

    res.sort(key=lambda x: x[1], reverse=True)

    return res

@app.route('/favicon.ico')
def favicon():
    return ""

@app.route('/', defaults={ 'path': '/' } )
@app.route('/<path:path>')
def proxy_path(path):
    if path in CACHED_PATHS:
        cache_response = redis_client.get(path)
    
        if cache_response:
            return json.loads(cache_response)

        return paginated_request(GITHUB_API_PATH + path)

    response = requests.get(GITHUB_API_PATH + path, headers=AUTH_HEADERS )
    return response.json(), response.status_code
