# API Examples

## Submit a legitimate ad

```bash
curl -X POST http://localhost:8000/api/v1/ads       -H "Content-Type: application/json"       -d '{
    "advertiser_name": "NorthPeak Retail",
    "advertiser_domain": "northpeak.co",
    "title": "Spring Running Collection",
    "body": "Discover lightweight shoes and new trail layers for your next weekend run.",
    "landing_page_url": "https://northpeak.co/spring-running",
    "call_to_action": "Shop now",
    "category": "retail",
    "creative_text": "New spring arrivals. Free shipping over $75.",
    "creative_tags": ["running", "spring", "footwear"],
    "geo_targets": ["US", "CA"],
    "budget_cents": 250000
  }'
```

## Submit a suspicious ad

```bash
curl -X POST http://localhost:8000/api/v1/ads       -H "Content-Type: application/json"       -d '{
    "advertiser_name": "Yield Booster Labs",
    "advertiser_domain": "yield-booster.click",
    "title": "Guaranteed returns in 24 hours",
    "body": "Start with $100 and watch it turn into $1,000 with our private crypto doubling strategy.",
    "landing_page_url": "https://yield-booster.click/instant-wealth",
    "call_to_action": "Act now",
    "category": "finance",
    "creative_text": "Free money system. Guaranteed returns.",
    "creative_tags": ["crypto", "wealth", "urgent"],
    "geo_targets": ["US", "GB", "AU"],
    "budget_cents": 900000
  }'
```

## Check summary analytics

```bash
curl http://localhost:8000/api/v1/analytics/overview
```

## Apply a reviewer decision

```bash
curl -X POST http://localhost:8000/api/v1/reviews/<AD_ID>/decision       -H "Content-Type: application/json"       -d '{
    "reviewer_name": "Ops Reviewer",
    "decision": "approved",
    "notes": "Destination page content was manually verified."
  }'
```
