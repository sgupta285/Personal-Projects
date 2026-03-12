select
    session_id,
    user_id,
    started_at,
    device_type,
    traffic_channel,
    product_category,
    user_recency,
    variant,
    landed,
    viewed_product,
    added_to_cart,
    started_checkout,
    purchased,
    order_value
from raw_sessions;
