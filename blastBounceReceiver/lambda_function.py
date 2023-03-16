import json
import boto3
import os
import traceback
from botocore.exceptions import ClientError

table_sent_log = os.environ['TABLE_SENT_LOG']
table_bounce   = os.environ['TABLE_BOUNCE']

def lambda_handler(event, context):
    # 履歴用テーブル・バウンス用テーブルの準備
    dynamodb = boto3.resource('dynamodb')
    tableSentLog = dynamodb.Table(table_sent_log)
    tableBounce  = dynamodb.Table(table_bounce)
    # リクエストから必要情報を取得
    body = json.loads(event['body'])
    events = body['events']
    # バウンス用テーブルに記録
    for bodyItem in events:
        try:
            bounceItem = BounceItem(tableSentLog, bodyItem['event'])
            tb_response = store(tableBounce, bounceItem)
            print('Result table:', tb_response)
        except Exception as e:
            # 例外→ログを残す
            print(traceback.format_exc())
            print(bounceItem)
            # 異常終了
            return {
                'statusCode': 500,
                'body'      : json.dumps({'message':'NG'})
    }
    # 正常終了
    return {
        'statusCode': 200,
        'body'      : json.dumps({'message':'OK'})
    }

class BounceItem():
    # バウンス項目クラス
    def __init__(self, table, item):
        # コンストラクタ

        # Webhookの情報を取得
        self.type          = item['type']
        self.datetime      = item['datetime']
        detail = item['detail']
        self.to_address    = detail['mailaddress']
        self.subject       = detail['subject']
        self.error_code    = str(detail['error_code'])
        self.error_message = detail['error_message']
        self.delivery_id   = detail['delivery_id']
        # 送信履歴の情報を取得
        response = table.get_item(Key={'deliveryId': self.delivery_id})
        sentItem = response['Item']
        self.from_address  = sentItem['fromAddress']
        self.from_name     = sentItem['fromName']
        self.to_name       = sentItem['toName']

def store(table, item):
    # バウンス用テーブルに転記
    response = table.put_item(
        Item={
            'deliveryId'  : item.delivery_id,
            'fromAddress' : item.from_address,
            'fromName'    : item.from_name,
            'toAddress'   : item.to_address,
            'toName'      : item.to_name,
            'subject'     : item.subject,
            'datetime'    : item.datetime,
            'type'        : item.type,
            'errorCode'   : item.error_code,
            'errorMessage': item.error_message
        }
    )
    if (response['ResponseMetadata']['HTTPStatusCode'] != 200):
        # ステータスコードが200以外→エラー
        print('DynamoDB put_item error:', response)
    return response
