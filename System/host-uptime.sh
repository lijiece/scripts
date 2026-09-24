#!/bin/bash
## Monitor the uptime of a remote host

# Configuration
REMOTE_USER="ubuntu"
REMOTE_IP="172.16.0.210"
LOG_FILE="./reboot_history.log"
CHECK_INTERVAL=60 

# State tracking
prev_uptime=0
connection_state="initial" # Possible: alive, unreachable, initial

touch "$LOG_FILE"
echo "Monitoring $REMOTE_IP. Alerts will be saved to $LOG_FILE."

while true; do
    # Attempt to get uptime
    raw_output=$(ssh -o ConnectTimeout=5 -o BatchMode=yes "${REMOTE_USER}@${REMOTE_IP}" "cat /proc/uptime" 2>/dev/null)
    current_uptime=$(echo "$raw_output" | awk '{print $1}' | cut -d. -f1)

    if [[ -n "$current_uptime" ]]; then
        # CASE 1: Device is UP
        if [[ "$connection_state" != "alive" ]]; then
            echo "$(date "+%H:%M:%S") - Status: Alive"
            connection_state="alive"
        fi

        # Detect if a reboot happened while we were watching
        if (( prev_uptime > 0 && current_uptime < prev_uptime )); then
            timestamp=$(date "+%Y-%m-%d %H:%M:%S")
            msg="[REBOOT] Detected at $timestamp. Previous session lasted ${prev_uptime}s."
            echo "$msg" | tee -a "$LOG_FILE"
        fi
        
        prev_uptime=$current_uptime
    else
        # CASE 2: Device is DOWN
        if [[ "$connection_state" != "unreachable" ]]; then
            timestamp=$(date "+%H:%M:%S")
            echo "$timestamp - Status: Unreachable. (Last known uptime: ${prev_uptime}s)"
            connection_state="unreachable"
        fi
    fi

    sleep "$CHECK_INTERVAL"
done
