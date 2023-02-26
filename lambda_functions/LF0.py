import boto3
import json

def lambda_handler(event, context):
    # TODO implement
    lex = boto3.client('lexv2-runtime')
    
    messages = json.loads(event['body'])['messages']
    response = lex.recognize_text(botId='KS4YQORYQI', botAliasId='GNNZSRTDOW', localeId='en_US', sessionId='LF0', text=messages[0]['unstructured']['text'])
    response['messages'][0]['type'] = 'unstructured'
    response['messages'][0]['unstructured'] = {}
    response['messages'][0]['unstructured']['text'] = response['messages'][0]['content']

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(response)
    }
