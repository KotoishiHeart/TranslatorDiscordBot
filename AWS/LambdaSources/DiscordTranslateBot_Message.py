import boto3
from botocore.exceptions import ClientError
import json
import logging

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

# DynamoDBクライアント
ddb_client = boto3.resource('dynamodb')

def lambda_handler(event, context):
    logger.info(event)
    
    try:
        # TODO implement
        body = event.get('body')
        message = json.loads(body).get('message')
        print(message)
        
        # メッセージ登録
        table = ddb_client.Table('DiscordTranslateBot_Message')
        res = table.put_item(
            Item={
                'message': message
            }
        )
        
        statusCode = 200
        body = json.dumps({
            'message': 'message'
        })
    except ClientError as e:
        statusCode = e.response["ResponseMetadata"]["HTTPStatusCode"]
        body = json.dumps(e.response)
            
    return {
        'isBase64Encoded': False,
        'statusCode': statusCode, 
        'headers':{}, 
        'body': body
    }