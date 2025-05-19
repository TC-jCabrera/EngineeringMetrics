-- Create simplified tables for storing integration data

-- Table for storing vendor metadata
CREATE TABLE IF NOT EXISTS vendor_meta (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    is_cloud BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing integrations
CREATE TABLE IF NOT EXISTS integrations (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    org_id INTEGER NOT NULL,
    vendor_meta_id INTEGER REFERENCES vendor_meta(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL,
    org_id INTEGER NOT NULL,
    vendor_type VARCHAR(50) NOT NULL,
    external_id VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    integration_id INTEGER REFERENCES integrations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_users_org_id ON users(org_id);
CREATE INDEX idx_integrations_org_id ON integrations(org_id); 