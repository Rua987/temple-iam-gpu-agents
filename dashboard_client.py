"""
📊 DASHBOARD CLIENT - ENVOI DE DONNÉES AU DASHBOARD BUN.JS ! 🔥
Objectif : Envoyer les métriques temps réel au serveur web

UTILISATION :
Ce module est importé par temple_iam_thermal_optimizer.py
Il envoie les données toutes les secondes au serveur Bun.js

PLUS ULTRA ! DATTEBAYO ! 🚀⚡
"""

import json
import time
import threading
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Try to import requests, fallback to urllib if not available
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False

logging.basicConfig(level=logging.INFO, format='📊 %(asctime)s - %(levelname)s - %(message)s')


class DashboardClient:
    """
    Client pour envoyer les données au Dashboard Bun.js
    """

    def __init__(self, server_url: str = "http://localhost:3000"):
        self.server_url = server_url
        self.api_endpoint = f"{server_url}/api/update"
        self.is_connected = False
        self.send_interval = 1.0  # Envoyer toutes les secondes
        self.last_send_time = 0
        self.send_queue = []
        self.is_enabled = True

        # Thread pour envoi async
        self.send_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        logging.info(f"📊 Dashboard Client initialisé")
        logging.info(f"   URL: {self.server_url}")
        logging.info(f"   Requests disponible: {HAS_REQUESTS}")

    def start(self):
        """Démarre le client en mode async"""
        self.stop_event.clear()
        self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self.send_thread.start()
        logging.info("📊 Dashboard Client démarré")

    def stop(self):
        """Arrête le client"""
        self.stop_event.set()
        if self.send_thread:
            self.send_thread.join(timeout=2)
        logging.info("📊 Dashboard Client arrêté")

    def send_data(self, data: Dict[str, Any]):
        """Ajoute des données à la queue d'envoi"""
        if not self.is_enabled:
            return

        # Ajouter le timestamp si absent
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()

        self.send_queue.append(data)

        # Limiter la taille de la queue
        if len(self.send_queue) > 10:
            self.send_queue.pop(0)

    def _send_loop(self):
        """Boucle d'envoi des données"""
        while not self.stop_event.is_set():
            try:
                if self.send_queue:
                    data = self.send_queue.pop(0)
                    success = self._send_to_server(data)
                    self.is_connected = success
                else:
                    time.sleep(0.1)

            except Exception as e:
                logging.debug(f"Erreur envoi dashboard: {e}")
                time.sleep(1)

    def _send_to_server(self, data: Dict[str, Any]) -> bool:
        """Envoie les données au serveur"""
        try:
            json_data = json.dumps(data, default=str)

            if HAS_REQUESTS:
                response = requests.post(
                    self.api_endpoint,
                    data=json_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=2
                )
                return response.status_code == 200
            else:
                # Fallback avec urllib
                req = urllib.request.Request(
                    self.api_endpoint,
                    data=json_data.encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=2) as response:
                    return response.status == 200

        except Exception as e:
            # Ne pas spammer les logs si le serveur n'est pas démarré
            if self.is_connected:
                logging.warning(f"⚠️ Dashboard déconnecté: {e}")
            return False

    def format_optimizer_data(self, thermal_data: Dict[str, Any],
                               fps_data: Any = None,
                               ml_prediction: Any = None,
                               sweet_spot: Any = None,
                               advanced_stats: Dict[str, Any] = None,
                               optimizations: list = None,
                               performance_score: Any = None) -> Dict[str, Any]:
        """
        Formate les données de l'optimiseur pour le dashboard

        Args:
            thermal_data: Données thermiques de _collect_thermal_data()
            fps_data: FPSData du fps_monitor
            ml_prediction: ThermalPrediction du ml_predictor
            sweet_spot: SweetSpotResult du sweet_spot_finder
            advanced_stats: Stats avancées
            optimizations: Liste des optimisations actives
        """
        # GPU Metrics
        gpu_metrics = {
            'timestamp': thermal_data.get('timestamp', datetime.now()).isoformat()
                         if hasattr(thermal_data.get('timestamp', ''), 'isoformat')
                         else str(thermal_data.get('timestamp', '')),
            'temperature': thermal_data.get('gpu_temperature', 0),
            'usage': thermal_data.get('gpu_usage', 0),
            'clock_speed': thermal_data.get('gpu_clock_speed', 0),
            'memory_clock': thermal_data.get('gpu_memory_clock', 0),
            'fan_speed': thermal_data.get('gpu_fan_speed', 0),
            'power_draw': advanced_stats.get('power_draw', 0) if advanced_stats else 0,
            'vram_used': 0,
            'vram_total': 8192
        }

        # Si on a les vraies métriques GPU
        if advanced_stats:
            gpu_metrics['clock_speed'] = advanced_stats.get('clock_current', 0)
            gpu_metrics['vram_used'] = (advanced_stats.get('vram_usage_percent', 0) / 100) * 8192

        # FPS Metrics
        fps_metrics = {
            'current': 0,
            'avg': 0,
            'min': 0,
            'max': 0,
            'fps_1_low': 0,
            'frametime_ms': 0
        }

        if fps_data:
            fps_metrics = {
                'current': fps_data.fps_current,
                'avg': fps_data.fps_avg,
                'min': fps_data.fps_min if fps_data.fps_min != float('inf') else 0,
                'max': fps_data.fps_max,
                'fps_1_low': fps_data.fps_1_percent_low,
                'frametime_ms': fps_data.frametime_ms
            }

        # ML Prediction
        ml_metrics = {
            'predicted_5s': 0,
            'predicted_10s': 0,
            'predicted_30s': 0,
            'trend': 'unknown',
            'spike_probability': 0,
            'recommended_action': 'none',
            'confidence': 0
        }

        if ml_prediction:
            ml_metrics = {
                'predicted_5s': ml_prediction.predicted_temp_5s,
                'predicted_10s': ml_prediction.predicted_temp_10s,
                'predicted_30s': ml_prediction.predicted_temp_30s,
                'trend': ml_prediction.trend,
                'spike_probability': ml_prediction.spike_probability,
                'recommended_action': ml_prediction.recommended_action,
                'confidence': ml_prediction.confidence
            }

        # Sweet Spot
        sweet_spot_data = None
        if sweet_spot:
            sweet_spot_data = {
                'optimal_clock': sweet_spot.optimal_clock_mhz,
                'optimal_temp': sweet_spot.optimal_temp_target,
                'expected_fps': sweet_spot.expected_fps,
                'efficiency': sweet_spot.efficiency_score,
                'recommendation': sweet_spot.recommendation
            }

        # Game info
        game_info = None
        if thermal_data.get('game_detected'):
            game_data = thermal_data.get('game_info', {})
            game_info = {
                'name': game_data.get('game_name', 'Unknown'),
                'profile': game_data.get('thermal_profile', 'medium'),
                'is_known': game_data.get('is_known', False)
            }

        # Optimizations list
        opt_list = []
        if optimizations:
            for opt_name, opt_value in optimizations.items():
                opt_list.append(f"{opt_name}: {opt_value}")

        # Performance Score - NOUVEAU !
        score_data = None
        if performance_score:
            score_data = {
                'overall': performance_score.overall_score,
                'state': performance_score.state.value,
                'strategy': performance_score.recommended_strategy.value,
                'thermal': performance_score.breakdown.thermal_score,
                'fps': performance_score.breakdown.fps_score,
                'efficiency': performance_score.breakdown.efficiency_score,
                'stability': performance_score.breakdown.stability_score,
                'trend': performance_score.trend,
                'trend_delta': performance_score.score_delta,
                'recommendations': performance_score.recommendations[:3] if performance_score.recommendations else []
            }

        return {
            'gpu': gpu_metrics,
            'fps': fps_metrics,
            'ml': ml_metrics,
            'sweet_spot': sweet_spot_data,
            'game': game_info,
            'optimizations': opt_list,
            'uptime_seconds': thermal_data.get('uptime_seconds', 0),
            'score': score_data  # NOUVEAU !
        }


