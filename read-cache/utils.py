import requests
import os
from datetime import datetime

GIT_TOKEN = os.getenv("GITHUB_API_TOKEN")
AUTH_HEADERS = { "Authorization": "Bearer " + GIT_TOKEN } if GIT_TOKEN else None

GITHUB_API_PATH = "https://api.github.com/"
NETFLIX_REPOS = "orgs/Netflix/repos"
CACHED_PATHS = set(["/", "orgs/Netflix", NETFLIX_REPOS, "orgs/Netflix/members"])

def paginated_request(url):
    response = requests.get(url, headers = AUTH_HEADERS)
    response_data = response.json()
    
    while 'next' in response.links.keys():
        response = requests.get(response.links['next']['url'], headers = AUTH_HEADERS )
        response_data.extend(response.json())
    return response_data

def timestamp_to_iso(timestamp):
    return datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%dT%H:%M:%SZ')