import time
from dotenv import load_dotenv
import openai
import os
from function import PricelineAPI

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

def setup():
    assistant = client.beta.assistants.create(
        name="Priceline Hotel Search Assistant",
        instructions="You are a bot to search for hotels based on user input.",
        model="gpt-4-turbo-preview",
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

def create_thread():
    thread = client.beta.threads.create()
    return thread.id

def start(thread_id, user_query):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_query
    )

def get_response(thread_id, assistant_id, user_query):
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
    output = PricelineAPI.fetch_hotels(query=user_query)
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

    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs
    )


assistant_id = os.getenv("ASSISTANT_ID")
thread_id = create_thread()
start(thread_id)

response = get_response(thread_id,assistant_id)
print(response)
