# Docker Flask Celery Redis

A basic [Docker Compose](https://docs.docker.com/compose/) template for orchestrating a [Flask](http://flask.pocoo.org/) application & a [Celery](http://www.celeryproject.org/) queue with [Redis](https://redis.io/)

![alt text](https://github.com/nyamba/ocr-api/img.png)

### Installation

```bash
git clone https://github.com/nyamba/ocr-api.git
```

### Build & Launch

```bash
docker-compose up -d --build
```

This will expose the Flask application's endpoints on port `5001` as well as a [Flower](https://github.com/mher/flower) server for monitoring workers on port `5555`

To add more workers:
```bash
docker-compose up -d --scale worker=5 --no-recreate
```

To shut down:

```bash
docker-compose down
```

To change the endpoints, update the code in [app.py]
---

MORE [http://allynh.com/blog/flask-asynchronous-background-tasks-with-celery-and-redis/]
