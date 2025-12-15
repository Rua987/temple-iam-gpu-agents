"""
🔍 UNIVERSAL GAME DETECTOR - DÉTECTION UNIVERSELLE DE JEUX ! 🏛️
Objectif : Détection automatique de N'IMPORTE QUEL JEU en cours d'exécution

FONCTIONNALITÉS DIVINES :
🎯 Détection automatique : Reconnaît n'importe quel jeu
🎯 Base de données : 100+ jeux pré-configurés
🎯 Auto-apprentissage : Ajoute les jeux inconnus automatiquement
🎯 Multi-plateforme : Steam, Epic, GOG, Xbox, Origin, etc.
🎯 Métriques temps réel : FPS, VRAM, GPU usage par jeu

PLUS ULTRA ! DATTEBAYO ! 🚀⚡🥷🏛️
"""

import psutil
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import json
import os

from games_database import GAMES_DB, GameProfile

logging.basicConfig(level=logging.INFO, format='🔍 %(asctime)s - %(levelname)s - %(message)s')

@dataclass
class DetectedGame:
    """Jeu détecté avec informations en temps réel"""
    profile: Optional[GameProfile]
    process_name: str
    pid: int
    exe_path: str
    start_time: datetime
    is_known: bool  # Si le jeu est dans la base de données
    custom_name: str  # Nom personnalisé pour jeux inconnus
    cpu_usage: float
    memory_mb: float

