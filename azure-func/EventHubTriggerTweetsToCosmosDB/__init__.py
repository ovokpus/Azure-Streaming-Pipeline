import json
import logging
from typing import List

import azure.functions as func

from shared_code.tweet_schema import to_cosmos_document


def main(events: List[func.EventHubEvent],
         outputDocument: func.Out[func.DocumentList]):
    # Collect the whole batch: calling .set() per event (as before) kept only the last one.
    docs = func.DocumentList()
    for event in events:
        docs.append(func.Document.from_dict(to_cosmos_document(json.loads(event.get_body()))))
    outputDocument.set(docs)
    logging.info("EventHub trigger wrote %d tweets to CosmosDB", len(docs))
