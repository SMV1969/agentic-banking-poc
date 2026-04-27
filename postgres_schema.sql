CREATE SCHEMA IF NOT EXISTS core_poc;

CREATE TABLE IF NOT EXISTS core_poc.customer_master (
    customer_id   VARCHAR(20) PRIMARY KEY,
    full_name     VARCHAR(200) NOT NULL,
    segment       VARCHAR(50),
    risk_rating   VARCHAR(10),
    onboard_date  DATE,
    country       VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS core_poc.account_master (
    account_id    VARCHAR(20) PRIMARY KEY,
    customer_id   VARCHAR(20) REFERENCES core_poc.customer_master(customer_id),
    product_type  VARCHAR(50),
    currency      VARCHAR(3),
    balance       NUMERIC(18,2) DEFAULT 0,
    open_date     DATE,
    status        VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS core_poc.transactions (
    txn_id        BIGSERIAL PRIMARY KEY,
    account_id    VARCHAR(20) REFERENCES core_poc.account_master(account_id),
    txn_date      TIMESTAMP,
    amount        NUMERIC(18,2),
    dr_cr         CHAR(1),
    channel       VARCHAR(20),
    narration     VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS core_poc.kyc_details (
    customer_id       VARCHAR(20) PRIMARY KEY REFERENCES core_poc.customer_master(customer_id),
    kyc_status        VARCHAR(20),
    kyc_last_review   DATE,
    kyc_next_due      DATE,
    pep_flag          BOOLEAN DEFAULT FALSE
);