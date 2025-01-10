#!/bin/bash
# Run both scripts in the background and wait for them
python3 health_checker.py &
# python3 main.py &


# Wait for all background jobs to finish
wait
