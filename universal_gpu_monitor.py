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
# Optimisation pilotee par le scorer mur (PerformanceScorer + SweetSpotFinder),
# pas par le sweep autoresearch (retire: il se faisait piéger par les samples
# hors-charge - cf. faux positif 1500MHz/8%-util sur Cyberpunk).
from performance_scorer import PERFORMANCE_SCORER, PerformanceState
from rtss_reader import RTSSReader
from external_upscaler import ExternalUpscaler
from sweet_spot_finder import SweetSpotFinder
from thermal_ml_predictor import ThermalMLPredictor
from cpu_thermal_controller import CPUThermalController

# Configuration du logging: TOUT part dans un fichier, PAS dans la console.
# Sinon les lignes de log (detection ML, alertes...) s'impriment par-dessus le
# dashboard chaque seconde et le rendent illisible. force=True ecrase les
# handlers deja poses par les modules importes (detecteur, ML, scorer).
# RotatingFileHandler: cap a 2 Mo x 3 backups pour ne pas grossir a l'infini.
from logging.handlers import RotatingFileHandler


class _SafeRotatingFileHandler(RotatingFileHandler):
    """Tolerant a Windows: si le .log est tenu ouvert par un autre process
    (WinError 32 au renommage), on rouvre le flux courant et on desactive la
    rotation pour ce process au lieu de spammer des erreurs de logging."""

    def doRollover(self):
        try:
            super().doRollover()
        except (PermissionError, OSError):
            if self.stream is None:
                self.stream = self._open()
            self.maxBytes = 0  # stoppe les tentatives de rollover (anti-flood)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[_SafeRotatingFileHandler(
        'universal_gpu_monitor.log', maxBytes=2_000_000, backupCount=3, encoding='utf-8')],
    force=True,
)

