import logging
from typing import List

import azure.functions as func


def main(events: List[func.EventHubEvent],
         outputDocument: func.Out[func.Document]):
    for event in events:
        json_data = event.get_body()
        outputDocument.set(func.Document.from_json(json_data))

        logging.info(
            "Python EventHub trigger processed an event, which is written to CosmosDB")
