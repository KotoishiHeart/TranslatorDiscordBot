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
            
        # 設定変更
        if 'SourceLanguageCode' in json.loads(body):
            sourceLanguageCode = json.loads(body).get('SourceLanguageCode')
            setLanguage = sourceLanguageCode
        else:
            targetLanguageCode = json.loads(body).get('TargetLanguageCode')
            setLanguage = targetLanguageCode
        
        # DynamoDB更新
        table = ddb_client.Table('DiscordTranslateBot_Langage')
        res = table.update_item(
            Key={
                'UserHash': userHash
            },
            UpdateExpression="set SourceLanguageCode = :slc, TargetLanguageCode = :tlc",
            ExpressionAttributeValues={
                ':slc': sourceLanguageCode,
                ':tlc': targetLanguageCode
            }
        )
        if sourceLanguageCode == targetLanguageCode:
            body = 'SourceAndTargetSameLanguage'
        else:
            body = setLanguage
        
        statusCode = 200
        body = json.dumps({
            'language': body
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