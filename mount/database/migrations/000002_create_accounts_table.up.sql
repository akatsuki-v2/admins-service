CREATE TABLE accounts (
    account_id SERIAL NOT NULL PRIMARY KEY,
    username VARCHAR(16) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    status VARCHAR(64) NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT NOW(),
    created_at DATETIME NOT NULL DEFAULT NOW()
);
