#!/bin/sh

# Check if the correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_file> <target_directory>"
    exit 1
fi

SOURCE_FILE="$1"
TARGET_DIR="$2"
# Use a basic approach to get the basename and extension
BASENAME=$(basename "$SOURCE_FILE")
EXTENSION=""
FILENAME="$BASENAME"

# Check if the filename contains a dot to separate extension
# This is a bit more manual than the bash version but works in sh
case "$BASENAME" in
    *.*)
        EXTENSION=".${BASENAME##*.}"
        FILENAME="${BASENAME%.*}"
        ;;
esac

COUNTER=0

# Check if the source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file '$SOURCE_FILE' not found."
    exit 1
fi

# Create the target directory if it doesn't exist
if [ ! -d "$TARGET_DIR" ]; then
    mkdir -p "$TARGET_DIR"
fi

# Loop to find a unique filename
while true; do
    NEW_FILENAME="$FILENAME"
    
    # If the counter is greater than 0, add it to the filename
    if [ "$COUNTER" -gt 0 ]; then
        NEW_FILENAME="${FILENAME}_${COUNTER}"
    fi
    
    # Reassemble the full path
    NEW_PATH="${TARGET_DIR}/${NEW_FILENAME}${EXTENSION}"

    # Check if the new path already exists
    if [ ! -f "$NEW_PATH" ]; then
        echo "Moving '$SOURCE_FILE' to '$NEW_PATH'..."
        mv "$SOURCE_FILE" "$NEW_PATH"
        break
    else
        # If it exists, increment the counter and try again
        COUNTER=$((COUNTER + 1))
    fi
done
