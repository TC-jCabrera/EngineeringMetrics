-- Teams table - simplified
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    org INTEGER,
    parent INTEGER,
    path VARCHAR(255)
);

-- Users table - simplified
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    external_id VARCHAR(255) NOT NULL
);

-- Team members relationship - simplified
CREATE TABLE team_members (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    team_id INTEGER NOT NULL REFERENCES teams(id)
);


-- Basic indexes for performance
CREATE INDEX idx_users_email ON users(email);
