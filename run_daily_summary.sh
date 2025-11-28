#!/bin/bash

# Absolute path to the project directory
PROJECT_DIR="/Users/y_sato/YOutubeSummary"

# Navigate to the project directory
cd "$PROJECT_DIR" || exit 1

# Log start time
echo "Starting daily summary at $(date)" >> "$PROJECT_DIR/cron_log.txt"

# Execute the script using the system python3
# Note: If you use a virtual environment, point to it here (e.g., .venv/bin/python3)
"$PROJECT_DIR/.venv/bin/python3" -m src.main >> "$PROJECT_DIR/cron_log.txt" 2>&1

# Log completion
echo "Finished daily summary at $(date)" >> "$PROJECT_DIR/cron_log.txt"
