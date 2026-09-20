#!/usr/bin/env python3
"""
APEX Holographic Mesh Supreme Runtime Supervisor v4.0
Unified daemon orchestrating:
  - Port 9000: Mega MCP Supreme Gateway
  - Port 8999: Smithery JSON-RPC Mesh Proxy
  - Port 8787: Mega Memory Substrate
  - Port 8990: APEX Device RPC Bridge
  - Port 3000: Colossus Gateway
  - Port 4000: Colossus Gatekeeper
  - Port 4001: Colossus Key Master
  - Port 4002: Supermemory Unified Brain
  - Port 8002: Nexus API Gateway
  - Port 8003: Apex Multi-Protocol Router
  - Port 8741: Mastermind API Engine
  - Background: Autonomous Tasklet Engine
  - Background: Self-Hosted GitHub Actions Runner Supervisor
  - Port 8888: Local Google MCP (owned by runtime optimizer)
"""

import os
import sys
import time
import signal
import threading
import subprocess
from http.server import ThreadingHTTPServer
from pathlib import Path

# Add python search paths
sys.path.insert(0, "/root/.agents/skills/apex-sovereign-supreme/scripts")
sys.path.insert(0, "/root/.agents/skills/smithery-holographic-mesh/scripts")
sys.path.insert(0, "/root/.agents/skills/apex-memory-substrate/scripts")
sys.path.insert(0, "/root/automation/tasklet")
sys.path.insert(0, "/root/src")
sys.path.insert(0, "/data/data/com.termux/files/home/mastermind/core")
sys.path.insert(0, "/data/data/com.termux/files/home/mastermind/core/engines")
sys.path.insert(0, "/data/data/com.termux/files/home/scripts")

from runtime_optimizer_supreme import MANAGED_SERVICES, probe_readiness

from connector_hub_supreme import ConnectorGatewayRequestHandler
from smithery_proxy_server import SmitheryProxyHandler
from apex_memory_server import MemoryServerHandler
from apex_tasklet_engine import TaskletRunner
from colossus_trinity_runner import GatewayHandler, GatekeeperHandler, KeyMasterHandler, SupermemoryBrainHandler
from device_access_supreme import DeviceRPCRequestHandler
from nexus_api import NexusHandler
from apex_router import RouterHandler
from server import MastermindHandler

def run_http_service(name: str, port: int, handler_cls):
    """Run a standard ThreadingHTTPServer on 127.0.0.1:port."""
    while True:
        try:
            class ResilientServer(ThreadingHTTPServer):
                allow_reuse_address = True
            server = ResilientServer(("127.0.0.1", port), handler_cls)
            print(f"⚡ [{name}] Active on http://127.0.0.1:{port}", flush=True)
            server.serve_forever()
        except Exception as e:
            print(f"❌ [{name} {port}] Error: {e}", flush=True)
            time.sleep(2)

def run_tasklets():
    """Background autonomous tasklet daemon."""
    try:
        time.sleep(3)
        runner = TaskletRunner()
        print("🚀 [Mega Automations] Tasklet Daemon active (300s interval)", flush=True)
        runner.daemon_loop(300)
    except Exception as e:
        print(f"❌ [Tasklet Daemon] Error: {e}", flush=True)

def run_actions_runner():
    """Supervises the self-hosted GitHub Actions runner in background."""
    time.sleep(2)
    runner_script = Path("/root/actions-runner/runner_service.py")
    if runner_script.exists():
        print("🤖 [GitHub Actions Runner] Launching runner supervisor...", flush=True)
        try:
            subprocess.run(["python3", str(runner_script)], check=False)
        except Exception as e:
            print(f"❌ [GitHub Actions Runner] Error: {e}", flush=True)

def run_ollama():
    """Supervises local Ollama neural engine on 127.0.0.1:11434."""
    time.sleep(1)
    ollama_bin = Path("/data/data/com.termux/files/usr/bin/ollama")
    models_dir = Path("/root/.ollama/models")
    if ollama_bin.exists():
        print("🦙 [Ollama Neural Engine] Launching on 127.0.0.1:11434...", flush=True)
        env = os.environ.copy()
        env["OLLAMA_MODELS"] = str(models_dir)
        while True:
            try:
                proc = subprocess.Popen(
                    [str(ollama_bin), "serve"],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                proc.wait()
            except Exception as e:
                print(f"❌ [Ollama Neural Engine] Error: {e}", flush=True)
            time.sleep(3)

def main():
    print("=== INITIALIZING FORWARD DEPLOYED AGENTIC AI — APEX RUNTIME v4.0 ===", flush=True)

    services = [
        ("Mega MCP Gateway", 9000, ConnectorGatewayRequestHandler),
        ("Smithery Mesh Proxy", 8999, SmitheryProxyHandler),
        ("Mega Memory Substrate", 8787, MemoryServerHandler),
        ("APEX Device RPC", 8990, DeviceRPCRequestHandler),
        ("Colossus Gateway", 3000, GatewayHandler),
        ("Colossus Gatekeeper", 4000, GatekeeperHandler),
        ("Colossus Key Master", 4001, KeyMasterHandler),
        ("Supermemory Unified Brain", 4002, SupermemoryBrainHandler),
        ("Nexus API Gateway", 8002, NexusHandler),
        ("Apex Router", 8003, RouterHandler),
        ("Mastermind API Engine", 8741, MastermindHandler),
    ]

    threads = []
    for name, port, handler in services:
        t = threading.Thread(target=run_http_service, args=(name, port, handler), daemon=True)
        t.start()
        threads.append(t)

    owned_services = [service for service in MANAGED_SERVICES if service.get("owner") == "mega_supervisor"]
    deadline = time.monotonic() + 15.0
    ready_ids = set()
    while time.monotonic() < deadline:
        ready_ids = {
            service["id"]
            for service in owned_services
            if probe_readiness(service).get("ready")
        }
        if len(ready_ids) == len(owned_services):
            break
        time.sleep(0.5)

    # Background Daemons
    t_tasklet = threading.Thread(target=run_tasklets, daemon=True)
    t_tasklet.start()

    t_runner = threading.Thread(target=run_actions_runner, daemon=True)
    t_runner.start()

    t_ollama = threading.Thread(target=run_ollama, daemon=True)
    t_ollama.start()

    if len(ready_ids) == len(owned_services):
        print(f"✅ All {len(owned_services)} owned Holographic Mesh services are READY.", flush=True)
    else:
        missing = [service["id"] for service in owned_services if service["id"] not in ready_ids]
        print(f"⚠️ {len(owned_services) - len(ready_ids)}/{len(owned_services)} owned services not ready: {', '.join(missing)}", flush=True)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
