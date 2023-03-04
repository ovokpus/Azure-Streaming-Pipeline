# Azure-Streaming-Pipeline

Data Streaming Pipeline that sends tweets and images to an Azure CosmosDB via APIM and Azure Functions, with visualization in PowerBI

---

![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/twitter-azure.jpeg)

---

This project is a prototype of a Data Pipeline that emulates streaming data of twitter messages to a Microsoft Azure REST API endpoint. This streaming data is then stored in an Azure blob storage container, and pushed to an Azure Event Hubs Instance. Then the data is persisted in an Azure CosmosDB database, then consumed in Power BI.

## Pipeline Architecture

Here's a high-level overview of the end-to-end pipeline architecture

---

![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/pipeline-architecture.png)

---

## Azure Resources Utilized

1. Connect: API Management
2. Process: Azure Functions
3. Buffer: Event Hub
4. Store and Serve: Blob Storage
5. Database: CosmosDB
6. Consume: Power BI

![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/azure-resource-group.png)

---

### Azure Functions

Azure Functions is an event-driven, compute-on-demand serverless offering that hosts a single method or function in a programming language that runs in response to an event. The programming language used here is python. We have two Azure functions in this pipeline. One of them is triggered by an API POST request, and the other is triggered by a push into Event Hubs.

### Azure API Management (APIM)

Azure API Management is a fully managed service that helps customers to securely expose their APIs to external and internal customers. It serves as a gatekeeper and front door for API implementations, enabling frictionless consumption by developers. APIM comes with features like:

1. Securing your API, including setting quotas and request throttling
2. A developer portal for users of your API, which included documentation ansd security key management.
3. Self-service subscription for API users
4. Monitor usage of your API

### Event Hubs

Event Hubs represents the front door for an event pipeline. It is often used as an event ingestor in Solution Architecture. An event ingestor is a component or service that sits between event publishers and event consumers to decouple the production of an event stream from the consumption of these events. Event Hubs provides a unified streaming platform with time retention buffer, decoupling event producers from event consumers

### Azure CosmosDB Core (NoSQL) API

CosmosDB is a fully managed NoSQL database for mordern application development. It has several API options, depending on particular use cases, such as key-value, wide-column, graph and document databases. For new projects, Microsoft Azure recommends the use of the core (NoSQL) API.

---

## The Data Source

The data is sources from 2 Kaggle projects:

1. [Hurricane Harvey Tweets](https://www.kaggle.com/datasets/dan195/hurricaneharvey) Tweets containing hurricane harvey in the message from the morning of the tropical storm event (20th August 2017) up to when it became a Hurricane and then downgraded back to a tropical storm.

2. [Satellite Images if Hurricane Damage](https://www.kaggle.com/datasets/kmader/satellite-images-of-hurricane-damage) Satellite images from Texas after the Hurricane. This dataset has been divided into 2 labels, for Machine learning purposes, to show photos that show damage and photos that do not show damage.

Original Data is sources from [this location](https://ieee-dataport.org/open-access/detecting-damaged-buildings-post-hurricane-satellite-imagery-based-customized)

---

## Project Prerequisites

1. WSL2 `(Ubuntu 22.04)` environment for Windows users
2. VSCode with Microsoft Azure and Remote containers extensions
3. Python
4. A Microsoft Azure Account with minimal spending
5. Docker and Docker-Compose

## Project Pipeline implementation steps/phases

### Preprocessing

The goal of this phase is to create a JSON file that contains tweet messages merged with images, with the images first encoded into base64 format. Then these merged tweet and image messages are sent as a request body to the REST API in Azure APIM. Python scripts have been prepared to perforom the following tasks, which can indeed be orchestrated in a regular schedule to procuce both batch or streaming data, depending on the use case of the prototype.

1. Preprocess the tweets, and convert them to JSON format
2. Preprocess the images and convert them to JSON format
3. Merge image and messages into single JSON schema
4. Push merged tweets to API to simulate streaming data

### Azure Function Development

1. Developing Azure Function in Python using VSCode extension, which includes Azure Functions SDK, Docker CLI, and related dependencies. The code ingests body of HTTP request, and validates JSON message against a predefined JSON schema.
2. Test function in Azure Function App from local project workspace.
3. Test function with the dataset preprocessed.
4. Deploy Azure Function App from your local project workspace.
5. Test function in Azure, then implement function type authorization to secure your API.
6. Bind function output to an Azure Blob Storage container. This can be done using the vscode extention functionalities that adds configuration to the `function.json` file.

Testing API with Insomnia
![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/api-testing-insomnia.png)

Function APP UI in Azure
![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/azure-function-code-in-portal.png)

---

### Set up Azure APIM instance and import function app into it

1. Create a new Azure API Management instance
2. Add API to APIM to expose and protect the Azure Function as a backend
3. Test it from within the APIM and locally from Insomnia
4. Add a basic authentication policy to a default subscription key to secure the API. This is done by:
   a. creating a key vault,
   b. enabling acess to key vault secrets,
   c. adding a username and password,
   d. creating names values in APIM with key vault url,
   e. adding an inbound policy definition
   f. Testing request with basic authorization header
5. Test it out from your API and Imported function app as well as from your python program, `push_tweets.py`

### Set Up Azure Event Hubs namespace

1. Create an Event Hubs namespace - standard tier
2. Create an Event Hub with 2 partitions and a 1-day message retention
3. Capture events using first Azure function and Azure Event Hubs Capture
4. Include an Azure Event Hubs binding in the Azure Function.

### Create CosmosDB Instance and create second Azure Function to pull tweets from Event Hubs into CosmosDB

1. Create a database with one container
2. Create Azure function to take tweets from Event Hub Instance and write it to CosmosDB

### Consumption layer - Power BI Dashboard

In this step, we create a live connection in PowerBI to Azure CosmosDB, and watch the real time and interactive changes as streaming messages are generated from the python scripts, through the Azure functions, into Event Hubs, and finally into CosmosDB

Power BI Dashboard report on Power BI Desktop
![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/power-bi-report.png)

---

## Metrics, Monitoring and other Images

Blob Storage JSON view
![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/blob-storage-json-view.png)

---

Event Hubs Instance
![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/event-hub-monitoring.png)

---

Logging information from Function App
![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/event-hub-trigger-logging.png)

---

Live metrics from Azure Function processing of streaming API calls
![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/live-metrics.png)

---

Application Insights Monitoring Dashboard
![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/tweet-stream-app-insights.png)

---

PowerBI Dashboard view in PowerBI service workspace
![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/power-bi-dashboard.png)

---

PowerBI Lineage information showing data sourced from CosmosDB
![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/power-bi-lineage-info.png)

---
