CREATE TABLE credentials (
    rec_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    credentials_id CHAR(36) NOT NULL UNIQUE,
    account_id INT NOT NULL,
    identifier_type TEXT NOT NULL,
    identifier TEXT NOT NULL,
    passphrase TEXT NOT NULL,
    status VARCHAR(64) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT NOW(),
    updated_at DATETIME NOT NULL DEFAULT NOW()
);
