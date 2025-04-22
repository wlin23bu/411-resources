#!/bin/bash

# Define the database path - strip off sqlite:/// prefix if present
if [[ "$DATABASE_URL" == sqlite:///* ]]; then
    DB_PATH="${DATABASE_URL#sqlite:///}"
else
    # Default path if DATABASE_URL isn't set or doesn't have the expected format
    DB_PATH="/app/db/app.db"
fi

echo "Database path: $DB_PATH"

# Create the directory structure if it doesn't exist
echo "Setting up database directory structure..."
DB_DIR=$(dirname "$DB_PATH")
mkdir -p "$DB_DIR"

# Check if the database file already exists
if [ -f "$DB_PATH" ]; then
    echo "Recreating database at $DB_PATH."
    # Remove the existing database
    rm -f "$DB_PATH"
fi

echo "Creating database at $DB_PATH."
# Create the database
touch "$DB_PATH"
chmod 666 "$DB_PATH"

# Initialize the database with the schema
echo "Initializing database schema..."
sqlite3 "$DB_PATH" < /app/sql/init_db.sql

echo "Database setup complete!"