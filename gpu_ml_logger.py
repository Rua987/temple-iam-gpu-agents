"""
🧠 GPU MACHINE LEARNING LOGGER - APPRENTISSAGE INTELLIGENT ! 🏛️
Objectif : Logger TOUTES les métriques GPU pour apprendre les patterns

FONCTIONNALITÉS ML :
🎯 Data Collection : Enregistre chaque milliseconde de gaming
🎯 Pattern Learning : Analyse les tendances thermiques par jeu
🎯 Predictive Optimization : Anticipe les problèmes avant qu'ils arrivent
🎯 Session History : Historique complet pour amélioration continue

PLUS ULTRA ! DATTEBAYO ! 🚀⚡🥷🏛️
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='🧠 %(asctime)s - %(levelname)s - %(message)s')

class GPUMLLogger:
    """Logger ML pour apprentissage des patterns GPU - INTELLIGENCE DIVINE ! 🧠"""

    def __init__(self, log_directory: str = "gpu_ml_data"):
        """
        Initialisation du logger ML

        Args:
            log_directory: Dossier où stocker les données ML
        """
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)

        # Session actuelle
        self.current_session_file = None
        self.current_session_start = None
        self.current_game = None
        self.session_datapoints = []

        # Statistiques de session
        self.session_stats = {
            'total_datapoints': 0,
            'avg_temp': 0,
            'max_temp': 0,
            'min_temp': 999,
            'avg_fps': 0,
            'avg_gpu_load': 0,
            'spikes_detected': 0
        }

        logging.info("🧠 GPU ML Logger initialisé - APPRENTISSAGE INTELLIGENT ACTIVÉ !")
        logging.info(f"📂 Dossier de données: {self.log_directory.absolute()}")

    def start_session(self, game_name: str):
        """Démarre une nouvelle session d'apprentissage"""
        self.current_game = game_name
        self.current_session_start = datetime.now()
        self.session_datapoints = []

        # Nom du fichier avec timestamp
        timestamp = self.current_session_start.strftime("%Y%m%d_%H%M%S")
        game_safe = game_name.replace(" ", "_").replace(":", "")
        self.current_session_file = self.log_directory / f"{game_safe}_{timestamp}.jsonl"

        # Métadonnées de session
        session_metadata = {
            'type': 'session_start',
            'game': game_name,
            'start_time': self.current_session_start.isoformat(),
            'timestamp': time.time()
        }

        self._write_datapoint(session_metadata)

        logging.info(f"🎮 Session ML démarrée: {game_name}")
        logging.info(f"📝 Fichier: {self.current_session_file.name}")

    def log_datapoint(self, gpu_stats: Dict[str, Any]):
        """
        Enregistre un point de données GPU

        Args:
            gpu_stats: Dictionnaire avec toutes les métriques GPU
        """
        if not self.current_session_file:
            logging.warning("⚠️ Aucune session active - datapoint ignoré")
            return

        # Enrichir avec métadonnées
        datapoint = {
            'type': 'gpu_metrics',
            'timestamp': time.time(),
            'session_time': (datetime.now() - self.current_session_start).total_seconds(),
            'game': self.current_game,
            **gpu_stats
        }

        # Écrire dans le fichier
        self._write_datapoint(datapoint)

        # Mettre à jour les stats de session
        self._update_session_stats(datapoint)

        # Garder en mémoire pour analyse rapide
        self.session_datapoints.append(datapoint)

        # Limiter la mémoire (garde les 1000 derniers points)
        if len(self.session_datapoints) > 1000:
            self.session_datapoints.pop(0)

    def detect_spike(self, current_load: float, threshold: float = 20.0) -> bool:
        """
        Détecte un spike de charge GPU soudain

        Args:
            current_load: Charge GPU actuelle (%)
            threshold: Seuil d'augmentation pour détecter un spike

        Returns:
            True si spike détecté
        """
        if len(self.session_datapoints) < 5:
            return False

        # Moyenne des 5 derniers points
        recent_loads = [dp.get('gpu_usage', 0) for dp in self.session_datapoints[-5:]]
        avg_recent = sum(recent_loads) / len(recent_loads)

        # Spike = augmentation soudaine
        spike_detected = (current_load - avg_recent) > threshold

        if spike_detected:
            self.session_stats['spikes_detected'] += 1

            # Logger le spike
            spike_event = {
                'type': 'spike_detected',
                'timestamp': time.time(),
                'session_time': (datetime.now() - self.current_session_start).total_seconds(),
                'load_before': avg_recent,
                'load_spike': current_load,
                'increase': current_load - avg_recent
            }
            self._write_datapoint(spike_event)

            logging.warning(f"⚠️ SPIKE DÉTECTÉ: {avg_recent:.1f}% → {current_load:.1f}% (+{current_load - avg_recent:.1f}%)")

        return spike_detected

    def get_thermal_trend(self, window_size: int = 10) -> str:
        """
        Analyse la tendance thermique récente

        Args:
            window_size: Nombre de points à analyser

        Returns:
            'rising', 'falling', 'stable'
        """
        if len(self.session_datapoints) < window_size:
            return 'stable'

        recent_temps = [dp.get('gpu_temperature', 0) for dp in self.session_datapoints[-window_size:]]

        # Moyenne première moitié vs deuxième moitié
        mid = window_size // 2
        first_half_avg = sum(recent_temps[:mid]) / mid
        second_half_avg = sum(recent_temps[mid:]) / (window_size - mid)

        diff = second_half_avg - first_half_avg

        if diff > 2:
            return 'rising'
        elif diff < -2:
            return 'falling'
        else:
            return 'stable'

    def predict_temperature(self, seconds_ahead: int = 60) -> Optional[float]:
        """
        Prédit la température GPU dans X secondes

        Args:
            seconds_ahead: Nombre de secondes dans le futur

        Returns:
            Température prédite (°C) ou None si pas assez de données
        """
        if len(self.session_datapoints) < 30:
            return None

        # Prend les 30 derniers points
        recent_temps = [dp.get('gpu_temperature', 0) for dp in self.session_datapoints[-30:]]
        recent_times = [dp.get('session_time', 0) for dp in self.session_datapoints[-30:]]

        # Régression linéaire simple
        n = len(recent_temps)
        sum_x = sum(recent_times)
        sum_y = sum(recent_temps)
        sum_xy = sum(x * y for x, y in zip(recent_times, recent_temps))
        sum_x2 = sum(x * x for x in recent_times)

        # Slope (tendance)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n

        # Prédit à t + seconds_ahead
        current_time = recent_times[-1]
        future_time = current_time + seconds_ahead
        predicted_temp = slope * future_time + intercept

        return predicted_temp

    def end_session(self):
        """Termine la session et sauvegarde le résumé"""
        if not self.current_session_file:
            logging.warning("⚠️ Aucune session active à terminer")
            return

        session_duration = (datetime.now() - self.current_session_start).total_seconds() / 60

        # Métadonnées de fin
        session_end = {
            'type': 'session_end',
            'game': self.current_game,
            'end_time': datetime.now().isoformat(),
            'duration_minutes': session_duration,
            'total_datapoints': self.session_stats['total_datapoints'],
            'statistics': self.session_stats
        }

        self._write_datapoint(session_end)

        logging.info(f"✅ Session terminée: {self.current_game}")
        logging.info(f"⏱️  Durée: {session_duration:.1f} minutes")
        logging.info(f"📊 Points de données: {self.session_stats['total_datapoints']}")
        logging.info(f"🌡️  Temp moyenne: {self.session_stats['avg_temp']:.1f}°C")
        logging.info(f"🌡️  Temp max: {self.session_stats['max_temp']:.1f}°C")
        logging.info(f"🎯 FPS moyen: {self.session_stats['avg_fps']:.1f}")
        logging.info(f"⚠️  Spikes détectés: {self.session_stats['spikes_detected']}")

        # Reset
        self.current_session_file = None
        self.current_game = None
        self.session_datapoints = []
        self.session_stats = {
            'total_datapoints': 0,
            'avg_temp': 0,
            'max_temp': 0,
            'min_temp': 999,
            'avg_fps': 0,
            'avg_gpu_load': 0,
            'spikes_detected': 0
        }

    def get_session_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de la session en cours"""
        return {
            'game': self.current_game,
            'duration_minutes': (datetime.now() - self.current_session_start).total_seconds() / 60 if self.current_session_start else 0,
            'datapoints': self.session_stats['total_datapoints'],
            **self.session_stats
        }

    def analyze_game_profile(self, game_name: str) -> Optional[Dict[str, Any]]:
        """
        Analyse toutes les sessions d'un jeu pour créer un profil

        Args:
            game_name: Nom du jeu

        Returns:
            Profil appris du jeu
        """
        # Trouve tous les fichiers de ce jeu
        game_safe = game_name.replace(" ", "_").replace(":", "")
        game_files = list(self.log_directory.glob(f"{game_safe}_*.jsonl"))

        if not game_files:
            logging.warning(f"⚠️ Aucune donnée trouvée pour {game_name}")
            return None

        logging.info(f"📊 Analyse de {len(game_files)} session(s) de {game_name}...")

        # Collecte toutes les métriques
        all_temps = []
        all_loads = []
        all_fps = []
        total_spikes = 0
        total_duration = 0

        for file in game_files:
            with open(file, 'r') as f:
                for line in f:
                    data = json.loads(line)

                    if data['type'] == 'gpu_metrics':
                        all_temps.append(data.get('gpu_temperature', 0))
                        all_loads.append(data.get('gpu_usage', 0))
                        all_fps.append(data.get('fps_estimate', 0))

                    elif data['type'] == 'spike_detected':
                        total_spikes += 1

                    elif data['type'] == 'session_end':
                        total_duration += data.get('duration_minutes', 0)

        if not all_temps:
            return None

        # Calcule le profil
        profile = {
            'game': game_name,
            'sessions_analyzed': len(game_files),
            'total_playtime_minutes': total_duration,
            'thermal_profile': {
                'avg_temp': sum(all_temps) / len(all_temps),
                'max_temp': max(all_temps),
                'min_temp': min(all_temps),
                'typical_range': f"{sorted(all_temps)[len(all_temps)//4]:.0f}-{sorted(all_temps)[3*len(all_temps)//4]:.0f}°C"
            },
            'performance_profile': {
                'avg_gpu_load': sum(all_loads) / len(all_loads),
                'avg_fps': sum(all_fps) / len(all_fps) if all_fps else 0
            },
            'stability': {
                'total_spikes': total_spikes,
                'spikes_per_hour': (total_spikes / total_duration * 60) if total_duration > 0 else 0
            },
            'learned_at': datetime.now().isoformat()
        }

        logging.info(f"✅ Profil créé pour {game_name}:")
        logging.info(f"   🌡️ Temp moyenne: {profile['thermal_profile']['avg_temp']:.1f}°C")
        logging.info(f"   🎯 GPU Load moyen: {profile['performance_profile']['avg_gpu_load']:.1f}%")
        logging.info(f"   📊 FPS moyen: {profile['performance_profile']['avg_fps']:.1f}")

        return profile

    def _write_datapoint(self, data: Dict[str, Any]):
        """Écrit un datapoint dans le fichier de session"""
        if self.current_session_file:
            with open(self.current_session_file, 'a') as f:
                f.write(json.dumps(data) + '\n')

    def _update_session_stats(self, datapoint: Dict[str, Any]):
        """Met à jour les statistiques de session"""
        self.session_stats['total_datapoints'] += 1

        temp = datapoint.get('gpu_temperature', 0)
        fps = datapoint.get('fps_estimate', 0)
        load = datapoint.get('gpu_usage', 0)

        # Moyenne cumulée
        n = self.session_stats['total_datapoints']
        self.session_stats['avg_temp'] = (self.session_stats['avg_temp'] * (n - 1) + temp) / n
        self.session_stats['avg_fps'] = (self.session_stats['avg_fps'] * (n - 1) + fps) / n
        self.session_stats['avg_gpu_load'] = (self.session_stats['avg_gpu_load'] * (n - 1) + load) / n

        # Min/Max
        self.session_stats['max_temp'] = max(self.session_stats['max_temp'], temp)
        self.session_stats['min_temp'] = min(self.session_stats['min_temp'], temp)


# Instance globale
ML_LOGGER = GPUMLLogger()


if __name__ == "__main__":
    print("🧠 GPU ML LOGGER - TEST")
    print("="*80)

    # Test du logger
    logger = GPUMLLogger()

    # Simule une session
    logger.start_session("Cyberpunk 2077")

    # Simule des datapoints
    for i in range(100):
        logger.log_datapoint({
            'gpu_temperature': 65 + i * 0.1,  # Température qui monte
            'gpu_usage': 85 + (i % 20),       # Load qui varie
            'fps_estimate': 60 - (i % 10)     # FPS qui varie
        })

        # Test spike detection
        if i == 50:
            logger.log_datapoint({
                'gpu_temperature': 75,
                'gpu_usage': 98,  # SPIKE!
                'fps_estimate': 45
            })

    # Stats de session
    stats = logger.get_session_stats()
    print(f"\n📊 STATS SESSION:")
    print(f"Durée: {stats['duration_minutes']:.2f} minutes")
    print(f"Datapoints: {stats['datapoints']}")
    print(f"Temp moyenne: {stats['avg_temp']:.1f}°C")
    print(f"Spikes: {stats['spikes_detected']}")

    # Prédiction
    predicted_temp = logger.predict_temperature(60)
    if predicted_temp:
        print(f"\n🔮 Température prédite dans 60s: {predicted_temp:.1f}°C")

    # Tendance
    trend = logger.get_thermal_trend()
    print(f"📈 Tendance thermique: {trend}")

    # Fin de session
    logger.end_session()

    print("\n" + "="*80)
    print("✅ Test terminé!")
