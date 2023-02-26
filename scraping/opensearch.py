import csv
import json

def csv_to_json(cuisine, csv_path, json_path):
    restaurants = []
    with open(csv_path, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['cuisine'] = cuisine
            restaurants.append(row)

    indexed_data = []
    for restaurant in restaurants:
        indexed_data.append({
            'index': {
                '_index': 'restaurants',
                '_id': restaurant['id']
            }
        })
        indexed_data.append({
            'id': restaurant['id'],
            'cuisine': restaurant['cuisine']
        })

    with open(json_path, mode='w', encoding='utf-8') as f:
        for item in indexed_data:
            f.write(json.dumps(item) + '\n')

if __name__ == '__main__':
    for cuisine in ['chinese', 'italian', 'japanese', 'mexican', 'thai']:
        csv_to_json(cuisine, f'{cuisine}.csv', f'{cuisine}.json')

# curl -XPOST https://search-yelp-restaurants-dining-uqjdd4t2jfqmkcjsesapxiy7aa.us-east-1.es.amazonaws.com/_bulk --data-binary @chinese.json -H 'Content-Type: application/json' -u master:pw
# curl -XPOST https://search-yelp-restaurants-dining-uqjdd4t2jfqmkcjsesapxiy7aa.us-east-1.es.amazonaws.com/_bulk --data-binary @italian.json -H 'Content-Type: application/json' -u master:pw
# curl -XPOST https://search-yelp-restaurants-dining-uqjdd4t2jfqmkcjsesapxiy7aa.us-east-1.es.amazonaws.com/_bulk --data-binary @japanese.json -H 'Content-Type: application/json' -u master:pw
# curl -XPOST https://search-yelp-restaurants-dining-uqjdd4t2jfqmkcjsesapxiy7aa.us-east-1.es.amazonaws.com/_bulk --data-binary @mexican.json -H 'Content-Type: application/json' -u master:pw
# curl -XPOST https://search-yelp-restaurants-dining-uqjdd4t2jfqmkcjsesapxiy7aa.us-east-1.es.amazonaws.com/_bulk --data-binary @thai.json -H 'Content-Type: application/json' -u master:pw