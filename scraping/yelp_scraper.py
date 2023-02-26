import requests
import json
from decimal import Decimal
import csv

API_KEY = 'nUVN07rHrxmrSSy8u4BtvSsZ91vsyi-XQp_PYohL1XaBb9dpILD03QX53IU0xKHsHT6yrbn7170uPjOskAmHJoNcvtcFnTkPqqdj-4z2hFXJh9syUJCXzCOT6yv7Y3Yx'
YELP_ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
YELP_HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def get_restaurants_for_cuisine(cuisine):
    restaurants = []
    restaurants_seen = set()
    for offset in range(0, 1000, 50):
        params = {
            'location': 'Manhattan',
            'term': cuisine,
            'offset': offset,
            'limit': 50
        }
        response = requests.get(YELP_ENDPOINT, headers=YELP_HEADERS, params=params)
        data = json.loads(response.text)

        for business in data['businesses']:
            if business['id'] in restaurants_seen:
                continue
            restaurants.append({
                'id': business['id'],
                'name': business['name'],
                'address': business['location']['address1'],
                'latitude': Decimal(str(business['coordinates']['latitude'])),
                'longitude': Decimal(str(business['coordinates']['longitude'])),
                'review_count': business['review_count'],
                'rating': Decimal(str(business['rating'])),
                'zip_code': business['location']['zip_code']
            })
            restaurants_seen.add(business['id'])

    with open(f'{cuisine}.csv', 'w+', newline='') as f:
        fieldnames = ['id', 'name', 'address', 'latitude', 'longitude', 'review_count', 'rating', 'zip_code']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for restaurant in restaurants:
            writer.writerow(restaurant)

def main():
    for cuisine in ['chinese', 'italian', 'japanese', 'mexican', 'thai']:
        get_restaurants_for_cuisine(cuisine)

if __name__ == '__main__':
    main()

