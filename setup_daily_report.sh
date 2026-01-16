#!/bin/bash
# Setup script for daily Oura report automation

echo "=== Oura Daily Report Setup ==="
echo

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Installation directory: $SCRIPT_DIR"
echo

# Make Python script executable
chmod +x "$SCRIPT_DIR/daily_oura_report.py"
echo "✓ Made daily_oura_report.py executable"

# Prompt for cron time
echo
echo "When would you like to receive your daily report?"
echo "Examples:"
echo "  8 0   - 8:00 AM"
echo "  21 0  - 9:00 PM"
echo "  12 30 - 12:30 PM"
echo
read -p "Enter hour (0-23): " HOUR
read -p "Enter minute (0-59): " MINUTE

# Validate input
if ! [[ "$HOUR" =~ ^[0-9]+$ ]] || [ "$HOUR" -lt 0 ] || [ "$HOUR" -gt 23 ]; then
    echo "Invalid hour. Using default: 8 AM"
    HOUR=8
    MINUTE=0
fi

if ! [[ "$MINUTE" =~ ^[0-9]+$ ]] || [ "$MINUTE" -lt 0 ] || [ "$MINUTE" -gt 59 ]; then
    echo "Invalid minute. Using default: 00"
    MINUTE=0
fi

# Create cron job entry
CRON_JOB="$MINUTE $HOUR * * * cd $SCRIPT_DIR && /usr/bin/python3 daily_oura_report.py >> $SCRIPT_DIR/oura_report.log 2>&1"

echo
echo "Cron job to be added:"
echo "$CRON_JOB"
echo

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "daily_oura_report.py"; then
    echo "Existing Oura report cron job found."
    read -p "Replace it? (y/n): " REPLACE
    if [ "$REPLACE" = "y" ] || [ "$REPLACE" = "Y" ]; then
        # Remove old cron job
        (crontab -l 2>/dev/null | grep -v "daily_oura_report.py"; echo "$CRON_JOB") | crontab -
        echo "✓ Cron job updated"
    else
        echo "Keeping existing cron job"
    fi
else
    # Add new cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✓ Cron job added"
fi

echo
echo "Current cron jobs:"
crontab -l | grep "daily_oura_report.py"

echo
echo "=== Setup Complete ==="
echo
echo "Your daily Oura report will run at $(printf '%02d:%02d' $HOUR $MINUTE)"
echo
echo "Manual commands:"
echo "  Test now:     python3 daily_oura_report.py"
echo "  View log:     tail -f oura_report.log"
echo "  List cron:    crontab -l"
echo "  Edit cron:    crontab -e"
echo "  Remove cron:  crontab -e  (then delete the line)"
echo
