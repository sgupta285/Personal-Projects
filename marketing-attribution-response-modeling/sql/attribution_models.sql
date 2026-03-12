-- Rule-based attribution reference queries for SQLite

with conversions as (
    select journey_id, revenue
    from journeys
    where converted = 1
),
ordered_touches as (
    select
        t.*, 
        row_number() over (partition by t.journey_id order by t.event_time asc, t.path_position asc) as rn_first,
        row_number() over (partition by t.journey_id order by t.event_time desc, t.path_position desc) as rn_last,
        count(*) over (partition by t.journey_id) as path_length
    from touchpoints t
    inner join conversions c on c.journey_id = t.journey_id
)
select * from ordered_touches;
