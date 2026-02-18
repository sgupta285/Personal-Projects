-- PostgreSQL schema for backtest results storage
-- Run: psql -d backtest -f sql/schema.sql

CREATE TABLE IF NOT EXISTS strategies (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    params          JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS backtests (
    id              SERIAL PRIMARY KEY,
    strategy_id     INTEGER REFERENCES strategies(id),
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    initial_capital NUMERIC(15,2) NOT NULL,
    final_equity    NUMERIC(15,2) NOT NULL,
    total_return    NUMERIC(10,6),
    ann_return      NUMERIC(10,6),
    ann_volatility  NUMERIC(10,6),
    sharpe_ratio    NUMERIC(8,4),
    sortino_ratio   NUMERIC(8,4),
    calmar_ratio    NUMERIC(8,4),
    max_drawdown    NUMERIC(10,6),
    max_dd_duration INTEGER,
    win_rate        NUMERIC(6,4),
    profit_factor   NUMERIC(8,4),
    total_trades    INTEGER,
    alpha           NUMERIC(10,6),
    beta            NUMERIC(8,4),
    info_ratio      NUMERIC(8,4),
    var_95          NUMERIC(10,6),
    cvar_95         NUMERIC(10,6),
    skewness        NUMERIC(8,4),
    kurtosis        NUMERIC(8,4),
    turnover        NUMERIC(8,2),
    runtime_ms      NUMERIC(10,2),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS equity_snapshots (
    id              SERIAL PRIMARY KEY,
    backtest_id     INTEGER REFERENCES backtests(id) ON DELETE CASCADE,
    bar_date        DATE NOT NULL,
    equity          NUMERIC(15,2) NOT NULL,
    cash            NUMERIC(15,2),
    positions_value NUMERIC(15,2),
    daily_return    NUMERIC(10,8),
    drawdown        NUMERIC(10,8),
    num_positions   INTEGER
);

CREATE TABLE IF NOT EXISTS trades (
    id              SERIAL PRIMARY KEY,
    backtest_id     INTEGER REFERENCES backtests(id) ON DELETE CASCADE,
    symbol          VARCHAR(20) NOT NULL,
    side            VARCHAR(4) NOT NULL,
    quantity        INTEGER NOT NULL,
    entry_price     NUMERIC(12,4),
    exit_price      NUMERIC(12,4),
    pnl             NUMERIC(15,2),
    return_pct      NUMERIC(10,6),
    holding_days    INTEGER,
    entry_date      DATE,
    exit_date       DATE
);

CREATE TABLE IF NOT EXISTS walk_forward_results (
    id              SERIAL PRIMARY KEY,
    strategy_id     INTEGER REFERENCES strategies(id),
    window_id       INTEGER NOT NULL,
    train_start     DATE,
    train_end       DATE,
    test_start      DATE,
    test_end        DATE,
    train_sharpe    NUMERIC(8,4),
    test_sharpe     NUMERIC(8,4),
    train_return    NUMERIC(10,6),
    test_return     NUMERIC(10,6),
    test_max_dd     NUMERIC(10,6),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_equity_backtest ON equity_snapshots(backtest_id, bar_date);
CREATE INDEX IF NOT EXISTS idx_trades_backtest ON trades(backtest_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_backtests_strategy ON backtests(strategy_id, created_at);
CREATE INDEX IF NOT EXISTS idx_wf_strategy ON walk_forward_results(strategy_id);

-- Useful views
CREATE OR REPLACE VIEW backtest_summary AS
SELECT
    b.id,
    s.name AS strategy,
    b.start_date,
    b.end_date,
    b.initial_capital,
    b.final_equity,
    ROUND(b.ann_return * 100, 2) AS ann_return_pct,
    ROUND(b.sharpe_ratio, 2) AS sharpe,
    ROUND(b.max_drawdown * 100, 2) AS max_dd_pct,
    ROUND(b.win_rate * 100, 1) AS win_rate_pct,
    b.total_trades,
    ROUND(b.alpha * 100, 2) AS alpha_pct,
    b.created_at
FROM backtests b
JOIN strategies s ON b.strategy_id = s.id
ORDER BY b.created_at DESC;
