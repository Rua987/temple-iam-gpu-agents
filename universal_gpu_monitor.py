"""
🎮 UNIVERSAL GPU MONITOR - MONITORING UNIVERSEL POUR TOUS LES JEUX ! 🏛️
Objectif : Monitoring GPU temps réel pour N'IMPORTE QUEL JEU

FONCTIONNALITÉS DIVINES :
🎯 Détection Automatique : Reconnaît n'importe quel jeu automatiquement
🎯 Monitoring Continu : Surveillance 24/7 multi-jeux
🎯 Métriques Temps Réel : GPU, CPU, Mémoire, FPS estimé par jeu
🎯 Alertes Intelligentes : Recommandations spécifiques par jeu
🎯 Dashboard Live : Affichage en temps réel multi-jeux
🎯 Auto-Optimisation : Ajustements automatiques par profil de jeu

PLUS ULTRA ! DATTEBAYO ! 🚀⚡🥷🏛️
"""

import time
import threading
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import sys

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from universal_game_detector import GAME_DETECTOR, DetectedGame
from games_database import GAMES_DB
from gpu_ml_logger import ML_LOGGER
from workload_thermal_controller import WorkloadThermalController
import gpu_autoresearch
from rtss_reader import RTSSReader

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='🎮 %(asctime)s - %(levelname)s - %(message)s')

