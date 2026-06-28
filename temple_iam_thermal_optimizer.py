"""
TEMPLE IAM THERMAL OPTIMIZER - OPTIMISATION THERMIQUE DIVINE !
Objectif : Optimisation automatique de la temperature GPU sans toucher aux parametres du jeu
VERSION UNIVERSELLE : Fonctionne avec N'IMPORTE QUEL JEU

CONTROLE REEL GPU via nvidia-smi (plus de simulation!)
- Lock GPU Clocks : REEL
- Ajustement dynamique : REEL
- Protection thermique : REEL

PLUS ULTRA ! DATTEBAYO !
"""

import time
import threading
import psutil
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List

from universal_game_detector import GAME_DETECTOR, DetectedGame
from gpu_real_controller import GPU_CONTROLLER, GPURealController, GPUControlCapability
from fps_monitor import FPS_MONITOR, FPSMonitor
from thermal_ml_predictor import THERMAL_PREDICTOR, ThermalMLPredictor
from sweet_spot_finder import SWEET_SPOT_FINDER, SweetSpotFinder
from dashboard_client import DASHBOARD_CLIENT, DashboardClient
from performance_scorer import PERFORMANCE_SCORER, PerformanceScorer, PerformanceState, OptimizationStrategy

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='🔥 %(asctime)s - %(levelname)s - %(message)s')

