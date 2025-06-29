#!/bin/bash

PORT=8000

# Find the PIDs of all processes using the port
PIDS=$(lsof -ti tcp:$PORT)

if [ -n "$PIDS" ]; then
  echo "Port $PORT is in use by PIDs: $PIDS. Killing all processes..."
  kill -9 $PIDS
  sleep 1
  # Check again
  PIDS_AFTER=$(lsof -ti tcp:$PORT)
  if [ -n "$PIDS_AFTER" ]; then
    echo "Port $PORT is STILL in use by: $PIDS_AFTER. Showing details:"
    lsof -i tcp:$PORT
    echo "Could not free port $PORT. Please check manually."
    exit 1
  else
    echo "Port $PORT is now free."
  fi
else
  echo "Port $PORT is free."
fi

# Activate virtual environment and run the server
source venv/bin/activate
uvicorn app.main:app --reload --port $PORT --host 127.0.0.1 