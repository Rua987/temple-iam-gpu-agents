"""Benchmark CUDA borne pour valider les profils MSI Afterburner.

Compare profile1 (stock/secours) et profile2 (undervolt) avec une charge
matmul PyTorch qui force les coeurs GPU, contrairement a Ollama qui etait
memory-bound. Retour profile1 garanti en finally.
"""

import csv
import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

import torch


AFTERBURNER = Path(r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe")
REPORT_PATH = Path("afterburner_torch_benchmark_results.json")


def run(cmd, timeout=10):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


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
        "tflops_avg": round(sum(s["tflops"] for s in active) / len(active), 2),
    }


def burn_for(seconds: int, stop_event: threading.Event, perf_state: dict):
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

    # 4096x4096 FP16 charge les Tensor Cores et pousse le boost GPU sans
    # remplir la VRAM comme un gros modele LLM.
    size = 4096
    a = torch.randn((size, size), device="cuda", dtype=torch.float16)
    b = torch.randn((size, size), device="cuda", dtype=torch.float16)
    c = torch.empty((size, size), device="cuda", dtype=torch.float16)

    torch.cuda.synchronize()
    end = time.time() + seconds
    ops_per_matmul = 2 * size * size * size
    iters = 0
    last = time.time()
    last_iters = 0

    while time.time() < end and not stop_event.is_set():
        torch.matmul(a, b, out=c)
        iters += 1
        now = time.time()
        if now - last >= 1.0:
            torch.cuda.synchronize()
            done = iters - last_iters
            perf_state["tflops"] = (done * ops_per_matmul) / ((now - last) * 1e12)
            last = now
            last_iters = iters

    torch.cuda.synchronize()


def run_phase(name: str, slot: int, seconds: int):
    ok = apply_profile(slot)
    print(f"[PHASE] {name}: profile{slot} applique={ok}")

    stop_event = threading.Event()
    perf_state = {"tflops": 0.0}
    worker = threading.Thread(target=burn_for, args=(seconds, stop_event, perf_state), daemon=True)
    worker.start()

    samples = []
    try:
        for t in range(seconds):
            sample = gpu_sample()
            sample["phase"] = name
            sample["t"] = t
            sample["tflops"] = float(perf_state.get("tflops", 0.0))
            samples.append(sample)
            print(
                f"{name:10s} t={t:02d}s | "
                f"gpu={sample['util_percent']:5.1f}% | "
                f"clock={sample['clock_mhz']:5.0f} MHz | "
                f"temp={sample['temp_c']:4.0f}C | "
                f"power={sample['power_w']:6.1f} W | "
                f"perf={sample['tflops']:5.1f} TFLOP/s"
            )
            if sample["temp_c"] >= 88:
                print("[SECURITE] Temperature >= 88C, arret de la phase")
                break
            time.sleep(1)
    finally:
        stop_event.set()
        worker.join(timeout=5)
        torch.cuda.empty_cache()

    return samples


def main():
    if not torch.cuda.is_available():
        print("[ERREUR] CUDA indisponible")
        return 1

    report = {
        "timestamp": datetime.now().isoformat(),
        "device": torch.cuda.get_device_name(0),
        "samples": [],
        "phases": {},
    }

    try:
        report["samples"].extend(run_phase("stock", 1, 35))
        time.sleep(8)
        report["samples"].extend(run_phase("undervolt", 2, 35))
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
