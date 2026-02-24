-- PostgreSQL schema for RCT Evaluation

CREATE TABLE IF NOT EXISTS subjects (
    subject_id       VARCHAR(10) PRIMARY KEY,
    age              NUMERIC(4,1),
    age_group        VARCHAR(10),
    gender           VARCHAR(10),
    severity         VARCHAR(10),
    bmi              NUMERIC(4,1),
    biomarker_a      NUMERIC(6,1),
    biomarker_b      INTEGER,
    pre_outcome      NUMERIC(8,2),
    assigned_treatment INTEGER NOT NULL,
    actual_treatment   INTEGER NOT NULL,
    compliance_type  VARCHAR(20),
    outcome          NUMERIC(8,2),
    attrited         BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS estimation_results (
    id               SERIAL PRIMARY KEY,
    method           VARCHAR(50) NOT NULL,
    estimand         VARCHAR(10),   -- 'ITT', 'ATE', 'LATE', 'CATE'
    estimate         NUMERIC(10,4),
    std_error        NUMERIC(10,4),
    ci_lower         NUMERIC(10,4),
    ci_upper         NUMERIC(10,4),
    p_value          NUMERIC(10,6),
    n_observations   INTEGER,
    true_value       NUMERIC(10,4),
    created_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS heterogeneity_results (
    id               SERIAL PRIMARY KEY,
    subgroup         VARCHAR(30),
    subgroup_value   VARCHAR(30),
    cate_estimate    NUMERIC(10,4),
    std_error        NUMERIC(10,4),
    p_value          NUMERIC(10,6),
    n_obs            INTEGER,
    true_cate        NUMERIC(10,4)
);

CREATE TABLE IF NOT EXISTS diagnostics (
    id               SERIAL PRIMARY KEY,
    check_name       VARCHAR(50),
    covariate        VARCHAR(30),
    smd              NUMERIC(8,4),
    p_value          NUMERIC(10,6),
    balanced         BOOLEAN
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_subjects_treatment ON subjects(assigned_treatment);
CREATE INDEX IF NOT EXISTS idx_subjects_compliance ON subjects(compliance_type);
CREATE INDEX IF NOT EXISTS idx_results_method ON estimation_results(method);
