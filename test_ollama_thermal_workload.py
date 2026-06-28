"""Mesure le workload Ollama derriere le pipeline agent (detection + thermal).

Lance une generation longue sur Qwen 3.5 abliterated, puis echantillonne
nvidia-smi + mode thermique applique par WorkloadThermalController.
Reset garanti en finally.
"""

from __future__ import annotations

import csv
import json
import logging
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime
from pathlib import Path

logging.disable(logging.INFO)

from universal_game_detector import UniversalGameDetector
from workload_thermal_controller import WorkloadThermalController

MODEL = "dolphin3:latest"
REPORT_PATH = Path("ollama_thermal_workload_results.json")
OUTPUT_PATH = Path("ollama_thermal_workload_output.txt")
DURATION_S = 75
WARMUP_S = 15


def gpu_sample() -> dict:
    fields = "clocks.gr,clocks.mem,temperature.gpu,utilization.gpu,power.draw,memory.used"
    result = subprocess.run(
        ["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    row = next(csv.reader([result.stdout.strip()]))
    return {
        "clock_mhz": float(row[0].strip()),
        "mem_clock_mhz": float(row[1].strip()),
        "temp_c": float(row[2].strip()),
        "util_percent": float(row[3].strip()),
        "power_w": float(row[4].strip()),
        "memory_mb": float(row[5].strip()),
    }


def summarize(samples: list[dict]) -> dict:
    if not samples:
        return {}
    active = [s for s in samples if s.get("util_percent", 0) >= 20] or samples
    return {
        "samples": len(samples),
        "active_samples": len(active),
        "clock_avg": round(sum(s["clock_mhz"] for s in active) / len(active), 1),
        "clock_max": max(s["clock_mhz"] for s in active),
        "temp_min": min(s["temp_c"] for s in active),
        "temp_max": max(s["temp_c"] for s in active),
        "power_avg": round(sum(s["power_w"] for s in active) / len(active), 2),
        "util_avg": round(sum(s["util_percent"] for s in active) / len(active), 1),
        "memory_max_mb": max(s["memory_mb"] for s in active),
    }


def start_ollama_generation(stop_event: threading.Event) -> threading.Thread:
    prompt = (
        "Tu es un ingenieur systeme. Ecris un rapport technique tres detaille en francais "
        "(au moins 3000 mots) comparant 5 architectures LLM pour inference locale sur GPU 8 Go. "
        "Pour chaque architecture, donne: VRAM, debit tokens/s, latence TTFT, compromis qualite, "
        "et recommandations d'undervolt thermique laptop. Ajoute des sections, tableaux textuels, "
        "et une conclusion argumentee."
    )
    payload = json.dumps(
        {
            "model": MODEL,
            "prompt": prompt,
            "stream": True,
            "options": {"num_predict": 4096, "temperature": 0.7},
        }
    ).encode("utf-8")

    def worker():
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with OUTPUT_PATH.open("w", encoding="utf-8", errors="replace") as out:
            try:
                with urllib.request.urlopen(req, timeout=300) as response:
                    for raw_line in response:
                        if stop_event.is_set():
                            break
                        try:
                            chunk = json.loads(raw_line.decode("utf-8"))
                            out.write(chunk.get("response", ""))
                            out.flush()
                        except json.JSONDecodeError:
                            continue
            except Exception as exc:
                out.write(f"\n[ERREUR OLLAMA] {exc}\n")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return thread


def main() -> int:
    global MODEL, WARMUP_S
    if len(sys.argv) > 1:
        MODEL = sys.argv[1]
    if len(sys.argv) > 2:
        WARMUP_S = int(sys.argv[2])
    detector = UniversalGameDetector(auto_learn=False)
    thermal = WorkloadThermalController()
    stop_event = threading.Event()

    report = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "duration_s": DURATION_S,
        "warmup_s": WARMUP_S,
        "samples": [],
    }

    print(f"[SETUP] Modele: {MODEL}")
    print(f"[SETUP] Warmup {WARMUP_S}s puis mesure {DURATION_S}s")
    print(f"{'t':>3} | {'workload':<12} | {'thermal':<14} | {'ai':<12} | {'GPU%':>5} | {'clock':>6} | {'temp':>4} | {'power':>6} | {'vram':>5}")
    print("-" * 95)

    thread = start_ollama_generation(stop_event)

    try:
        for t in range(WARMUP_S + DURATION_S):
            detector.detect_running_games()
            primary = detector.get_primary_game()
            profile = detector.get_game_optimization_profile(primary) if primary else None
            target_mode = thermal.resolve_mode(profile)
            thermal.apply_for_workload(profile)

            sample = gpu_sample()
            ai_profile = thermal.adjust_for_temperature(sample["temp_c"], profile)
            sample.update(
                {
                    "t": t,
                    "workload": primary.custom_name if primary else "(aucun)",
                    "category": profile.get("category", "-") if profile else "-",
                    "optimization_mode": profile.get("optimization_mode", "-") if profile else "-",
                    "thermal_mode": thermal.current_mode or target_mode,
                    "ai_profile": ai_profile or "none",
                    "afterburner_profile": thermal.afterburner.current_profile,
                    "clock_locked": thermal.gpu_controller.is_clock_locked,
                    "ollama_running": thread.is_alive(),
                }
            )
            report["samples"].append(sample)

            print(
                f"{t:>3} | {sample['workload'][:12]:<12} | {sample['thermal_mode']:<14} | "
                f"{str(sample.get('ai_profile', '-')):<12} | "
                f"{sample['util_percent']:5.1f} | {sample['clock_mhz']:6.0f} | "
                f"{sample['temp_c']:4.0f} | {sample['power_w']:6.1f} | {sample['memory_mb']:5.0f}"
            )
            time.sleep(1)
    finally:
        stop_event.set()
        thread.join(timeout=5)
        thermal.release()

    active = [s for s in report["samples"] if s["t"] >= WARMUP_S]
    report["summary"] = summarize(active)
    report["summary"]["thermal_mode_seen"] = sorted({s["thermal_mode"] for s in active})
    report["summary"]["ai_profiles_seen"] = sorted(
        {s.get("ai_profile") for s in active if s.get("ai_profile") and s.get("ai_profile") != "none"}
    )
    report["summary"]["workload_detected"] = any(s["workload"] == "Ollama" for s in active)

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("-" * 95)
    print(f"[RESUME] {report['summary']}")
    print(f"[RAPPORT] {REPORT_PATH}")
    print(f"[SORTIE] {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
