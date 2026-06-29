"""Diagnostic READ-ONLY pour testeurs.

Affiche l'environnement (OS, Python, GPU, driver, capacites de controle, outils
detectes) et ecrit un rapport `diagnostic_report.txt`. Ne MODIFIE rien: aucune
action GPU, aucun cap, aucun lancement d'outil. A faire tourner et a renvoyer
au mainteneur pour anticiper les problemes par hardware.

Usage:  python diagnostic.py
"""

import os
import sys
import platform
import shutil
import subprocess
from datetime import datetime


def _line(label, value):
    return f"{label:<28} {value}"


def _nvidia_smi_query():
    """Interroge nvidia-smi directement (sans dependance), retourne un dict."""
    exe = shutil.which("nvidia-smi") or "nvidia-smi"
    fields = "name,driver_version,memory.total,temperature.gpu,utilization.gpu,power.draw,clocks.gr,clocks.max.gr"
    try:
        out = subprocess.run(
            [exe, f"--query-gpu={fields}", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=8,
        )
        if out.returncode != 0:
            return {"error": (out.stderr or out.stdout).strip() or "nvidia-smi a echoue"}
        rows = [r.strip() for r in out.stdout.strip().splitlines() if r.strip()]
        gpus = []
        for r in rows:
            p = [x.strip() for x in r.split(",")]
            gpus.append(dict(zip(
                ["name", "driver", "vram", "temp", "util", "power", "clock", "clock_max"], p)))
        return {"gpus": gpus}
    except FileNotFoundError:
        return {"error": "nvidia-smi introuvable (driver NVIDIA installe ?)"}
    except Exception as e:
        return {"error": str(e)}


def _control_capability():
    """Capacite de controle via le controleur de l'agent (sans rien actuer)."""
    try:
        from gpu_real_controller import GPURealController
        c = GPURealController(dry_run=True)  # dry_run par securite
        return str(getattr(c.capabilities, "value", c.capabilities))
    except Exception as e:
        return f"indeterminee ({e})"


def _tool(label, available, detail=""):
    mark = "OK" if available else "absent"
    return _line(label, f"[{mark}] {detail}".rstrip())


def collect_report() -> str:
    lines = []
    lines.append("=" * 64)
    lines.append("  DIAGNOSTIC GPU AGENT (read-only)")
    lines.append("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("=" * 64)

    # --- Systeme ---
    lines.append("\n[ SYSTEME ]")
    lines.append(_line("OS", f"{platform.system()} {platform.release()} ({platform.version()})"))
    lines.append(_line("Python", sys.version.split()[0] + f" ({sys.executable})"))
    lines.append(_line("Machine", platform.machine()))

    # --- GPU via nvidia-smi ---
    lines.append("\n[ GPU (nvidia-smi) ]")
    smi = _nvidia_smi_query()
    if "error" in smi:
        lines.append(_line("Statut", f"ERREUR: {smi['error']}"))
    else:
        for i, g in enumerate(smi["gpus"]):
            lines.append(_line(f"GPU {i}", g.get("name", "?")))
            lines.append(_line("  Driver", g.get("driver", "?")))
            lines.append(_line("  VRAM", g.get("vram", "?")))
            lines.append(_line("  Temp / Util", f"{g.get('temp','?')} / {g.get('util','?')}"))
            lines.append(_line("  Power / Clock", f"{g.get('power','?')} / {g.get('clock','?')} (max {g.get('clock_max','?')})"))

    # --- Capacite de controle ---
    lines.append("\n[ CONTROLE GPU ]")
    cap = _control_capability()
    lines.append(_line("Capacite", cap))
    lines.append(_line("Note", "READ_ONLY = pas de cap possible ; CLOCK_ONLY = caps clocks ; FULL = + power"))

    # --- Outils detectes ---
    lines.append("\n[ OUTILS DETECTES ]")
    # RTSS (vrais FPS)
    try:
        from rtss_reader import RTSSReader
        rtss = RTSSReader()
        lines.append(_tool("RTSS (vrais FPS)", rtss.available,
                           "MSI Afterburner/RTSS lance" if rtss.available else "lancer RTSS pour les FPS reels"))
    except Exception as e:
        lines.append(_tool("RTSS (vrais FPS)", False, str(e)))
    # Upscaler externe
    try:
        from external_upscaler import ExternalUpscaler
        up = ExternalUpscaler()
        lines.append(_tool("Upscaler (Magpie/LS)", up.available, up.name if up.available else "aucun (gaming uniquement)"))
    except Exception as e:
        lines.append(_tool("Upscaler (Magpie/LS)", False, str(e)))
    # Afterburner
    ab = r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe"
    lines.append(_tool("MSI Afterburner", os.path.isfile(ab), ab if os.path.isfile(ab) else "optionnel"))
    # Ollama (workload IA)
    lines.append(_tool("Ollama (workload IA)", shutil.which("ollama") is not None,
                       "detecte" if shutil.which("ollama") else "optionnel"))

    lines.append("\n" + "=" * 64)
    lines.append("  Aucune action GPU n'a ete effectuee (diagnostic read-only).")
    lines.append("  Renvoyez diagnostic_report.txt au mainteneur.")
    lines.append("=" * 64)
    return "\n".join(lines)


def main():
    report = collect_report()
    print(report)
    try:
        with open("diagnostic_report.txt", "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print("\n-> Rapport ecrit dans diagnostic_report.txt")
    except Exception as e:
        print(f"\n(!) Impossible d'ecrire le rapport: {e}")


if __name__ == "__main__":
    main()
