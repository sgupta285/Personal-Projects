select
    device_type,
    traffic_channel,
    product_category,
    user_recency,
    variant,
    count(*) as sessions,
    avg(case when viewed_product = 1 then 1.0 else 0.0 end) as product_view_rate,
    avg(case when added_to_cart = 1 then 1.0 else 0.0 end) as cart_rate,
    avg(case when started_checkout = 1 then 1.0 else 0.0 end) as checkout_rate,
    avg(case when purchased = 1 then 1.0 else 0.0 end) as purchase_rate,
    avg(order_value) as revenue_per_session
from raw_sessions
group by 1,2,3,4,5;
