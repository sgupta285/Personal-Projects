-- PostgreSQL materialized view examples for production deployments.
-- Local development uses refreshable rollup tables so the repo can run without a specialized setup.

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_usage_daily AS
SELECT
  workspace_id,
  date_trunc('day', event_time) AS bucket_start,
  SUM(request_units) AS request_units,
  SUM(billable_units) AS billable_units,
  ROUND(SUM(cost_usd)::numeric, 2) AS total_cost_usd,
  ROUND(AVG(latency_ms)::numeric, 2) AS avg_latency_ms,
  SUM(export_count) AS export_count
FROM usage_events
GROUP BY workspace_id, date_trunc('day', event_time);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_usage_daily_workspace_bucket
  ON mv_usage_daily (workspace_id, bucket_start);
