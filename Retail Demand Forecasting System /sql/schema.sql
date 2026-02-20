-- PostgreSQL schema for Retail Demand Forecasting
-- Run: psql -d demand_forecast -f sql/schema.sql

CREATE TABLE IF NOT EXISTS stores (
    store_id        VARCHAR(10) PRIMARY KEY,
    size            VARCHAR(10),
    latitude        NUMERIC(8,5),
    longitude       NUMERIC(9,5),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    product_id      VARCHAR(10) PRIMARY KEY,
    category        VARCHAR(30),
    base_price      NUMERIC(10,2),
    shelf_life_days INTEGER,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_sales (
    date            DATE NOT NULL,
    store_id        VARCHAR(10) NOT NULL REFERENCES stores(store_id),
    product_id      VARCHAR(10) NOT NULL REFERENCES products(product_id),
    quantity        INTEGER NOT NULL,
    revenue         NUMERIC(12,2),
    sell_price      NUMERIC(10,2),
    discount_pct    NUMERIC(5,1),
    is_promotion    BOOLEAN DEFAULT FALSE,
    is_holiday      BOOLEAN DEFAULT FALSE,
    temperature     NUMERIC(5,1),
    PRIMARY KEY (date, store_id, product_id)
);

CREATE TABLE IF NOT EXISTS forecasts (
    id              SERIAL PRIMARY KEY,
    date            DATE NOT NULL,
    store_id        VARCHAR(10) REFERENCES stores(store_id),
    product_id      VARCHAR(10) REFERENCES products(product_id),
    model_name      VARCHAR(30) NOT NULL,
    predicted_qty   NUMERIC(12,2),
    actual_qty      INTEGER,
    error           NUMERIC(12,2),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_runs (
    id              SERIAL PRIMARY KEY,
    model_name      VARCHAR(30) NOT NULL,
    train_start     DATE,
    train_end       DATE,
    test_start      DATE,
    test_end        DATE,
    mae             NUMERIC(10,2),
    rmse            NUMERIC(10,2),
    mape            NUMERIC(8,2),
    r_squared       NUMERIC(8,4),
    bias            NUMERIC(10,2),
    n_features      INTEGER,
    training_time_s NUMERIC(8,2),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sales_date ON daily_sales(date);
CREATE INDEX IF NOT EXISTS idx_sales_store ON daily_sales(store_id, date);
CREATE INDEX IF NOT EXISTS idx_forecasts_date ON forecasts(date, model_name);
CREATE INDEX IF NOT EXISTS idx_model_runs_name ON model_runs(model_name, created_at DESC);

-- Useful views
CREATE OR REPLACE VIEW v_forecast_accuracy AS
SELECT
    model_name,
    COUNT(*) as n_forecasts,
    ROUND(AVG(ABS(error)), 2) as avg_abs_error,
    ROUND(SQRT(AVG(error * error)), 2) as rmse,
    ROUND(AVG(CASE WHEN actual_qty > 0
        THEN ABS(error) / actual_qty * 100 ELSE NULL END), 2) as mape
FROM forecasts
WHERE actual_qty IS NOT NULL
GROUP BY model_name;
