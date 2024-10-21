#!/bin/bash

# Read the input JSON object
eval "$(jq -r '@sh "HOSTNAME=\(.hostname)"')"

# Function to get IP with retries
get_ip_with_retry() {
    local hostname=$1
    local max_attempts=30
    local wait_time=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        IP=$(dig +short $hostname | grep -E '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$' | head -n 1)
        if [ -n "$IP" ]; then
            echo $IP
            return 0
        fi
        echo "Attempt $attempt: No IP found. Retrying in $wait_time seconds..." >&2
        sleep $wait_time
        attempt=$((attempt + 1))
    done

    echo "Failed to resolve IP after $max_attempts attempts" >&2
    return 1
}

# Try to get the IP with retries
IP=$(get_ip_with_retry $HOSTNAME)

# Return the IP address as a JSON object
if [ -n "$IP" ]; then
    jq -n --arg ip "$IP" '{"ip":$ip}'
else
    jq -n '{"ip":null}'
fi