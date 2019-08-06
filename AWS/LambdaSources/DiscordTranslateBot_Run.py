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
        
        # 翻訳
        body = json.loads(body).get('TargetText')
        
        translate_scheme = json.dumps({
            "SourceLanguageCode": sourceLanguageCode,
            "TargetLanguageCode": targetLanguageCode,
            "TargetText": body
        })
        
        # DynamoDBから翻訳後のデータを取得
        table = ddb_client.Table('DiscordTranslateBot_TranslatedText')
        res = table.get_item(
            Key={
                'translate_scheme':translate_scheme
            }
        )
        if 'Item' in res:
            # テーブルに記録されている場合そのデータを返す
            statusCode = 200
            body = res.get('Item').get("TranslatedText")
        else:
            print(sourceLanguageCode)
            print(targetLanguageCode)
            # テーブルに記録されていない場合Amazon Translatorで翻訳する
            translate = boto3.client("translate", region_name="us-west-2")
            response = translate.translate_text(
                Text=body,
                SourceLanguageCode=sourceLanguageCode,
                TargetLanguageCode=targetLanguageCode
            )
            logger.info(response)
            
            # 翻訳データを返す
            statusCode = 200
            body = response['TranslatedText']
            
            # DynamoDBに翻訳後のデータを記録する
            response = table.put_item(
                Item={
                    'translate_scheme':translate_scheme,
                    'TranslatedText':body
                }
            )
    except ClientError as e:
        statusCode = e.response["ResponseMetadata"]["HTTPStatusCode"]
        body = json.dumps(e.response)
        
    return {
        'isBase64Encoded': False,
        'statusCode': statusCode, 
        'headers':{}, 
        'body': json.dumps({
            'translatedText':body
        })
    }