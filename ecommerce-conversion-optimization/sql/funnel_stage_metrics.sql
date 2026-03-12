with stage_counts as (
    select
        stage_name,
        min(stage_order) as stage_order,
        count(distinct session_id) as sessions_at_stage
    from raw_events
    group by stage_name
), ordered as (
    select
        stage_name,
        stage_order,
        sessions_at_stage,
        lag(sessions_at_stage) over (order by stage_order) as previous_stage_sessions
    from stage_counts
)
select
    stage_name,
    stage_order,
    sessions_at_stage,
    previous_stage_sessions,
    case
        when previous_stage_sessions is null then 1.0
        else round(1.0 * sessions_at_stage / previous_stage_sessions, 4)
    end as conversion_from_previous,
    case
        when previous_stage_sessions is null then 0.0
        else round(1.0 - (1.0 * sessions_at_stage / previous_stage_sessions), 4)
    end as dropoff_from_previous
from ordered
order by stage_order;
