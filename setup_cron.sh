#!/bin/bash

# Absolute path to the project directory
PROJECT_DIR="/Users/y_sato/Downloads/YOutubeSummary"
SCRIPT_PATH="$PROJECT_DIR/run_daily_summary.sh"

# Ensure the script is executable
chmod +x "$SCRIPT_PATH"

# Backup current crontab
crontab -l > mycron.backup 2>/dev/null

# Remove existing jobs for this script to avoid duplicates
grep -v "$SCRIPT_PATH" mycron.backup > mycron.new

# Add new jobs
# 06:00 JST
echo "0 6 * * * $SCRIPT_PATH" >> mycron.new
# 10:00 JST
echo "0 10 * * * $SCRIPT_PATH" >> mycron.new
# 14:00 JST
echo "0 14 * * * $SCRIPT_PATH" >> mycron.new
# 18:00 JST
echo "0 18 * * * $SCRIPT_PATH" >> mycron.new
# 22:00 JST
echo "0 22 * * * $SCRIPT_PATH" >> mycron.new

# Install new crontab
crontab mycron.new

# Clean up
rm mycron.new

echo "Cron jobs updated successfully."
echo "Current crontab:"
crontab -l
