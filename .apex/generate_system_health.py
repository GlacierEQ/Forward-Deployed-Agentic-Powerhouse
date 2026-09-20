#!/usr/bin/env python3
"""Generate a source-linked, fail-closed APEX runtime health record."""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

SCRIPT_DIR = Path("/root/.agents/skills/apex-sovereign-supreme/scripts")
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, "/root")

from runtime_optimizer_supreme import MANAGED_SERVICES, probe_readiness
from supabase_vault_client import SupabaseVaultClient


def ping_http(url: str, timeout: float = 1.0) -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "APEX-HealthCheck/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if response.status != 200 or not isinstance(payload, dict):
                return {"status": "OFFLINE", "http_status": response.status, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "reason": "invalid response"}
            return {"status": "ONLINE", "http_status": response.status, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "payload_status": payload.get("status")}
    except Exception as exc:
        return {"status": "OFFLINE", "reason": str(exc), "latency_ms": round((time.perf_counter() - started) * 1000, 2)}


def get_battery_info() -> Dict[str, Any]:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8990/api/battery", timeout=2.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
        data = payload.get("data", {}) if isinstance(payload, dict) else {}
        if payload.get("success") is not True or not isinstance(data.get("percentage"), (int, float)):
            return {"status": "DEGRADED", "reason": "battery schema invalid"}
        return {"status": "ONLINE", **data}
    except Exception as exc:
        return {"status": "OFFLINE", "reason": str(exc)}


def get_supabase_stats() -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        count = SupabaseVaultClient().count_total_keys()
        return {"status": "ONLINE" if count > 0 else "DEGRADED", "keys_indexed": count, "latency_ms": round((time.perf_counter() - started) * 1000, 2)}
    except Exception as exc:
        return {"status": "OFFLINE", "reason": str(exc), "latency_ms": round((time.perf_counter() - started) * 1000, 2)}


def get_quantum_proof() -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        sys.path.insert(0, "/root/src")
        from apex_quantum_logic_compiler import QuantumLogicCompiler
        certificate = QuantumLogicCompiler().emit_proof_certificate()
        theorems = len(certificate.get("theorems_compiled", [])) if isinstance(certificate, dict) else 0
        return {"status": "ONLINE" if theorems > 0 else "DEGRADED", "theorems_proven": theorems, "latency_ms": round((time.perf_counter() - started) * 1000, 2)}
    except Exception as exc:
        return {"status": "OFFLINE", "reason": str(exc), "latency_ms": round((time.perf_counter() - started) * 1000, 2)}


def generate_health() -> Dict[str, Any]:
    mesh_status = {}
    ready = 0
    for service in MANAGED_SERVICES:
        probe = probe_readiness(service)
        mesh_status[service["id"]] = {"name": service["name"], "port": service["port"], "owner": service.get("owner"), **probe}
        if probe.get("ready"):
            ready += 1
    battery = get_battery_info()
    vault = get_supabase_stats()
    quantum = get_quantum_proof()
    healthy = ready == len(MANAGED_SERVICES) and battery.get("status") == "ONLINE" and vault.get("status") == "ONLINE" and quantum.get("status") == "ONLINE"
    return {
        "schema": "apex.runtime-health/v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runtime_excellence": {
            "tier": "HOLOGRAPHIC_MESH",
            "microservices_ready": f"{ready}/{len(MANAGED_SERVICES)}",
            "uptime_ratio": round(ready / len(MANAGED_SERVICES), 3),
            "gate_08_runtime_healthy": healthy,
        },
        "holographic_mesh": mesh_status,
        "device_telemetry": battery,
        "supabase_vault": vault,
        "quantum_ml_logic": quantum,
        "status": "HEALTHY" if healthy else "DEGRADED",
    }


def main() -> int:
    record = generate_health()
    output = Path(os.environ.get("APEX_HEALTH_REPORT", "/root/.apex/system_health_runtime.json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, output)
    print(json.dumps({"status": record["status"], "report": str(output), "summary": record["runtime_excellence"]}, indent=2))
    return 0 if record["status"] == "HEALTHY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
