#!/bin/bash

# Variables
HOST="127.0.0.1" # Replace with your Redis host
PORT=6379        # Replace with your Redis port
PASSWORD="yourpassword" # Replace with your Redis password
DATABASE=1       # Database number to select

# Connect to Redis, select the database and flush it
redis-cli -h $HOST -p $PORT -a $PASSWORD <<EOF
SELECT $DATABASE
FLUSHDB
EOF

echo "Database $DATABASE flushed successfully."

