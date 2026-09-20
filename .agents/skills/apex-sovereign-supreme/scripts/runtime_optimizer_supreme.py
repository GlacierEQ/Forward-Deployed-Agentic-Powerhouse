#!/usr/bin/env python3
"""Evidence-backed APEX service readiness, recovery, and resource governor."""

import argparse
import fcntl
import gc
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


SKILL_SCRIPTS = Path("/root/.agents/skills/apex-sovereign-supreme/scripts")
TERMUX_HOME = Path("/data/data/com.termux/files/home")
MANIFEST_PATH = Path("/root/.apex/apex_service_manifest.json")
STATE_DIR = Path("/root/.apex/runtime")
PID_DIR = STATE_DIR / "pids"
LOCK_PATH = STATE_DIR / "optimizer.lock"
MEGA_SUPERVISOR_PID = Path("/root/.apex/state/mega_supervisor.pid")
STARTUP_TIMEOUT = float(os.environ.get("APEX_SERVICE_STARTUP_TIMEOUT", "12"))
STARTUP_ATTEMPTS = int(os.environ.get("APEX_SERVICE_STARTUP_ATTEMPTS", "3"))


def load_manifest(path: Path = MANIFEST_PATH) -> List[Dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"Unable to load service manifest {path}: {exc}") from exc
    services = payload.get("services") if isinstance(payload, dict) else None
    if not isinstance(services, list) or not services:
        raise RuntimeError(f"Service manifest has no services: {path}")
    ids = [service.get("id") for service in services]
    ports = [service.get("port") for service in services]
    if any(not service_id for service_id in ids) or len(ids) != len(set(ids)):
        raise RuntimeError("Service manifest contains missing or duplicate service ids")
    if any(not isinstance(port, int) or not 1 <= port <= 65535 for port in ports) or len(ports) != len(set(ports)):
        raise RuntimeError("Service manifest contains missing or duplicate ports")
    return services


MANAGED_SERVICES = load_manifest()


