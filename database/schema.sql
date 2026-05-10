CREATE TABLE IF NOT EXISTS tokens (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(30) NOT NULL UNIQUE,
    base_asset VARCHAR(20) NOT NULL,
    quote_asset VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dex_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(30) NOT NULL,
    dex_name VARCHAR(100) NOT NULL,
    network VARCHAR(50) NOT NULL,
    price NUMERIC(30, 10) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS spread_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(30) NOT NULL,
    highest_dex VARCHAR(100) NOT NULL,
    lowest_dex VARCHAR(100) NOT NULL,
    spread_percentage NUMERIC(10, 4) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS token_mappings (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50),
    network VARCHAR(50),
    contract_address VARCHAR(255),
    liquidity NUMERIC,
    UNIQUE (network, contract_address)
);
