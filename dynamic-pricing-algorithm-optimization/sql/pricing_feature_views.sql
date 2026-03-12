-- Reference SQL for warehouse-style feature derivation.
with base as (
    select
        date,
        product_id,
        category,
        channel,
        demand_regime,
        base_price,
        unit_cost,
        price,
        discount_pct,
        competitor_price,
        inventory_level,
        max_inventory,
        seasonality_index,
        returning_customer_share,
        page_views,
        cart_add_rate,
        weekday,
        month,
        is_holiday,
        units_sold
    from transactions
),
features as (
    select
        *,
        price / nullif(base_price, 0) as price_index_vs_base,
        (price - competitor_price) / nullif(competitor_price, 0) as competitor_gap_pct,
        discount_pct as promotion_intensity,
        1 - inventory_level / nullif(max_inventory, 0) as inventory_pressure,
        price - unit_cost as gross_margin_per_unit,
        case when weekday >= 5 then 1 else 0 end as is_weekend,
        case when discount_pct > 0.10 then 1 else 0 end as markdown_flag
    from base
)
select * from features;
