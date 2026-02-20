-- PostgreSQL schema for Product Metrics & Analytics

CREATE TABLE IF NOT EXISTS users (
    user_id         VARCHAR(10) PRIMARY KEY,
    signup_date     DATE NOT NULL,
    platform        VARCHAR(10),
    country         VARCHAR(5),
    variant         VARCHAR(15),
    is_subscriber   BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id      VARCHAR(15) PRIMARY KEY,
    user_id         VARCHAR(10) REFERENCES users(user_id),
    date            DATE NOT NULL,
    platform        VARCHAR(10),
    duration_sec    INTEGER,
    page_views      INTEGER,
    n_features      INTEGER
);

CREATE TABLE IF NOT EXISTS events (
    event_id        SERIAL PRIMARY KEY,
    session_id      VARCHAR(15),
    user_id         VARCHAR(10) REFERENCES users(user_id),
    event_type      VARCHAR(30) NOT NULL,
    feature         VARCHAR(30),
    revenue         NUMERIC(10,2) DEFAULT 0,
    timestamp       TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS experiments (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    metric          VARCHAR(50),
    control_rate    NUMERIC(10,6),
    treatment_rate  NUMERIC(10,6),
    p_value         NUMERIC(10,6),
    is_significant  BOOLEAN,
    lift_pct        NUMERIC(8,2),
    method          VARCHAR(30),
    n_control       INTEGER,
    n_treatment     INTEGER,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_metrics (
    date            DATE PRIMARY KEY,
    dau             INTEGER,
    wau             INTEGER,
    mau             INTEGER,
    stickiness      NUMERIC(6,4),
    total_revenue   NUMERIC(12,2),
    new_users       INTEGER
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id, date);
CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type, timestamp);

-- Views
CREATE OR REPLACE VIEW v_daily_active AS
SELECT date, COUNT(DISTINCT user_id) as dau
FROM sessions GROUP BY date ORDER BY date;

CREATE OR REPLACE VIEW v_feature_adoption AS
SELECT feature, COUNT(DISTINCT user_id) as unique_users, COUNT(*) as total_uses
FROM events WHERE event_type = 'feature_use'
GROUP BY feature ORDER BY unique_users DESC;