class TempleIAMThermalOptimizer:
    """Optimiseur thermique Temple IAM - REFROIDISSEMENT DIVIN AUTOMATIQUE UNIVERSEL !"""

    def __init__(self):
        """Initialisation de l'optimiseur thermique divin universel"""
        self.is_running = False
        self.optimization_active = False
        self.thermal_data = []
        self.optimization_history = []

        # NOUVEAU: Controleur GPU REEL (pas de simulation!)
        self.gpu_controller = GPU_CONTROLLER
        self.real_control_enabled = self.gpu_controller.capabilities != GPUControlCapability.READ_ONLY

        # Detecteur de jeux universel
        self.game_detector = GAME_DETECTOR
        self.current_game: Optional[DetectedGame] = None
        self.current_game_profile: Optional[Dict[str, Any]] = None

        # Configuration thermique (sera mise a jour selon le jeu)
        self.thermal_config = {
            'target_temp': 75.0,  # Temperature cible (C)
            'critical_temp': 85.0,  # Temperature critique (C)
            'safe_temp': 70.0,  # Temperature sure (C)
            'monitor_interval': 2.0,  # Intervalle de monitoring (secondes)
            'optimization_cooldown': 5.0,  # Reduit! Reactions plus rapides
            'max_history': 500  # Points de donnees maximum
        }

        # Seuils d'optimisation LAPTOP GAMING (seront mis a jour selon le profil du jeu)
        self.optimization_thresholds = {
            'temp_warning': 83.0,  # Debut optimisation legere - LAPTOP OK jusqu'a 83
            'temp_aggressive': 86.0,  # Optimisation aggressive
            'temp_critical': 88.0,  # Optimisation critique
            'temp_emergency': 90.0  # Mode urgence
        }

        # Etat des optimisations
        self.current_optimizations = {}
        self.last_optimization_time = 0

        # NOUVELLES STATS AVANCÉES pour exploitation GPU optimale
        self.advanced_stats = {
            'total_underutilized_time': 0,      # Temps GPU sous-exploité (secondes)
            'total_boost_time': 0,              # Temps en mode boost (secondes)
            'total_throttle_time': 0,           # Temps en throttle (secondes)
            'boost_activations': 0,             # Nombre d'activations boost
            'bottleneck_cpu_count': 0,          # Détections CPU bottleneck
            'bottleneck_vram_count': 0,         # Détections VRAM bottleneck
            'avg_efficiency_score': 0,          # Score efficacité moyen
            'efficiency_samples': [],           # Échantillons pour moyenne
            'peak_performance_time': 0,         # Temps en performance optimale
            'last_boost_check': 0               # Dernier check boost
        }

        # Mode BOOST automatique
        self.boost_mode_enabled = True
        self.boost_active = False
        self.boost_cooldown = 10.0  # Secondes entre les checks boost

        # FPS Monitor - NOUVEAU !
        self.fps_monitor = FPS_MONITOR
        self.fps_session_active = False
        self.fps_data_history = []

        # ML Predictor - NOUVEAU !
        self.ml_predictor = THERMAL_PREDICTOR
        self.ml_preemptive_throttle = True  # Activer le throttle préventif ML

        # Sweet Spot Finder - NOUVEAU !
        self.sweet_spot_finder = SWEET_SPOT_FINDER
        self.sweet_spot_enabled = True  # Activer les recommandations Sweet Spot

        # Dashboard Client - NOUVEAU !
        self.dashboard_client = DASHBOARD_CLIENT
        self.dashboard_enabled = True  # Activer l'envoi au dashboard web

        # Performance Scorer - NOUVEAU !
        self.performance_scorer = PERFORMANCE_SCORER
        self.score_based_decisions = True  # Activer les decisions basees sur le score
        self.current_score = None  # Dernier score calcule

        # Initialisation GPU
        self._initialize_gpu_control()

        logging.info("Temple IAM Thermal Optimizer UNIVERSEL initialise")
        if self.real_control_enabled:
            logging.info("CONTROLE GPU REEL ACTIVE via nvidia-smi!")
        else:
            logging.warning("Controle GPU limite - mode monitoring seulement")
    
    def _initialize_gpu_control(self):
        """Initialisation du contrôle GPU - CONTRÔLE DIVIN ! ⚡"""
        try:
            # Import GPU monitoring
            import GPUtil
            self.gpu_available = True
            
            # Test initial
            gpus = GPUtil.getGPUs()
            if gpus:
                self.gpu = gpus[0]
                self.gpu_name = self.gpu.name
                logging.info(f"✅ GPU détecté: {self.gpu_name}")
                
                # Initialisation des paramètres de base
                self._initialize_gpu_parameters()
            else:
                logging.warning("⚠️ Aucun GPU détecté")
                self.gpu_available = False
                
        except ImportError:
            logging.warning("⚠️ GPUtil non disponible - Contrôle GPU limité")
            self.gpu_available = False
        except Exception as e:
            logging.error(f"❌ Erreur initialisation GPU: {str(e)}")
            self.gpu_available = False
    
    def _initialize_gpu_parameters(self):
        """Initialisation des paramètres GPU - PARAMÈTRES DIVINS ! ⚙️"""
        try:
            # Paramètres de base pour optimisation
            self.gpu_parameters = {
                'base_fan_speed': 50,  # Vitesse ventilateur de base (%)
                'base_power_limit': 100,  # Limite de puissance de base (%)
                'base_clock_speed': 0,  # Décalage horloge de base (MHz)
                'base_memory_clock': 0,  # Décalage mémoire de base (MHz)
                'base_voltage': 0,  # Décalage tension de base (mV)
                'max_fan_speed': 100,  # Vitesse ventilateur maximale (%)
                'min_power_limit': 70,  # Limite de puissance minimale (%)
                'max_clock_reduction': -200,  # Réduction horloge maximale (MHz)
                'max_memory_reduction': -500,  # Réduction mémoire maximale (MHz)
                'max_voltage_reduction': -100  # Réduction tension maximale (mV)
            }
            
            logging.info("✅ Paramètres GPU initialisés")
            
        except Exception as e:
            logging.error(f"❌ Erreur initialisation paramètres GPU: {str(e)}")
    
    def start_thermal_optimization(self):
        """Démarrage de l'optimisation thermique - OPTIMISATION DIVINE ! 🚀"""
        logging.info("🔥 DÉMARRAGE OPTIMISATION THERMIQUE TEMPLE IAM !")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        try:
            # Démarrage du monitoring et optimisation en continu
            self._run_thermal_optimization_loop()
            
        except KeyboardInterrupt:
            logging.info("🛑 Arrêt manuel de l'optimisation...")
        except Exception as e:
            logging.error(f"❌ Erreur optimisation: {str(e)}")
        finally:
            self.stop_thermal_optimization()
    
    def _run_thermal_optimization_loop(self):
        """Boucle d'optimisation thermique - BOUCLE DIVINE ! 🔄"""
        print("\n" + "="*80)
        print("🔥 TEMPLE IAM THERMAL OPTIMIZER - OPTIMISATION DIVINE EN COURS")
        print("="*80)
        print("💡 Ce système optimise automatiquement la température GPU")
        print("💡 Sans toucher aux paramètres du jeu !")
        print("💡 Appuie sur Ctrl+C pour arrêter")
        if self.dashboard_enabled:
            print("📊 Dashboard web: http://localhost:3000")
        print("="*80)

        # Démarrer le client dashboard
        if self.dashboard_enabled:
            self.dashboard_client.start()
            logging.info("📊 Dashboard Client démarré - Données envoyées en temps réel")
        
        while self.is_running:
            try:
                # Collecte des données thermiques
                thermal_data = self._collect_thermal_data()
                
                # Stockage des données
                self.thermal_data.append(thermal_data)
                if len(self.thermal_data) > self.thermal_config['max_history']:
                    self.thermal_data.pop(0)
                
                # Affichage temps réel
                self._display_thermal_status(thermal_data)
                
                # Analyse et optimisation automatique
                self._analyze_and_optimize(thermal_data)

                # Envoi au Dashboard Web
                if self.dashboard_enabled:
                    self._send_to_dashboard(thermal_data)

                # Attente avant la prochaine itération
                time.sleep(self.thermal_config['monitor_interval'])
                
            except Exception as e:
                logging.error(f"❌ Erreur boucle optimisation: {str(e)}")
                time.sleep(5)
    
    def _collect_thermal_data(self) -> Dict[str, Any]:
        """Collecte des données thermiques - COLLECTE DIVINE ! 📊"""
        try:
            timestamp = datetime.now()

            # Métriques GPU
            gpu_metrics = self._get_gpu_thermal_metrics()

            # Métriques système
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            # Détection universelle de jeux
            detected_games = self.game_detector.detect_running_games()
            primary_game = self.game_detector.get_primary_game()

            # Mise à jour du jeu actuel et de son profil
            self._update_game_profile(primary_game)

            # Démarrer/arrêter session FPS selon le jeu
            if primary_game and not self.fps_session_active:
                self.fps_monitor.start_session(primary_game.custom_name)
                self.fps_session_active = True
                logging.info(f"🎮 Session FPS démarrée pour {primary_game.custom_name}")

                # ML: Définir le jeu actuel pour l'apprentissage
                self.ml_predictor.set_current_game(primary_game.custom_name)

                # Sweet Spot: Définir le jeu actuel
                self.sweet_spot_finder.set_current_game(primary_game.custom_name)

            elif not primary_game and self.fps_session_active:
                self.fps_monitor.stop_session()
                self.fps_session_active = False
                logging.info("🛑 Session FPS arrêtée - Aucun jeu détecté")

                # ML: Arrêter l'apprentissage
                self.ml_predictor.set_current_game(None)

                # Sweet Spot: Arrêter l'analyse
                self.sweet_spot_finder.set_current_game(None)

            # Informations sur le jeu actuel
            game_info = {}
            if primary_game:
                game_info = {
                    'game_name': primary_game.custom_name,
                    'process_name': primary_game.process_name,
                    'is_known': primary_game.is_known,
                    'thermal_profile': self.current_game_profile.get('thermal_profile', 'medium') if self.current_game_profile else 'medium'
                }

            # Temps de fonctionnement
            uptime = (timestamp - self.start_time).total_seconds() if self.start_time else 0

            return {
                'timestamp': timestamp,
                'uptime_seconds': uptime,
                'gpu_temperature': gpu_metrics.get('temperature', 0),
                'gpu_usage': gpu_metrics.get('usage', 0),
                'gpu_fan_speed': gpu_metrics.get('fan_speed', 0),
                'gpu_power_usage': gpu_metrics.get('power_usage', 0),
                'gpu_clock_speed': gpu_metrics.get('clock_speed', 0),
                'gpu_memory_clock': gpu_metrics.get('memory_clock', 0),
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'game_detected': primary_game is not None,
                'game_info': game_info,
                'all_games_count': len(detected_games),
                'optimization_active': self.optimization_active,
                'current_optimizations': self.current_optimizations.copy()
            }

        except Exception as e:
            logging.error(f"❌ Erreur collecte données thermiques: {str(e)}")
            return {
                'timestamp': datetime.now(),
                'error': str(e)
            }
    
    def _get_gpu_thermal_metrics(self) -> Dict[str, Any]:
        """Collecte des métriques thermiques GPU - MÉTRIQUES DIVINES ! 🌡️

        UTILISE nvidia-smi directement pour des données fiables !
        """
        try:
            # PRIORITÉ 1: Utiliser gpu_controller (nvidia-smi) - PLUS FIABLE !
            if self.real_control_enabled:
                gpu_metrics = self.gpu_controller.get_gpu_metrics()
                if gpu_metrics and gpu_metrics.get('temperature', 0) > 0:
                    return {
                        'temperature': gpu_metrics.get('temperature', 0),
                        'usage': gpu_metrics.get('utilization', 0),  # nvidia-smi utilise 'utilization'
                        'fan_speed': gpu_metrics.get('fan_speed', -1),
                        'power_usage': gpu_metrics.get('power_draw', 0),
                        'clock_speed': gpu_metrics.get('clock_current', 0),
                        'memory_clock': gpu_metrics.get('memory_clock', 0)
                    }

            # FALLBACK: Utiliser GPUtil si nvidia-smi échoue
            if self.gpu_available:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    return {
                        'temperature': gpu.temperature if gpu.temperature else 0,
                        'usage': (gpu.load * 100) if gpu.load else 0,
                        'fan_speed': getattr(gpu, 'fan', -1),
                        'power_usage': getattr(gpu, 'power', 0),
                        'clock_speed': getattr(gpu, 'clock', 0),
                        'memory_clock': getattr(gpu, 'memory_clock', 0)
                    }

            return {
                'temperature': 0,
                'usage': 0,
                'fan_speed': -1,
                'power_usage': 0,
                'clock_speed': 0,
                'memory_clock': 0
            }

        except Exception as e:
            logging.error(f"❌ Erreur métriques thermiques GPU: {str(e)}")
            return {
                'temperature': 0,
                'usage': 0,
                'fan_speed': -1,
                'power_usage': 0,
                'clock_speed': 0,
                'memory_clock': 0
            }
    
    def _update_game_profile(self, game: Optional[DetectedGame]):
        """Met à jour le profil du jeu actuel et les seuils thermiques

        NOUVELLE APPROCHE PROACTIVE :
        - ULTRA : Cible 65°C - Jeux très lourds (Teardown, Flight Sim, Cities Skylines 2)
        - EXTREME : Cible 70°C - Jeux AAA lourds (Cyberpunk)
        - HIGH : Cible 75°C - AAA standard
        - MEDIUM : Cible 75°C - Standard
        - LOW : Cible 70°C - Jeux légers
        - ESPORT : Cible 80°C - Priorité FPS, tolère plus de chaleur
        """
        if game != self.current_game:
            if game:
                self.current_game = game
                self.current_game_profile = self.game_detector.get_game_optimization_profile(game)

                # Mise à jour des seuils thermiques selon le profil
                target_temp = self.current_game_profile.get('target_temp', 75.0)
                thermal_profile = self.current_game_profile.get('thermal_profile', 'medium')

                self.thermal_config['target_temp'] = target_temp

                # NOUVEAUX SEUILS PROACTIFS - TA LOGIQUE !
                # ULTRA/EXTREME: 65°C | HIGH: 70°C | MEDIUM/LOW: 75°C | ESPORT: 80°C
                thermal_adjustments = {
                    'ultra': {'warning': 0, 'aggressive': 3, 'critical': 7, 'emergency': 13},    # Cible 65°C
                    'extreme': {'warning': 0, 'aggressive': 3, 'critical': 7, 'emergency': 13},  # Cible 65°C
                    'high': {'warning': 0, 'aggressive': 3, 'critical': 7, 'emergency': 12},     # Cible 70°C
                    'medium': {'warning': 0, 'aggressive': 2, 'critical': 5, 'emergency': 10},   # Cible 75°C
                    'low': {'warning': 0, 'aggressive': 2, 'critical': 5, 'emergency': 10},      # Cible 75°C
                    'esport': {'warning': 0, 'aggressive': 2, 'critical': 5, 'emergency': 8}     # Cible 80°C
                }

                adjustments = thermal_adjustments.get(thermal_profile, thermal_adjustments['medium'])
                self.optimization_thresholds['temp_warning'] = target_temp + adjustments['warning']
                self.optimization_thresholds['temp_aggressive'] = target_temp + adjustments['aggressive']
                self.optimization_thresholds['temp_critical'] = target_temp + adjustments['critical']
                self.optimization_thresholds['temp_emergency'] = target_temp + adjustments['emergency']

                # Affichage info profil
                profile_icons = {
                    'ultra': '🔥🔥🔥',
                    'extreme': '🔥🔥',
                    'high': '🔥',
                    'medium': '🌡️',
                    'low': '❄️',
                    'esport': '🎯'
                }
                icon = profile_icons.get(thermal_profile, '🌡️')

                logging.info(f"🎮 Profil appliqué: {game.custom_name}")
                logging.info(f"{icon} Mode: {thermal_profile.upper()} - Cible: {target_temp}°C")
                logging.info(f"   Seuils LAPTOP: Warning={self.optimization_thresholds['temp_warning']}°C, "
                           f"Agressif={self.optimization_thresholds['temp_aggressive']}°C, "
                           f"Critique={self.optimization_thresholds['temp_critical']}°C, "
                           f"Emergency={self.optimization_thresholds['temp_emergency']}°C")
            else:
                self.current_game = None
                self.current_game_profile = None
    
    def _display_thermal_status(self, data: Dict[str, Any]):
        """Affichage du statut thermique - VISION DIVINE ! 👁️"""
        try:
            # Nettoyage de l'écran
            os.system('cls' if os.name == 'nt' else 'clear')

            # En-tête
            print("\n" + "="*80)
            print(f"🔥 TEMPLE IAM THERMAL OPTIMIZER UNIVERSEL - {data['timestamp'].strftime('%H:%M:%S')}")
            print("="*80)

            # Statut du jeu détecté
            if data.get('game_detected', False):
                game_info = data.get('game_info', {})
                status_icon = "✅" if game_info.get('is_known') else "🆕"
                thermal_profile = game_info.get('thermal_profile', 'medium')

                # Icônes et descriptions pour chaque profil - LAPTOP GAMING !
                profile_display = {
                    'ultra': ('🔥🔥🔥', 'ULTRA (Cible 80°C - Refroidissement AGRESSIF)'),
                    'extreme': ('🔥🔥', 'EXTREME (Cible 83°C - Jeux AAA lourds)'),
                    'high': ('🔥', 'HIGH (Cible 82°C - AAA standard)'),
                    'medium': ('🌡️', 'MEDIUM (Cible 83°C - Standard)'),
                    'low': ('❄️', 'LOW (Cible 85°C - Jeux légers)'),
                    'esport': ('🎯', 'ESPORT (Cible 87°C - Priorité FPS)')
                }

                icon, profile_desc = profile_display.get(thermal_profile, ('🌡️', thermal_profile.upper()))

                print(f"{status_icon} JEU: {game_info.get('game_name', 'Inconnu')} - OPTIMISATION THERMIQUE ACTIVE !")
                print(f"   {icon} Profil: {profile_desc}")
            else:
                print("⏳ AUCUN JEU DÉTECTÉ - MONITORING ACTIF")
                if data.get('all_games_count', 0) > 0:
                    print(f"   ({data.get('all_games_count')} processus de jeu surveillés)")

            print("="*80)
            
            # Métriques thermiques - utiliser les vraies données de nvidia-smi
            temp = data.get('gpu_temperature', 0)
            temp_status = self._get_temperature_status(temp)

            # Récupérer métriques GPU réelles
            gpu_metrics = self.gpu_controller.get_gpu_metrics() if self.real_control_enabled else {}
            power_draw = gpu_metrics.get('power_draw', 0)
            fan_speed = gpu_metrics.get('fan_speed', -1)

            print(f"🌡️ TEMPÉRATURE GPU: {temp:.1f}°C {temp_status}")
            print(f"🖥️ USAGE GPU: {data.get('gpu_usage', 0):.1f}%")

            # Ventilateur - afficher N/A si non disponible (laptop)
            # fan_speed = -1 signifie non disponible, 0 peut être valide (ventilo éteint)
            if fan_speed == -1 or fan_speed == 0:
                print(f"💨 VENTILATEUR: N/A (contrôlé par BIOS)")
            else:
                print(f"💨 VENTILATEUR: {fan_speed:.0f}%")

            # Puissance
            if power_draw > 0:
                print(f"⚡ PUISSANCE: {power_draw:.1f}W")
            else:
                print(f"⚡ PUISSANCE: N/A")

            # FPS en temps réel - NOUVEAU !
            if self.fps_session_active:
                fps_data = self.fps_monitor.get_current_data()
                if fps_data.fps_current > 0:
                    # Indicateur de stabilité FPS
                    if fps_data.fps_current >= fps_data.fps_avg * 0.9:
                        fps_icon = "🟢"
                    elif fps_data.fps_current >= fps_data.fps_avg * 0.7:
                        fps_icon = "🟡"
                    else:
                        fps_icon = "🔴"

                    print(f"\n🎮 FPS TEMPS RÉEL ({fps_data.source.upper()}):")
                    print(f"   {fps_icon} Actuel: {fps_data.fps_current:.1f} FPS ({fps_data.frametime_ms:.1f}ms)")
                    print(f"   📊 Moyenne: {fps_data.fps_avg:.1f} FPS")
                    print(f"   📉 Min: {fps_data.fps_min:.1f} | Max: {fps_data.fps_max:.1f}")
                    if fps_data.fps_1_percent_low > 0:
                        print(f"   📈 1% Low: {fps_data.fps_1_percent_low:.1f} FPS")
                else:
                    print(f"\n🎮 FPS: En attente de données ({fps_data.source})...")

            # ML PRÉDICTION - NOUVEAU !
            if self.ml_preemptive_throttle and len(self.ml_predictor.current_buffer) >= 10:
                prediction = self.ml_predictor.predict()

                # Icônes selon la tendance
                trend_icons = {
                    'rising': '📈 MONTÉE',
                    'stable': '➡️ STABLE',
                    'falling': '📉 DESCENTE',
                    'unknown': '❓ INCONNU'
                }
                trend_display = trend_icons.get(prediction.trend, '❓')

                # Couleur spike probability
                if prediction.spike_probability < 0.3:
                    spike_icon = "🟢"
                elif prediction.spike_probability < 0.6:
                    spike_icon = "🟡"
                else:
                    spike_icon = "🔴"

                print(f"\n🧠 ML PRÉDICTION ({prediction.confidence*100:.0f}% confiance):")
                print(f"   {trend_display}")
                print(f"   🔮 Prédit dans 5s: {prediction.predicted_temp_5s:.1f}°C")
                print(f"   🔮 Prédit dans 10s: {prediction.predicted_temp_10s:.1f}°C")
                print(f"   🔮 Prédit dans 30s: {prediction.predicted_temp_30s:.1f}°C")
                print(f"   {spike_icon} Probabilité spike: {prediction.spike_probability*100:.0f}%")

                # Action recommandée
                if prediction.recommended_action == 'throttle_now':
                    print(f"   🚨 ACTION: THROTTLE MAINTENANT !")
                elif prediction.recommended_action == 'prepare_throttle':
                    print(f"   ⚠️ ACTION: Préparer throttle préventif")
                else:
                    print(f"   ✅ ACTION: Aucune (température stable)")

                # Pattern appris pour le jeu actuel
                if self.current_game:
                    pattern_summary = self.ml_predictor.get_pattern_summary()
                    if pattern_summary:
                        samples = pattern_summary.get('samples', 0)
                        if samples > 0:
                            print(f"   📊 Données apprises: {samples} échantillons")
                            print(f"      Temp stabilisation: {pattern_summary.get('stabilization_temp', 0)}°C")
                            if pattern_summary.get('temp_rise_rate', 0) > 0:
                                print(f"      Taux montée: +{pattern_summary.get('temp_rise_rate', 0):.2f}°C/s")

            # SWEET SPOT FINDER - NOUVEAU !
            if self.sweet_spot_enabled and self.current_game:
                sweet_spot_summary = self.sweet_spot_finder.get_game_summary()

                if sweet_spot_summary:
                    status = sweet_spot_summary.get('status', 'unknown')

                    if status == 'collecting':
                        # En cours de collecte
                        total_points = sweet_spot_summary.get('total_points', 0)
                        print(f"\n🎯 SWEET SPOT FINDER:")
                        print(f"   📊 Collecte en cours... ({total_points} points)")
                        if total_points >= 100:
                            print(f"   ⏳ Analyse disponible bientôt (min: 100 points par niveau)")
                    elif status == 'analyzed':
                        # Résultat disponible
                        print(f"\n🎯 SWEET SPOT TROUVÉ ({sweet_spot_summary.get('confidence', 0):.0f}% confiance):")
                        print(f"   ⚡ Clock optimal: {sweet_spot_summary.get('optimal_clock_mhz', 0)} MHz")
                        print(f"   🌡️ Temp cible: {sweet_spot_summary.get('optimal_temp_target', 0):.0f}°C")
                        print(f"   🎮 FPS attendu: {sweet_spot_summary.get('expected_fps', 0):.1f}")
                        print(f"   📊 Efficacité: {sweet_spot_summary.get('efficiency_score', 0):.2f}")

                        # Recommandation temps réel
                        if data.get('gpu_temperature', 0) > 0:
                            fps_current = 0
                            if self.fps_session_active:
                                fps_data_rt = self.fps_monitor.get_current_data()
                                fps_current = fps_data_rt.fps_current if fps_data_rt else 0

                            gpu_metrics_rt = self.gpu_controller.get_gpu_metrics() if self.real_control_enabled else {}
                            current_clock = gpu_metrics_rt.get('clock_current', 0)

                            rec = self.sweet_spot_finder.get_real_time_recommendation(
                                current_temp=data.get('gpu_temperature', 0),
                                current_fps=fps_current,
                                current_clock=current_clock
                            )

                            if rec['action'] != 'none':
                                action_icons = {
                                    'reduce_clock': '📉',
                                    'increase_clock': '📈',
                                    'adjust_clock': '🔧'
                                }
                                icon = action_icons.get(rec['action'], '💡')
                                print(f"   {icon} Recommandation: {rec['reason']}")

            # ========== PERFORMANCE SCORE - SCORE GLOBAL ==========
            if self.current_score:
                score = self.current_score
                state_display = {
                    PerformanceState.EMERGENCY: ('🚨', 'URGENCE', '\033[91m'),     # Rouge
                    PerformanceState.POOR: ('🔴', 'FAIBLE', '\033[91m'),            # Rouge
                    PerformanceState.ACCEPTABLE: ('🟡', 'ACCEPTABLE', '\033[93m'), # Jaune
                    PerformanceState.GOOD: ('🟢', 'BON', '\033[92m'),               # Vert
                    PerformanceState.EXCELLENT: ('💚', 'EXCELLENT', '\033[92m'),   # Vert
                    PerformanceState.PEAK: ('⭐', 'OPTIMAL', '\033[96m')            # Cyan
                }
                icon, label, color = state_display.get(score.state, ('❓', 'INCONNU', '\033[0m'))
                reset = '\033[0m'

                # Barre de progression visuelle
                bar_length = 30
                filled = int(score.overall_score / 100 * bar_length)
                bar = '█' * filled + '░' * (bar_length - filled)

                print(f"\n{'='*60}")
                print(f"🎯 SCORE PERFORMANCE GLOBAL")
                print(f"{'='*60}")
                print(f"   [{bar}] {score.overall_score:.0f}/100")
                print(f"   {icon} État: {label}")
                print(f"   📊 Détails:")
                print(f"      🌡️ Thermique: {score.breakdown.thermal_score:.0f}/100 - {score.breakdown.thermal_details}")
                print(f"      🎮 FPS: {score.breakdown.fps_score:.0f}/100 - {score.breakdown.fps_details}")
                print(f"      ⚡ Efficacité: {score.breakdown.efficiency_score:.0f}/100 - {score.breakdown.efficiency_details}")
                print(f"      📈 Stabilité: {score.breakdown.stability_score:.0f}/100 - {score.breakdown.stability_details}")

                # Tendance
                trend_icons = {'rising': '📈', 'stable': '➡️', 'falling': '📉'}
                trend_icon = trend_icons.get(score.trend, '❓')
                if score.score_delta != 0:
                    print(f"   {trend_icon} Tendance: {score.trend.upper()} ({score.score_delta:+.1f})")

                # Strategie recommandee
                strategy_display = {
                    OptimizationStrategy.EMERGENCY_THROTTLE: '🚨 URGENCE - Throttle agressif',
                    OptimizationStrategy.THERMAL_FOCUS: '🌡️ THERMIQUE - Priorité refroidissement',
                    OptimizationStrategy.BALANCED: '⚖️ ÉQUILIBRÉ - Balance perf/temp',
                    OptimizationStrategy.PERFORMANCE: '⚡ PERFORMANCE - Priorité FPS',
                    OptimizationStrategy.BOOST: '🚀 BOOST - GPU peut être poussé !'
                }
                print(f"   💡 Stratégie: {strategy_display.get(score.recommended_strategy, 'Inconnue')}")

                # Recommandations (max 2)
                if score.recommendations:
                    print(f"   📝 Recommandations:")
                    for rec in score.recommendations[:2]:
                        print(f"      • {rec}")

                print(f"{'='*60}")

            # Optimisations actives + Status controle reel
            print(f"\n--- CONTROLE GPU ---")
            if self.real_control_enabled:
                print(f"Mode: CONTROLE REEL (nvidia-smi)")
                if self.gpu_controller.current_profile:
                    profile = self.gpu_controller.CLOCK_PROFILES[self.gpu_controller.current_profile]
                    print(f"Profil: {profile.name} (max {profile.max_clock_mhz} MHz)")
                else:
                    print(f"Profil: Aucun (clocks libres)")
            else:
                print(f"Mode: Monitoring seulement")

            # Afficher le niveau d'optimisation actuel basé sur la température
            current_level = self._determine_optimization_level(data.get('gpu_temperature', 0))
            if current_level > 0:
                print(f"\nOPTIMISATIONS ACTIVES (Niveau {current_level}):")
                for opt_name, opt_value in data.get('current_optimizations', {}).items():
                    print(f"   {opt_name}: {opt_value}")
            else:
                print(f"\n✅ AUCUN THROTTLE NÉCESSAIRE (temp < seuil warning)")
                if data.get('current_optimizations'):
                    print(f"   (Dernières optimisations gardées en mémoire)")
            
            # Métriques système
            print(f"\n🧠 SYSTÈME:")
            print(f"   CPU: {data.get('cpu_usage', 0):.1f}%")
            print(f"   RAM: {data.get('memory_usage', 0):.1f}%")

            # NOUVELLES STATS AVANCÉES
            advanced = data.get('advanced_stats', {})
            if advanced:
                print(f"\n📈 STATS AVANCÉES:")

                # Headroom thermique avec indicateur visuel
                headroom = advanced.get('thermal_headroom', 0)
                if headroom > 15:
                    headroom_icon = "🟢"
                    headroom_status = "LARGE MARGE"
                elif headroom > 5:
                    headroom_icon = "🟡"
                    headroom_status = "MARGE OK"
                elif headroom > 0:
                    headroom_icon = "🟠"
                    headroom_status = "MARGE FAIBLE"
                else:
                    headroom_icon = "🔴"
                    headroom_status = "DÉPASSÉ"
                print(f"   {headroom_icon} Headroom thermique: {headroom:+.1f}°C ({headroom_status})")

                # Clock utilization
                clock_util = advanced.get('clock_utilization', 0)
                clock_current = advanced.get('clock_current', 0)
                clock_max = advanced.get('clock_max', 0)
                print(f"   ⚡ Clocks: {clock_current}/{clock_max} MHz ({clock_util:.0f}%)")

                # VRAM
                vram_percent = advanced.get('vram_usage_percent', 0)
                vram_headroom = advanced.get('vram_headroom_mb', 0)
                vram_icon = "🟢" if vram_percent < 70 else "🟡" if vram_percent < 85 else "🔴"
                print(f"   {vram_icon} VRAM: {vram_percent:.0f}% ({vram_headroom:.0f}MB libre)")

                # Score efficacité
                eff_score = advanced.get('efficiency_score', 0)
                avg_eff = advanced.get('avg_efficiency', 0)
                print(f"   📊 Efficacité: {eff_score:.1f} (moy: {avg_eff:.1f})")

                # Puissance
                power = advanced.get('power_draw', 0)
                if power > 0:
                    print(f"   🔌 Puissance: {power:.1f}W")

                # ALERTES INTELLIGENTES
                print(f"\n🎯 ÉTAT EXPLOITATION:")
                exploitation = advanced.get('exploitation_state', 'INCONNU')
                bottleneck = advanced.get('bottleneck', None)

                if exploitation == 'SOUS-EXPLOITÉ':
                    print(f"   🟢 GPU SOUS-EXPLOITÉ - Marge de {headroom:.0f}°C disponible !")
                    if advanced.get('can_boost', False):
                        print(f"   🚀 BOOST POSSIBLE - GPU froid, on peut pousser !")
                elif exploitation == 'PEAK PERFORMANCE':
                    print(f"   🔥 PEAK PERFORMANCE - GPU bien exploité !")
                elif exploitation == 'THROTTLE':
                    print(f"   🔴 THROTTLE ACTIF - Réduction des clocks")
                else:
                    print(f"   🟡 OPTIMAL - Équilibre performance/température")

                # Bottleneck detection
                if bottleneck:
                    if bottleneck == 'CPU':
                        print(f"   ⚠️ BOTTLENECK CPU DÉTECTÉ - Le CPU limite le GPU !")
                        print(f"   💡 GPU throttle désactivé (inutile quand CPU limite)")
                    elif bottleneck == 'VRAM':
                        print(f"   ⚠️ BOTTLENECK VRAM DÉTECTÉ - Mémoire GPU saturée !")

                # Mode BOOST actif
                if self.boost_active:
                    print(f"   🚀 MODE BOOST ACTIF - Clocks libérés à 2100MHz !")

                # CPU Bottleneck boost
                if hasattr(self, '_cpu_bottleneck_boost_applied') and self._cpu_bottleneck_boost_applied:
                    print(f"   🎯 MODE CPU-BOTTLENECK - GPU libéré (CPU={data.get('cpu_usage', 0):.0f}%)")

            # Temps de fonctionnement
            uptime_minutes = data.get('uptime_seconds', 0) / 60
            print(f"\n⏰ Temps d'optimisation: {uptime_minutes:.1f} minutes")

            # Historique optimisations
            if self.optimization_history:
                print(f"\n📊 OPTIMISATIONS RÉCENTES:")
                for opt in self.optimization_history[-3:]:
                    print(f"   {opt['timestamp'].strftime('%H:%M:%S')}: {opt['action']}")

            print("="*80)
            
        except Exception as e:
            logging.error(f"❌ Erreur affichage statut: {str(e)}")
    
    def _get_temperature_status(self, temp: float) -> str:
        """Statut de température - LAPTOP HOT ADJUSTED ! 🌡️"""
        # Seuils fixes adaptés aux laptops gaming qui chauffent
        if temp < 65:
            return "✅ FROID"
        elif temp < 75:
            return "🟢 NORMAL"
        elif temp < 83:
            return "🟡 CHAUD"
        elif temp < 88:
            return "🟠 TRÈS CHAUD"
        elif temp < 92:
            return "🔴 CRITIQUE"
        else:
            return "🚨 URGENCE"
    
    def _calculate_advanced_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcul des stats avancées pour exploitation GPU optimale"""
        try:
            current_temp = data.get('gpu_temperature', 0)
            gpu_usage = data.get('gpu_usage', 0)
            cpu_usage = data.get('cpu_usage', 0)
            memory_usage = data.get('memory_usage', 0)

            # Récupérer les métriques GPU détaillées
            gpu_metrics = self.gpu_controller.get_gpu_metrics() if self.real_control_enabled else {}
            clock_current = gpu_metrics.get('clock_current', 0)
            clock_max = gpu_metrics.get('clock_max', 2100)  # RTX 2070 default
            vram_used = gpu_metrics.get('memory_used_mb', 0)
            vram_total = gpu_metrics.get('memory_total_mb', 8192)  # 8GB default
            power_draw = gpu_metrics.get('power_draw', 0)

            # Température cible selon profil
            target_temp = self.thermal_config.get('target_temp', 75)

            # 1. HEADROOM THERMIQUE - Marge disponible pour booster
            thermal_headroom = target_temp - current_temp

            # 2. CLOCK UTILIZATION - % des clocks utilisés
            clock_utilization = (clock_current / clock_max * 100) if clock_max > 0 else 0

            # 3. VRAM HEADROOM - Marge VRAM disponible
            vram_headroom_mb = vram_total - vram_used
            vram_usage_percent = (vram_used / vram_total * 100) if vram_total > 0 else 0

            # 4. SCORE D'EFFICACITÉ - Performance / Chaleur
            # Plus c'est haut = meilleure exploitation
            if current_temp > 0 and gpu_usage > 0:
                efficiency_score = (gpu_usage * clock_utilization) / current_temp
            else:
                efficiency_score = 0

            # Stocker pour moyenne
            self.advanced_stats['efficiency_samples'].append(efficiency_score)
            if len(self.advanced_stats['efficiency_samples']) > 100:
                self.advanced_stats['efficiency_samples'].pop(0)

            # 5. DÉTECTION BOTTLENECK
            bottleneck = None
            if gpu_usage < 60:
                if cpu_usage > 85:
                    bottleneck = 'CPU'
                    self.advanced_stats['bottleneck_cpu_count'] += 1
                elif vram_usage_percent > 90:
                    bottleneck = 'VRAM'
                    self.advanced_stats['bottleneck_vram_count'] += 1

            # 6. ÉTAT D'EXPLOITATION - LAPTOP HOT ADJUSTED
            # Pour laptops: throttle seulement si vraiment en mode emergency (>90°C)
            exploitation_state = 'OPTIMAL'
            if gpu_usage < 50 and current_temp < 75:
                exploitation_state = 'SOUS-EXPLOITÉ'
                self.advanced_stats['total_underutilized_time'] += self.thermal_config['monitor_interval']
            elif gpu_usage > 85 and current_temp < 88:
                exploitation_state = 'PEAK PERFORMANCE'
                self.advanced_stats['peak_performance_time'] += self.thermal_config['monitor_interval']
            elif current_temp >= 90:  # Seulement en vrai throttle (emergency)
                exploitation_state = 'THROTTLE'
                self.advanced_stats['total_throttle_time'] += self.thermal_config['monitor_interval']

            # 7. POTENTIEL DE BOOST - LAPTOP HOT ADJUSTED
            can_boost = (
                current_temp < 70 and  # GPU vraiment froid pour un laptop
                gpu_usage < 70 and
                clock_utilization < 90
            )

            return {
                'thermal_headroom': thermal_headroom,
                'clock_utilization': clock_utilization,
                'clock_current': clock_current,
                'clock_max': clock_max,
                'vram_headroom_mb': vram_headroom_mb,
                'vram_usage_percent': vram_usage_percent,
                'efficiency_score': efficiency_score,
                'avg_efficiency': sum(self.advanced_stats['efficiency_samples']) / len(self.advanced_stats['efficiency_samples']) if self.advanced_stats['efficiency_samples'] else 0,
                'bottleneck': bottleneck,
                'exploitation_state': exploitation_state,
                'can_boost': can_boost,
                'power_draw': power_draw
            }

        except Exception as e:
            logging.error(f"❌ Erreur calcul stats avancées: {str(e)}")
            return {}

    def _check_and_apply_boost(self, data: Dict[str, Any], advanced_stats: Dict[str, Any]):
        """Mode BOOST automatique - Pousser le GPU quand c'est possible !"""
        try:
            if not self.boost_mode_enabled or not self.real_control_enabled:
                return

            current_time = time.time()
            if current_time - self.advanced_stats['last_boost_check'] < self.boost_cooldown:
                return

            self.advanced_stats['last_boost_check'] = current_time

            current_temp = data.get('gpu_temperature', 0)
            gpu_usage = data.get('gpu_usage', 0)
            thermal_headroom = advanced_stats.get('thermal_headroom', 0)
            can_boost = advanced_stats.get('can_boost', False)

            # CONDITIONS DE BOOST
            # GPU froid + sous-exploité = ON POUSSE !
            if can_boost and not self.boost_active:
                # Activer le boost - passer en mode performance
                success = self.gpu_controller.apply_profile('performance')
                if success:
                    self.boost_active = True
                    self.advanced_stats['boost_activations'] += 1
                    logging.info(f"🚀 BOOST ACTIVÉ ! Temp={current_temp}°C, Headroom={thermal_headroom}°C")

                    self.optimization_history.append({
                        'timestamp': data['timestamp'],
                        'level': 0,
                        'action': f"🚀 BOOST: GPU froid ({current_temp}°C), clocks libérés à 2100MHz",
                        'temperature': current_temp,
                        'thermal_profile': 'boost',
                        'gpu_profile': 'performance',
                        'real_control': True
                    })

            # Désactiver le boost si température monte
            elif self.boost_active:
                self.advanced_stats['total_boost_time'] += self.boost_cooldown

                # Si on dépasse la cible ou usage élevé avec chaleur
                target_temp = self.thermal_config.get('target_temp', 75)
                if current_temp >= target_temp - 3 or (gpu_usage > 85 and current_temp > target_temp - 5):
                    self.boost_active = False
                    logging.info(f"🔥 BOOST DÉSACTIVÉ - Temp={current_temp}°C, retour contrôle thermique")

        except Exception as e:
            logging.error(f"❌ Erreur check boost: {str(e)}")

    def _should_use_score_based_decision(self) -> bool:
        """Determine si on doit utiliser les decisions basees sur le score"""
        # Utiliser le score si:
        # - Le scoring est active
        # - On a un score valide
        # - Le score a ete calcule recemment
        if not self.score_based_decisions or not self.current_score:
            return False

        # Si le score est en mode EMERGENCY, toujours agir
        if self.current_score.state == PerformanceState.EMERGENCY:
            return True

        # Sinon, utiliser le score si on a assez d'historique (stabilite)
        return len(self.performance_scorer.score_history) >= 3

    def _apply_score_based_optimization(self, data: Dict[str, Any]) -> bool:
        """
        Applique les optimisations basees sur le score global

        Returns:
            True si une action a ete prise, False sinon
        """
        if not self.current_score:
            return False

        score = self.current_score
        strategy = score.recommended_strategy
        state = score.state
        current_temp = data.get('gpu_temperature', 0)

        # Log du score actuel (toutes les 10 secondes)
        if not hasattr(self, '_last_score_log') or time.time() - self._last_score_log > 10:
            state_icons = {
                PerformanceState.EMERGENCY: '🚨',
                PerformanceState.POOR: '🔴',
                PerformanceState.ACCEPTABLE: '🟡',
                PerformanceState.GOOD: '🟢',
                PerformanceState.EXCELLENT: '💚',
                PerformanceState.PEAK: '⭐'
            }
            icon = state_icons.get(state, '❓')
            logging.info(f"{icon} SCORE: {score.overall_score:.0f}/100 ({state.value}) - Strategie: {strategy.value}")
            self._last_score_log = time.time()

        # ========== ACTIONS SELON LA STRATEGIE ==========

        if strategy == OptimizationStrategy.EMERGENCY_THROTTLE:
            # URGENCE - Throttle agressif immediat
            if self.real_control_enabled:
                self.gpu_controller.apply_profile('emergency')
                self.boost_active = False
                self.optimization_active = True

                self.optimization_history.append({
                    'timestamp': data['timestamp'],
                    'level': 4,
                    'action': f"🚨 SCORE URGENCE ({score.overall_score:.0f}) - Throttle Emergency",
                    'temperature': current_temp,
                    'score': score.overall_score,
                    'gpu_profile': 'emergency',
                    'real_control': True
                })

                logging.warning(f"🚨 SCORE URGENCE: {score.overall_score:.0f}/100 - Throttle EMERGENCY applique!")
                return True

        elif strategy == OptimizationStrategy.THERMAL_FOCUS:
            # Priorite refroidissement
            if self.real_control_enabled and not self.optimization_active:
                # Appliquer un profil de refroidissement selon le score
                if score.overall_score < 50:
                    profile = 'critical'
                elif score.overall_score < 60:
                    profile = 'quiet'
                else:
                    profile = 'balanced'

                self.gpu_controller.apply_profile(profile)
                self.boost_active = False
                self.optimization_active = True

                self.optimization_history.append({
                    'timestamp': data['timestamp'],
                    'level': 2,
                    'action': f"🌡️ SCORE THERMAL ({score.overall_score:.0f}) - Profil {profile}",
                    'temperature': current_temp,
                    'score': score.overall_score,
                    'gpu_profile': profile,
                    'real_control': True
                })

                logging.info(f"🌡️ THERMAL FOCUS: Score {score.overall_score:.0f} - Profil {profile} applique")
                return True

        elif strategy == OptimizationStrategy.BOOST:
            # Mode boost - on peut pousser !
            if self.real_control_enabled and not self.boost_active:
                self.gpu_controller.apply_profile('performance')
                self.boost_active = True
                self.optimization_active = False

                self.optimization_history.append({
                    'timestamp': data['timestamp'],
                    'level': 0,
                    'action': f"🚀 SCORE BOOST ({score.overall_score:.0f}) - Mode Performance",
                    'temperature': current_temp,
                    'score': score.overall_score,
                    'gpu_profile': 'performance',
                    'real_control': True
                })

                logging.info(f"🚀 BOOST MODE: Score {score.overall_score:.0f} - Clocks liberes!")
                return True

        elif strategy == OptimizationStrategy.PERFORMANCE:
            # Priorite FPS - equilibre vers performance
            if self.real_control_enabled:
                if self.optimization_active:
                    # On etait en throttle, on peut relacher
                    self.gpu_controller.apply_profile('balanced')
                    self.optimization_active = False

                    logging.info(f"⚡ PERFORMANCE: Score {score.overall_score:.0f} - Retour profil balanced")
                    return True

        elif strategy == OptimizationStrategy.BALANCED:
            # Equilibre - pas d'action specifique, laisser la logique standard
            # Mais desactiver le boost si actif et score pas assez bon
            if self.boost_active and score.overall_score < 75:
                self.boost_active = False
                self.gpu_controller.apply_profile('balanced')
                logging.info(f"⚖️ BALANCED: Score {score.overall_score:.0f} - Boost desactive")
                return True

        # Pas d'action prise par le scorer
        return False

    def _analyze_and_optimize(self, data: Dict[str, Any]):
        """Analyse et optimisation automatique - INTELLIGENCE DIVINE ! 🧠"""
        try:
            current_temp = data.get('gpu_temperature', 0)
            current_time = time.time()
            gpu_usage = data.get('gpu_usage', 0)
            cpu_usage = data.get('cpu_usage', 0)

            # NOUVEAU: Calcul des stats avancées
            advanced_stats = self._calculate_advanced_stats(data)
            data['advanced_stats'] = advanced_stats

            # NOUVEAU: Détection CPU bottleneck intelligent
            is_cpu_bottleneck = (cpu_usage > 85 and gpu_usage < 60)
            data['is_cpu_bottleneck'] = is_cpu_bottleneck

            # ML: Ajouter le point de données pour l'apprentissage
            gpu_metrics = self.gpu_controller.get_gpu_metrics() if self.real_control_enabled else {}
            fps_data = self.fps_monitor.get_current_data() if self.fps_session_active else None

            self.ml_predictor.add_data_point(
                temp=current_temp,
                gpu_usage=gpu_usage,
                clock_speed=gpu_metrics.get('clock_current', 0),
                power_draw=gpu_metrics.get('power_draw', 0),
                fps=fps_data.fps_current if fps_data else 0
            )

            # Sweet Spot: Ajouter le point de données
            if self.sweet_spot_enabled and fps_data:
                self.sweet_spot_finder.add_data_point(
                    clock_mhz=gpu_metrics.get('clock_current', 0),
                    temperature=current_temp,
                    fps=fps_data.fps_current,
                    gpu_usage=gpu_usage,
                    power_draw=gpu_metrics.get('power_draw', 0),
                    frametime_ms=fps_data.frametime_ms
                )

            # ========================================================
            # PERFORMANCE SCORER - CALCUL DU SCORE GLOBAL
            # ========================================================
            if self.score_based_decisions:
                # Configurer le scorer selon le profil du jeu
                if self.current_game_profile:
                    self.performance_scorer.configure_for_game(self.current_game_profile)

                # Calculer le score
                self.current_score = self.performance_scorer.calculate_score(
                    temperature=current_temp,
                    gpu_usage=gpu_usage,
                    fps_current=fps_data.fps_current if fps_data else 0,
                    fps_avg=fps_data.fps_avg if fps_data else 0,
                    fps_1_low=fps_data.fps_1_percent_low if fps_data else 0,
                    frametime_ms=fps_data.frametime_ms if fps_data else 0,
                    clock_current=gpu_metrics.get('clock_current', 0),
                    clock_max=gpu_metrics.get('clock_max', 2100),
                    power_draw=gpu_metrics.get('power_draw', 0),
                    vram_usage_percent=advanced_stats.get('vram_usage_percent', 0),
                    cpu_usage=cpu_usage,
                    is_throttling=self.optimization_active,
                    is_boosting=self.boost_active,
                    game_name=self.current_game.custom_name if self.current_game else "",
                    thermal_profile=self.current_game_profile.get('thermal_profile', 'medium') if self.current_game_profile else 'medium'
                )

                # Stocker dans data pour le dashboard
                data['performance_score'] = self.current_score

                # Utiliser le score pour les decisions automatiques
                if self._should_use_score_based_decision():
                    action_taken = self._apply_score_based_optimization(data)
                    if action_taken:
                        return  # Decision prise par le scorer, skip l'ancienne logique

            # ========================================================
            # NOUVEAU: LOGIQUE CPU BOTTLENECK - NE PAS THROTTLER INUTILEMENT
            # ========================================================
            # Si CPU bottleneck ET température acceptable, on peut relâcher le GPU
            # car throttler le GPU ne changera rien aux FPS (c'est le CPU qui limite)
            if is_cpu_bottleneck and current_temp < 88:
                # Le CPU limite le jeu, pas le GPU - throttler le GPU est inutile
                # On peut même augmenter les clocks car le GPU est sous-utilisé
                if current_temp < 82 and self.real_control_enabled:
                    # GPU froid + CPU bottleneck = on peut pousser le GPU
                    # Ça peut aider via DLSS/FSR ou calculs GPU
                    if not hasattr(self, '_cpu_bottleneck_boost_applied') or not self._cpu_bottleneck_boost_applied:
                        self.gpu_controller.apply_profile('balanced')  # 1950 MHz
                        self._cpu_bottleneck_boost_applied = True
                        logging.info(f"🎯 CPU BOTTLENECK: GPU libéré (CPU={cpu_usage:.0f}%, GPU={gpu_usage:.0f}%, Temp={current_temp}°C)")

                # Ne pas appliquer de throttle GPU si c'est le CPU qui limite
                # SAUF si température vraiment critique (>88°C)
                if current_temp < 85:
                    # Skip les optimisations GPU - ça ne servirait à rien
                    return
            else:
                # Pas de CPU bottleneck - reset le flag
                self._cpu_bottleneck_boost_applied = False

            # ML: Prédiction et throttle préventif
            if self.ml_preemptive_throttle:
                prediction = self.ml_predictor.predict()
                data['ml_prediction'] = prediction

                # CORRIGÉ: Utiliser le target_temp du jeu actuel (pas le défaut!)
                # Pour laptop gaming, on utilise 83°C comme cible par défaut
                target_temp = self.thermal_config.get('target_temp', 83)

                # Récupérer le target du profil jeu si disponible
                if self.current_game_profile:
                    target_temp = self.current_game_profile.get('target_temp', target_temp)

                should_throttle, reason = self.ml_predictor.should_preemptive_throttle(current_temp, target_temp)

                # MODIFIÉ: Ne pas throttler préventivement si CPU bottleneck
                # ET seulement si on DÉPASSE la limite (pas juste proche)
                # Pour laptop gaming: on laisse le GPU tranquille jusqu'à target_temp
                if should_throttle and not self.boost_active and not is_cpu_bottleneck and current_temp >= target_temp:
                    logging.info(f"🧠 ML PRÉVENTIF: {reason}")
                    # Forcer une optimisation même si on n'a pas atteint le seuil
                    if self._determine_optimization_level(current_temp) == 0:
                        self._apply_optimizations(1, data)  # Appliquer niveau 1 de manière préventive

            # NOUVEAU: Check mode BOOST (GPU froid = on pousse !)
            self._check_and_apply_boost(data, advanced_stats)

            # Si boost actif, on ne throttle pas sauf urgence
            if self.boost_active and current_temp < self.thermal_config.get('target_temp', 75):
                return

            # Vérification du délai entre optimisations
            if current_time - self.last_optimization_time < self.thermal_config['optimization_cooldown']:
                return

            # Détermination du niveau d'optimisation nécessaire
            optimization_level = self._determine_optimization_level(current_temp)

            if optimization_level > 0:
                # Désactiver boost si on doit throttle
                if self.boost_active:
                    self.boost_active = False
                    logging.info("🔥 BOOST désactivé - Passage en mode thermique")

                # Application des optimisations
                self._apply_optimizations(optimization_level, data)
                self.last_optimization_time = current_time
            elif optimization_level == 0 and self.optimization_active:
                # CORRIGÉ: Restaurer quand niveau = 0 (pas besoin de throttle)
                # Applique le profil "balanced" ou "performance" selon la température
                if self.real_control_enabled:
                    thermal_profile = self.current_game_profile.get('thermal_profile', 'medium') if self.current_game_profile else 'medium'
                    new_profile = self.gpu_controller.auto_adjust_for_temperature(int(current_temp), thermal_profile)
                    if new_profile and new_profile not in ['none', 'readonly']:
                        logging.info(f"✅ Temp OK ({current_temp}°C) - Profil GPU: {new_profile}")
                # Reset le flag d'optimisation si on est bien en dessous du seuil
                if current_temp < self.optimization_thresholds['temp_warning'] - 3:
                    self.optimization_active = False
                    self.current_optimizations.clear()

        except Exception as e:
            logging.error(f"❌ Erreur analyse et optimisation: {str(e)}")

    def _send_to_dashboard(self, data: Dict[str, Any]):
        """Envoie les données au Dashboard Web Bun.js"""
        try:
            # Récupérer les données supplémentaires
            fps_data = self.fps_monitor.get_current_data() if self.fps_session_active else None
            ml_prediction = data.get('ml_prediction', None)
            advanced_stats = data.get('advanced_stats', {})

            # Sweet Spot
            sweet_spot = None
            if self.sweet_spot_enabled and self.current_game:
                sweet_spot = self.sweet_spot_finder.get_sweet_spot()

            # Performance Score - NOUVEAU !
            performance_score = self.current_score if self.score_based_decisions else None

            # Formater et envoyer
            dashboard_data = self.dashboard_client.format_optimizer_data(
                thermal_data=data,
                fps_data=fps_data,
                ml_prediction=ml_prediction,
                sweet_spot=sweet_spot,
                advanced_stats=advanced_stats,
                optimizations=self.current_optimizations,
                performance_score=performance_score
            )

            self.dashboard_client.send_data(dashboard_data)

        except Exception as e:
            # Ne pas bloquer l'optimiseur si le dashboard échoue
            logging.debug(f"Erreur envoi dashboard: {e}")

    def _determine_optimization_level(self, temp: float) -> int:
        """Détermination du niveau d'optimisation - NIVEAU DIVIN ! 🎯"""
        # DEBUG: Log les seuils actuels (une fois toutes les 60 secondes)
        if not hasattr(self, '_last_threshold_log') or time.time() - self._last_threshold_log > 60:
            logging.info(f"📊 Seuils actuels: warning={self.optimization_thresholds['temp_warning']}°C, "
                         f"agg={self.optimization_thresholds['temp_aggressive']}°C, "
                         f"crit={self.optimization_thresholds['temp_critical']}°C, "
                         f"emerg={self.optimization_thresholds['temp_emergency']}°C | Temp={temp}°C")
            self._last_threshold_log = time.time()

        if temp >= self.optimization_thresholds['temp_emergency']:
            return 4  # Urgence
        elif temp >= self.optimization_thresholds['temp_critical']:
            return 3  # Critique
        elif temp >= self.optimization_thresholds['temp_aggressive']:
            return 2  # Agressif
        elif temp >= self.optimization_thresholds['temp_warning']:
            return 1  # Légère
        else:
            return 0  # Aucune
    
    def _apply_optimizations(self, level: int, data: Dict[str, Any]):
        """Application des optimisations REELLES via nvidia-smi !

        NOUVELLE APPROCHE PROACTIVE :
        Utilise le profil thermique du jeu pour déterminer l'agressivité du refroidissement
        """
        try:
            # Récupérer le profil thermique du jeu actuel
            thermal_profile = 'medium'
            if self.current_game_profile:
                thermal_profile = self.current_game_profile.get('thermal_profile', 'medium')

            current_temp = data.get('gpu_temperature', 0)

            logging.info(f"🔧 Application optimisations niveau {level} (profil: {thermal_profile})")

            optimizations_applied = []
            profile_to_apply = None

            # NOUVEAU: Utilisation du controleur REEL avec profil thermique
            if self.real_control_enabled:
                # Utiliser la nouvelle méthode auto_adjust_for_temperature avec le profil
                applied_profile = self.gpu_controller.auto_adjust_for_temperature(
                    int(current_temp),
                    thermal_profile
                )

                if applied_profile and applied_profile != 'none' and applied_profile != 'readonly':
                    profile_to_apply = applied_profile
                    if applied_profile in self.gpu_controller.CLOCK_PROFILES:
                        profile_info = self.gpu_controller.CLOCK_PROFILES[applied_profile]
                        optimizations_applied.append(
                            f"GPU Clocks: {profile_info.max_clock_mhz}MHz max ({profile_info.name})"
                        )

            # Note: the only real action applied is the GPU clock profile
            # (auto_adjust_for_temperature) above. Fan, power-limit, voltage,
            # memory and process-priority tuning were never implemented.

            # Mise a jour de l'etat
            if optimizations_applied:
                self.optimization_active = True
                # CORRIGÉ: Nettoyer les niveaux supérieurs quand on descend
                # Si on est au niveau 1, supprimer niveau 2, 3, 4
                for old_level in range(level + 1, 5):
                    self.current_optimizations.pop(f"niveau_{old_level}", None)
                self.current_optimizations[f"niveau_{level}"] = ", ".join(optimizations_applied)

                # Enregistrement dans l'historique
                self.optimization_history.append({
                    'timestamp': data['timestamp'],
                    'level': level,
                    'action': f"Niveau {level}: {', '.join(optimizations_applied)}",
                    'temperature': current_temp,
                    'thermal_profile': thermal_profile,
                    'gpu_profile': profile_to_apply,
                    'real_control': self.real_control_enabled
                })

                # Limitation de l'historique
                if len(self.optimization_history) > 50:
                    self.optimization_history.pop(0)

                logging.info(f"✅ Optimisations PROACTIVES appliquees: {', '.join(optimizations_applied)}")

        except Exception as e:
            logging.error(f"❌ Erreur application optimisations: {str(e)}")
    
    def _restore_normal_parameters(self):
        """Restauration des parametres normaux - Reset GPU REEL !"""
        try:
            logging.info("Restauration parametres normaux")

            # NOUVEAU: Reset REEL via nvidia-smi
            if self.real_control_enabled:
                success = self.gpu_controller.reset_gpu_clocks()
                if success:
                    logging.info("GPU Clocks RESET (REEL via nvidia-smi)")
                else:
                    logging.warning("Echec reset GPU clocks")

            # Reset de l'etat
            self.optimization_active = False
            self.current_optimizations.clear()

            logging.info("Parametres normaux restaures")

        except Exception as e:
            logging.error(f"Erreur restauration parametres: {str(e)}")
    
    def stop_thermal_optimization(self):
        """Arrêt de l'optimisation thermique - ARRÊT DIVIN ! 🛑"""
        logging.info("🛑 ARRÊT OPTIMISATION THERMIQUE TEMPLE IAM")

        self.is_running = False

        # Arrêter le dashboard client
        if self.dashboard_enabled:
            self.dashboard_client.stop()
            logging.info("📊 Dashboard Client arrêté")

        # Restauration des paramètres normaux
        self._restore_normal_parameters()
        
        # Affichage du résumé final
        self._display_final_summary()
        
        logging.info("✅ Optimisation thermique arrêtée avec succès")
    
    def _display_final_summary(self):
        """Affichage du résumé final - RÉSUMÉ DIVIN ! 📊"""
        if not self.thermal_data:
            return

        print("\n" + "="*80)
        print("🏁 RÉSUMÉ FINAL - TEMPLE IAM THERMAL OPTIMIZER")
        print("="*80)

        # Statistiques générales
        total_points = len(self.thermal_data)
        optimization_count = len(self.optimization_history)
        uptime_minutes = self.thermal_data[-1].get('uptime_seconds', 0) / 60 if self.thermal_data else 0

        print(f"\n📊 STATISTIQUES DE SESSION:")
        print(f"   Points de données: {total_points}")
        print(f"   Durée totale: {uptime_minutes:.1f} minutes")
        print(f"   Optimisations appliquées: {optimization_count}")

        if self.thermal_data:
            # Températures
            temps = [data.get('gpu_temperature', 0) for data in self.thermal_data]
            avg_temp = sum(temps) / len(temps)
            max_temp = max(temps)
            min_temp = min(temps)

            print(f"\n🌡️ TEMPÉRATURES:")
            print(f"   Moyenne: {avg_temp:.1f}°C")
            print(f"   Maximum: {max_temp:.1f}°C")
            print(f"   Minimum: {min_temp:.1f}°C")

            # Usage GPU
            usages = [data.get('gpu_usage', 0) for data in self.thermal_data]
            avg_usage = sum(usages) / len(usages) if usages else 0
            max_usage = max(usages) if usages else 0

            print(f"\n🖥️ UTILISATION GPU:")
            print(f"   Moyenne: {avg_usage:.1f}%")
            print(f"   Maximum: {max_usage:.1f}%")

        # NOUVELLES STATS AVANCÉES
        print(f"\n📈 STATS AVANCÉES:")

        # Temps dans chaque état
        underutil_min = self.advanced_stats['total_underutilized_time'] / 60
        boost_min = self.advanced_stats['total_boost_time'] / 60
        throttle_min = self.advanced_stats['total_throttle_time'] / 60
        peak_min = self.advanced_stats['peak_performance_time'] / 60

        print(f"   ⏱️ Temps sous-exploité: {underutil_min:.1f} min")
        print(f"   🚀 Temps en boost: {boost_min:.1f} min")
        print(f"   🔥 Temps peak perf: {peak_min:.1f} min")
        print(f"   🔴 Temps en throttle: {throttle_min:.1f} min")

        # Efficacité
        if self.advanced_stats['efficiency_samples']:
            avg_eff = sum(self.advanced_stats['efficiency_samples']) / len(self.advanced_stats['efficiency_samples'])
            max_eff = max(self.advanced_stats['efficiency_samples'])
            print(f"\n   📊 Score efficacité moyen: {avg_eff:.1f}")
            print(f"   📊 Score efficacité max: {max_eff:.1f}")

        # Boost stats
        print(f"\n   🚀 Activations boost: {self.advanced_stats['boost_activations']}")

        # Bottlenecks
        cpu_bottlenecks = self.advanced_stats['bottleneck_cpu_count']
        vram_bottlenecks = self.advanced_stats['bottleneck_vram_count']
        if cpu_bottlenecks > 0 or vram_bottlenecks > 0:
            print(f"\n⚠️ BOTTLENECKS DÉTECTÉS:")
            if cpu_bottlenecks > 0:
                print(f"   CPU bottleneck: {cpu_bottlenecks} fois")
            if vram_bottlenecks > 0:
                print(f"   VRAM bottleneck: {vram_bottlenecks} fois")

        # Calcul du score global d'exploitation
        if uptime_minutes > 0:
            total_time_sec = uptime_minutes * 60
            exploitation_score = ((peak_min * 60 + boost_min * 60) / total_time_sec) * 100 if total_time_sec > 0 else 0
            underutil_percent = (underutil_min * 60 / total_time_sec) * 100 if total_time_sec > 0 else 0
            throttle_percent = (throttle_min * 60 / total_time_sec) * 100 if total_time_sec > 0 else 0

            print(f"\n🎯 SCORE D'EXPLOITATION GPU:")
            print(f"   Performance optimale: {exploitation_score:.1f}% du temps")
            print(f"   Sous-exploitation: {underutil_percent:.1f}% du temps")
            print(f"   Throttling: {throttle_percent:.1f}% du temps")

            # Recommandation finale
            print(f"\n💡 RECOMMANDATION:")
            if underutil_percent > 30:
                print(f"   → GPU sous-exploité ! Tu peux monter les graphiques du jeu.")
            elif throttle_percent > 20:
                print(f"   → Throttling fréquent. Améliore le refroidissement ou baisse les graphiques.")
            elif exploitation_score > 50:
                print(f"   → Excellente exploitation du GPU ! Configuration optimale.")
            else:
                print(f"   → Exploitation correcte. Le système fonctionne bien.")

        # Stats FPS si disponibles
        if self.fps_session_active:
            fps_summary = self.fps_monitor.get_session_summary()
            if fps_summary:
                print(f"\n🎮 STATS FPS ({fps_summary.get('source', 'N/A').upper()}):")
                print(f"   Échantillons: {fps_summary.get('samples', 0)}")
                print(f"   FPS Moyen: {fps_summary.get('fps_avg', 0):.1f}")
                print(f"   FPS Min: {fps_summary.get('fps_min', 0):.1f}")
                print(f"   FPS Max: {fps_summary.get('fps_max', 0):.1f}")
                print(f"   1% Low: {fps_summary.get('fps_1_low', 0):.1f}")
                print(f"   Stabilité: {fps_summary.get('fps_stability', 0):.1f}%")

            # Arrêter la session FPS
            self.fps_monitor.stop_session()
            self.fps_session_active = False

        # Stats ML PRÉDICTION
        if self.current_game:
            pattern_summary = self.ml_predictor.get_pattern_summary()
            if pattern_summary and pattern_summary.get('samples', 0) > 0:
                print(f"\n🧠 STATS ML APPRISES ({pattern_summary.get('game', 'N/A')}):")
                print(f"   Échantillons collectés: {pattern_summary.get('samples', 0)}")
                print(f"   Temp moyenne: {pattern_summary.get('avg_temp', 0):.1f}°C")
                print(f"   Temp max observée: {pattern_summary.get('max_temp', 0):.1f}°C")
                print(f"   Temp stabilisation: {pattern_summary.get('stabilization_temp', 0)}°C")
                print(f"   Taux montée: +{pattern_summary.get('temp_rise_rate', 0):.2f}°C/s")
                print(f"   Taux descente: -{pattern_summary.get('temp_drop_rate', 0):.2f}°C/s")
                print(f"   Corrélation GPU/Temp: {pattern_summary.get('usage_correlation', 0):.2f}")

                # Afficher les spikes détectés
                spikes = pattern_summary.get('spike_temps', [])
                if spikes:
                    print(f"   Spikes détectés: {len(spikes)} (derniers: {', '.join([f'{s:.0f}°C' for s in spikes[-3:]])})")

            # Sauvegarder les données ML
            self.ml_predictor._save_data()
            print(f"   💾 Données ML sauvegardées pour sessions futures")

        # Résumé tous les jeux appris
        all_games = self.ml_predictor.get_all_games_summary()
        if len(all_games) > 1:
            print(f"\n📚 TOUS LES JEUX APPRIS ({len(all_games)}):")
            for game_summary in all_games[:5]:  # Top 5
                print(f"   • {game_summary.get('game', 'N/A')}: {game_summary.get('samples', 0)} samples, "
                      f"avg {game_summary.get('avg_temp', 0):.0f}°C, max {game_summary.get('max_temp', 0):.0f}°C")

        # Stats SWEET SPOT
        if self.current_game:
            sweet_spot_summary = self.sweet_spot_finder.get_game_summary()
            if sweet_spot_summary and sweet_spot_summary.get('status') == 'analyzed':
                print(f"\n🎯 SWEET SPOT FINAL ({sweet_spot_summary.get('game', 'N/A')}):")
                print(f"   Clock optimal: {sweet_spot_summary.get('optimal_clock_mhz', 0)} MHz")
                print(f"   Temp cible: {sweet_spot_summary.get('optimal_temp_target', 0):.0f}°C")
                print(f"   FPS attendu: {sweet_spot_summary.get('expected_fps', 0):.1f}")
                print(f"   Efficacité: {sweet_spot_summary.get('efficiency_score', 0):.2f}")
                print(f"   Confiance: {sweet_spot_summary.get('confidence', 0):.0f}%")
                print(f"   {sweet_spot_summary.get('recommendation', '')}")

        # Résumé tous les Sweet Spots
        all_sweet_spots = self.sweet_spot_finder.get_all_games_summary()
        if len(all_sweet_spots) > 1:
            print(f"\n📊 TOUS LES SWEET SPOTS ({len(all_sweet_spots)}):")
            for ss in all_sweet_spots[:5]:
                print(f"   • {ss.get('game', 'N/A')}: {ss.get('optimal_clock_mhz', 0)}MHz, "
                      f"~{ss.get('expected_fps', 0):.0f}FPS @ {ss.get('expected_temp', 0):.0f}°C")

        # Optimisations appliquées
        if self.optimization_history:
            print(f"\n⚙️ DERNIÈRES OPTIMISATIONS:")
            for opt in self.optimization_history[-5:]:
                print(f"   {opt['timestamp'].strftime('%H:%M:%S')}: {opt['action']}")

        print("\n" + "="*80)
        print("🔥 TEMPLE IAM THERMAL OPTIMIZER TERMINÉ - MISSION ACCOMPLIE !")
        print("Plus Ultra ! DATTEBAYO ! ⚡")
        print("="*80)

def main():
    """Fonction principale - DÉMARRAGE DIVIN ! 🚀"""
    print("🔥 TEMPLE IAM THERMAL OPTIMIZER - OPTIMISATION THERMIQUE DIVINE")
    print("="*60)
    print("💡 Ce système optimise automatiquement la température GPU")
    print("💡 Sans toucher aux paramètres du jeu !")
    print("💡 Appuie sur Ctrl+C pour arrêter")
    print("="*60)
    
    # Création et démarrage de l'optimiseur
    optimizer = TempleIAMThermalOptimizer()
    
    try:
        optimizer.start_thermal_optimization()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt manuel de l'optimiseur...")
        optimizer.stop_thermal_optimization()

if __name__ == "__main__":
    main() 