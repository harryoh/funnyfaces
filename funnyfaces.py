from __future__ import print_function

# import json
import os
import urllib
import logging
import pymysql
import cognitive_face as CF

import config

FACE_API_KEY = os.getenv('FACE_API_KEY', config.face_api_key)
RDS_HOST = os.getenv('RDS_HOST', config.rds_host)
RDS_PORT = os.getenv('RDS_PORT', config.rds_port)
RDS_USER = os.getenv('RDS_USER', config.rds_user)
RDS_PWD = os.getenv('RDS_PWD', config.rds_pwd)
RDS_DB = os.getenv('RDS_DB', config.rds_db)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def write_data(s3url, faces):
    conn = pymysql.connect(RDS_HOST, user=RDS_USER, passwd=RDS_PWD, db=RDS_DB,
                           connect_timeout=5)
    query = (
        'INSERT INTO faces_tbl (face_id, smile, age, male, female, img_url) '
        'VALUES (%s, %s, %s, %s, %s, %s)'
    )

    with conn.cursor() as cur:
        for face in faces:
            face_attr = face['faceAttributes']
            data = (face['faceId'], face_attr['smile']*100,
                    face_attr['age'],
                    face_attr['gender'] == 'male',
                    face_attr['gender'] == 'female',
                    s3url)
            cur.execute(query, data)
        conn.commit()

    return len(data)


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    region = event['Records'][0]['awsRegion']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    s3url = 'https://s3.{}.amazonaws.com/{}/{}'.format(region, bucket, key)

    CF.Key.set(FACE_API_KEY)
    result = CF.face.detect(s3url, attributes='age,gender,smile')

    item_count = write_data(s3url, result)
    return item_count
