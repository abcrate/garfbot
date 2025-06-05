import config
import requests
from base64 import b64encode
from garfpy import logger


class Kroger:
    def __init__(self):
        self.client_id = config.CLIENT_ID
        self.client_secret = config.CLIENT_SECRET
        self.auth = b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

    def kroger_token(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self.auth}'
        }

        response = requests.post('https://api.kroger.com/v1/connect/oauth2/token', headers=headers, data={
            'grant_type': 'client_credentials',
            'scope': 'product.compact'
        })

        response.raise_for_status()
        return response.json()['access_token']

    def find_store(self, zipcode, kroken):
        headers = {
            'Authorization': f'Bearer {kroken}',
        }
        params = {
            'filter.zipCode.near': zipcode,
            'filter.limit': 1,
        }
        response = requests.get('https://api.kroger.com/v1/locations', headers=headers, params=params)
        return response.json()

    def search_product(self, product, loc_id, kroken):
        logger.info(f"Searching for {product}...")
        headers = {
            'Authorization': f'Bearer {kroken}',
        }
        params = {
            'filter.term': product,
            'filter.locationId': loc_id,
            'filter.limit': 10
        }
        response = requests.get('https://api.kroger.com/v1/products', headers=headers, params=params)
        return response.json()

    def garfshop(self, query):
        try:
            query = query.split()
            kroken = self.kroger_token()
            product = query[-2]
            zipcode = query[-1]
            loc_data = self.find_store(zipcode, kroken)
            loc_id = loc_data['data'][0]['locationId']
            store_name = loc_data['data'][0]['name']
            product_query = self.search_product(product, loc_id, kroken)
            products = product_query['data']
            sorted_products = sorted(products, key=lambda item: item['items'][0]['price']['regular'])
            response = f"Prices for `{product}` at `{store_name}` near `{zipcode}`:\n"
            for item in sorted_products:
                product_name = item['description']
                price = item['items'][0]['price']['regular']
                response += f"- `${price}`: {product_name} \n"
            return response
        except Exception as e:
            return e
