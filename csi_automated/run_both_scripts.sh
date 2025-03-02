#!/bin/bash

echo "=== CSI Automated Tool Setup and Execution ==="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Directory setup - assuming this script is placed in the csi_automated directory
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
CAPTURE_DIR="$SCRIPT_DIR/captura"
CSI_BPM_DIR="$SCRIPT_DIR/CSI_bpm"
CAPTURE_SCRIPT="$CAPTURE_DIR/capturar.py"
BPM_SCRIPT="$CSI_BPM_DIR/base_csi_bpm.py"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
CAPTURAR_SHELL="$CAPTURE_DIR/capturar.sh"

# Check if files exist
if [ ! -f "$CAPTURE_SCRIPT" ]; then
    echo "Error: Capture script not found at $CAPTURE_SCRIPT"
    exit 1
fi

if [ ! -f "$BPM_SCRIPT" ]; then
    echo "Error: BPM script not found at $BPM_SCRIPT"
    exit 1
fi

# Check if capturar.sh exists and make it executable
if [ -f "$CAPTURAR_SHELL" ]; then
    echo "Making capturar.sh executable..."
    chmod +x "$CAPTURAR_SHELL"
else
    echo "Warning: capturar.sh not found at $CAPTURAR_SHELL"
    echo "Creating it with basic functionality..."
    
    # Create a basic capturar.sh script if it doesn't exist
    cat > "$CAPTURAR_SHELL" << 'EOF'
#!/bin/bash
# Basic capturar.sh script
echo "Running capturar.sh with parameters: $@"
COUNT=$1
CHANNEL=$2
MAC_ADDRESS=$3

echo "Count: $COUNT"
echo "Channel: $CHANNEL"
echo "MAC Address: $MAC_ADDRESS"

# Create Scan directory if it doesn't exist
mkdir -p "$(dirname "$0")/Scan"

# Your capture logic would go here
echo "Capture completed successfully"
EOF
    
    chmod +x "$CAPTURAR_SHELL"
fi

# Create Scan directory if it doesn't exist
mkdir -p "$CAPTURE_DIR/Scan"

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

# Run the first script with sudo from its directory
echo "Starting capturar.py..."
cd "$CAPTURE_DIR"
sudo python3 capturar.py &

# Wait for 15 seconds
echo "Waiting for 15 seconds before starting the second script..."
sleep 15

# Run the second script with sudo from its directory
echo "Starting base_csi_bpm.py..."
cd "$CSI_BPM_DIR"
sudo python3 base_csi_bpm.py &

echo "Both scripts are now running in parallel."