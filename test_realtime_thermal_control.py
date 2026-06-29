"""
Test temps reel du CONTROLE GPU (clocks) - necessite un Go explicite + admin.

Sequence :
  Phase A - boucle auto_adjust_for_temperature(profil local_ai) sous charge reelle
  Phase B - preuve de controle : cap force des clocks, effet mesure
  Phase C - reset garanti (finally) + verification retour a la normale

Reversible : nvidia-smi -rgc remet les clocks par defaut.
Le power limit est sauvegarde avant init et restaure si l'init l'a modifie.

Usage : python test_realtime_thermal_control.py
"""

import io
import json
import logging
import subprocess
import sys
import time
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.disable(logging.INFO)

REPORT_PATH = "realtime_control_results.json"


def smi_query(fields: str) -> str:
    result = subprocess.run(
        ['nvidia-smi', f'--query-gpu={fields}', '--format=csv,noheader,nounits'],
        capture_output=True, text=True, timeout=5
    )
    return result.stdout.strip()


def read_power_limit() -> float:
    try:
        return float(smi_query('power.limit'))
    except (ValueError, subprocess.SubprocessError):
        return -1.0


def main():
    # Sauvegarde du power limit AVANT init du controleur
    # (son _detect_capabilities teste '-pl 100' sans restaurer)
    power_limit_before = read_power_limit()
    print(f"[SETUP] Power limit actuel : {power_limit_before} W")

    from gpu_real_controller import GPURealController

    controller = GPURealController()
    print(f"[SETUP] Capacites detectees : {controller.capabilities.value}")

    power_limit_after_init = read_power_limit()
    if power_limit_before > 0 and abs(power_limit_after_init - power_limit_before) > 1:
        print(f"[SETUP] Power limit modifie par l'init ({power_limit_after_init} W) - restauration...")
        subprocess.run(['nvidia-smi', '-pl', str(int(power_limit_before))],
                       capture_output=True, text=True, timeout=5)
        print(f"[SETUP] Power limit restaure : {read_power_limit()} W")

    if controller.capabilities.value == 'readonly':
        print("[ERREUR] Controle clocks non supporte/pas de droits - test annule")
        return 1

    report = {
        'timestamp': datetime.now().isoformat(),
        'capabilities': controller.capabilities.value,
        'phase_a': [], 'phase_b': [], 'phase_c': {},
        'actions': [],
    }

    try:
        # ---- Phase A : boucle d'ajustement automatique (profil local_ai), 40 s
        print("\n[PHASE A] auto_adjust_for_temperature(local_ai) - 20 ticks x 2s")
        print(f"{'t':>3} | {'temp':>4} | {'clock':>6} | {'profil appliquee':<14} | action")
        for t in range(20):
            metrics = controller.get_gpu_metrics()
            temp = metrics.get('temperature', 0)
            clock = metrics.get('clock_current', 0)
            before = controller.current_profile
            applied = controller.auto_adjust_for_temperature(temp, thermal_profile='local_ai')
            action = f"{before} -> {applied}" if applied != before else "-"
            if applied != before:
                report['actions'].append({'phase': 'A', 't': t, 'temp': temp, 'action': action})
            report['phase_a'].append({'t': t, 'temp': temp, 'clock': clock, 'profile': applied})
            print(f"{t:>3} | {temp:>4} | {clock:>6} | {str(applied):<14} | {action}")
            time.sleep(2)

        # ---- Phase B : preuve de controle reel - cap force a 1000 MHz, 16 s
        print("\n[PHASE B] Cap force 300-1000 MHz (profil 'emergency') - effet mesure")
        ok = controller.apply_profile('emergency')
        print(f"[PHASE B] apply_profile('emergency') = {ok}")
        for t in range(8):
            metrics = controller.get_gpu_metrics()
            sample = {
                't': t,
                'temp': metrics.get('temperature', 0),
                'clock': metrics.get('clock_current', 0),
                'power': metrics.get('power_draw', 0),
            }
            report['phase_b'].append(sample)
            print(f"{t:>3} | temp {sample['temp']:>3}C | clock {sample['clock']:>5} MHz | {sample['power']:>6.1f} W")
            time.sleep(2)

    finally:
        # ---- Phase C : reset TOUJOURS execute
        print("\n[PHASE C] Reset des clocks (nvidia-smi -rgc)")
        reset_ok = controller.reset_gpu_clocks()
        time.sleep(3)
        metrics = controller.get_gpu_metrics()
        report['phase_c'] = {
            'reset_ok': reset_ok,
            'temp': metrics.get('temperature', 0),
            'clock': metrics.get('clock_current', 0),
            'clock_locked': controller.is_clock_locked,
            'power_limit_final': read_power_limit(),
        }
        print(f"[PHASE C] reset_ok={reset_ok} | temp={report['phase_c']['temp']}C | "
              f"clock={report['phase_c']['clock']} MHz | power_limit={report['phase_c']['power_limit_final']} W")

        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[RESUME] Actions d'ajustement : {len(report['actions'])}")
        print(f"[RESUME] Rapport ecrit : {REPORT_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
