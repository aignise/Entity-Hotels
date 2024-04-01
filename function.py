import os
import requests
from dotenv import load_dotenv

load_dotenv()

class PricelineAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://priceline-com-provider.p.rapidapi.com/v1"

    @staticmethod
    def search_hotels_locations(query):
        url = "https://priceline-com-provider.p.rapidapi.com/v1/hotels/locations"
        querystring = {"name": query, "search_type": "ALL"}
        headers = {
            "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        if data and isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            first_item_id = first_item['id']
            return first_item_id
        else:
            print("No locations found for the given query.")
            return None

    @staticmethod
    def fetch_hotels(query):
        city_id = PricelineAPI.search_hotels_locations(query)
        if city_id:
            url = "https://priceline-com-provider.p.rapidapi.com/v1/hotels/search"
            headers = {
                "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
                "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
            }
            params = {
                "location_id": city_id,
                "date_checkin": "2024-07-24",
                "date_checkout": "2024-07-25",
                "sort_order": "HDR",
                "star_rating_ids": "3.0,3.5,4.0,4.5,5.0",
                "rooms_number": "1",
                "amenities_ids": "FINTRNT,FBRKFST"
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        else:
            return None
