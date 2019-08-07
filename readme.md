# Flask-Redis-Celery

#### **Description**
Basic Flask app structure for integration with Redis and Celery.

Flask-Redis-Celery is divided in 3 microservices:
- Flask is a Python Web Framework. Is the base webapp. (http://flask.pocoo.org)
- Celery is an background asynchronous task service. (http://www.celeryproject.org)
- Redis is in-memory data structure store, which can be used as a database, cache and message broker. Default Redis installation (password-protected)


### Installation

```bash
git clone https://github.com/nyamba/ocr-api.git
```

### Build & Launch

```bash
docker-compose build && docker-compose up -d 
```



To shut down:

```bash
docker-compose down
```
Request:
```
https://localhost:5000/?file_key=WTf/pdf
```


To change the endpoints, update the code in [app.py](app.py)
---

MORE [http://allynh.com/blog/flask-asynchronous-background-tasks-with-celery-and-redis/]
