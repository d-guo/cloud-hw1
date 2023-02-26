import json
import boto3

from boto3.dynamodb.conditions import Key
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def get_sqs():
    sqs = boto3.client('sqs')
    url = 'https://sqs.us-east-1.amazonaws.com/537502574872/dining-concierge-requests'

    res = sqs.receive_message(
        QueueUrl=url,
        AttributeNames=['SentTimestamp'],
        MessageAttributeNames=['All'],
        MaxNumberOfMessages=10
    )
    
    messages = []
    if 'Messages' in res:
        for m in res['Messages']:
            messages.append({key: val['StringValue'] for key, val in m['MessageAttributes'].items()})
            sqs.delete_message(QueueUrl=url, ReceiptHandle=m['ReceiptHandle'])
    
    return messages

def query_opensearch(cuisine):
    REGION = 'us-east-1'
    HOST = 'search-yelp-restaurants-dining-uqjdd4t2jfqmkcjsesapxiy7aa.us-east-1.es.amazonaws.com'
    INDEX = 'restaurants'
    q = {'size': 5, 'query': {'multi_match': {'query': cuisine}}}

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)
    res = client.search(index=INDEX, body=q)
    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])

    restaurant_ids = [result['id'] for result in results]
    
    return restaurant_ids

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

def query_dynamodb(restaurant_ids):
    client = boto3.resource('dynamodb')
    table = client.Table('yelp-restaurants')

    restaurants = []
    for id in restaurant_ids:
        response = table.get_item(
            Key={
                'id': id
            }
        )
        restaurants.append(response['Item'])

    return restaurants

def send_ses(recommendation_info, email):
    client = boto3.client('ses')
    message = f"""
    Hello! This is your dining concierge.
    
    Here are my restaurant suggestions for {recommendation_info['cuisine']} food, for {recommendation_info['people']} people, for {recommendation_info['date']} at {recommendation_info['time']}:
    1. {recommendation_info['recs'][0]['name']}, located at {recommendation_info['recs'][0]['address']},
    2. {recommendation_info['recs'][1]['name']}, located at {recommendation_info['recs'][1]['address']},
    3. {recommendation_info['recs'][2]['name']}, located at {recommendation_info['recs'][2]['address']}.
    
    Enjoy your meal!
    """
    response = client.send_email(
        Destination={
            'ToAddresses': [email]
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': message
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'Your Requested Restaurant Recommendations'
            }
        },
        Source='dg3287@columbia.edu'
    )

def lambda_handler(event, context):
    messages = get_sqs()
    for message in messages:
        restaurant_ids = query_opensearch(message['cuisine'])
        restaurants = query_dynamodb(restaurant_ids)
        recommendation_info = message.copy()
        recommendation_info['recs'] = restaurants
        send_ses(recommendation_info, message['email'])

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }
