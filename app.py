from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)
load_dotenv()

class PricelineAPI:
    @staticmethod
    def search_hotels_locations(query):
        url = "https://priceline-com-provider.p.rapidapi.com/v1/hotels/locations"

        querystring = {"name": query, "search_type": "ALL"}

        headers = {
            "X-RapidAPI-Key": os.getenv('API_KEY'),
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
            "X-RapidAPI-Key": os.getenv('API_KEY'),
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

def get_booking_details(hotel_id, checkin_date, checkout_date, rooms_number):
    url = "https://priceline-com-provider.p.rapidapi.com/v1/hotels/booking-details"

    querystring = {
        "hotel_id": hotel_id,
        "date_checkin": checkin_date,
        "date_checkout": checkout_date,
        "rooms_number": rooms_number
    }

    headers = {
        "X-RapidAPI-Key": os.getenv('API_KEY'),
        "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("Error accessing booking details:", e)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_hotels():
    city_name = request.form['city']
    city_id = PricelineAPI.search_hotels_locations(city_name)
    nearby_hotels_response = PricelineAPI.search_nearby_hotels(city_id)
    hotels = nearby_hotels_response.get("hotels", [])
    return render_template('search_results.html', hotels=hotels)

@app.route('/booking/<hotel_id>')
def view_booking_details(hotel_id):
    checkin_date = "2024-07-24"
    checkout_date = "2024-07-25"
    rooms_number = "1"
    booking_details = get_booking_details(hotel_id, checkin_date, checkout_date, rooms_number)
    return render_template('booking_details.html', booking_details=booking_details)

if __name__ == '__main__':
    app.run(debug=True)
