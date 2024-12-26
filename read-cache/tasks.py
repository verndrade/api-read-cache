from celery import Celery, Task, shared_task

from cache import redis_client
from utils import CACHED_PATHS, GITHUB_API_PATH, NETFLIX_REPOS, paginated_request

from datetime import datetime
import json

@shared_task()
def refresh_cache(path):
    data = paginated_request(GITHUB_API_PATH + path)
    redis_client.set(path, json.dumps(data))

    if path == NETFLIX_REPOS:
        for obj in data:
            redis_client.zadd("forks", { obj["full_name"]: obj["forks"] } )

            timestamp = datetime.fromisoformat(obj["updated_at"]).timestamp() 
            redis_client.zadd("last_updated", { obj["full_name"]: timestamp } )
            
            redis_client.zadd("open_issues", { obj["full_name"]: obj["open_issues"] } )
            redis_client.zadd("stars", { obj["full_name"]: obj["stargazers_count"] } )

    return path + " cached!"
    
@shared_task()
def periodic_refresh():
    for path in CACHED_PATHS:
        refresh_cache.delay(path)

    return "queued refresh tasks!"