def check_port(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def readiness_url(service: Dict[str, Any]) -> str:
    readiness = service.get("readiness", {})
    path = readiness.get("path", "/health")
    if not str(path).startswith("/"):
        path = f"/{path}"
    return f"http://{service['host']}:{service['port']}{path}"


def probe_readiness(service: Dict[str, Any], timeout: float = 1.5) -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        request = urllib.request.Request(
            readiness_url(service),
            headers={"User-Agent": "APEX-Readiness/1.0", "Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(1024 * 1024)
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                return {"ready": False, "reason": "response is not a JSON object", "http_status": response.status}
            readiness = service.get("readiness", {})
            expected = {str(value).lower() for value in readiness.get("status", ["OK", "ONLINE", "ok"])}
            actual = str(payload.get("status", "")).lower()
            required = readiness.get("required", ["status"])
            missing = [key for key in required if key not in payload]
            if response.status != 200:
                return {"ready": False, "reason": f"HTTP {response.status}", "http_status": response.status}
            if actual not in expected:
                return {"ready": False, "reason": f"unexpected status {actual!r}", "http_status": response.status}
            if missing:
                return {"ready": False, "reason": f"missing fields: {', '.join(missing)}", "http_status": response.status}
            return {
                "ready": True,
                "reason": "ready",
                "http_status": response.status,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }
    except (OSError, ValueError, urllib.error.URLError) as exc:
        return {
            "ready": False,
            "reason": str(exc),
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        }


def pid_file(service: Dict[str, Any]) -> Path:
    return PID_DIR / f"{service['id']}.pid"


def read_pid(path: Path) -> Optional[int]:
    try:
        value = int(path.read_text(encoding="ascii").strip())
        return value if value > 0 else None
    except (OSError, ValueError):
        return None


def pid_is_alive(pid: Optional[int]) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def process_matches(pid: Optional[int], command: Iterable[str]) -> bool:
    if not pid:
        return False
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
    except OSError:
        return False
    return any(str(part) and str(part) in raw for part in command if str(part))


def acquire_lock() -> Any:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PID_DIR.mkdir(parents=True, exist_ok=True)
    lock = LOCK_PATH.open("a+")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        raise RuntimeError("Runtime optimizer is already running")
    return lock


def spawn_service(service: Dict[str, Any]) -> Dict[str, Any]:
    command = [str(part) for part in service.get("command", [])]
    if not command:
        return {"ok": False, "reason": "service has no command"}
    log_path = Path(service.get("log_file", f"/tmp/{service['id']}.log"))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        log_handle = log_path.open("ab")
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )
        log_handle.close()
        pid_file(service).write_text(f"{process.pid}\n", encoding="ascii")
        return {"ok": True, "pid": process.pid, "command": command}
    except OSError as exc:
        return {"ok": False, "reason": str(exc)}


def stop_pid(service: Dict[str, Any], timeout: float = 5.0) -> bool:
    pid = read_pid(pid_file(service))
    if not pid_is_alive(pid):
        return True
    try:
        os.kill(pid, 15)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if not pid_is_alive(pid):
                return True
            time.sleep(0.1)
        os.kill(pid, 9)
        return True
    except OSError:
        return False


def supervisor_is_alive() -> bool:
    return pid_is_alive(read_pid(MEGA_SUPERVISOR_PID))


def wait_ready(service: Dict[str, Any], timeout: float = STARTUP_TIMEOUT) -> Dict[str, Any]:
    deadline = time.monotonic() + timeout
    last = {"ready": False, "reason": "no readiness probe completed"}
    while time.monotonic() < deadline:
        last = probe_readiness(service)
        if last["ready"]:
            return last
        time.sleep(0.4)
    return last


class RuntimeOptimizer:
    @classmethod
    def status(cls) -> Dict[str, Any]:
        results = []
        ready = 0
        for service in MANAGED_SERVICES:
            probe = probe_readiness(service)
            if probe["ready"]:
                ready += 1
            results.append({
                "id": service["id"],
                "name": service["name"],
                "port": service["port"],
                "owner": service.get("owner", "unknown"),
                "status": "READY" if probe["ready"] else ("LISTENING" if check_port(service["host"], service["port"]) else "OFFLINE"),
                **probe,
            })
        return {
            "success": ready == len(MANAGED_SERVICES),
            "runtime_summary": {
                "total_managed": len(MANAGED_SERVICES),
                "ready_services": ready,
                "health_percentage": round(ready * 100 / len(MANAGED_SERVICES), 1),
            },
            "services": results,
        }

    @classmethod
    def auto_heal_services(cls, verbose: bool = True) -> Dict[str, Any]:
        lock = acquire_lock()
        results = []
        restored = 0
        ready = 0
        try:
            for service in MANAGED_SERVICES:
                probe = probe_readiness(service)
                if probe["ready"]:
                    ready += 1
                    results.append({"service": service["name"], "id": service["id"], "port": service["port"], "status": "READY", "action": "None (ready)"})
                    continue
                if check_port(service["host"], service["port"]):
                    results.append({"service": service["name"], "id": service["id"], "port": service["port"], "status": "DEGRADED", "action": "Readiness failed", **probe})
                    continue
                if service.get("owner") == "mega_supervisor" and supervisor_is_alive():
                    if verbose:
                        print(f"[{service['name']}] waiting for mega supervisor recovery", flush=True)
                    probe = wait_ready(service, timeout=min(5.0, STARTUP_TIMEOUT))
                    if probe["ready"]:
                        ready += 1
                        results.append({"service": service["name"], "id": service["id"], "port": service["port"], "status": "READY", "action": "Recovered by owner", **probe})
                    else:
                        results.append({"service": service["name"], "id": service["id"], "port": service["port"], "status": "DEGRADED", "action": "Owner did not restore readiness", **probe})
                    continue
                if verbose:
                    print(f"[{service['name']}] offline; bounded recovery attempts", flush=True)
                spawn_result = spawn_service(service)
                if not spawn_result["ok"]:
                    results.append({"service": service["name"], "id": service["id"], "port": service["port"], "status": "ERROR", "action": spawn_result["reason"]})
                    continue
                for attempt in range(1, STARTUP_ATTEMPTS + 1):
                    probe = wait_ready(service, timeout=STARTUP_TIMEOUT / STARTUP_ATTEMPTS)
                    if probe["ready"]:
                        ready += 1
                        restored += 1
                        results.append({"service": service["name"], "id": service["id"], "port": service["port"], "status": "READY", "action": "Resurrected", "attempt": attempt, **probe})
                        break
                    if attempt < STARTUP_ATTEMPTS:
                        time.sleep(min(2 ** (attempt - 1), 4))
                else:
                    results.append({"service": service["name"], "id": service["id"], "port": service["port"], "status": "OFFLINE", "action": "Recovery attempts exhausted", **probe})
            summary = {
                "total_managed": len(MANAGED_SERVICES),
                "ready_services": ready,
                "restored_services": restored,
                "health_percentage": round(ready * 100 / len(MANAGED_SERVICES), 1),
            }
            return {"success": ready == len(MANAGED_SERVICES), "runtime_summary": summary, "services": results}
        finally:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            finally:
                lock.close()

    @classmethod
    def optimize_memory_and_logs(cls) -> Dict[str, Any]:
        log_paths = {Path(path) for pattern in ("/tmp/*.log", "/tmp/apex_*.log") for path in Path("/tmp").glob(pattern)}
        rotated = []
        bytes_reclaimed = 0
        for path in sorted(log_paths):
            try:
                if not path.is_file() or path.stat().st_size <= 5 * 1024 * 1024:
                    continue
                before = path.stat().st_size
                rotated_path = path.with_name(path.name + ".1")
                if rotated_path.exists():
                    rotated_path.unlink()
                path.rename(rotated_path)
                bytes_reclaimed += before - (rotated_path.stat().st_size if rotated_path.exists() else 0)
                rotated.append(str(path))
            except OSError:
                continue
        gc.collect()
        return {
            "success": True,
            "logs_rotated": len(rotated),
            "rotated_paths": rotated,
            "bytes_reclaimed": bytes_reclaimed,
            "memory_freed_mb": round(bytes_reclaimed / (1024 * 1024), 2),
        }

    @classmethod
    def get_performance_telemetry(cls) -> Dict[str, Any]:
        mem_info: Dict[str, str] = {}
        mem_error = None
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as stream:
                for line in stream:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        mem_info[key.strip()] = value.strip()
        except OSError as exc:
            mem_error = str(exc)
        disk_paths = ["/root", "/data/data/com.termux/files/home"]
        disks = {}
        for path in disk_paths:
            try:
                usage = shutil.disk_usage(path)
                disks[path] = {"free_gb": round(usage.free / (1024 ** 3), 2), "total_gb": round(usage.total / (1024 ** 3), 2)}
            except OSError as exc:
                disks[path] = {"error": str(exc)}
        return {
            "success": not mem_error and all("error" not in value for value in disks.values()),
            "telemetry": {
                "timestamp": time.time(),
                "ram_total": mem_info.get("MemTotal"),
                "ram_available": mem_info.get("MemAvailable"),
                "ram_free": mem_info.get("MemFree"),
                "memory_error": mem_error,
                "disks": disks,
                "cpu_cores": os.cpu_count(),
            },
        }

    @classmethod
    def run_watchdog_loop(cls, interval: int = 30) -> None:
        if interval <= 0:
            raise ValueError("interval must be positive")
        print(json.dumps({"event": "watchdog_started", "interval_seconds": interval}), flush=True)
        while True:
            started = time.monotonic()
            try:
                result = cls.auto_heal_services(verbose=False)
                print(json.dumps({"event": "watchdog_heal", **result["runtime_summary"], "success": result["success"]}), flush=True)
                cls.optimize_memory_and_logs()
            except Exception as exc:
                print(json.dumps({"event": "watchdog_error", "error": str(exc)}), flush=True)
            time.sleep(max(1, interval - (time.monotonic() - started)))


def main() -> int:
    parser = argparse.ArgumentParser(description="APEX service readiness and recovery governor")
    parser.add_argument("action", nargs="?", default="status", choices=["status", "heal", "wait", "restart", "optimize", "telemetry", "daemon", "manifest"])
    parser.add_argument("--service", help="Service id for restart")
    parser.add_argument("--interval", "-i", type=int, default=30)
    args = parser.parse_args()
    if args.action == "manifest":
        print(json.dumps({"schema": "apex.service-manifest/v1", "services": MANAGED_SERVICES}, indent=2))
        return 0
    if args.action == "daemon":
        RuntimeOptimizer.run_watchdog_loop(args.interval)
        return 0
    if args.action == "status":
        result = RuntimeOptimizer.status()
    elif args.action == "heal":
        result = RuntimeOptimizer.auto_heal_services(verbose=True)
    elif args.action == "wait":
        result = RuntimeOptimizer.status()
    elif args.action == "restart":
        if not args.service:
            parser.error("--service is required for restart")
        service = next((item for item in MANAGED_SERVICES if item["id"] == args.service), None)
        if not service:
            print(json.dumps({"success": False, "error": f"unknown service: {args.service}"}))
            return 2
        if service.get("owner") != "runtime_optimizer":
            print(json.dumps({"success": False, "error": f"service is owned by {service.get('owner')}", "service": service["id"]}))
            return 2
        stop_pid(service)
        spawn_result = spawn_service(service)
        probe = wait_ready(service) if spawn_result["ok"] else {"ready": False, "reason": spawn_result["reason"]}
        result = {"success": bool(probe.get("ready")), "service": service["id"], "spawn": spawn_result, "readiness": probe}
    elif args.action == "optimize":
        result = RuntimeOptimizer.optimize_memory_and_logs()
    else:
        result = RuntimeOptimizer.get_performance_telemetry()
    print(json.dumps(result, indent=2))
    return 0 if result.get("success", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
