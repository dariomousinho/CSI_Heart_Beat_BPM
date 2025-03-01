#!/bin/bash

echo "=== CSI Automated Tool Setup and Execution ==="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Directory setup - assuming this script is placed in the csi_automated directory
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
CAPTURE_SCRIPT="$SCRIPT_DIR/captura/capturar.py"
BPM_SCRIPT="$SCRIPT_DIR/CSI_bpm/base_csi_bpm.py"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

# Install dependencies if requirements.txt exists
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing required Python dependencies..."
    pip3 install -r "$REQUIREMENTS_FILE" || {
        echo "Failed to install dependencies. Trying with sudo..."
        sudo pip3 install -r "$REQUIREMENTS_FILE" || {
            echo "Error: Failed to install dependencies even with sudo."
            echo "Please install the dependencies manually with:"
            echo "sudo pip3 install -r $REQUIREMENTS_FILE"
            exit 1
        }
    }
    echo "Dependencies installed successfully."
else
    echo "Warning: requirements.txt not found at $REQUIREMENTS_FILE"
    echo "Dependencies will not be installed automatically."
fi

# Run the first script with sudo
echo "Starting capturar.py..."
sudo python3 "$CAPTURE_SCRIPT" &

# Wait for 15 seconds
echo "Waiting for 15 seconds before starting the second script..."
sleep 15

# Run the second script with sudo
echo "Starting base_csi_bpm.py..."
sudo python3 "$BPM_SCRIPT" &

echo "Both scripts are now running in parallel."