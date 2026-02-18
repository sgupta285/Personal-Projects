-- PostgreSQL + TimescaleDB schema for pairs trading
-- Run: psql -d pairs_trading -f sql/schema.sql

CREATE TABLE IF NOT EXISTS pairs (
    id              SERIAL PRIMARY KEY,
    symbol_a        VARCHAR(20) NOT NULL,
    symbol_b        VARCHAR(20) NOT NULL,
    hedge_ratio     NUMERIC(10,6) NOT NULL,
    half_life       NUMERIC(8,2),
    correlation     NUMERIC(6,4),
    trace_stat      NUMERIC(10,4),
    adf_pvalue      NUMERIC(8,6),
    score           NUMERIC(10,4),
    discovered_at   TIMESTAMP DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT TRUE,
    UNIQUE(symbol_a, symbol_b)
);

CREATE TABLE IF NOT EXISTS ticks (
    time            TIMESTAMPTZ NOT NULL,
    symbol          VARCHAR(20) NOT NULL,
    price           NUMERIC(12,4) NOT NULL,
    volume          NUMERIC(15,2)
);

-- TimescaleDB hypertable (comment out if not using TimescaleDB)
-- SELECT create_hypertable('ticks', 'time', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS signals (
    id              SERIAL PRIMARY KEY,
    pair_id         INTEGER REFERENCES pairs(id),
    signal_type     VARCHAR(20) NOT NULL,
    zscore          NUMERIC(8,4),
    hedge_ratio     NUMERIC(10,6),
    spread          NUMERIC(12,4),
    confidence      NUMERIC(6,4),
    latency_ms      NUMERIC(8,3),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS positions (
    id              SERIAL PRIMARY KEY,
    pair_id         INTEGER REFERENCES pairs(id),
    direction       VARCHAR(20) NOT NULL,
    qty_a           INTEGER NOT NULL,
    qty_b           INTEGER NOT NULL,
    entry_price_a   NUMERIC(12,4),
    entry_price_b   NUMERIC(12,4),
    entry_spread    NUMERIC(12,4),
    entry_zscore    NUMERIC(8,4),
    opened_at       TIMESTAMPTZ DEFAULT NOW(),
    closed_at       TIMESTAMPTZ,
    is_open         BOOLEAN DEFAULT TRUE,
    pnl             NUMERIC(15,2),
    exit_reason     VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS equity_snapshots (
    time            TIMESTAMPTZ NOT NULL,
    equity          NUMERIC(15,2) NOT NULL,
    cash            NUMERIC(15,2),
    positions_value NUMERIC(15,2),
    daily_return    NUMERIC(10,8),
    drawdown        NUMERIC(10,8),
    n_positions     INTEGER
);

CREATE TABLE IF NOT EXISTS kalman_state (
    pair_id         INTEGER REFERENCES pairs(id),
    time            TIMESTAMPTZ NOT NULL,
    beta            NUMERIC(10,6),
    intercept       NUMERIC(12,4),
    spread          NUMERIC(12,4),
    spread_var      NUMERIC(12,6),
    PRIMARY KEY (pair_id, time)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ticks_symbol_time ON ticks(symbol, time DESC);
CREATE INDEX IF NOT EXISTS idx_signals_pair ON signals(pair_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_positions_open ON positions(is_open) WHERE is_open = TRUE;
CREATE INDEX IF NOT EXISTS idx_equity_time ON equity_snapshots(time DESC);
CREATE INDEX IF NOT EXISTS idx_pairs_active ON pairs(is_active) WHERE is_active = TRUE;
