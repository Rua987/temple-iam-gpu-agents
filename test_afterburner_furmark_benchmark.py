"""Benchmark FurMark 2 pour comparer profile1/profile2 MSI Afterburner.

Source attendue : FurMark2 ZIP officiel extrait dans %TEMP%\\FurMark2.
Le script lance un vrai rendu OpenGL sur RTX (option --hpgfx 1), mesure via
nvidia-smi, coupe a 88C, puis remet toujours le profil 1.
"""

import csv
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path


AFTERBURNER = Path(r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe")
FURMARK = Path(os.environ["TEMP"]) / "FurMark2" / "FurMark_win64" / "furmark.exe"
REPORT_PATH = Path("afterburner_furmark_benchmark_results.json")


def run(cmd, timeout=10, cwd=None):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)


def apply_profile(slot: int) -> bool:
    result = run([str(AFTERBURNER), f"-profile{slot}"], timeout=10)
    time.sleep(4)
    return result.returncode == 0


def gpu_sample():
    fields = "clocks.gr,clocks.mem,temperature.gpu,utilization.gpu,power.draw,memory.used"
    result = run(["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits"], timeout=5)
    row = next(csv.reader([result.stdout.strip()]))
    return {
        "clock_mhz": float(row[0].strip()),
        "mem_clock_mhz": float(row[1].strip()),
        "temp_c": float(row[2].strip()),
        "util_percent": float(row[3].strip()),
        "power_w": float(row[4].strip()),
        "memory_mb": float(row[5].strip()),
    }


def summarize(samples):
    active = [s for s in samples if s["util_percent"] >= 60] or samples
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


def run_phase(name: str, slot: int, seconds: int):
    ok = apply_profile(slot)
    print(f"[PHASE] {name}: profile{slot} applique={ok}")

    cmd = [
        str(FURMARK),
        "--hpgfx", "1",
        "--demo", "furmark-gl",
        "--width", "1920",
        "--height", "1080",
        "--max-time", str(seconds),
        "--vsync", "0",
        "--no-score-box",
        "--disable-logfile",
        "--disable-traces",
    ]

    proc = subprocess.Popen(
        cmd,
        cwd=str(FURMARK.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    samples = []
    try:
        for t in range(seconds + 5):
            sample = gpu_sample()
            sample["phase"] = name
            sample["t"] = t
            sample["furmark_running"] = proc.poll() is None
            samples.append(sample)
            print(
                f"{name:10s} t={t:02d}s | "
                f"gpu={sample['util_percent']:5.1f}% | "
                f"clock={sample['clock_mhz']:5.0f} MHz | "
                f"temp={sample['temp_c']:4.0f}C | "
                f"power={sample['power_w']:6.1f} W | "
                f"vram={sample['memory_mb']:5.0f} MB"
            )
            if sample["temp_c"] >= 88:
                print("[SECURITE] Temperature >= 88C, arret FurMark")
                proc.terminate()
                break
            if proc.poll() is not None:
                break
            time.sleep(1)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()

    output = ""
    if proc.stdout:
        try:
            output = proc.stdout.read()[-2000:]
        except Exception:
            output = ""
    return samples, output


def main():
    if not FURMARK.exists():
        print(f"[ERREUR] FurMark introuvable: {FURMARK}")
        return 1

    report = {
        "timestamp": datetime.now().isoformat(),
        "furmark": str(FURMARK),
        "samples": [],
        "phases": {},
        "furmark_output": {},
    }

    try:
        stock_samples, stock_out = run_phase("stock", 1, 30)
        report["samples"].extend(stock_samples)
        report["furmark_output"]["stock"] = stock_out
        time.sleep(12)
        undervolt_samples, undervolt_out = run_phase("undervolt", 2, 30)
        report["samples"].extend(undervolt_samples)
        report["furmark_output"]["undervolt"] = undervolt_out
    finally:
        apply_profile(1)

    for phase in ("stock", "undervolt"):
        phase_samples = [s for s in report["samples"] if s["phase"] == phase]
        report["phases"][phase] = summarize(phase_samples)

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("[RESUME]")
    for phase, summary in report["phases"].items():
        print(f"{phase}: {summary}")
    print(f"[RAPPORT] {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
