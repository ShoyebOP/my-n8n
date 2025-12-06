#!/bin/bash

# ================= CONFIGURATION =================
# 1. Your specific Codespace name (Run 'gh codespace list' to find it)
CS_NAME="YOUR_CODESPACE_NAME"

# 2. The base URL of your n8n instance (No trailing slash)
N8N_BASE_URL="https://n8n.your-domain.com"

# 3. Your n8n Public API Key (Settings > Public API)
N8N_API_KEY="YOUR_N8N_API_KEY"

# 4. The folder path inside the Codespace where your compose.yaml lives, to get this you have to run pwd in the home of your cs
PROJECT_PATH="/workspaces/your-repo-name"

# 5. How long to wait between checks (in seconds). 300s = 5 minutes.
WAIT_TIME=300

# 6. The Grace Period Multiplier.
# If set to 3, the script waits for 3 checks (15 minutes total) of silence
# before it decides to shut down the server.
MAX_IDLE_CHECKS=3
# =================================================

# Define colors for pretty terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color (Reset)

# --- Function: Stop Codespace ---
# This is called when the idle limit is reached or the user presses 'q'.
stop_cs_and_exit() {
    echo -e "\n${RED}[STOP] Stopping Codespace ${CS_NAME}...${NC}"
    # Tells GitHub to shut down the VM immediately to save billing hours
    gh codespace stop -c "$CS_NAME"
    echo -e "${RED}[END] Script finished.${NC}"
    exit 0
}

# --- Function: Check n8n Activity ---
# Queries the API to see if anything is happening.
# Returns 0 (Success) if Busy. Returns 1 (Failure) if Idle.
check_n8n_active() {
    # We check two statuses: 'running' (active processing) and 'waiting' (webhooks/timers).
    # -k: Insecure mode (Bypasses Termux SSL errors for custom domains).
    # -s: Silent mode (Hides the download progress bar).
    
    # 1. Get Running Workflows
    RUN_DATA=$(curl -k -s -X GET "${N8N_BASE_URL}/api/v1/executions?status=running&includeData=false" -H "X-N8N-API-KEY: ${N8N_API_KEY}")
    
    # 2. Get Waiting Workflows
    WAIT_DATA=$(curl -k -s -X GET "${N8N_BASE_URL}/api/v1/executions?status=waiting&includeData=false" -H "X-N8N-API-KEY: ${N8N_API_KEY}")

    # Use 'jq' to count the number of items in the 'data' list.
    # 2>/dev/null hides errors if the API returns broken JSON (like a 502 Bad Gateway).
    C1=$(echo "$RUN_DATA" | jq '.data | length' 2>/dev/null)
    C2=$(echo "$WAIT_DATA" | jq '.data | length' 2>/dev/null)
    
    # Add them up. If C1 is empty/null, use 0.
    TOTAL=$(( ${C1:-0} + ${C2:-0} ))

    if [[ "$TOTAL" -gt 0 ]]; then
        return 0 # Found work -> Codespace is ACTIVE
    else
        return 1 # No work -> Codespace is IDLE
    fi
}

# --- Function: Wait with User Interrupt ---
# Pauses the script for $WAIT_TIME, but allows the user to press 'q' to quit early.
wait_with_quit() {
    local seconds=$1
    echo -e "${YELLOW}[WAIT] Waiting ${seconds}s... (Press 'q' to Stop & Exit)${NC}"
    
    # read -t: times out after $seconds
    # -n 1: reads exactly one character
    # -s: silent (doesn't show the character you typed)
    read -t "$seconds" -n 1 -s key
    
    # If the user typed 'q', kill the process.
    if [[ "$key" == "q" ]]; then
        echo -e "\n${RED}[USER] 'q' pressed.${NC}"
        stop_cs_and_exit
    fi
}

# --- Function: Keep Alive ---
# Sends a harmless command via SSH.
# This "tricks" GitHub into resetting the 30-minute auto-shutdown timer.
send_keep_alive() {
    gh codespace ssh -c "$CS_NAME" -- "ls" > /dev/null 2>&1
}

# --- Function: Boot Services ---
# Runs only if the Codespace is currently Shutdown.
start_n8n_services() {
    echo -e "${GREEN}[INIT] Booting Codespace & Starting Docker...${NC}"
    
    # We construct a complex remote command:
    # 1. 'until docker info': Docker takes a few seconds to wake up after boot. 
    #    We loop and sleep until the daemon is ready.
    # 2. 'docker compose ...': Starts your actual n8n container.
    REMOTE_SCRIPT="
        echo '--- Loading Env ---';
        until docker info > /dev/null 2>&1; do sleep 2; done; 
        cd $PROJECT_PATH;
        docker compose -f compose.yaml up --build -d;
    "
    
    # We use 'bash -l' (Login Shell) so that your .bashrc and Secrets are loaded.
    gh codespace ssh -c "$CS_NAME" -- "bash -l -c \"$REMOTE_SCRIPT\""
}

# ================= MAIN LOGIC FLOW =================

# 1. OPTIMIZATION CHECK
# Before booting, check if it's already running to save time.
echo -ne "${YELLOW}[INIT] Checking Codespace Status... ${NC}"

# 'gh codespace view' gets the JSON status. 'jq' or '-q' filters just the state string.
CURRENT_STATE=$(gh codespace view -c "$CS_NAME" --json state -q .state 2>/dev/null)
echo -e "${GREEN}$CURRENT_STATE${NC}"

if [[ "$CURRENT_STATE" == "Available" ]]; then
    # If already ON, we don't need to run the boot script.
    echo -e "${GREEN}[INFO] Codespace is already running. Skipping boot command.${NC}"
else
    # If OFF (Shutdown), run the robust boot sequence.
    start_n8n_services
fi

# 2. START THE WATCHDOG LOOP
idle_streak=0

while true; do
    # A. Wait for the defined interval (allows user to press 'q')
    wait_with_quit $WAIT_TIME

    echo -ne "   Checking Status... "
    
    # B. Query the API
    if check_n8n_active; then
        # === CASE 1: N8N IS BUSY ===
        echo -e "${GREEN}ACTIVE${NC}"
        
        # If we were counting idle streaks, reset them because work appeared.
        if [ $idle_streak -gt 0 ]; then
             echo -e "${GREEN}[RESET] Activity detected! Idle counter reset to 0.${NC}"
        fi
        idle_streak=0
        
        # [NEW] Add this line here to see the action:
        echo -e "${GREEN}[ACTION] Extending Codespace Timer...${NC}"
        
        # Ping the server so GitHub doesn't put it to sleep while n8n is working.
        send_keep_alive
    else
        # === CASE 2: N8N IS IDLE ===
        echo -e "${YELLOW}INACTIVE${NC}"
        
        # Increment the idle counter
        ((idle_streak++))
        echo -e "${YELLOW}[LOGIC] Idle Streak: $idle_streak / $MAX_IDLE_CHECKS${NC}"
        
        # C. Decide Action
        if [ "$idle_streak" -ge "$MAX_IDLE_CHECKS" ]; then
            # We have been idle too long. Kill it.
            stop_cs_and_exit
        else
            # We are idle, but haven't hit the limit yet.
            # Keep it alive for now (Grace Period).
            send_keep_alive
        fi
    fi
done
