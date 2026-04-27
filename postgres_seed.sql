INSERT INTO core_poc.customer_master (customer_id, full_name, segment, risk_rating, onboard_date, country) VALUES
('CUST1', 'John Doe', 'Gold', 'Low', '2018-05-10', 'KSA'),
('CUST2', 'Mary Smith', 'Silver', 'Medium', '2020-03-15', 'KSA')
ON CONFLICT (customer_id) DO NOTHING;

INSERT INTO core_poc.account_master (account_id, customer_id, product_type, currency, balance, open_date, status) VALUES
('ACC001', 'CUST1', 'Current Account', 'SAR', 25000.00, '2018-05-10', 'Open'),
('ACC002', 'CUST1', 'Savings Account', 'SAR', 150000.00, '2019-02-01', 'Open'),
('ACC003', 'CUST1', 'Term Deposit', 'SAR', 50000.00, '2021-11-20', 'Open'),
('ACC101', 'CUST2', 'Current Account', 'SAR', 12000.00, '2020-03-15', 'Open')
ON CONFLICT (account_id) DO NOTHING;

INSERT INTO core_poc.kyc_details (customer_id, kyc_status, kyc_last_review, kyc_next_due, pep_flag) VALUES
('CUST1', 'KYC_OK', '2024-01-15', '2027-01-15', FALSE),
('CUST2', 'KYC_DUE', '2021-06-01', '2024-06-01', FALSE)
ON CONFLICT (customer_id) DO NOTHING;