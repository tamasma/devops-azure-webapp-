import azure.functions as func
import logging
import json
import uuid
from datetime import datetime

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="HttpTrigger", methods=["POST"])
def HttpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing HTTP trigger request.')

    try:
        req_body = req.get_json()
    except ValueError:
        logging.error('Invalid JSON in request body')
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    name = req_body.get('name')
    message = req_body.get('message')

    if not name or not message:
        logging.warning('Missing required fields: name or message')
        return func.HttpResponse(
            json.dumps({"error": "Missing required fields: name and message"}),
            status_code=400,
            mimetype="application/json"
        )

    response_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    processed_message = f"Hello {name}, your message '{message}' has been processed"

    logging.info(f'Request processed successfully. ID: {response_id}')

    response_body = {
        "id": response_id,
        "timestamp": timestamp,
        "processed_message": processed_message
    }

    return func.HttpResponse(
        json.dumps(response_body),
        status_code=200,
        mimetype="application/json"
    )
