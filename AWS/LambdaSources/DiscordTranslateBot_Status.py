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
        userHash = json.loads(body).get('userHash')
        print(userHash)
        
        # DynamoDBから翻訳先の言語を取得
        table = ddb_client.Table('DiscordTranslateBot_Langage')
        res = table.get_item(
            Key={
                'UserHash': userHash
            }
        )
        if 'Item' in res:
            sourceLanguageCode = res.get('Item').get('SourceLanguageCode')
            targetLanguageCode = res.get('Item').get('TargetLanguageCode')
        else:
            sourceLanguageCode = 'auto'
            targetLanguageCode = 'ja'
            res = table.put_item(
                Item={
                    'UserHash': userHash,
                    'SourceLanguageCode':sourceLanguageCode,
                    'TargetLanguageCode':targetLanguageCode
                }
            )
            
        statusCode = 200
        body = json.dumps({
            'info': {
                'SourceLanguageCode': sourceLanguageCode,
                'TargetLanguageCode': targetLanguageCode
            }
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
