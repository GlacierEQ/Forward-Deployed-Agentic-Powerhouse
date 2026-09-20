#!/usr/bin/env bash
# APEX Tri-Pillar Convergence Mega Services Supervisor
set -e

mkdir -p /root/.apex/logs /root/.apex/pids

echo "=== Launching APEX Tri-Pillar Mega Services ==="

# 1. Mega MCP Gateway (Port 9000)
if ! ss -tulpn 2>/dev/null | grep -q ":9000 " && ! lsof -i :9000 >/dev/null 2>&1; then
    echo "Starting Mega MCP Gateway on port 9000..."
    nohup python3 /root/.agents/skills/apex-sovereign-supreme/scripts/connector_hub_supreme.py --serve > /root/.apex/logs/gateway_9000.log 2>&1 &
    echo $! > /root/.apex/pids/gateway_9000.pid
else
    echo "Mega MCP Gateway (Port 9000) already active."
fi

# 2. Smithery JSON-RPC Mesh Proxy (Port 8999)
if ! ss -tulpn 2>/dev/null | grep -q ":8999 " && ! lsof -i :8999 >/dev/null 2>&1; then
    echo "Starting Smithery JSON-RPC Mesh Proxy on port 8999..."
    nohup python3 /root/.agents/skills/smithery-holographic-mesh/scripts/smithery_proxy_server.py 8999 > /root/.apex/logs/smithery_8999.log 2>&1 &
    echo $! > /root/.apex/pids/smithery_8999.pid
else
    echo "Smithery Proxy (Port 8999) already active."
fi

# 3. Mega Memory Substrate (Port 8787)
if ! ss -tulpn 2>/dev/null | grep -q ":8787 " && ! lsof -i :8787 >/dev/null 2>&1; then
    echo "Starting Mega Memory Substrate on port 8787..."
    nohup python3 /root/.agents/skills/apex-memory-substrate/scripts/apex_memory_server.py 8787 > /root/.apex/logs/memory_8787.log 2>&1 &
    echo $! > /root/.apex/pids/memory_8787.pid
else
    echo "Mega Memory Substrate (Port 8787) already active."
fi

# 4. Mega Automations Tasklet Daemon (Interval: 300s)
if ! pgrep -f "apex_tasklet_engine.py --daemon" >/dev/null 2>&1; then
    echo "Starting Autonomous Tasklet Daemon..."
    nohup python3 /root/automation/tasklet/apex_tasklet_engine.py --daemon 300 > /root/.apex/logs/tasklets.log 2>&1 &
    echo $! > /root/.apex/pids/tasklets.pid
else
    echo "Autonomous Tasklet Daemon already active."
fi

sleep 2
echo "=== All Tri-Pillar Services Initialized ==="
