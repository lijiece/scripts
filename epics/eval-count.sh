#!/bin/bash

pv_name="det1.CNT"
round=1

# Clean exit when you press Ctrl+C
trap 'echo -e "\nMonitoring stopped by user."; exit 0' SIGINT

while true; do
    echo "--- Round $round ---"
    
    # 1. Trigger the process variable
    caput "$pv_name" 1 > /dev/null
    
    # 2. Track the start time for this specific round
    start_time=$(date +%s)
    
    # 3. Monitor loop for the current round
    while true; do
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
    
        # Fetch current PV state string
        pv_result=$(caget -t "$pv_name")
    
        # Check for the text string "Done" instead of the number 0
        if [[ "$pv_result" == *"Done"* ]]; then
            printf "\rRound %d finished! Total time: %d seconds.\n\n" "$round" "$elapsed"
            break
        fi
    
        # 5. Continuous single-line update while active
        printf "\rPV is active. State: [%s] | Elapsed: %d seconds.\e[K" "$pv_result" "$elapsed"
    
        sleep 1
    done

    # Increment the round counter for the next iteration
    ((round++))
done