class UniversalGPUMonitor:
    """Moniteur GPU Universel - SURVEILLANCE DIVINE MULTI-JEUX ! 🎮"""

    def __init__(self, monitor_interval: float = 1.0, max_history: int = 1000):
        """
        Initialisation du moniteur GPU universel

        Args:
            monitor_interval: Intervalle de monitoring en secondes
            max_history: Nombre maximum de points de données à conserver
        """
        self.is_running = False
        self.monitoring_data = []
        self.alert_history = []
        self.monitor_interval = monitor_interval
        self.max_history = max_history

        # Détecteur de jeux
        self.game_detector = GAME_DETECTOR

        # ML Logger pour apprentissage intelligent
        self.ml_logger = ML_LOGGER
        self.ml_session_active = False
        self.thermal_controller = WorkloadThermalController()

        # Jeu actuellement surveillé
        self.current_game: Optional[DetectedGame] = None
        self.current_game_profile: Optional[Dict[str, Any]] = None

        # Auto-tuning: track tuned workloads to avoid re-tuning
        self.tuned_workloads: Dict[str, int] = {}  # {workload_name: optimal_mhz}
        self.tuning_thread: Optional[threading.Thread] = None
        self.tuning_in_progress = False

        # Seuils d'alerte dynamiques (mis à jour selon le jeu)
        self.alert_thresholds = {
            'gpu_usage': 95.0,
            'gpu_memory': 90.0,
            'gpu_temperature': 65.0,  # Activation plus précoce pour meilleure protection thermique
            'cpu_usage': 95.0,
            'memory_usage': 90.0,
            'fps_drop': 30.0
        }

        # Initialisation GPU
        self._initialize_gpu_monitoring()

        logging.info("🎮 Universal GPU Monitor initialisé - SURVEILLANCE DIVINE MULTI-JEUX ACTIVE !")

    def _initialize_gpu_monitoring(self):
        """Initialisation du monitoring GPU - CONFIGURATION DIVINE ! ⚡"""
        self.gpu_name = "NVIDIA GPU"  # Default
        self.gpu_available = False

        try:
            # Import GPU monitoring
            import GPUtil

            # Test initial
            gpus = GPUtil.getGPUs()
            if gpus:
                self.gpu = gpus[0]
                self.gpu_name = self.gpu.name
                self.gpu_available = True
                logging.info(f"✅ GPU détecté: {self.gpu_name}")
            else:
                logging.warning("⚠️ Aucun GPU NVIDIA détecté")

        except ImportError:
            logging.warning("⚠️ GPUtil non disponible - Monitoring GPU limité")
        except Exception as e:
            logging.error(f"❌ Erreur initialisation GPU: {str(e)}")

    def start_monitoring(self):
        """Démarrage du monitoring continu - SURVEILLANCE DIVINE ! 👁️"""
        logging.info("🎮 DÉMARRAGE MONITORING GPU UNIVERSEL !")

        self.is_running = True
        self.start_time = datetime.now()

        try:
            # Démarrage du monitoring en continu
            self._run_continuous_monitoring()

        except KeyboardInterrupt:
            logging.info("🛑 Arrêt manuel du monitoring...")
        except Exception as e:
            logging.error(f"❌ Erreur monitoring: {str(e)}")
        finally:
            self.stop_monitoring()

    def _run_continuous_monitoring(self):
        """Exécution du monitoring continu - VISION DIVINE ! 🔮"""
        print("\n" + "="*80)
        print("🎮 UNIVERSAL GPU MONITOR - SURVEILLANCE DIVINE MULTI-JEUX")
        print("="*80)
        print("💡 Ce système surveille TOUS les jeux automatiquement")
        print("💡 Détection automatique + optimisations intelligentes")
        print("💡 Appuie sur Ctrl+C pour arrêter")
        print("="*80)

        while self.is_running:
            try:
                # 1. Détection des jeux en cours
                detected_games = self.game_detector.detect_running_games()

                # 2. Sélection du jeu principal
                primary_game = self.game_detector.get_primary_game()

                # 3. Mise à jour du jeu actuel
                self._update_current_game(primary_game)

                # 4. Collecte des métriques GPU
                monitoring_data = self._collect_monitoring_data(primary_game, detected_games)

                if self.current_game_profile:
                    self.thermal_controller.adjust_for_temperature(
                        monitoring_data.get("gpu_temperature", 0),
                        self.current_game_profile,
                    )

                # 5. Stockage des données
                self.monitoring_data.append(monitoring_data)
                if len(self.monitoring_data) > self.max_history:
                    self.monitoring_data.pop(0)

                # 5.5. ML Logging - Apprentissage intelligent
                if self.ml_session_active and monitoring_data.get('game_detected'):
                    self.ml_logger.log_datapoint({
                        'gpu_temperature': monitoring_data.get('gpu_temperature', 0),
                        'gpu_usage': monitoring_data.get('gpu_usage', 0),
                        'gpu_memory_percent': monitoring_data.get('gpu_memory_percent', 0),
                        'cpu_usage': monitoring_data.get('cpu_usage', 0),
                        'memory_usage': monitoring_data.get('memory_usage', 0),
                        'fps_estimate': monitoring_data.get('fps_estimate', 0)
                    })

                    # Détection de spikes ML
                    gpu_load = monitoring_data.get('gpu_usage', 0)
                    self.ml_logger.detect_spike(gpu_load)

                # 6. Affichage temps réel
                self._display_monitoring_status(monitoring_data)

                # 7. Analyse et alertes
                self._analyze_and_alert(monitoring_data)

                # 8. Attente avant la prochaine itération
                time.sleep(self.monitor_interval)

            except Exception as e:
                logging.error(f"❌ Erreur boucle monitoring: {str(e)}")
                time.sleep(5)

    def _update_current_game(self, game: Optional[DetectedGame]):
        """Met à jour le jeu actuellement surveillé"""
        # Comparer les noms de jeux au lieu des objets pour éviter de recréer des sessions
        new_game_name = game.custom_name if game else None
        current_game_name = self.current_game.custom_name if self.current_game else None

        # Debug: Log la comparaison
        if new_game_name and current_game_name:
            logging.info(f"🔍 DEBUG ML: NEW='{new_game_name}' | OLD='{current_game_name}' | SAME={new_game_name == current_game_name}")

        if new_game_name != current_game_name:
            # Terminer la session ML précédente si elle existe
            if self.ml_session_active:
                self.ml_logger.end_session()
                self.ml_session_active = False

            if game:
                self.current_game = game
                self.current_game_profile = self.game_detector.get_game_optimization_profile(game)

                # Mise à jour des seuils d'alerte selon le profil
                self._update_alert_thresholds(self.current_game_profile)

                # Démarrer une session ML pour ce jeu
                self.ml_logger.start_session(game.custom_name)
                self.ml_session_active = True

                category = self.current_game_profile.get('category', 'gaming')
                mode = self.current_game_profile.get('optimization_mode', 'active')
                self.thermal_controller.apply_for_workload(self.current_game_profile)
                logging.info(f"🎮 Workload actif: {game.custom_name} ({game.process_name}) [{category}/{mode}]")
                if game.is_known:
                    logging.info(f"✅ Profil connu appliqué: {self.current_game_profile['thermal_profile']}")
                else:
                    logging.info(f"📋 Profil {mode} appliqué (cible {self.current_game_profile['target_temp']}°C)")
                    # Launch auto-tuning in background for unknown/new workloads
                    if game.custom_name not in self.tuned_workloads:
                        self._start_auto_tuning_thread(game.custom_name, is_gaming=(category == 'gaming'))
            else:
                self.current_game = None
                self.current_game_profile = None
                self.thermal_controller.apply_for_workload(None)
                logging.info("🎮 Aucun jeu actif")

    def _update_alert_thresholds(self, profile: Dict[str, Any]):
        """Met à jour les seuils d'alerte selon le profil du jeu"""
        thermal_map = {
            'low': {'gpu_temperature': 60.0, 'gpu_usage': 70.0},
            'medium': {'gpu_temperature': 65.0, 'gpu_usage': 80.0},
            'high': {'gpu_temperature': 70.0, 'gpu_usage': 90.0},
            'extreme': {'gpu_temperature': 75.0, 'gpu_usage': 95.0}
        }

        thermal_profile = profile.get('thermal_profile', 'medium')
        thresholds = thermal_map.get(thermal_profile, thermal_map['medium'])

        self.alert_thresholds.update(thresholds)
        # Seuil = température cible du jeu - 5°C pour activation précoce
        self.alert_thresholds['gpu_temperature'] = profile.get('target_temp', 65.0)

    def _collect_monitoring_data(self, primary_game: Optional[DetectedGame], all_games: List[DetectedGame]) -> Dict[str, Any]:
        """Collecte des données de monitoring - COLLECTE DIVINE ! 📊"""
        try:
            timestamp = datetime.now()

            # Métriques GPU
            gpu_metrics = self._get_gpu_metrics()

            # Métriques système
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            # Estimation FPS (basée sur GPU usage)
            fps_estimate = self._estimate_fps(gpu_metrics)

            # Temps de fonctionnement
            uptime = (timestamp - self.start_time).total_seconds() if self.start_time else 0

            # Informations sur le jeu actuel
            game_info = {}
            if primary_game:
                game_info = {
                    'game_name': primary_game.custom_name,
                    'process_name': primary_game.process_name,
                    'is_known': primary_game.is_known,
                    'pid': primary_game.pid,
                    'game_cpu_usage': primary_game.cpu_usage,
                    'game_memory_mb': primary_game.memory_mb,
                    'optimization_profile': self.current_game_profile
                }

            return {
                'timestamp': timestamp,
                'uptime_seconds': uptime,

                # GPU
                'gpu_name': self.gpu_name,
                'gpu_usage': gpu_metrics.get('usage', 0),
                'gpu_temperature': gpu_metrics.get('temperature', 0),
                'gpu_memory_used_mb': gpu_metrics.get('memory_used_mb', 0),
                'gpu_memory_total_mb': gpu_metrics.get('memory_total_mb', 0),
                'gpu_memory_percent': gpu_metrics.get('memory_percent', 0),
                'gpu_power_usage': gpu_metrics.get('power_usage', 0),

                # Système
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'memory_available_gb': memory.available / (1024**3),

                # Performance
                'fps_estimate': fps_estimate,

                # Jeu actuel
                'game_detected': primary_game is not None,
                'game_info': game_info,

                # Tous les jeux détectés
                'all_games_count': len(all_games),
                'all_games': [
                    {
                        'name': g.custom_name,
                        'process': g.process_name,
                        'is_known': g.is_known
                    }
                    for g in all_games
                ]
            }

        except Exception as e:
            logging.error(f"❌ Erreur collecte données: {str(e)}")
            return {
                'timestamp': datetime.now(),
                'error': str(e)
            }

    def _get_gpu_metrics(self) -> Dict[str, Any]:
        """Collecte des métriques GPU - MÉTRIQUES DIVINES ! 📈"""
        try:
            if not self.gpu_available:
                return {}

            import GPUtil
            gpus = GPUtil.getGPUs()

            if not gpus:
                return {}

            gpu = gpus[0]

            return {
                'usage': gpu.load * 100,
                'temperature': gpu.temperature,
                'memory_used_mb': gpu.memoryUsed,
                'memory_total_mb': gpu.memoryTotal,
                'memory_percent': (gpu.memoryUsed / gpu.memoryTotal * 100) if gpu.memoryTotal > 0 else 0,
                'power_usage': 0  # GPUtil ne fournit pas cette info
            }

        except Exception as e:
            logging.error(f"❌ Erreur métriques GPU: {str(e)}")
            return {}

    def _estimate_fps(self, gpu_metrics: Dict[str, Any]) -> float:
        """Estimation FPS basée sur l'utilisation GPU"""
        if not gpu_metrics or not self.current_game_profile:
            return 0.0

        gpu_usage = gpu_metrics.get('usage', 0)
        target_fps = self.current_game_profile.get('target_fps', 60)

        # Estimation simple: FPS proportionnel à l'utilisation GPU
        if gpu_usage > 95:
            return target_fps * 0.9  # GPU saturé, FPS réduit
        elif gpu_usage > 80:
            return target_fps
        else:
            return target_fps * 1.1  # GPU pas saturé, potentiel FPS supérieur

    def _display_monitoring_status(self, data: Dict[str, Any]):
        """Affichage du statut de monitoring - AFFICHAGE DIVIN ! 📺"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print("\n" + "="*80)
        print("🎮 UNIVERSAL GPU MONITOR - SURVEILLANCE DIVINE MULTI-JEUX")
        print("="*80)

        # Temps de fonctionnement
        uptime = int(data.get('uptime_seconds', 0))
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        print(f"⏱️  Temps de fonctionnement: {hours:02d}:{minutes:02d}:{seconds:02d}")

        # Jeu détecté
        print("\n" + "-"*80)
        print("🎮 DÉTECTION DE JEU")
        print("-"*80)

        if data.get('game_detected'):
            game_info = data.get('game_info', {})
            status_icon = "✅" if game_info.get('is_known') else "🆕"
            print(f"{status_icon} Jeu: {game_info.get('game_name', 'Inconnu')}")
            print(f"   Processus: {game_info.get('process_name', 'N/A')}")
            print(f"   Statut: {'Connu (profil optimisé)' if game_info.get('is_known') else 'Nouveau (profil générique)'}")

            # Profil d'optimisation
            if game_info.get('optimization_profile'):
                profile = game_info['optimization_profile']
                print(f"   Profil thermique: {profile.get('thermal_profile', 'N/A').upper()}")
                print(f"   Température cible: {profile.get('target_temp', 'N/A')}°C")
                print(f"   FPS cible: {profile.get('target_fps', 'N/A')}")
                if profile.get('supports_dlss'):
                    print(f"   DLSS: ✅ Supporté")
                if profile.get('supports_ray_tracing'):
                    print(f"   Ray Tracing: ✅ Supporté")
        else:
            print("⚠️  Aucun jeu détecté")
            print(f"   {data.get('all_games_count', 0)} processus de jeu potentiels surveillés")

        thermal = self.thermal_controller.get_display_status()
        print("\n" + "-"*80)
        print("🌡️  CONTRÔLE THERMIQUE ACTIF")
        print("-"*80)
        print(f"Mode workload:     {thermal['workload_mode']}")
        print(f"Action en cours:   {thermal['active_action']}")
        print(f"Afterburner:       {thermal['afterburner_profile']}")
        print(f"Cap pilote:        {thermal['driver_cap']}")
        print(f"Echelle IA:        {thermal['ai_ladder']}")
        print(f"Clock verrouille:  {thermal['clock_locked']}")

        # Métriques GPU
        print("\n" + "-"*80)
        print("🖥️  MÉTRIQUES GPU")
        print("-"*80)
        print(f"GPU: {data.get('gpu_name', 'N/A')}")

        gpu_usage = data.get('gpu_usage', 0)
        gpu_temp = data.get('gpu_temperature', 0)
        gpu_mem = data.get('gpu_memory_percent', 0)

        # Barres de progression avec couleurs
        print(f"Utilisation:  {self._create_bar(gpu_usage, 100)} {gpu_usage:5.1f}%")
        print(f"Température:  {self._create_bar(gpu_temp, 100)} {gpu_temp:5.1f}°C")
        print(f"Mémoire VRAM: {self._create_bar(gpu_mem, 100)} {gpu_mem:5.1f}% ({data.get('gpu_memory_used_mb', 0):.0f}/{data.get('gpu_memory_total_mb', 0):.0f} MB)")

        # FPS estimé
        fps = data.get('fps_estimate', 0)
        if fps > 0:
            print(f"FPS estimé:   {fps:5.1f}")

        # Métriques système
        print("\n" + "-"*80)
        print("💻 MÉTRIQUES SYSTÈME")
        print("-"*80)
        cpu_usage = data.get('cpu_usage', 0)
        mem_usage = data.get('memory_usage', 0)
        print(f"CPU:          {self._create_bar(cpu_usage, 100)} {cpu_usage:5.1f}%")
        print(f"RAM:          {self._create_bar(mem_usage, 100)} {mem_usage:5.1f}% ({data.get('memory_available_gb', 0):.1f} GB dispo)")

        # ML Insights - Apprentissage intelligent
        if self.ml_session_active and data.get('game_detected'):
            print("\n" + "-"*80)
            print("🧠 ML INSIGHTS - APPRENTISSAGE INTELLIGENT")
            print("-"*80)

            # Tendance thermique
            trend = self.ml_logger.get_thermal_trend()
            trend_icons = {
                'rising': '📈 MONTÉE',
                'falling': '📉 DESCENTE',
                'stable': '➡️ STABLE'
            }
            print(f"Tendance temp: {trend_icons.get(trend, trend)}")

            # Prédiction température
            predicted_temp = self.ml_logger.predict_temperature(60)
            if predicted_temp:
                current_temp = data.get('gpu_temperature', 0)
                delta = predicted_temp - current_temp
                delta_sign = "+" if delta > 0 else ""
                print(f"Préd. +60s:   {predicted_temp:.1f}°C ({delta_sign}{delta:.1f}°C)")

            # Stats session
            ml_stats = self.ml_logger.get_session_stats()
            print(f"Session:      {ml_stats['duration_minutes']:.1f} min | {ml_stats['datapoints']} points")
            if ml_stats['spikes_detected'] > 0:
                print(f"⚠️  Spikes GPU:   {ml_stats['spikes_detected']} détecté(s)")

        # Tous les jeux détectés
        if data.get('all_games_count', 0) > 1:
            print("\n" + "-"*80)
            print(f"🎯 AUTRES JEUX DÉTECTÉS ({data.get('all_games_count', 0) - 1})")
            print("-"*80)
            for game in data.get('all_games', [])[:5]:
                if data.get('game_detected') and game['name'] == data['game_info']['game_name']:
                    continue
                status = "✅" if game['is_known'] else "🆕"
                print(f"  {status} {game['name']} ({game['process']})")

        print("\n" + "="*80)
        print("💡 Appuie sur Ctrl+C pour arrêter le monitoring")
        print("="*80)

    def _create_bar(self, value: float, max_value: float, length: int = 30) -> str:
        """Crée une barre de progression"""
        percent = min(value / max_value, 1.0) if max_value > 0 else 0
        filled = int(length * percent)
        bar = '█' * filled + '░' * (length - filled)

        # Couleur selon le pourcentage
        if percent > 0.9:
            return f"🔴 {bar}"
        elif percent > 0.7:
            return f"🟡 {bar}"
        else:
            return f"🟢 {bar}"

    def _analyze_and_alert(self, data: Dict[str, Any]):
        """Analyse et génération d'alertes - ANALYSE DIVINE ! 🚨"""
        alerts = []

        # Vérification température GPU
        gpu_temp = data.get('gpu_temperature', 0)
        if gpu_temp > self.alert_thresholds['gpu_temperature']:
            alerts.append({
                'level': 'WARNING',
                'type': 'temperature',
                'message': f"Température GPU élevée: {gpu_temp:.1f}°C (seuil: {self.alert_thresholds['gpu_temperature']:.1f}°C)",
                'recommendation': 'Réduire les paramètres graphiques ou augmenter la ventilation'
            })

        # Vérification utilisation GPU
        gpu_usage = data.get('gpu_usage', 0)
        if gpu_usage > self.alert_thresholds['gpu_usage']:
            alerts.append({
                'level': 'INFO',
                'type': 'gpu_usage',
                'message': f"GPU saturé: {gpu_usage:.1f}%",
                'recommendation': 'Performance limitée par GPU - réduire résolution/qualité'
            })

        # Vérification mémoire GPU
        gpu_mem = data.get('gpu_memory_percent', 0)
        if gpu_mem > self.alert_thresholds['gpu_memory']:
            alerts.append({
                'level': 'WARNING',
                'type': 'vram',
                'message': f"VRAM élevée: {gpu_mem:.1f}%",
                'recommendation': 'Réduire textures/résolution pour éviter stuttering'
            })

        # Sauvegarde des alertes
        if alerts:
            timestamp = datetime.now()
            for alert in alerts:
                alert['timestamp'] = timestamp
                self.alert_history.append(alert)
                logging.warning(f"🚨 {alert['level']}: {alert['message']}")

        # Limiter l'historique
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]

    def stop_monitoring(self):
        """Arrêt du monitoring - ARRÊT GRACIEUX ! 🛑"""
        self.is_running = False

        # Terminer la session ML si active
        if self.ml_session_active:
            self.ml_logger.end_session()
            self.ml_session_active = False

        self.thermal_controller.release()
        logging.info("🛑 Monitoring arrêté")

        # Statistiques finales
        if self.monitoring_data:
            print("\n" + "="*80)
            print("📊 STATISTIQUES FINALES")
            print("="*80)

            total_points = len(self.monitoring_data)
            avg_gpu_usage = sum(d.get('gpu_usage', 0) for d in self.monitoring_data) / total_points
            avg_gpu_temp = sum(d.get('gpu_temperature', 0) for d in self.monitoring_data) / total_points
            max_gpu_temp = max(d.get('gpu_temperature', 0) for d in self.monitoring_data)

            print(f"Points de données: {total_points}")
            print(f"GPU usage moyen: {avg_gpu_usage:.1f}%")
            print(f"Température moyenne: {avg_gpu_temp:.1f}°C")
            print(f"Température max: {max_gpu_temp:.1f}°C")
            print(f"Alertes générées: {len(self.alert_history)}")
            print("="*80)

    def _start_auto_tuning_thread(self, workload_name: str, is_gaming: bool = True):
        """Launch auto-tuning in a background thread (non-blocking)."""
        if self.tuning_in_progress:
            logging.info(f"🔄 Auto-tuning déjà en cours, {workload_name} en attente")
            return
        self.tuning_in_progress = True
        self.tuning_thread = threading.Thread(
            target=self._auto_tune_worker,
            args=(workload_name, is_gaming),
            daemon=True
        )
        self.tuning_thread.start()

    def _auto_tune_worker(self, workload_name: str, is_gaming: bool):
        """Worker thread: run the auto-tuning sweep and apply the result."""
        try:
            logging.info(f"🚀 Auto-tuning de '{workload_name}' (gaming={is_gaming}) - durée ~30s")

            # Prepare perf provider for gaming (RTSS FPS) or just use default (None = proxy)
            perf_provider = None
            if is_gaming:
                rtss = RTSSReader()
                if rtss.available:
                    perf_provider = lambda: rtss.read_max_fps(workload_name)

            # Run the sweep
            optimal_mhz = gpu_autoresearch.auto_tune_workload(
                workload_name=workload_name,
                perf_provider=perf_provider,
                perf_unit="fps" if is_gaming else "tok/s",
                is_gaming=is_gaming,
                duration_s=30.0  # Total sweep time
            )

            if optimal_mhz:
                self.tuned_workloads[workload_name] = optimal_mhz
                logging.info(f"✅ Auto-tuning '{workload_name}': optimum = {optimal_mhz}MHz")
            else:
                logging.warning(f"⚠️ Auto-tuning '{workload_name}' inconclusive (GPU read-only or no signal)")

        except Exception as e:
            logging.error(f"❌ Auto-tuning error for '{workload_name}': {e}")
        finally:
            self.tuning_in_progress = False


def main():
    """Point d'entrée principal"""
    print("🎮 UNIVERSAL GPU MONITOR - DÉMARRAGE")

    # Création et démarrage du moniteur
    monitor = UniversalGPUMonitor(
        monitor_interval=1.0,
        max_history=1000
    )

    monitor.start_monitoring()

if __name__ == "__main__":
    main()
