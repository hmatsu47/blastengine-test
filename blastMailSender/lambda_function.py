import boto3
import datetime
import json
import os
import random
import time
import traceback
from base64 import b64decode
from blastengine.Client import Blastengine
from blastengine.Transaction import Transaction
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer

deserializer = TypeDeserializer()

be_api_user = boto3.client('kms').decrypt(
    CiphertextBlob=b64decode(os.environ['BLASTENGINE_API_USER']),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext'].decode('utf-8')
be_api_key = boto3.client('kms').decrypt(
    CiphertextBlob=b64decode(os.environ['BLASTENGINE_API_KEY']),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext'].decode('utf-8')

table_sender   = os.environ['TABLE_SENDER']
table_sent_log = os.environ['TABLE_SENT_LOG']

MAX_REQUEST_COUNT = 3
TIME_SLEEP  = 60
TIME_JITTER = 5

def lambda_handler(event, context):
    # blastengine初期化
    Blastengine(be_api_user, be_api_key)
    # テーブルの準備
    dynamodb = boto3.resource('dynamodb')
    tableLog = dynamodb.Table(table_sent_log)
    tableSender = dynamodb.Table(table_sender)
    # ストリームから受け取った変更後レコードリストをループ処理
    for record in event['Records']:
        eventName = record['eventName']
        # DynamoDB StreamsのフィルタでもeventNameをフィルタしているが設定ミスでの課金を防ぐためeventNameを確認
        if (eventName == 'INSERT' or eventName == 'MODIFY'):
            image = record['dynamodb']['NewImage']
            request_count = 0
            mail_sent     = 0
            delivery_id   = 0
            while request_count < MAX_REQUEST_COUNT:
                try:
                    # eventをdictに変換して値を抽出
                    item = deserialize(image)
                    message = Message(item)
                    # blastengineで送信
                    if (mail_sent == 0):
                        delivery_id = send(message)
                        mail_sent = 1
                    # 履歴用テーブルに転記
                    tb_response = store(tableLog, message, delivery_id)
                    print('Result table:', tb_response)
                    # 送信用テーブルからレコード削除
                    tableSender.delete_item(Key={'id': message.id})
                    # 送信 OK
                    request_count = MAX_REQUEST_COUNT
                except Exception as e:
                    # 例外→ログを残す
                    print(traceback.format_exc())
                    request_count += 1
                    if (request_count >= MAX_REQUEST_COUNT):
                        # 連続失敗上限到達→スキップ
                        print(image)
                        print('Retry count exceeded. -> skip')
                    else:
                        # 60～64秒スリープしてリトライ
                        time.sleep(TIME_SLEEP + random.randrange(TIME_JITTER))
                        print('Retry:', request_count)
    return 'Successfully processed {} records.'.format(len(event['Records']))

class Message():
    # 送信メールメッセージクラス
    def __init__(self, item):
        # コンストラクタ
        self.id           = item['id']
        self.from_address = item['fromAddress']
        self.from_name    = item['fromName']
        self.subject      = item['subject']
        self.text_part    = item['textPart']
        self.to_address   = item['toAddress']
        self.to_name      = item['toName']

def deserialize(image):
    # dictに変換
    d = {}
    for key in image:
        d[key] = deserializer.deserialize(image[key])
    return d

def send(message):
    # blastengineで通知
    transaction = Transaction()
    transaction.subject(message.subject)
    transaction.text_part(message.text_part)
    transaction.fromAddress(message.from_address, message.from_name)
    transaction.to(message.to_address)

    return transaction.send()

def store(table, message, delivery_id):
    # 送信ログ用テーブルに転記
    response = table.put_item(
        Item={
            'deliveryId' : delivery_id,
            'fromAddress': message.from_address,
            'fromName'   : message.from_name,
            'subject'    : message.subject,
            'toAddress'  : message.to_address,
            'toName'     : message.to_name
        }
    )
    if (response['ResponseMetadata']['HTTPStatusCode'] != 200):
        # ステータスコードが200以外→エラー
        print('DynamoDB put_item error:', response)
    return response