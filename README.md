# Azure-Streaming-Pipeline

Data Streaming Pipeline that sends tweets and images to an Azure CosmosDB via APIM and Azure Functions, with visualization in PowerBI

---

![image](https://github.com/ovokpus/Azure-Streaming-Pipeline/blob/main/img/twitter-azure.jpeg)

---

This project is a prototype of a Data Pipeline that emulates streaming data of twitter messages to a Microsoft Azure REST API endpoint. This streaming data is then stored in an Azure blob storage container, and pushed to an Azure Event Hubs Instance. Then the data is persisted in an Azure CosmosDB database, then consumed in Power BI.

## Pipeline Architecture

---

![image](architecture)

---

## Azure Resources Utilized

1. Connect: API Management
2. Process: Azure Functions
3. Buffer: Event Hub
4. Store and Serve: Blob Storage
5. Database: CosmosDB
6. Consume: Power BI

![image](resources)

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

## The Data Source

## Project Pipeline steps/phases
