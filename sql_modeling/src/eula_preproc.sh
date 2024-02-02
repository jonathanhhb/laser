#!/bin/bash

# Check if a filename and threshold are provided as arguments
if [ $# -ne 2 ]; then
    echo "Usage: $0 <filename> <threshold>"
    exit 1
fi

# Assign the filename and threshold to variables
filename=$1
threshold=$2

# Run awk to split the file based on the age column and the provided threshold
awk -v threshold="$threshold" -F ',' '{
    if ($3 > threshold) {
        print > "age_gt_" threshold ".csv"
    } else if ($3 < threshold) {
        print > "age_lt_" threshold ".csv"
    }
}' "$filename"

