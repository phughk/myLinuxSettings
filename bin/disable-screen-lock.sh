#!/bin/bash

# Function to display help message
function show_help() {
    echo "Usage: $0 [DURATION]"
    echo "Temporarily disable screen lock for a specified duration."
    echo ""
    echo "Examples:"
    echo "  $0 16h   # Disable screen lock for 16 hours"
    echo "  $0 3d    # Disable screen lock for 3 days"
    echo "  $0 --help  # Show this help message"
    exit 0
}

# Check if help option is passed
if [[ "$1" == "--help" || -z "$1" ]]; then
    show_help
fi

# Convert duration to minutes for cron job scheduling
DURATION=$(echo $1 | sed -E 's/([0-9]+)h/\1*60/; s/([0-9]+)d/\1*1440/; s/([0-9]+)m/\1/' | bc)

# Validate duration
if ! [[ "$DURATION" =~ ^[0-9]+$ ]]; then
    echo "Error: Invalid duration format. Use [Nh], [Nd], or [Nm] (e.g., 16h, 3d, 45m)."
    exit 1
fi

# Disable screen lock
echo "Disabling screen lock for $1..."
gsettings set org.gnome.desktop.lockdown disable-lock-screen 'true'

# Schedule re-enabling via cron
echo "Re-enabling screen lock in $1..."
CRON_JOB="$(which gsettings) set org.gnome.desktop.lockdown disable-lock-screen 'false'"
(echo "$(date -d "+$DURATION minutes" "+%M %H %d %m %w") $CRON_JOB") | crontab -

echo "Cron job set to re-enable screen lock after $1."

