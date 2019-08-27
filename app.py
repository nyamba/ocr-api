import time, sys, os, json

import pdf2image
import pytesseract
import boto3
import botocore
from PIL    import Image
from PyPDF2 import PdfFileReader
from flask  import Flask , request
from celery import Celery
from graphqlclient import GraphQLClient


DPI = 300
HASURA_SECRET = os.environ.get('HASURA_SECRET')
HASURA_GQL_URL = os.environ.get('HASURA_GQL_URL')
PAGE_SEPERATOR = os.environ.get('PAGE_SEPERATOR')

flask_app = Flask(__name__)
flask_app.config.update(
    CELERY_BROKER_URL='redis://redis:6379',
    CELERY_RESULT_BACKEND='redis://redis:6379'
)

client = GraphQLClient(HASURA_GQL_URL)
client.inject_token(HASURA_SECRET, 'x-hasura-admin-secret')


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

def extract_pdf(pdf_path, pages_len, content_id):
    full_text = []
    for index in range(pages_len):
        start_time = time.time()
        print('extracting page: ', index+1, '/', pages_len)
        pil_images = pdf2image.convert_from_path(pdf_path, dpi=DPI, first_page=index+1, last_page=index+1)
        text =  pytesseract.image_to_string(pil_images[0], lang='mon+eng', config='--psm  6')
        end_time = time.time()
        print(text)
        print('#' * 15, ' time:' + str(end_time - start_time), '#'*15)
        full_text.append(text)
        #TODO why is progress always 0
        progress = (index+1)/pages_len * 100
        print('percentage', index, pages_len, progress)
        gq_update_status(content_id, index+1, PAGE_SEPERATOR.join(full_text))

    return full_text


@celery.task()
def parse_pdf(data):
    BUCKET_NAME = data['bucket']
    file_key = data['key']
    content_id = data['content_id']

    #set status to starting
    gq_insert_entry(content_id)

    s3 = boto3.resource('s3')
    s3.Bucket(BUCKET_NAME).download_file(file_key, 'sample/' + file_key)
    pdf_path = 'sample/' + file_key

    with open(pdf_path, 'r') as f:
        pdf = PdfFileReader(f)
        pages_len = pdf.getNumPages()

    print('TOTAL PAGE: ', pages_len)
    start = time.time()
    full_text = extract_pdf(pdf_path, pages_len, content_id)
    end = time.time()
    print('Total time: ', round(end-start))
    os.remove(pdf_path)
    print('File Deleted : ' , pdf_path)
    text = PAGE_SEPERATOR.join(full_text)

    #set status done
    gq_update_text(content_id, text, len(full_text))
    return 'DONE'


@flask_app.route('/', methods=['GET', 'POST'])
def add_task():
    content = request.json
    task = parse_pdf.delay(content)
    return 'ok ok'


def gq_insert_entry(content_id):
    gql = '''
    mutation{
        delete_plagiarism_content_texts(where:{content_id: {_eq: %d}}){
            returning{
              id
              content_id
            }
          }
        insert_plagiarism_content_texts(objects: {content_id: %d, status:"start" ,text:""}){
            returning{
              id
              content_id
            }
          }
    }
    ''' % (content_id, content_id)
    result = client.execute(gql)
    print(result)


def gq_update_text(content_id, text, page_count):
    gql = '''
    mutation update($content_id: bigint!, $text: String!, $meta: jsonb!){
      update_plagiarism_content_texts(
            where: {content_id: {_eq: $content_id}}, 
            _set: {status: "done", text: $text, meta: $meta})
        {
        returning{
          id
        }
      }
    }
    '''
    variables = {
        "content_id": content_id,
        "text": text,
        "meta": {"page_count": page_count}
    }
    result = client.execute(gql, variables)
    print(result)


def gq_update_status(content_id, progress, text):
    gql = '''
    mutation update($content_id: bigint!, $progress: String!, $text: String!){
        update_plagiarism_content_texts(
            where: {content_id: {_eq: $content_id}}, 
            _set: {status: $progress, text: $text})
            {
                returning{
                  id
                  status
                }
            }
    }
    '''
    variables = {
        "content_id": content_id,
        "progress": "inprogress - %d" % (progress),
        "text": text
    }
    result = client.execute(gql, variables)
    print(result)

