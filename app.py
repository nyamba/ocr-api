import time, sys, os

import pdf2image
import pytesseract
import boto3
import botocore
from PIL    import Image
from PyPDF2 import PdfFileReader
from flask  import Flask , request
from celery import Celery


DPI = 200
flask_app = Flask(__name__)
flask_app.config.update(
    CELERY_BROKER_URL='redis://redis:6379',
    CELERY_RESULT_BACKEND='redis://redis:6379'
)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(flask_app)

def extract_pdf(pdf_path, pages_len):
    full_text = []
    for index in range(pages_len):
        start_time = time.time()
        print('extracting page: ', index+1, '/', pages_len)
        pil_images = pdf2image.convert_from_path(pdf_path, dpi=DPI, first_page=index+1, last_page=index+1)
        text =  pytesseract.image_to_string(pil_images[0], lang='mon+eng+eq', config='--psm  6')
        end_time = time.time()
        print(text)
        print('#' * 15, ' time:' + str(end_time - start_time), '#'*15)
        full_text.append(text)

    return full_text


@celery.task()
def parse_pdf(file_key):
    BUCKET_NAME = 'contents-demo1'
    s3 = boto3.resource('s3')
    s3.Bucket(BUCKET_NAME).download_file(file_key, 'sample/' + file_key)
    pdf_path = 'sample/' + file_key

    with open(pdf_path, 'r') as f:
        pdf = PdfFileReader(f)
        pages_len = pdf.getNumPages()

    print('TOTAL PAGE: ', pages_len)
    start = time.time()
    text = extract_pdf(pdf_path, pages_len)
    end = time.time()
    print('Total time: ', round(end-start))
    os.remove(pdf_path)
    print('File Deleted : ' , pdf_path)
    update_text(doc_id, full_text)
    return 'DONE'



@flask_app.route('/')
def add_task():
    task = parse_pdf.delay(request.args['file_key'])
    return 'ok ok'


def update_text(doc_id, text):
    pass


def update_status(doc_id, progress):
    pass
