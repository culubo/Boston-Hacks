#!/bin/bash

echo "Reverting to backup version..."

# Stop any running processes
killall python3 2>/dev/null || true

# Restore backup
if [ -f "live_screen_blocker_backup.py" ]; then
    cp live_screen_blocker_backup.py live_screen_blocker.py
    echo "Successfully reverted to backup version"
    echo "You can now run: python3 live_screen_blocker.py"
else
    echo "Error: Backup file not found!"
    exit 1
fi
