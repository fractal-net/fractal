#!/bin/bash

# The host of the Redis server
REDIS_HOST="localhost"
# The port the Redis server is running on
REDIS_PORT=6379
# Redis password 
REDIS_PASSWORD="your_password_here"

# Connect to the Redis server and execute FLUSHALL
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_CS_PASSWORD FLUSHALL

