# API Read Cache - Netflix

## Technologies used:
- Flask - for API routing
- Celery - for Task Scheduling
- Redis - for Caching

## To run the service:

1. Install Python 3 
2. Run `pip3 install -r requirements.txt` to install dependencies
3. Install redis-server 
    - On Linux: `sudo apt-get install redis` then `sudo service redis-server start`
4. Run `cd read-cache`
5. Add optional GITHUB_API_TOKEN env variable
    - `export GITHUB_API_TOKEN=###`

In individual terminal windows: 

6.  Run Celery task queue
    - `celery -A app.celery_app worker`
7. Run Celery beat scheduler
    - `celery -A app.celery_app beat`
8. Run Flask App with optional PORT parameter
    - `flask run -p PORT`


