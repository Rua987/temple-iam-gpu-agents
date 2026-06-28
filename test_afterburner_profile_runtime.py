"""Test borne des profils MSI Afterburner sous charge Ollama.

Objectif : verifier le cablage profile1/profile2 et mesurer clocks/temp/power.
Le test finit toujours par remettre le profil 1 (stock/secours).
"""

import csv
import json
import subprocess
import threading
import time
import urllib.request
from datetime import datetime
from pathlib import Path


AFTERBURNER = Path(r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe")
REPORT_PATH = Path("afterburner_profile_runtime_results.json")
OLLAMA_OUTPUT = Path("afterburner_runtime_ollama_output.txt")


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
    if not samples:
        return {}
    active = [s for s in samples if s["util_percent"] >= 40]
    src = active or samples
    return {
        "samples": len(samples),
        "active_samples": len(active),
        "clock_avg": round(sum(s["clock_mhz"] for s in src) / len(src), 1),
        "clock_max": max(s["clock_mhz"] for s in src),
        "temp_min": min(s["temp_c"] for s in src),
        "temp_max": max(s["temp_c"] for s in src),
        "power_avg": round(sum(s["power_w"] for s in src) / len(src), 2),
        "util_avg": round(sum(s["util_percent"] for s in src) / len(src), 1),
        "memory_max_mb": max(s["memory_mb"] for s in src),
    }


def collect_phase(name, profile_slot, seconds, proc):
    ok = apply_profile(profile_slot)
    print(f"[PHASE] {name}: profile{profile_slot} applique={ok}")
    samples = []
    for t in range(seconds):
        sample = gpu_sample()
        sample["t"] = t
        sample["phase"] = name
        sample["ollama_running"] = proc.is_alive()
        samples.append(sample)
        print(
            f"{name:10s} t={t:02d}s | "
            f"gpu={sample['util_percent']:5.1f}% | "
            f"clock={sample['clock_mhz']:5.0f} MHz | "
            f"temp={sample['temp_c']:4.0f}C | "
            f"power={sample['power_w']:6.1f} W | "
            f"vram={sample['memory_mb']:5.0f} MB"
        )
        time.sleep(1)
    return samples


def main():
    if not AFTERBURNER.exists():
        print("[ERREUR] MSI Afterburner introuvable")
        return 1

    prompt = (
        "Ecris une tres longue histoire technique et detaillee en francais, "
        "au moins 5000 mots, sur une expedition spatiale. Ajoute beaucoup "
        "de descriptions, de dialogues et de details scientifiques."
    )

    report = {
        "timestamp": datetime.now().isoformat(),
        "model": "qwen3.5:2b",
        "phases": {},
        "samples": [],
    }

    stop_event = threading.Event()

    def ollama_generate():
        payload = json.dumps({
            "model": "qwen3.5:2b",
            "prompt": prompt,
            "stream": True,
            "options": {"num_predict": 4096},
        }).encode("utf-8")

        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with OLLAMA_OUTPUT.open("w", encoding="utf-8", errors="replace") as out:
            try:
                with urllib.request.urlopen(req, timeout=120) as response:
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

    proc = threading.Thread(target=ollama_generate, daemon=True)
    proc.start()

    try:
        time.sleep(8)  # laisser le modele entrer en generation
        report["samples"].extend(collect_phase("stock", 1, 25, proc))
        report["samples"].extend(collect_phase("undervolt", 2, 25, proc))
    finally:
        apply_profile(1)
        stop_event.set()
        proc.join(timeout=5)

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