class UniversalGPUMonitor:
    """Moniteur GPU Universel - SURVEILLANCE DIVINE MULTI-JEUX ! 🎮"""

    def __init__(self, monitor_interval: float = 1.0, max_history: int = 1000, dry_run: bool = False, gpu_index: int = 0, cpu_control: bool = False):
        """
        Initialisation du moniteur GPU universel

        Args:
            monitor_interval: Intervalle de monitoring en secondes
            max_history: Nombre maximum de points de données à conserver
            dry_run: simulation - detecte, score, affiche, mais N'APPLIQUE AUCUNE
                     action GPU reelle (caps clocks, Afterburner, upscaler). Pour
                     que les testeurs valident la detection sans risque.
            gpu_index: carte ciblee (multi-GPU). 0 = mono-GPU (comportement teste).
        """
        self.is_running = False
        self.dry_run = dry_run
        self.gpu_index = gpu_index
        self.monitoring_data = []
        self.alert_history = []
        self.monitor_interval = monitor_interval
        self.max_history = max_history

        # Détecteur de jeux
        self.game_detector = GAME_DETECTOR

        # ML Logger pour apprentissage intelligent
        self.ml_logger = ML_LOGGER
        self.ml_session_active = False
        self.thermal_controller = WorkloadThermalController(dry_run=dry_run, gpu_index=gpu_index)

        # Jeu actuellement surveillé
        self.current_game: Optional[DetectedGame] = None
        self.current_game_profile: Optional[Dict[str, Any]] = None

        # Optimisation par score: scorer mur + memo des workloads deja optimises
        self.performance_scorer = PERFORMANCE_SCORER
        self.optimized_workloads: set = set()  # workloads deja passes au scorer
        self.last_score = None  # dernier PerformanceScore calcule
        # Vrais FPS via RTSS (gaming) + conseiller upscaling (gating "gaming" only)
        self.rtss = RTSSReader()
        self.last_advice: Optional[str] = None
        self.fps_is_real = False
        # Upscaler externe (Lossless Scaling / Magpie) orchestre par l'agent,
        # GAMING uniquement. Debounce pour ne pas le lancer/couper sans arret
        # quand la detection de process principal clignote (Edge/Ollama).
        self.upscaler = ExternalUpscaler(dry_run=dry_run)
        self._no_game_ticks = 0
        self._STOP_AFTER_TICKS = 10  # arrete l'upscaler apres ~10s sans jeu
        # Sweet spot finder: controle FIN (cap continu vers le clock optimal
        # perf/qualite appris par jeu). GAMING uniquement. Le frein d'urgence
        # reste le plancher de securite.
        self.sweet_spot = SweetSpotFinder()
        self._analyze_counter = 0
        # Predicteur thermique: anticipe les pics (regression sur la pente) pour
        # freiner AVANT d'atteindre le seuil. GAMING uniquement.
        self.thermal_predictor = ThermalMLPredictor()
        self.last_prediction = None
        # Etage CPU (opt-in --cpu-control): frein par paliers de max processor
        # state (powercfg). TOUS workloads - sur laptop, CPU et GPU partagent la
        # dissipation, donc freiner le CPU aide aussi le GPU.
        self.cpu_controller = CPUThermalController(dry_run=dry_run) if cpu_control else None

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

    def _enable_ansi(self) -> bool:
        """Active le traitement des sequences ANSI sur la console.

        Sur Windows il faut poser ENABLE_VIRTUAL_TERMINAL_PROCESSING via
        SetConsoleMode ; le vieux truc os.system('') n'est pas fiable. Retourne
        True si l'ANSI est utilisable (-> refresh en place), False sinon (-> cls).
        """
        if os.name != 'nt':
            return True
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_uint32()
            if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                return False
            ENABLE_VT = 0x0004
            if not kernel32.SetConsoleMode(handle, mode.value | ENABLE_VT):
                return False
            return True
        except Exception:
            return False

    def _run_continuous_monitoring(self):
        """Exécution du monitoring continu - VISION DIVINE ! 🔮"""
        # Affichage: cls a chaque frame (infaillible sur Windows). L'ANSI en
        # place s'est avere trop fragile selon le terminal (charabia/residus);
        # les logs partent dans un fichier donc cls suffit a un ecran propre.
        os.system('cls' if os.name == 'nt' else 'clear')

        print("="*80)
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

                # 4.5. Vrais FPS via RTSS pour le gaming (l'estimation util-based
                # est trompeuse: 100% util en path tracing = 2 FPS, pas 40).
                self._inject_real_fps(monitoring_data, primary_game)

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

                # 5.7. Scoring temps-reel (remplace l'autoresearch)
                if self.current_game_profile:
                    score = self._score_current_workload(monitoring_data)
                    # 5.8. Pilote thermique: securite (frein d'urgence) + controle
                    # fin (sweet spot) en regime normal.
                    self._apply_thermal_control(monitoring_data, score)
                    # 5.9. Conseiller upscaling (gaming only) - APRES l'action
                    # thermique, pour refleter l'etat du frein de ce tick.
                    self._gaming_advisor(monitoring_data)

                # 5.95. Cycle de vie de l'upscaler externe (gaming only, debounce)
                self._manage_upscaler()

                # 5.97. Etage CPU (si --cpu-control): frein par paliers powercfg
                # selon la temp CPU. Tous workloads (dissipation partagee laptop).
                if self.cpu_controller is not None:
                    self.cpu_controller.update()

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
                # Sweet spot + predicteur = GAMING uniquement (jamais local_ai).
                gaming_name = game.custom_name if category == 'gaming' else None
                self.sweet_spot.set_current_game(gaming_name)
                self.thermal_predictor.set_current_game(gaming_name)
                self.thermal_controller.apply_for_workload(self.current_game_profile)
                logging.info(f"🎮 Workload actif: {game.custom_name} ({game.process_name}) [{category}/{mode}]")
                if game.is_known:
                    logging.info(f"✅ Profil connu appliqué: {self.current_game_profile['thermal_profile']}")
                else:
                    logging.info(f"📋 Profil {mode} appliqué (cible {self.current_game_profile['target_temp']}°C)")
                    # Workload inconnu: on s'appuie sur le scorer mur en temps reel
                    # (evalue chaque seconde dans la boucle), pas sur un sweep.
                    self.optimized_workloads.add(game.custom_name)
            else:
                self.current_game = None
                self.current_game_profile = None
                self.sweet_spot.set_current_game(None)
                self.thermal_predictor.set_current_game(None)
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
                'gpu_clock_current': gpu_metrics.get('clock_current', 0),

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
        """Collecte des métriques GPU via nvidia-smi (GPURealController).

        On n'utilise PLUS GPUtil: il n'est pas installe dans tous les interpreteurs
        (ex: Python310 hors conda -> import echoue -> metriques a zero). nvidia-smi
        marche partout et donne EN PLUS la puissance reelle et le clock courant.
        """
        try:
            m = self.thermal_controller.gpu_controller.get_gpu_metrics()
            if not m:
                return {}
            used = m.get('memory_used_mb', 0) or 0
            total = m.get('memory_total_mb', 0) or 0
            return {
                'usage': m.get('utilization', 0),
                'temperature': m.get('temperature', 0),
                'memory_used_mb': used,
                'memory_total_mb': total,
                'memory_percent': (used / total * 100) if total > 0 else 0,
                'power_usage': m.get('power_draw', 0),
                'clock_current': m.get('clock_current', 0),
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
        """Affichage COMPACT (tient sur un ecran, ne defile pas)."""
        # cls a chaque frame: simple et infaillible. Avec les logs en fichier,
        # l'ecran reste propre (9 lignes, pas d'empilement).
        os.system('cls' if os.name == 'nt' else 'clear')

        uptime = int(data.get('uptime_seconds', 0))
        clock = f"{uptime//3600:02d}:{(uptime%3600)//60:02d}:{uptime%60:02d}"
        print(f"🎮 GPU MONITOR · {clock} · Ctrl+C pour arreter (logs -> universal_gpu_monitor.log)")
        if self.dry_run:
            print("🧪 MODE DRY-RUN — simulation, AUCUNE action GPU reelle (caps/Afterburner/upscaler)")

        # --- Mode: jeu vs IA (le dashboard s'adapte au workload) ---
        prof = self.current_game_profile or {}
        is_ai = bool(prof) and prof.get('category', '') == 'local_ai'

        # --- Workload (1 ligne) ---
        if data.get('game_detected'):
            gi = data.get('game_info', {})
            name = gi.get('game_name', '?')
            if is_ai:
                print(f"🧠 Workload IA: {name} [cible {prof.get('target_temp','?')}°C] — gestion thermique pure")
            else:
                tag = f"[{prof.get('thermal_profile','?').upper()}, cible {prof.get('target_temp','?')}°C / {prof.get('target_fps','?')} fps]"
                print(f"🎮 Jeu: {name} {tag}")
        else:
            print(f"Workload: aucun ({data.get('all_games_count', 0)} process surveilles)")

        # --- GPU (3 lignes, barres courtes) ---
        gpu_usage = data.get('gpu_usage', 0)
        gpu_temp = data.get('gpu_temperature', 0)
        gpu_mem = data.get('gpu_memory_percent', 0)
        # Derniere colonne: FPS pour le jeu, Power/Clock pour l'IA (le LLM n'a pas de FPS).
        if is_ai:
            extra = f"Power {data.get('gpu_power_usage',0):.0f}W · Clock {data.get('gpu_clock_current',0):.0f} MHz"
        else:
            fps = data.get('fps_estimate', 0)
            extra = f"FPS {fps:.1f} (RTSS reel)" if self.fps_is_real else f"FPS~{fps:.0f} (estime)"
        print(f"Temp  {self._create_bar(gpu_temp, 100, 20)} {gpu_temp:5.1f}°C")
        print(f"Util  {self._create_bar(gpu_usage, 100, 20)} {gpu_usage:5.1f}%")
        print(f"VRAM  {self._create_bar(gpu_mem, 100, 20)} {gpu_mem:5.1f}% ({data.get('gpu_memory_used_mb',0):.0f}/{data.get('gpu_memory_total_mb',0):.0f} MB) · {extra}")

        # --- Action thermique (1 ligne, le coeur du rebranch) ---
        thermal = self.thermal_controller.get_display_status()
        print(f"🌡️  {thermal['active_action']} · cap pilote: {thermal['driver_cap']}")

        # --- Anticipation (predicteur de pics, gaming) — affiche si ca signale ---
        p = self.last_prediction
        if p is not None and getattr(p, 'recommended_action', 'none') != 'none':
            print(f"🔮 Anticipation: ~{p.predicted_temp_10s:.0f}°C dans 10s ({p.trend}) → {p.recommended_action}")

        # --- Score (2 lignes) ---
        if self.last_score is not None:
            s = self.last_score
            b = s.breakdown
            print(f"🎯 Score {self._create_bar(s.overall_score, 100, 20)} {s.overall_score:5.1f}/100 [{s.state.value.upper()}]")
            if is_ai:
                # Pas de FPS pour un LLM: on masque la dimension FPS, et on n'affiche
                # la reco que si elle est thermique (pas un message FPS hors-sujet).
                rec = ""
                if s.recommendations and 'fps' not in s.recommendations[0].lower():
                    rec = f" · 💡 {s.recommendations[0]}"
                print(f"   T{b.thermal_score:.0f} E{b.efficiency_score:.0f} S{b.stability_score:.0f} · {s.recommended_strategy.value} ({s.trend}){rec}")
            else:
                rec = f" · 💡 {s.recommendations[0]}" if s.recommendations else ""
                print(f"   T{b.thermal_score:.0f} F{b.fps_score:.0f} E{b.efficiency_score:.0f} S{b.stability_score:.0f} · {s.recommended_strategy.value} ({s.trend}){rec}")

        # --- Conseiller upscaling (gaming only, si zone injouable) ---
        if self.last_advice:
            print(f"🎮 {self.last_advice}")

        # --- Upscaler externe (statut, gaming seulement) ---
        if is_ai:
            print("🧠 Upscaler: desactive (workload IA - jamais d'upscaling sur l'entrainement)")
        else:
            print(f"🔧 Upscaler externe: {self.upscaler.status_line()}")

        # --- Systeme (1 ligne, + etage CPU si actif) ---
        cpu_extra = f" · 🧊 {self.cpu_controller.status_line()}" if self.cpu_controller is not None else ""
        print(f"💻 CPU {data.get('cpu_usage',0):.0f}% · RAM {data.get('memory_usage',0):.0f}% ({data.get('memory_available_gb',0):.1f} GB libre){cpu_extra}")
        print('', end='', flush=True)

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
        # Arrete l'upscaler externe SI c'est nous qui l'avons lance.
        self.upscaler.stop()
        # Restaure le max processor state a 100% (powercfg PERSISTE apres le
        # process - sans ca, le CPU resterait bride apres l'arret du monitor).
        if self.cpu_controller is not None:
            self.cpu_controller.release()
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

    def _score_current_workload(self, data: Dict[str, Any]):
        """Evalue le workload courant via le scorer mur (PerformanceScorer).

        Remplace le sweep autoresearch: au lieu de balayer des clocks et de se
        faire piéger par une scène hors-charge, on note la perf reelle chaque
        seconde. Le score d'efficacite penalise la sous-charge (gpu_usage bas),
        donc plus de faux positif type 1500MHz/8%-util.
        """
        if not self.current_game_profile:
            return None

        profile = self.current_game_profile
        try:
            score = self.performance_scorer.calculate_score(
                temperature=data.get('gpu_temperature', 0),
                gpu_usage=data.get('gpu_usage', 0),
                fps_current=data.get('fps_estimate', 0),
                clock_max=profile.get('max_clock_mhz', 2100),
                power_draw=data.get('gpu_power_usage', 0),
                vram_usage_percent=data.get('gpu_memory_percent', 0),
                cpu_usage=data.get('cpu_usage', 0),
                game_name=data.get('game_info', {}).get('game_name', ''),
                thermal_profile=profile.get('thermal_profile', 'medium'),
            )
            self.last_score = score
            return score
        except Exception as e:
            logging.error(f"❌ Scoring erreur: {e}")
            return None

    def _apply_thermal_control(self, data: Dict[str, Any], score) -> None:
        """Pilote thermique a deux etages:

        1. SECURITE (plancher, tous workloads): le frein d'urgence du scorer
           (heavy_cool/critical) prime des que la temp derape. Non negociable.
        2. CONTROLE FIN (gaming uniquement): en regime normal, on converge vers le
           clock optimal perf/qualite APPRIS par le sweet_spot_finder (cap continu,
           pas les paliers discrets). Le LLM/training n'a pas de FPS -> pas de
           controle fin, juste la securite.
        """
        profile = self.current_game_profile or {}
        temp = data.get('gpu_temperature', 0)
        target_temp = profile.get('target_temp', 75)
        strategy = score.recommended_strategy.value if score is not None else 'balanced'
        is_gaming = profile.get('category', '') == 'gaming'
        clock = int(data.get('gpu_clock_current', 0) or 0)
        fps = data.get('fps_estimate', 0)

        # --- Etage 0: ANTICIPATION (gaming) - predit un pic AVANT le seuil ---
        # Le predicteur (regression sur la pente) dit throttle_now si la temp va
        # depasser ~88°C dans 10s -> on freine preventivement; prepare_throttle ->
        # on bloque les hausses de clock (pas d'huile sur le feu qui arrive).
        self.last_prediction = None
        preempt_brake = False
        hold_clock = False
        if is_gaming:
            try:
                self.thermal_predictor.add_data_point(
                    temp=temp, gpu_usage=data.get('gpu_usage', 0),
                    clock_speed=clock, power_draw=data.get('gpu_power_usage', 0), fps=fps,
                )
                pred = self.thermal_predictor.predict()
                self.last_prediction = pred
                if not self.thermal_controller.emergency_active:
                    preempt_brake = pred.recommended_action == 'throttle_now'
                    hold_clock = pred.recommended_action == 'prepare_throttle'
            except Exception as e:
                logging.error(f"Predicteur thermique: {e}")

        # --- Etage 1: securite (avec anticipation) + relachement quand ca refroidit ---
        # Pic predit -> on escalade en thermal_focus (cap critical preventif) meme si
        # la temp reelle n'a pas encore atteint le seuil.
        eff_strategy = 'thermal_focus' if preempt_brake else strategy
        self.thermal_controller.apply_thermal_strategy(eff_strategy, temp, target_temp)
        if self.thermal_controller.emergency_active:
            return  # on freine: pas de controle fin tant que ca chauffe

        # --- Etage 2: controle fin sweet spot (GAMING seulement) ---
        if not is_gaming:
            return  # local_ai/browser: securite thermique seule

        # Nourrit l'apprentissage (les points invalides sont filtres en interne).
        try:
            self.sweet_spot.add_data_point(
                clock_mhz=clock, temperature=temp, fps=fps,
                gpu_usage=data.get('gpu_usage', 0),
                power_draw=data.get('gpu_power_usage', 0),
            )
        except Exception as e:
            logging.error(f"Sweet spot add_data_point: {e}")

        # Rafraichit periodiquement le sweet spot appris (~30s).
        self._analyze_counter += 1
        if self._analyze_counter >= 30:
            self._analyze_counter = 0
            try:
                self.sweet_spot.analyze_sweet_spot()
            except Exception as e:
                logging.error(f"Sweet spot analyse: {e}")

        # Recommandation temps-reel -> cap continu vers le sweet spot.
        try:
            rec = self.sweet_spot.get_real_time_recommendation(temp, fps, clock or 2100)
            action = rec.get('action')
            # Anticipation: si un pic approche (prepare_throttle), on n'AUGMENTE pas
            # le clock (on attend que ca passe). Les baisses restent autorisees.
            if hold_clock and action == 'increase_clock':
                action = 'none'
            if action not in (None, 'none') and rec.get('target_clock'):
                self.thermal_controller.apply_target_clock(int(rec['target_clock']), rec.get('reason', ''))
        except Exception as e:
            logging.error(f"Sweet spot reco: {e}")

    def _inject_real_fps(self, data: Dict[str, Any], primary_game) -> None:
        """Remplace le fps_estimate (util-based, trompeur) par les VRAIS FPS RTSS
        quand un jeu est detecte. Sans RTSS, on garde l'estimation."""
        self.fps_is_real = False
        if not primary_game or not self.rtss.available:
            return
        try:
            # filtre = nom du process sans extension (ex: Cyberpunk2077.exe -> cyberpunk2077)
            name = (primary_game.process_name or "").lower().replace(".exe", "")
            fps = self.rtss.read_max_fps(name) if name else 0.0
            if fps > 0:
                data['fps_estimate'] = round(fps, 1)
                self.fps_is_real = True
        except Exception as e:
            logging.error(f"RTSS read erreur: {e}")

    def _gaming_advisor(self, data: Dict[str, Any]) -> Optional[str]:
        """Conseiller upscaling - GATING GAMING UNIQUEMENT.

        Ne se declenche QUE pour category == 'gaming'. Pour local_ai (Ollama,
        training GPT-2) il ne fait jamais rien -> l'agent reste pur thermique.

        Detecte la zone injouable: FPS REELS tres bas + GPU sature (compute-bound,
        donc c'est les settings, pas un menu) -> recommande l'upscaling.
        """
        self.last_advice = None
        profile = self.current_game_profile or {}
        if profile.get('category', 'gaming') != 'gaming':
            return None  # local_ai / browser: pas de conseil upscaling (jamais Ollama/training)

        fps = data.get('fps_estimate', 0)
        util = data.get('gpu_usage', 0)
        temp = data.get('gpu_temperature', 0)
        target_fps = profile.get('target_fps', 45)

        # --- Cas 1 (PRIORITAIRE): l'agent FREINE pour la chaleur ---
        # DLSS reduit la charge -> moins de chaleur -> l'agent arrete de freiner
        # -> on recupere les FPS perdus au cap, SANS le compromis thermique.
        # Ne depend PAS de RTSS: on connait l'etat du frein de facon fiable.
        tc = self.thermal_controller
        if getattr(tc, 'emergency_active', False):
            cap = getattr(tc, 'emergency_profile', None) or 'cap thermique'
            self.last_advice = (
                f"L'agent BRIDE le GPU ({cap}, {temp:.0f}°C) -> tu perds des FPS pour "
                f"sauver la temp. Active DLSS Performance Ultra: -charge -> -chaleur -> "
                f"l'agent relache -> tu RECUPERES les FPS sans le compromis thermique."
            )
            return self.last_advice

        # --- Cas 2: zone injouable via VRAIS FPS (RTSS) + GPU sature ---
        if self.fps_is_real and fps > 0 and fps < min(25.0, target_fps * 0.6) and util >= 92:
            gain = max(2, int(target_fps / fps))
            self.last_advice = (
                f"ZONE INJOUABLE ({fps:.1f} fps reels, GPU {util:.0f}%) -> "
                f"active DLSS Performance Ultra + Ray Reconstruction "
                f"(ou baisse Path Tracing/RT) · gain attendu ~{gain}x sans cout thermique"
            )
        return self.last_advice

    def _manage_upscaler(self) -> None:
        """Cycle de vie de l'upscaler externe - GAMING UNIQUEMENT.

        - jeu (category gaming) actif -> lance l'upscaler (s'il est installe)
        - plus de jeu pendant ~10 ticks -> l'arrete (libere les ressources)
        Jamais lance pour local_ai (Ollama/training) ni browser.
        Le debounce evite de le lancer/couper en boucle quand la detection de
        process principal clignote (Edge/Ollama qui passent 'principal').
        """
        if not self.upscaler.available:
            return  # rien d'installe: no-op silencieux

        profile = self.current_game_profile or {}
        is_gaming = bool(profile) and profile.get('category', '') == 'gaming'

        if is_gaming:
            self._no_game_ticks = 0
            if not self.upscaler.running:
                self.upscaler.start()
        else:
            self._no_game_ticks += 1
            if self.upscaler.running and self._no_game_ticks >= self._STOP_AFTER_TICKS:
                self.upscaler.stop()


def main():
    """Point d'entrée principal"""
    import argparse
    parser = argparse.ArgumentParser(
        description="Universal GPU Monitor - surveillance + optimisation thermique adaptative."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simulation: detecte, score et affiche, mais N'APPLIQUE aucune action "
             "GPU reelle (caps clocks, Afterburner, upscaler). Sans risque pour tester.",
    )
    parser.add_argument(
        "--gpu-index", type=int, default=0, metavar="N",
        help="Index du GPU a surveiller/controler (multi-GPU). Defaut 0 (mono-GPU).",
    )
    parser.add_argument(
        "--interval", type=float, default=float(os.getenv("MONITOR_INTERVAL", "1.0")),
        metavar="S", help="Intervalle de polling en secondes (ou env MONITOR_INTERVAL). Defaut 1.0.",
    )
    parser.add_argument(
        "--cpu-control", action="store_true",
        help="PROTOTYPE: active l'etage CPU - frein par paliers de 'max processor "
             "state' (powercfg) selon la temp CPU (zone ACPI). Restaure 100%% a l'arret. "
             "Respecte --dry-run.",
    )
    args = parser.parse_args()

    flags = []
    if args.dry_run:
        flags.append("DRY-RUN")
    if args.gpu_index:
        flags.append(f"GPU#{args.gpu_index}")
    if args.cpu_control:
        flags.append("CPU-CONTROL")
    suffix = f" [{', '.join(flags)}]" if flags else ""
    print("🎮 UNIVERSAL GPU MONITOR - DÉMARRAGE" + suffix)

    monitor = UniversalGPUMonitor(
        monitor_interval=args.interval,
        max_history=1000,
        dry_run=args.dry_run,
        gpu_index=args.gpu_index,
        cpu_control=args.cpu_control,
    )

    monitor.start_monitoring()

if __name__ == "__main__":
    main()