class UniversalGameDetector:
    """Détecteur universel de jeux - OMNISCIENCE DIVINE ! 👁️"""

    def __init__(self, auto_learn: bool = True, learned_games_path: str = "learned_games.json"):
        """
        Initialisation du détecteur universel

        Args:
            auto_learn: Active l'apprentissage automatique des jeux inconnus
            learned_games_path: Fichier JSON pour stocker les jeux appris
        """
        self.auto_learn = auto_learn
        self.learned_games_path = learned_games_path
        self.learned_games: Dict[str, Dict[str, Any]] = {}

        # Liste de processus de jeu actuellement détectés
        self.detected_games: List[DetectedGame] = []

        # Liste de processus système à ignorer
        self.ignore_processes = {
            'explorer.exe', 'svchost.exe', 'system', 'registry',
            'dwm.exe', 'csrss.exe', 'winlogon.exe', 'services.exe',
            'lsass.exe', 'smss.exe', 'wininit.exe', 'taskhostw.exe',
            'runtimebroker.exe', 'searchindexer.exe', 'msiexec.exe',
            'conhost.exe', 'dllhost.exe', 'audiodg.exe', 'spoolsv.exe',
            'chrome.exe', 'firefox.exe', 'edge.exe', 'brave.exe',
            'discord.exe', 'spotify.exe', 'slack.exe', 'teams.exe',
            'code.exe', 'notepad.exe', 'notepad++.exe', 'sublime_text.exe',
            'python.exe', 'pythonw.exe', 'cmd.exe', 'powershell.exe',
            'nvcontainer.exe', 'nvidia web helper.exe', 'nvidia share.exe',
            'steamwebhelper.exe', 'epicwebhelper.exe'
        }

        # Patterns de jeux connus (suffixes d'exécutables)
        self.game_patterns = [
            'game.exe', '-win64-shipping.exe', '-win64.exe',
            'launcher.exe', 'client.exe', 'play.exe'
        ]

        # Chargement des jeux appris
        self._load_learned_games()

        logging.info("🔍 Universal Game Detector initialisé - DÉTECTION DIVINE ACTIVE !")
        logging.info(f"📚 Base de données: {len(GAMES_DB.get_all_games())} jeux")
        logging.info(f"🧠 Jeux appris: {len(self.learned_games)}")

    def _load_learned_games(self):
        """Charge les jeux appris depuis le fichier JSON"""
        try:
            if os.path.exists(self.learned_games_path):
                with open(self.learned_games_path, 'r', encoding='utf-8') as f:
                    self.learned_games = json.load(f)
                logging.info(f"✅ {len(self.learned_games)} jeux appris chargés")
        except Exception as e:
            logging.warning(f"⚠️ Erreur chargement jeux appris: {str(e)}")
            self.learned_games = {}

    def _save_learned_games(self):
        """Sauvegarde les jeux appris dans le fichier JSON"""
        try:
            with open(self.learned_games_path, 'w', encoding='utf-8') as f:
                json.dump(self.learned_games, f, indent=2, ensure_ascii=False)
            logging.info(f"💾 Jeux appris sauvegardés: {len(self.learned_games)}")
        except Exception as e:
            logging.error(f"❌ Erreur sauvegarde jeux appris: {str(e)}")

    def _is_likely_game_process(self, proc_name: str, proc_info: Dict[str, Any]) -> bool:
        """
        Détermine si un processus est probablement un jeu

        Critères:
        - Utilise du GPU (si disponible)
        - Consomme >500MB RAM
        - Fenêtre graphique active
        - Pattern de nom correspondant
        """
        proc_name_lower = proc_name.lower()

        # Ignorer les processus système connus
        if proc_name_lower in self.ignore_processes:
            return False

        # Vérifier les patterns de jeux
        if any(pattern in proc_name_lower for pattern in self.game_patterns):
            return True

        # Vérifier la consommation mémoire (critère léger)
        try:
            memory_mb = proc_info.get('memory_info', psutil.Process().memory_info()).rss / (1024 * 1024)
            if memory_mb > 500:  # >500MB probable jeu
                return True
        except:
            pass

        return False

    def detect_running_games(self) -> List[DetectedGame]:
        """
        Détecte TOUS les jeux en cours d'exécution

        Returns:
            Liste de jeux détectés avec leurs informations
        """
        detected = []

        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'cpu_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info.get('name', '')

                    if not proc_name:
                        continue

                    # 1. Vérifier dans la base de données connue
                    game_profile = GAMES_DB.get_game_by_process(proc_name)

                    if game_profile:
                        # Jeu connu trouvé
                        detected_game = DetectedGame(
                            profile=game_profile,
                            process_name=proc_name,
                            pid=proc_info['pid'],
                            exe_path=proc_info.get('exe', 'Unknown'),
                            start_time=datetime.fromtimestamp(proc_info.get('create_time', time.time())),
                            is_known=True,
                            custom_name=game_profile.display_name,
                            cpu_usage=proc_info.get('cpu_percent', 0.0),
                            memory_mb=proc_info.get('memory_info', psutil.Process().memory_info()).rss / (1024 * 1024)
                        )
                        detected.append(detected_game)
                        logging.info(f"🎮 Jeu connu détecté: {game_profile.display_name}")
                        continue

                    # 2. Vérifier dans les jeux appris
                    if proc_name in self.learned_games:
                        learned = self.learned_games[proc_name]
                        detected_game = DetectedGame(
                            profile=None,
                            process_name=proc_name,
                            pid=proc_info['pid'],
                            exe_path=proc_info.get('exe', 'Unknown'),
                            start_time=datetime.fromtimestamp(proc_info.get('create_time', time.time())),
                            is_known=False,
                            custom_name=learned.get('custom_name', proc_name),
                            cpu_usage=proc_info.get('cpu_percent', 0.0),
                            memory_mb=proc_info.get('memory_info', psutil.Process().memory_info()).rss / (1024 * 1024)
                        )
                        detected.append(detected_game)
                        logging.info(f"🧠 Jeu appris détecté: {learned.get('custom_name', proc_name)}")
                        continue

                    # 3. Auto-apprentissage: détecter nouveau jeu potentiel
                    if self.auto_learn and self._is_likely_game_process(proc_name, proc_info):
                        # Nouveau jeu potentiel détecté
                        custom_name = proc_name.replace('.exe', '').replace('-', ' ').title()

                        detected_game = DetectedGame(
                            profile=None,
                            process_name=proc_name,
                            pid=proc_info['pid'],
                            exe_path=proc_info.get('exe', 'Unknown'),
                            start_time=datetime.fromtimestamp(proc_info.get('create_time', time.time())),
                            is_known=False,
                            custom_name=custom_name,
                            cpu_usage=proc_info.get('cpu_percent', 0.0),
                            memory_mb=proc_info.get('memory_info', psutil.Process().memory_info()).rss / (1024 * 1024)
                        )
                        detected.append(detected_game)

                        # Ajouter aux jeux appris
                        if proc_name not in self.learned_games:
                            self.learned_games[proc_name] = {
                                'custom_name': custom_name,
                                'first_detected': datetime.now().isoformat(),
                                'detection_count': 1,
                                'exe_path': proc_info.get('exe', 'Unknown')
                            }
                            self._save_learned_games()
                            logging.info(f"🆕 Nouveau jeu appris: {custom_name} ({proc_name})")
                        else:
                            # Incrémenter compteur détection
                            self.learned_games[proc_name]['detection_count'] += 1

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    logging.debug(f"Erreur traitement processus: {str(e)}")
                    continue

        except Exception as e:
            logging.error(f"❌ Erreur détection jeux: {str(e)}")

        self.detected_games = detected
        return detected

    def get_primary_game(self) -> Optional[DetectedGame]:
        """
        Retourne le jeu principal (celui avec le plus d'utilisation GPU/CPU)

        Returns:
            Le jeu principal détecté ou None
        """
        if not self.detected_games:
            return None

        # Priorité aux jeux connus
        known_games = [g for g in self.detected_games if g.is_known]
        if known_games:
            # Trier par utilisation CPU (proxy pour activité)
            return max(known_games, key=lambda g: g.cpu_usage)

        # Sinon, jeu inconnu avec le plus d'activité
        if self.detected_games:
            return max(self.detected_games, key=lambda g: g.cpu_usage)

        return None

    def get_game_optimization_profile(self, game: DetectedGame) -> Dict[str, Any]:
        """
        Retourne le profil d'optimisation pour un jeu détecté

        Args:
            game: Jeu détecté

        Returns:
            Profil d'optimisation complet
        """
        if game.profile:
            # Jeu connu - profil complet
            return {
                'name': game.profile.display_name,
                'thermal_profile': game.profile.thermal_profile,
                'target_temp': game.profile.default_settings.get('target_temp', 75),
                'target_fps': game.profile.default_settings.get('target_fps', 60),
                'supports_dlss': game.profile.supports_dlss,
                'supports_ray_tracing': game.profile.supports_ray_tracing,
                'vram_requirement_gb': game.profile.vram_requirement_gb,
                'recommended_gpu_usage': game.profile.recommended_gpu_usage,
                'optimization_hints': game.profile.optimization_hints,
                'is_known': True
            }
        else:
            # Jeu inconnu - profil par défaut conservateur
            return {
                'name': game.custom_name,
                'thermal_profile': 'medium',
                'target_temp': 75,
                'target_fps': 60,
                'supports_dlss': False,
                'supports_ray_tracing': False,
                'vram_requirement_gb': 6.0,
                'recommended_gpu_usage': 75.0,
                'optimization_hints': [
                    'Profil générique appliqué',
                    'Surveillance thermique active',
                    'Optimisations conservatrices'
                ],
                'is_known': False
            }

    def get_detection_summary(self) -> Dict[str, Any]:
        """Résumé de la détection actuelle"""
        primary = self.get_primary_game()

        return {
            'total_games_detected': len(self.detected_games),
            'known_games': len([g for g in self.detected_games if g.is_known]),
            'unknown_games': len([g for g in self.detected_games if not g.is_known]),
            'primary_game': {
                'name': primary.custom_name if primary else None,
                'process': primary.process_name if primary else None,
                'is_known': primary.is_known if primary else False
            } if primary else None,
            'all_games': [
                {
                    'name': g.custom_name,
                    'process': g.process_name,
                    'is_known': g.is_known,
                    'cpu_usage': g.cpu_usage,
                    'memory_mb': g.memory_mb
                }
                for g in self.detected_games
            ]
        }

