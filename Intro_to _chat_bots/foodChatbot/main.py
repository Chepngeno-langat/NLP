from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    if intent == 'track.order - context: ongoing-tracking':
        track_order(parameters)

def track_order(parameters: dict):
    order_id = parameters['order_id']

    
    return JSONResponse(content={
        'fulfillmentText': f'Received =={intent}== in the backend'
    })