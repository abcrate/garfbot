import config
import requests
from base64 import b64encode
from garfpy import logger


client_id = config.CLIENT_ID
client_secret = config.CLIENT_SECRET

auth = b64encode(f"{client_id}:{client_secret}".encode()).decode()

def kroger_token():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {auth}'
    }

    response = requests.post('https://api.kroger.com/v1/connect/oauth2/token', headers=headers, data={
        'grant_type': 'client_credentials',
        'scope': 'product.compact'
    })

    response.raise_for_status()
    return response.json()['access_token']

def find_store(zipcode, kroken):
    headers = {
        'Authorization': f'Bearer {kroken}',
    }
    params = {
        'filter.zipCode.near': zipcode,
        'filter.limit': 1,
    }
    response = requests.get('https://api.kroger.com/v1/locations', headers=headers, params=params)
    return response.json()

def search_product(product, loc_id, kroken):
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