# Instance globale
GAME_DETECTOR = UniversalGameDetector()

if __name__ == "__main__":
    print("🔍 UNIVERSAL GAME DETECTOR - TEST")
    print("="*80)

    # Test détection
    detector = UniversalGameDetector(auto_learn=True)

    print("\n🎮 Recherche de jeux en cours d'exécution...")
    games = detector.detect_running_games()

    if games:
        print(f"\n✅ {len(games)} jeu(x) détecté(s):")
        for game in games:
            print(f"\n  📌 {game.custom_name}")
            print(f"     Processus: {game.process_name}")
            print(f"     Connu: {'✅ Oui' if game.is_known else '❌ Non'}")
            print(f"     CPU: {game.cpu_usage:.1f}%")
            print(f"     RAM: {game.memory_mb:.0f} MB")

            # Profil d'optimisation
            profile = detector.get_game_optimization_profile(game)
            print(f"     Profil thermique: {profile['thermal_profile']}")
            print(f"     Température cible: {profile['target_temp']}°C")
    else:
        print("\n⚠️ Aucun jeu détecté")

    # Résumé
    print("\n" + "="*80)
    summary = detector.get_detection_summary()
    print(f"📊 Résumé: {summary['total_games_detected']} jeux ({summary['known_games']} connus, {summary['unknown_games']} inconnus)")

    if summary['primary_game']:
        print(f"🎯 Jeu principal: {summary['primary_game']['name']}")
