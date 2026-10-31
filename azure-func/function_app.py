"""Hurricane tweet pipeline on the Azure Functions Python v2 programming model.

Triggers and bindings are declared with decorators here; there is no function.json.
App-setting names in `connection=` and %...% expressions resolve from app settings
in Azure and from local.settings.json / environment variables locally.
"""
import json
import typing
import logging
import os

import azure.functions as func

from shared_code.tweet_schema import TweetValidationError, parse_and_validate, to_cosmos_document

# Function keys by default (APIM sits in front in Azure). The local docker compose host sets
# HTTP_AUTH_LEVEL=anonymous because it has no key store to hand keys out from.
app = func.FunctionApp(http_auth_level=func.AuthLevel(os.getenv("HTTP_AUTH_LEVEL", "function").lower()))


@app.function_name(name="TriggerTweetsToBlobAndEventHub")
@app.route(route="TriggerTweetsToBlobAndEventHub", methods=["GET", "POST"])
@app.blob_output(arg_name="outputBlob", path="tweets/{rand-guid}.json",
                 connection="STORAGE_CONNECTION")
@app.event_hub_output(arg_name="outputEventHubMessage", event_hub_name="%EVENTHUB_NAME%",
                      connection="EVENTHUB_CONNECTION")
def tweets_to_blob_and_event_hub(req: func.HttpRequest,
                                 outputBlob: func.Out[bytes],
                                 outputEventHubMessage: func.Out[bytes]) -> func.HttpResponse:
    """Validate a tweet, archive it to Blob Storage and forward it to Event Hubs."""
    body = req.get_body()
    try:
        parse_and_validate(body)
    except TweetValidationError as err:
        logging.error(str(err))
        return func.HttpResponse(str(err), status_code=400)

    outputBlob.set(body)
    outputEventHubMessage.set(body)
    logging.info("Tweet written to blob storage and forwarded to Event Hub.")
    return func.HttpResponse("This HTTP triggered function executed successfully.", status_code=200)


@app.function_name(name="EventHubTriggerTweetsToCosmosDB")
@app.event_hub_message_trigger(arg_name="events", event_hub_name="%EVENTHUB_NAME%",
                               connection="EVENTHUB_CONNECTION",
                               consumer_group="%EVENTHUB_FUNCTIONS_CONSUMER_GROUP%",
                               cardinality=func.Cardinality.MANY, data_type=func.DataType.BINARY)
@app.cosmos_db_output(arg_name="outputDocument", connection="COSMOS_CONNECTION",
                      database_name="%COSMOS_DATABASE%", container_name="%COSMOS_CONTAINER%",
                      create_if_not_exists=True, partition_key="/account_id")
def event_hub_to_cosmos(events: typing.List[func.EventHubEvent],
                        outputDocument: func.Out[func.DocumentList]) -> None:
    # typing.List, not list[...]: the worker indexer silently drops functions annotated
    # with the builtin generic (verified against the 4.x Python 3.12 host image).
    """Write the whole Event Hub batch to Cosmos DB (one document per tweet, id = tweet_id)."""
    docs = func.DocumentList()
    for event in events:
        docs.append(func.Document.from_dict(to_cosmos_document(json.loads(event.get_body()))))
    outputDocument.set(docs)
    logging.info("EventHub trigger wrote %d tweets to CosmosDB", len(docs))
