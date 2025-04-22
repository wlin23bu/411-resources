-- Create Users table
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    salt VARCHAR(32) NOT NULL,
    password VARCHAR(64) NOT NULL
);

-- Create Boxers table
DROP TABLE IF EXISTS boxers;
CREATE TABLE boxers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR UNIQUE NOT NULL,
    weight FLOAT NOT NULL,
    height FLOAT NOT NULL,
    reach FLOAT NOT NULL,
    age INTEGER NOT NULL,
    fights INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    weight_class VARCHAR
);

-- Index for faster lookup by name
CREATE INDEX IF NOT EXISTS idx_boxers_name ON boxers(name);