-- PostgreSQL schema for Demand Elasticity Analysis

CREATE TABLE IF NOT EXISTS products (
    product_id      VARCHAR(10) PRIMARY KEY,
    category        VARCHAR(30),
    base_price      NUMERIC(10,2),
    marginal_cost   NUMERIC(10,2),
    true_elasticity NUMERIC(6,3)
);

CREATE TABLE IF NOT EXISTS weekly_sales (
    date            DATE NOT NULL,
    store_id        VARCHAR(10) NOT NULL,
    product_id      VARCHAR(10) REFERENCES products(product_id),
    price           NUMERIC(10,2) NOT NULL,
    quantity        INTEGER NOT NULL,
    revenue         NUMERIC(12,2),
    is_promotion    BOOLEAN DEFAULT FALSE,
    discount_pct    NUMERIC(5,1),
    cost_shock      NUMERIC(8,4),
    PRIMARY KEY (date, store_id, product_id)
);

CREATE TABLE IF NOT EXISTS elasticity_estimates (
    id              SERIAL PRIMARY KEY,
    product_id      VARCHAR(10) REFERENCES products(product_id),
    method          VARCHAR(30) NOT NULL,
    own_elasticity  NUMERIC(8,4),
    std_error       NUMERIC(8,4),
    p_value         NUMERIC(10,6),
    r_squared       NUMERIC(6,4),
    n_obs           INTEGER,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cross_elasticities (
    product_i       VARCHAR(10) REFERENCES products(product_id),
    product_j       VARCHAR(10) REFERENCES products(product_id),
    cross_elasticity NUMERIC(8,4),
    std_error       NUMERIC(8,4),
    p_value         NUMERIC(10,6),
    relationship    VARCHAR(20),
    PRIMARY KEY (product_i, product_j)
);

CREATE TABLE IF NOT EXISTS pricing_recommendations (
    id              SERIAL PRIMARY KEY,
    product_id      VARCHAR(10) REFERENCES products(product_id),
    current_price   NUMERIC(10,2),
    optimal_price   NUMERIC(10,2),
    price_change_pct NUMERIC(6,1),
    profit_uplift_pct NUMERIC(8,1),
    elasticity_used NUMERIC(6,3),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sales_product ON weekly_sales(product_id, date);
CREATE INDEX IF NOT EXISTS idx_estimates_product ON elasticity_estimates(product_id);
