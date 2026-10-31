# Business case: Azure Streaming Pipeline

**Validated, queryable social posts during a disaster, through serverless Azure.**

## Who buys this

The buyer is the technology lead at an emergency-management agency, a relief organisation or an insurer's catastrophe team. The users are analysts who need to see incoming posts and photos about damage as they arrive.

## The problem and what it costs

Disasters generate a flood of posts, and responders need them validated, stored and searchable while they still matter. The scale of the events is large: NOAA reports that Hurricanes Harvey, Irma and Maria together cost **US$339.2 billion** (CPI-adjusted) in 2017 ([NOAA Office for Coastal Management](https://coast.noaa.gov/states/fast-facts/hurricane-costs.html)). That is the cost of the events, not a saving this pipeline delivers.

## How the repo solves it

| Need | What in the repo does it |
|---|---|
| Ingest | A REST endpoint behind API Management, with JSON Schema validation in an Azure Function (`azure-func/function_app.py`, Python v2 model) |
| Keep the raw record | Raw JSON lands in Blob Storage |
| Stream | Events go to Event Hubs, and a second Function upserts them into Cosmos DB |
| Analyse | Power BI in the cloud design, and a React live view (SSE) locally |
| Run without Azure | Azurite, the Event Hubs emulator, the Cosmos DB emulator and the real Functions host, all in `docker compose`. A producer replays tweets and sends every 25th one invalid on purpose. |

## Use-case scenarios

All of these organisations are fictional.

1. **A county emergency-operations centre** watches posts that mention flooding by area during a storm.
2. **An insurer's catastrophe team** collects geotagged damage photos to plan adjuster deployment.
3. **A relief charity** keeps a validated, timestamped record of public posts for its after-action review.

## ROI: a worked model (illustrative)

These figures are **illustrative assumptions** unless a source is linked.

| Input | Value | Basis |
|---|---|---|
| Analysts monitoring social feeds during an event | 4 | Assumption |
| Hours a day each spends collecting and cleaning posts by hand | 3 | Assumption |
| Share automated | 60% | Assumption |
| Event days a year | 20 | Assumption |
| Analyst loaded cost an hour | US$60 | Assumption |

Saving: 4 × 3 h × 60% × 20 days × $60 ≈ **US$8,600 a year**. The real value is faster awareness during an event, which this model doesn't price.

## Path to production

1. Replace the replayed tweets with a licensed social-data feed. Platform API access and terms have changed a lot since 2017.
2. Add classification (for example damage vs. not) between Event Hubs and Cosmos DB.
3. Deploy with managed identity and Key Vault instead of connection strings.

## Risks and limits

- Social posts are noisy and sometimes false, so they need human verification before anyone acts.
- The pipeline stores posts, which may include personal data. Retention rules apply.
- The dataset is from Hurricane Harvey in 2017.

**Case strength:** **Moderate.** The architecture is sound and the need is real, but the money case is small and the data source is the hard part.

## Sources

- NOAA Office for Coastal Management, Hurricane Costs: https://coast.noaa.gov/states/fast-facts/hurricane-costs.html
