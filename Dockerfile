FROM python:2.7-alpine

RUN apk add --no-cache gcc musl-dev linux-headers \
	poppler-utils tesseract-ocr \
	build-base python-dev py-pip jpeg-dev zlib-dev 


WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN mkdir sample
CMD ["flask", "run"]