# Instance globale
DASHBOARD_CLIENT = DashboardClient()


def test_dashboard_client():
    """Test du client dashboard"""
    print("=" * 60)
    print("📊 TEST DASHBOARD CLIENT - TEMPLE IAM")
    print("=" * 60)

    client = DashboardClient()
    client.start()

    print("\n📡 Envoi de données de test...")

    for i in range(5):
        test_data = {
            'gpu': {
                'timestamp': datetime.now().isoformat(),
                'temperature': 65 + i * 2,
                'usage': 70 + i * 5,
                'clock_speed': 1800 + i * 50,
                'memory_clock': 7000,
                'fan_speed': 50 + i * 5,
                'power_draw': 100 + i * 10,
                'vram_used': 4000,
                'vram_total': 8192
            },
            'fps': {
                'current': 60 + i,
                'avg': 58,
                'min': 45,
                'max': 75,
                'fps_1_low': 42,
                'frametime_ms': 16.6
            },
            'ml': {
                'predicted_5s': 67 + i,
                'predicted_10s': 69 + i,
                'predicted_30s': 72 + i,
                'trend': 'rising' if i < 3 else 'stable',
                'spike_probability': 0.2 + i * 0.1,
                'recommended_action': 'none',
                'confidence': 0.5 + i * 0.1
            },
            'sweet_spot': {
                'optimal_clock': 1950,
                'optimal_temp': 75,
                'expected_fps': 65,
                'efficiency': 1.85,
                'recommendation': 'Configuration optimale !'
            },
            'game': {
                'name': 'Test Game',
                'profile': 'high',
                'is_known': True
            },
            'optimizations': ['Clock: 1950MHz', 'Mode: Balanced'],
            'uptime_seconds': i * 60
        }

        client.send_data(test_data)
        print(f"   [{i+1}/5] Données envoyées (temp={test_data['gpu']['temperature']}°C)")
        time.sleep(1)

    client.stop()

    print("\n" + "=" * 60)
    print("✅ TEST TERMINÉ")
    print("=" * 60)
    print("💡 Si le serveur Bun.js est lancé, les données sont visibles sur")
    print("   http://localhost:3000")


if __name__ == "__main__":
    test_dashboard_client()
