import json
from django.http import JsonResponse
import requests
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("API_KEY")
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
        data = response.json()

        if data:
            first_item = data[0]
            first_item_id = first_item['id']
            return first_item_id
        else:
            print("No locations found for the given query.")

    @staticmethod
    def search_nearby_hotels(city_id):
        url = "https://priceline-com-provider.p.rapidapi.com/v1/hotels/search"
        headers = {
            "X-RapidAPI-Key": api_key,
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
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()


def get_booking_details(hotel_id, checkin_date, checkout_date, rooms_number):
    url = "https://priceline-com-provider.p.rapidapi.com/v1/hotels/booking-details"

    querystring = {
        "hotel_id": hotel_id,
        "date_checkin": checkin_date,
        "date_checkout": checkout_date,
        "rooms_number": rooms_number
    }

    headers = {
        "X-RapidAPI-Key": os.getenv("X-RapidAPI-Key"),
        "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  
        data = response.json()
        print("Description:", data.get('description'))

        print("Check-in Time:", data.get('policies', {}).get('checkInTime'))
        print("Check-out Time:", data.get('policies', {}).get('checkOutTime'))

        print("Children Description:", data.get('policies', {}).get('childrenDescription'))

        print("Hotel Features:", data.get('hotelFeatures', {}).get('features'))

        print("Hotel Amenities:")
        for amenity in data.get('hotelFeatures', {}).get('hotelAmenities', []):
            print("-", amenity.get('name'))

    except requests.exceptions.RequestException as e:
        print("Error accessing booking details:", e)


def main():
    api_key = os.getenv("X-RapidAPI-Key")
    city_name = input("Enter the city name: ")
    city_id = PricelineAPI.search_hotels_locations(city_name)

    nearby_hotels_response = PricelineAPI.search_nearby_hotels(city_id)
    hotels = nearby_hotels_response.get("hotels", [])

    for hotel in hotels:
        print("Name:", hotel.get("name"))
        hotel_id = hotel.get("hotelId")
        print("Hotel ID:", hotel_id)
        print("Star Rating:", hotel.get("starRating"))
        print("Address:", hotel.get("location", {}).get("address", {}).get("addressLine1"))
        print("Overall Guest Rating:", hotel.get("overallGuestRating"))
        print("Total Review Count:", hotel.get("totalReviewCount"))
        print("Proximity:", hotel.get("proximity"))
        print("Min Price:", hotel.get("ratesSummary", {}).get("minPrice"), hotel.get("ratesSummary", {}).get("minCurrencyCode"))
        print("Thumbnail URL:", hotel.get("thumbnailUrl"))
        
        hotel_id = hotel_id
        checkin_date = "2024-07-24"
        checkout_date = "2024-07-25"
        rooms_number = "1"

        booking_details = get_booking_details(hotel_id, checkin_date, checkout_date, rooms_number)
        if booking_details:
            print(booking_details)
            print()
        
if __name__ == "__main__":
    main()
