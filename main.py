import time
import openai
from dotenv import load_dotenv
import os
import requests

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

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

        if data and isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            first_item_id = first_item['id']
            return first_item_id
        else:
            print("No locations found for the given query.")
            return None


def setup():
    assistant = client.beta.assistants.create(
        name="Priceline Hotel Search Assistant",
        instructions="You are a bot to search for hotels based on user input.",
        model="gpt-4-turbo-preview",  # Adjust the model as needed
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "fetch_hotels",
                    "description": "Fetches hotels from Priceline API based on user input.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "City name to search for hotels"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    )

    return assistant.id

def fetch_hotels(query):
    city_id = PricelineAPI.search_hotels_locations(query)
    if city_id:
        url = "https://priceline-com-provider.p.rapidapi.com/v1/hotels/search"
        headers = {
            "X-RapidAPI-Key": os.getenv("X-RapidAPI-Key"),
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
    else:
        return None

def create_thread():
    """Creates a thread for conversation."""
    thread = client.beta.threads.create()
    return thread.id

def start(thread_id, user_query):
    """Starts a conversation in the specified thread with the given user query."""
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_query
    )
    
def get_response(thread_id, assistant_id, user_query):
    """Retrieves the response from the OpenAI API."""
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Answer user questions using custom functions available to you."
    )
    
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == 'requires_action':
            submit_tool_outputs(thread_id, run.id, run_status, user_query)
        
        time.sleep(1)
    
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value
    return response

def submit_tool_outputs(thread_id, run_id, run_status, user_query):
    """Submits tool outputs to the OpenAI API."""
    output = fetch_hotels(query=user_query)  # Fetch hotels based on user query
    output_str = ""
    if output and 'hotels' in output:
        for hotel in output['hotels']:
            output_str += f"Hotel: {hotel['name']}\n"
            output_str += f"Star Rating: {hotel['starRating']}\n"
            output_str += f"Address: {hotel['location']['address']['addressLine1']}\n"
            output_str += f"Overall Guest Rating: {hotel['overallGuestRating']}\n"
            output_str += f"Total Review Count: {hotel['totalReviewCount']}\n"
            output_str += f"Proximity: {hotel['proximity']}\n"
            output_str += f"Min Price: {hotel['ratesSummary']['minPrice']} {hotel['ratesSummary']['minCurrencyCode']}\n"
            output_str += f"Thumbnail URL: {hotel['thumbnailUrl']}\n\n"
    else:
        output_str = "No hotels found."

    tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
    
    tool_outputs = []
    for tool_call in tool_calls:
        tool_outputs.append({
            "tool_call_id": tool_call.id,
            "output": output_str
        })
    
    # Submit tool outputs to OpenAI API
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs
    )

def main():
    # Create a thread for conversation
    thread_id = create_thread()

    user_query_prompt = "Please provide a city name to search for hotels: "
    user_query = input(user_query_prompt)

    assistant_id = os.getenv("ASSISTANT_ID")
    
    start(thread_id, user_query)

    response = get_response(thread_id, assistant_id, user_query)

    print("Hotels:", response)


if __name__ == "__main__":
    main()
