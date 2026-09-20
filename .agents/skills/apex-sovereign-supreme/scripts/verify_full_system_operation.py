#!/usr/bin/env python3
"""Fail-closed end-to-end verification for the APEX holographic runtime."""

import json
import os
import sys
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, "/root")

from runtime_optimizer_supreme import MANAGED_SERVICES, RuntimeOptimizer, probe_readiness
from supabase_vault_client import SupabaseVaultClient


@dataclass
class TestResult:
    layer: str
    target: str
    status: str
    latency_ms: float
    details: str


class SovereignVerificationSuite:
    def __init__(self) -> None:
        self.results: List[TestResult] = []
        self.start_time = time.perf_counter()

    def add(self, layer: str, target: str, passed: bool, latency_ms: float, details: str) -> bool:
        self.results.append(TestResult(layer, target, "PASSED" if passed else "FAILED", round(latency_ms, 2), details))
        return passed

    def verify_all_services(self) -> None:
        for service in MANAGED_SERVICES:
            started = time.perf_counter()
            probe = probe_readiness(service)
            self.add(
                "Microservice Mesh",
                f"{service['name']} ({service['port']})",
                bool(probe.get("ready")),
                (time.perf_counter() - started) * 1000,
                probe.get("reason", "ready"),
            )

    def verify_device_rpc_apis(self) -> None:
        started = time.perf_counter()
        try:
            request = urllib.request.Request("http://127.0.0.1:8990/api/battery")
            with urllib.request.urlopen(request, timeout=3.0) as response:
                data = json.loads(response.read().decode("utf-8"))
            battery = data.get("data") if isinstance(data, dict) else None
            percentage = battery.get("percentage") if isinstance(battery, dict) else None
            temperature = battery.get("temperature") if isinstance(battery, dict) else None
            passed = data.get("success") is True and isinstance(percentage, (int, float)) and isinstance(temperature, (int, float))
            self.add("Android Device RPC", "Battery & Power Telemetry", passed, (time.perf_counter() - started) * 1000, f"Charge: {percentage}% | Temp: {temperature} C")
        except Exception as exc:
            self.add("Android Device RPC", "Battery & Power Telemetry", False, (time.perf_counter() - started) * 1000, str(exc))

    def verify_supabase_vault(self) -> None:
        started = time.perf_counter()
        try:
            client = SupabaseVaultClient()
            count = client.count_total_keys()
            value = client.get_key("ANTHROPIC_API_KEY")
            passed = count > 0 and isinstance(value, str) and bool(value.strip())
            self.add("Cloud Key Vault", "Supabase PostgreSQL Vault", passed, (time.perf_counter() - started) * 1000, f"{count} keys indexed; credential lookup validated")
        except Exception as exc:
            self.add("Cloud Key Vault", "Supabase PostgreSQL Vault", False, (time.perf_counter() - started) * 1000, str(exc))

    def verify_quantum_logic(self) -> None:
        started = time.perf_counter()
        try:
            sys.path.insert(0, "/root/src")
            from apex_quantum_logic_compiler import QuantumLogicCompiler
            certificate = QuantumLogicCompiler().emit_proof_certificate()
            theorems = len(certificate.get("theorems_compiled", [])) if isinstance(certificate, dict) else 0
            nodes = certificate.get("tensor_vector_clusters", {}).get("total_tensor_nodes", 0) if isinstance(certificate, dict) else 0
            passed = isinstance(certificate, dict) and theorems > 0
            self.add("Quantum ML & Logic", "First-Order Logic Proof Compiler", passed, (time.perf_counter() - started) * 1000, f"{theorems} theorems | {nodes} vector nodes")
        except Exception as exc:
            self.add("Quantum ML & Logic", "First-Order Logic Proof Compiler", False, (time.perf_counter() - started) * 1000, str(exc))

    def run_all_verifications(self) -> Dict[str, Any]:
        self.verify_all_services()
        self.verify_device_rpc_apis()
        self.verify_supabase_vault()
        self.verify_quantum_logic()
        passed = sum(1 for result in self.results if result.status == "PASSED")
        total = len(self.results)
        return {
            "schema": "apex.runtime-verification/v1",
            "summary": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "total_tests": total,
                "passed_tests": passed,
                "failed_tests": total - passed,
                "success_rate_percent": round(passed * 100 / total, 1) if total else 0.0,
                "total_duration_ms": round((time.perf_counter() - self.start_time) * 1000, 2),
            },
            "results": [asdict(result) for result in self.results],
        }


def main() -> int:
    print("=" * 76)
    print("FORWARD DEPLOYED AGENTIC AI: END-TO-END VERIFICATION")
    print("=" * 76)
    report = SovereignVerificationSuite().run_all_verifications()
    for result in report["results"]:
        badge = "PASS" if result["status"] == "PASSED" else "FAIL"
        print(f"{badge} | [{result['layer']:<20}] {result['target']:<34} ({result['latency_ms']} ms)")
        print(f"       - {result['details']}")
    summary = report["summary"]
    print("=" * 80)
    print(f"SUMMARY: {summary['passed_tests']}/{summary['total_tests']} tests passed ({summary['success_rate_percent']}%)")
    report_path = Path("/root/.apex/verification_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = report_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, report_path)
    print(f"REPORT: {report_path}")
    return 0 if summary["failed_tests"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
