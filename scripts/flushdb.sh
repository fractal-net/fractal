#!/bin/bash 

# The host of the Redis server
REDIS_HOST="localhost"
# The port the Redis server is running on
REDIS_PORT=6379
# The Redis database number to clear
REDIS_DB=0
# Redis password 
REDIS_PASSWORD="your_password_here"

# Connect to the Redis server and execute FLUSHDB
redis-cli -h $REDIS_HOST -p $REDIS_PORT -n $REDIS_DB -a $REDIS_PASSWORD FLUSHDB


