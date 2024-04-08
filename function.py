import json
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
            "X-RapidAPI-Key": os.getenv("X-RapidAPI-Key"),
            "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        try:
            data = response.json()
            #print("Response from location search API:", data)
        except json.decoder.JSONDecodeError:
            print("Failed to decode JSON response. Response text:", response.text)
            data = None
        if data and isinstance(data, list) and len(data) > 0:
            return data
        else:
            print("No locations found for the given query.")
            return None


    @staticmethod
    def fetch_hotels(query):
        locations = PricelineAPI.search_hotels_locations(query)
        if locations:
            for location in locations:
                print("Location Name:", location.get("itemName"))
                print("Location ID:", location.get("id"))
                print("City Name:", location.get("cityName"))
                print("Country Name:", location.get("countryName"))
                print("Address:", location.get("address"))
                print()
                hotel_id = location.get("id")
                PricelineAPI.fetch_hotel_details(hotel_id)
        else:
            print("Failed to fetch hotel data.")

    @staticmethod
    def fetch_hotel_details(hotel_id):
        url = "https://priceline-com-provider.p.rapidapi.com/v1/hotels/details"
        querystring = {"hotel_id": hotel_id}
        headers = {
            "X-RapidAPI-Key": os.getenv("X-RapidAPI-Key"),
            "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        if data:
            print("Hotel Amenities:")
            for amenity in data.get("hotelFeatures", {}).get("hotelAmenities", []):
                print(f"- {amenity.get('name')}")
            print("Overall Guest Rating:", data.get("overallGuestRating"))
            print("Total Review Count:", data.get("totalReviewCount"))
            print("Check-In Time:", data.get("policies", {}).get("checkInTime"))
            print("Check-Out Time:", data.get("policies", {}).get("checkOutTime"))
            print("Children Description:", data.get("policies", {}).get("childrenDescription"))
            print("Pet Description:", data.get("policies", {}).get("petDescription"))
            print("Review Rating Summary:", data.get("reviewRatingSummary"))
            print("Description:", data.get("description"))
            print("Location Address:", data.get("location", {}).get("address"))
            print("Price:", data.get("price"))
            print()
        else:
            print(f"No details available for hotel ID {hotel_id}.")

location_query = input("Enter the location you want to search for hotels: ")

priceline_api = PricelineAPI(api_key=os.getenv("X-RapidAPI-Key"))
priceline_api.fetch_hotels(location_query)
