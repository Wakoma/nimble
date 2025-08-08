#!/bin/bash

# Run CadOrchestrator with XVFB
xvfb-run -a --server-args='-screen 0 1024x768x24' cadorchestrator serve --production

# Capture the exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: xvfb-run failed with exit code $EXIT_CODE"
    exit $EXIT_CODE
fi
