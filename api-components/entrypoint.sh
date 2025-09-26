#!/bin/sh

# Start the API server in the background
/usr/local/bin/apiserver &

# Check if arguments were passed to the script.
# "$#" holds the count of arguments.
if [ "$#" -gt 0 ]; then
  # If there are arguments, execute them as the main command.
  # This is for containers that have a CMD (e.g., CMD ["python", "app.py"])
  exec "$@"
else
  # If there are no arguments, keep the container alive.
  # This is for tool containers that have no CMD.
  echo "No CMD detected. Starting in standby mode."
  # Use 'tail -f /dev/null' to wait forever.
  exec tail -f /dev/null
fi
