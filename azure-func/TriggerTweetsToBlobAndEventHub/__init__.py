import logging

import azure.functions as func

from shared_code.tweet_schema import TweetValidationError, parse_and_validate

# Schema + validation live in shared_code/ so the local stand-in API (stream/api.py)
# enforces exactly the same contract as the deployed function.


def main(req: func.HttpRequest,
         outputBlob: func.Out[bytes],
         outputEventHubMessage: func.Out[bytes]
         ) -> func.HttpResponse:

    logging.info('Python HTTP trigger function processed a request.')
    json_data = req.get_body()
    try:
        parse_and_validate(json_data)
    except TweetValidationError as err:
        logging.error(str(err))
        return func.HttpResponse(str(err), status_code=400)

    logging.info("JSON schema is valid!")
    outputBlob.set(json_data)
    logging.info('Tweet is written to blob storage.')
    outputEventHubMessage.set(json_data)
    logging.info('Tweet is forwarded to Event Hub.')
    return func.HttpResponse(
        "This HTTP triggered function executed successfully.", status_code=200)
