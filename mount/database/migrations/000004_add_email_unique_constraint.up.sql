ALTER TABLE accounts
ADD CONSTRAINT accounts_email_address_key UNIQUE (email_address);
