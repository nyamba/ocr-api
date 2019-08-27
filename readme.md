# Flask-Redis-Celery OCR

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
 ### ENV FILE
 create .env file with following variables
 ```
AWS_ACCESS_KEY_ID=<Your AWS key id>
AWS_SECRET_ACCESS_KEY=<aws secret>
HASURA_SECRET= < hasura key>
HASURA_GQL_URL=< hasura url>
PAGE_SEPERATOR=##############
 ```


To shut down:

```bash
docker-compose down
```
Request:
```
curl --header "Content-Type: application/json" --request POST --data '{"content_id": 2803, "key": "10a2r67jxu0yqqh_ST_470002200_3584.PDF", "bucket": "contents-demo1"}' localhost:5000/
```

### Monitoring Web
http://localhost:5555
![alt text](https://github.com/Tsevel/ocr-api/blob/master/flower.PNG)
