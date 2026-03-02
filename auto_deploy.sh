#!/bin/bash

# Environment setup
VENV_NAME="env_aurora-executor"
CONFIG_FILE="config.ini"

# Install system dependencies
sudo apt-get update
sudo apt-get install -y virtualenv expect tmux

# Create Python virtual environment
virtualenv $VENV_NAME

# Install Python dependencies
$VENV_NAME/bin/pip install -e . \
    questionary==2.1.0

# Download Sliver server
echo -e "\n[+] Downloading Sliver server..."
mkdir -p attack_tools
cd attack_tools
if [ ! -f "sliver-server_linux-amd64" ]; then
    wget https://github.com/BishopFox/sliver/releases/download/v1.7.2/sliver-server_linux-amd64
    chmod +x sliver-server_linux-amd64
    echo -e "[+] Sliver server downloaded successfully"
else
    echo -e "[*] Sliver server already exists, skipping download"
fi
cd ..

# Set default values without user interaction
# read -p "Path to Sliver client config [default: ~/zer0cool.cfg]: " sliver_path
# read -p "Metasploit RPC password [default: glycNshR]: " msf_pass
sliver_path="$PWD/zer0cool.cfg"
msf_pass="123456"

# Generate config file
cat > $CONFIG_FILE << EOF
[sliver]
client_config_file = $sliver_path

[metasploit]
password = $msf_pass
host_ip = 127.0.0.1
listening_port = 55552
EOF

# Kill existing tmux sessions
tmux kill-session -t msf 2>/dev/null
tmux kill-session -t sliver 2>/dev/null

# Start Metasploit RPC service
echo -e "\n[+] Starting Metasploit RPC service..."
tmux new-session -d -s msf \
  "msfconsole -q -x 'load msgrpc Pass=$msf_pass; setg MSGRPC_Pass $msf_pass; sleep 60000'"

# Start Sliver C2 server
echo -e "[+] Starting Sliver C2 server..."
tmux new-session -d -s sliver \
  "./attack_tools/sliver-server_linux-amd64"

# Wait for server initialization
sleep 10

# Execute Sliver setup commands
echo -e "[+] Configuring Sliver server..."
tmux send-keys -t sliver "new-operator --name zer0cool --lhost localhost --lport 34567 --save $sliver_path -P all" Enter
sleep 3
tmux send-keys -t sliver "multiplayer --lport 34567" Enter


echo -e "\n[+] Deployment completed!"
echo -e "[*] Service management commands:"
echo -e "  View Metasploit session: tmux attach -t msf"
echo -e "  View Sliver session: tmux attach -t sliver"

# Activate virtual environment automatically
echo -e "\n[+] Activating virtual environment..."
source $VENV_NAME/bin/activate
