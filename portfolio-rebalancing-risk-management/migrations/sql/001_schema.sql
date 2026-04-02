CREATE TABLE IF NOT EXISTS price_history (
    trade_date DATE NOT NULL,
    ticker TEXT NOT NULL,
    close_price DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (trade_date, ticker)
);

CREATE TABLE IF NOT EXISTS target_allocations (
    ticker TEXT PRIMARY KEY,
    asset_class TEXT NOT NULL,
    target_weight DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS positions (
    ticker TEXT PRIMARY KEY,
    shares DOUBLE PRECISION NOT NULL,
    lot_cost DOUBLE PRECISION NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS risk_snapshots (
    snapshot_date DATE NOT NULL,
    portfolio_value DOUBLE PRECISION NOT NULL,
    daily_var DOUBLE PRECISION NOT NULL,
    daily_cvar DOUBLE PRECISION NOT NULL,
    volatility DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (snapshot_date)
);
