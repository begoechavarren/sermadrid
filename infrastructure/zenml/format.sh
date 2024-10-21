#!/bin/bash

# Name this file format_terraform.sh and place it in your modules directory

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Find all directories containing .tf files
dirs=$(find . -type f -name "*.tf" -exec dirname {} \; | sort -u)

# Loop through each directory and run terraform fmt
for dir in $dirs
do
    log "Formatting Terraform files in $dir"
    (cd "$dir" && terraform fmt)
done

log "Terraform formatting complete"