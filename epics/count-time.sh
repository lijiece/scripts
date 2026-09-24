#!/bin/bash
## This script records how much time does a detector count.

start_time=$(date +%s)
pv_name="det1.CNT"

# Start the loop
while true; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))

    pv_result=$(caget -t "$pv_name")

    if [[ "$pv_result" == *"Done"* ]]; then
        echo "Status is Done!"
        break
    fi
    
    echo "Counting. Elapsed: $elapsed seconds."
    
    sleep 60
done

echo "Counting finished. Elapsed: $elapsed seconds."
