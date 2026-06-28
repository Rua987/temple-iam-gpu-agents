"""
Test temps reel borne du pipeline Temple IAM (lecture seule).

Lance le vrai pipeline detection -> profil -> monitoring -> ML logging
pendant N secondes sur la machine reelle, puis ecrit un rapport JSON.

Aucun controle GPU : pas de clocks, pas d'undervolt, pas de power limit.
(gpu_real_controller n'est volontairement PAS importe : son init teste -lgc)

Usage : python test_realtime_monitoring.py [duree_secondes]
"""

import io
import json
import logging
import sys
import time
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Les modules loggent avec emojis ; on coupe le bruit pour un terminal propre
logging.disable(logging.INFO)

from universal_game_detector import UniversalGameDetector
from universal_gpu_monitor import UniversalGPUMonitor
from thermal_ml_predictor import ThermalMLPredictor

REPORT_PATH = "realtime_test_results.json"


def main(duration: int = 60):
    detector = UniversalGameDetector(auto_learn=False)
    monitor = UniversalGPUMonitor(monitor_interval=1.0, max_history=duration + 10)
    monitor.game_detector = detector  # auto_learn off pour ne pas polluer learned_games.json
    monitor.start_time = datetime.now()
    predictor = ThermalMLPredictor()

    if not monitor.gpu_available:
        print("[ERREUR] GPU non disponible via GPUtil - test annule")
        return 1

    print(f"[REALTIME] GPU: {monitor.gpu_name}")
    print(f"[REALTIME] Session {duration}s - monitoring lecture seule, 1 Hz")
    print(f"{'t(s)':>4} | {'workload':<20} | {'categorie':<15} | {'mode':<15} | {'GPU%':>5} | {'temp':>5} | {'VRAM%':>6} | {'tend.':<8}")
    print("-" * 100)

    samples = []
    for t in range(duration):
        tick_start = time.time()

        detector.detect_running_games()
        primary = detector.get_primary_game()
        monitor._update_current_game(primary)
        data = monitor._collect_monitoring_data(primary, detector.detected_games)

        profile = monitor.current_game_profile or {}
        category = profile.get('category', '-')
        mode = profile.get('optimization_mode', '-')
        name = primary.custom_name if primary else '(aucun)'

        # Pipeline ML reel : logging + apprentissage thermique
        if primary and monitor.ml_session_active:
            monitor.ml_logger.log_datapoint({
                'gpu_temperature': data.get('gpu_temperature', 0),
                'gpu_usage': data.get('gpu_usage', 0),
                'gpu_memory_percent': data.get('gpu_memory_percent', 0),
                'cpu_usage': data.get('cpu_usage', 0),
                'memory_usage': data.get('memory_usage', 0),
                'fps_estimate': data.get('fps_estimate', 0)
            })
            monitor.ml_logger.detect_spike(data.get('gpu_usage', 0))
            predictor.set_current_game(primary.custom_name)
            predictor.add_data_point(
                temp=data.get('gpu_temperature', 0),
                gpu_usage=data.get('gpu_usage', 0),
                clock_speed=0,
                power_draw=data.get('gpu_power_usage', 0)
            )

        trend = monitor.ml_logger.get_thermal_trend() if monitor.ml_session_active else '-'

        samples.append({
            't': t,
            'workload': name,
            'category': category,
            'mode': mode,
            'gpu_usage': data.get('gpu_usage', 0),
            'gpu_temperature': data.get('gpu_temperature', 0),
            'gpu_memory_percent': round(data.get('gpu_memory_percent', 0), 1),
            'target_temp': profile.get('target_temp'),
            'trend': trend,
        })

        print(f"{t:>4} | {name[:20]:<20} | {category:<15} | {mode:<15} | "
              f"{data.get('gpu_usage', 0):>5.1f} | {data.get('gpu_temperature', 0):>5.1f} | "
              f"{data.get('gpu_memory_percent', 0):>6.1f} | {trend:<8}")

        elapsed = time.time() - tick_start
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

    # Fin de session ML + prediction thermique
    prediction = predictor.predict()
    if monitor.ml_session_active:
        session_stats = monitor.ml_logger.get_session_stats()
        monitor.ml_logger.end_session()
    else:
        session_stats = {}

    active = [s for s in samples if s['category'] != '-']
    summary = {
        'timestamp': datetime.now().isoformat(),
        'gpu_name': monitor.gpu_name,
        'duration_s': duration,
        'samples_collected': len(samples),
        'samples_with_workload': len(active),
        'workloads_seen': sorted({(s['workload'], s['category'], s['mode']) for s in active}),
        'gpu_usage_min': min(s['gpu_usage'] for s in samples),
        'gpu_usage_max': max(s['gpu_usage'] for s in samples),
        'gpu_temp_min': min(s['gpu_temperature'] for s in samples),
        'gpu_temp_max': max(s['gpu_temperature'] for s in samples),
        'vram_percent_max': max(s['gpu_memory_percent'] for s in samples),
        'ml_session_stats': {k: round(v, 2) if isinstance(v, float) else v
                             for k, v in session_stats.items()},
        'thermal_prediction': {
            'current_temp': prediction.current_temp,
            'predicted_temp_30s': round(prediction.predicted_temp_30s, 1),
            'trend': prediction.trend,
            'spike_probability': round(prediction.spike_probability, 2),
            'recommended_action': prediction.recommended_action,
            'confidence': round(prediction.confidence, 2),
        },
    }

    # tuples -> listes pour JSON
    summary['workloads_seen'] = [list(w) for w in summary['workloads_seen']]

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump({'summary': summary, 'samples': samples}, f, indent=2, ensure_ascii=False)

    print("-" * 100)
    print(f"[RESUME] Workloads detectes : {summary['workloads_seen']}")
    print(f"[RESUME] GPU usage  : {summary['gpu_usage_min']:.0f}% -> {summary['gpu_usage_max']:.0f}%")
    print(f"[RESUME] GPU temp   : {summary['gpu_temp_min']:.0f}C -> {summary['gpu_temp_max']:.0f}C")
    print(f"[RESUME] VRAM max   : {summary['vram_percent_max']:.1f}%")
    print(f"[RESUME] Prediction : {summary['thermal_prediction']['trend']} | +30s = "
          f"{summary['thermal_prediction']['predicted_temp_30s']}C | action = "
          f"{summary['thermal_prediction']['recommended_action']}")
    print(f"[RESUME] Rapport ecrit : {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    sys.exit(main(duration))
