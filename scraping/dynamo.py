import boto3
import csv
import datetime

def add_restaurants_for_cuisine(cuisine):
    db = boto3.resource('dynamodb', region_name='us-east-1')
    table = db.Table('yelp-restaurants')

    with open(f'{cuisine}.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['cuisine'] = cuisine
            row['insertedAtTimestamp'] = str(datetime.datetime.now())
            table.put_item(Item=row)

if __name__ == '__main__':
    for cuisine in ['chinese', 'italian', 'japanese', 'mexican', 'thai']:
        print(f'starting {cuisine}')
        add_restaurants_for_cuisine(cuisine)
        print(f'finished {cuisine}')
