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
    """Workload GPU détecté avec informations en temps réel (jeu, IA locale, etc.)"""
    profile: Optional[GameProfile]
    process_name: str
    pid: int
    exe_path: str
    start_time: datetime
    is_known: bool  # Si le jeu est dans la base de données
    custom_name: str  # Nom personnalisé pour jeux inconnus
    cpu_usage: float
    memory_mb: float
    category: str = "gaming"  # gaming, local_ai, browser_webview, unknown_gpu_app


# Workloads GPU non-jeux connus : on les détecte et on adapte l'optimisation
# au lieu de les traiter comme des jeux.
KNOWN_WORKLOAD_CATEGORIES = {
    # IA locale - charge GPU soutenue, priorité au refroidissement stable
    'ollama.exe': 'local_ai',
    'lm studio.exe': 'local_ai',
    'lmstudio.exe': 'local_ai',
    'koboldcpp.exe': 'local_ai',
    'llama-server.exe': 'local_ai',
    'text-generation-webui.exe': 'local_ai',
    'comfyui.exe': 'local_ai',
    # WebView/navigateurs embarqués - GPU léger, observation seulement
    'msedgewebview2.exe': 'browser_webview',
    'webview2.exe': 'browser_webview',
}

# Marqueurs par SOUS-CHAINE, testés si l'exact-match ci-dessus échoue.
# Necessaire car les suites IA lancent plusieurs binaires: le serveur
# ("ollama.exe") mais aussi l'interface ("ollama app.exe") et des helpers.
# Sans ca, "ollama app.exe" tombait en 'unknown_gpu_app' et s'affichait avec
# une cible FPS - absurde pour de l'inference.
WORKLOAD_NAME_MARKERS = (
    ('ollama', 'local_ai'),
    ('lm studio', 'local_ai'),
    ('lmstudio', 'local_ai'),
    ('koboldcpp', 'local_ai'),
    ('llama-server', 'local_ai'),
    ('llama_server', 'local_ai'),
    ('llamacpp', 'local_ai'),
    ('llama.cpp', 'local_ai'),
    ('text-generation-webui', 'local_ai'),
    ('comfyui', 'local_ai'),
    ('stable-diffusion', 'local_ai'),
    ('webview2', 'browser_webview'),
)

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

        # Liste de processus systeme a ignorer (COMPLETE!)
        self.ignore_processes = {
            # Windows systeme core
            'explorer.exe', 'svchost.exe', 'system', 'registry', 'idle',
            'dwm.exe', 'csrss.exe', 'winlogon.exe', 'services.exe',
            'lsass.exe', 'smss.exe', 'wininit.exe', 'taskhostw.exe',
            'runtimebroker.exe', 'searchindexer.exe', 'msiexec.exe',
            'conhost.exe', 'dllhost.exe', 'audiodg.exe', 'spoolsv.exe',
            'fontdrvhost.exe', 'sihost.exe', 'ctfmon.exe', 'dashost.exe',
            'shellexperiencehost.exe', 'startmenuexperiencehost.exe',
            'searchhost.exe', 'textinputhost.exe', 'applicationframehost.exe',

            # Windows Update et Services
            'usoclient.exe', 'sihclient.exe', 'wuauclt.exe', 'trustedinstaller.exe',
            'tiworker.exe', 'musnotification.exe', 'windowsupdateelevatedinstaller.exe',

            # Windows memoire et compression
            'memcompression', 'vmmem', 'vmmemwsl', 'memory compression',

            # Antivirus et securite (TOUTES les variantes!)
            'msmpeng.exe', 'MsMpEng.exe', 'msmpeng', 'mssense.exe', 'nissrv.exe',
            'securityhealthservice.exe', 'securityhealthsystray.exe',
            'avastui.exe', 'avgui.exe', 'mbamservice.exe', 'mbam.exe',
            'avgnt.exe', 'avguard.exe', 'avshadow.exe',
            'windows defender', 'defender', 'antimalware service executable',

            # Navigateurs
            'chrome.exe', 'firefox.exe', 'edge.exe', 'brave.exe',
            'msedge.exe', 'opera.exe', 'vivaldi.exe', 'iexplore.exe',
            'chromium.exe', 'tor.exe',

            # Communication
            'discord.exe', 'spotify.exe', 'slack.exe', 'teams.exe',
            'zoom.exe', 'skype.exe', 'telegram.exe', 'whatsapp.exe',
            'signal.exe', 'guilded.exe',

            # Developpement et editeurs
            'code.exe', 'notepad.exe', 'notepad++.exe', 'sublime_text.exe',
            'pycharm64.exe', 'idea64.exe', 'rider64.exe', 'webstorm64.exe',
            'python.exe', 'pythonw.exe', 'node.exe', 'java.exe', 'javaw.exe',
            'cmd.exe', 'powershell.exe', 'pwsh.exe', 'bash.exe', 'wsl.exe',
            'git.exe', 'ssh.exe', 'mintty.exe', 'windowsterminal.exe',

            # AI Assistants
            'claude.exe', 'claude code.exe', 'cursor.exe', 'copilot.exe',

            # GPU/Hardware utilities
            'nvcontainer.exe', 'nvidia web helper.exe', 'nvidia share.exe',
            'nvdisplay.container.exe', 'nvspcaps64.exe', 'nvbackend.exe',
            'nvtelemetrycontainer.exe', 'nvcplui.exe',
            'radeonrelivehost.exe', 'amdrsserv.exe', 'amddvr.exe',

            # Launchers helpers (not the games themselves)
            'steamwebhelper.exe', 'epicwebhelper.exe', 'origin.exe',
            'uplay.exe', 'uplaywebcore.exe', 'battlenet.exe', 'battle.net.exe',
            'eadesktop.exe', 'eabackgroundservice.exe',
            'gogalaxy.exe', 'gogalaxycommunication.exe',

            # Utilitaires systeme
            'taskmgr.exe', 'perfmon.exe', 'resmon.exe', 'mmc.exe',
            'control.exe', 'regedit.exe', 'msconfig.exe', 'systemsettings.exe',
            'settingssynchost.exe', 'phoneexperiencehost.exe'
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

    def _classify_workload(self, proc_name: str) -> str:
        """
        Classe un processus détecté par type de workload GPU.

        Returns:
            'gaming', 'local_ai', 'browser_webview' ou 'unknown_gpu_app'
        """
        name = proc_name.lower()
        exact = KNOWN_WORKLOAD_CATEGORIES.get(name)
        if exact:
            return exact
        # Repli par sous-chaine: attrape les variantes (GUI, helpers, serveurs)
        # d'une meme suite, ex. "ollama app.exe" ou "LM Studio Helper.exe".
        for marker, category in WORKLOAD_NAME_MARKERS:
            if marker in name:
                return category
        return 'unknown_gpu_app'

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

                    # 0. FILTRAGE PRIORITAIRE : Ignorer les processus système
                    proc_name_lower = proc_name.lower()
                    if proc_name_lower in self.ignore_processes:
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
                            memory_mb=proc_info.get('memory_info', psutil.Process().memory_info()).rss / (1024 * 1024),
                            category='gaming'
                        )
                        detected.append(detected_game)
                        logging.info(f"🎮 Jeu connu détecté: {game_profile.display_name}")
                        continue

                    # 2. Vérifier dans les workloads appris
                    if proc_name in self.learned_games:
                        learned = self.learned_games[proc_name]
                        # Une regle explicite prime sur une categorie APPRISE:
                        # l'auto-apprentissage a pu figer un 'unknown_gpu_app'
                        # avant que le marqueur existe (ex. "ollama app.exe").
                        # Auto-repare donc les entrees periemees sans editer le JSON.
                        classified = self._classify_workload(proc_name)
                        category = (classified if classified != 'unknown_gpu_app'
                                    else (learned.get('category') or 'unknown_gpu_app'))
                        detected_game = DetectedGame(
                            profile=None,
                            process_name=proc_name,
                            pid=proc_info['pid'],
                            exe_path=proc_info.get('exe', 'Unknown'),
                            start_time=datetime.fromtimestamp(proc_info.get('create_time', time.time())),
                            is_known=False,
                            custom_name=learned.get('custom_name', proc_name),
                            cpu_usage=proc_info.get('cpu_percent', 0.0),
                            memory_mb=proc_info.get('memory_info', psutil.Process().memory_info()).rss / (1024 * 1024),
                            category=category
                        )
                        detected.append(detected_game)
                        logging.info(f"🧠 Workload appris détecté: {learned.get('custom_name', proc_name)} [{category}]")
                        continue

                    # 3. Auto-apprentissage: détecter nouveau workload GPU potentiel
                    if self.auto_learn and self._is_likely_game_process(proc_name, proc_info):
                        # Nouveau workload potentiel détecté
                        custom_name = proc_name.replace('.exe', '').replace('-', ' ').title()
                        category = self._classify_workload(proc_name)

                        detected_game = DetectedGame(
                            profile=None,
                            process_name=proc_name,
                            pid=proc_info['pid'],
                            exe_path=proc_info.get('exe', 'Unknown'),
                            start_time=datetime.fromtimestamp(proc_info.get('create_time', time.time())),
                            is_known=False,
                            custom_name=custom_name,
                            cpu_usage=proc_info.get('cpu_percent', 0.0),
                            memory_mb=proc_info.get('memory_info', psutil.Process().memory_info()).rss / (1024 * 1024),
                            category=category
                        )
                        detected.append(detected_game)

                        # Ajouter aux workloads appris
                        if proc_name not in self.learned_games:
                            self.learned_games[proc_name] = {
                                'custom_name': custom_name,
                                'category': category,
                                'first_detected': datetime.now().isoformat(),
                                'detection_count': 1,
                                'exe_path': proc_info.get('exe', 'Unknown')
                            }
                            self._save_learned_games()
                            logging.info(f"🆕 Nouveau workload appris: {custom_name} ({proc_name}) [{category}]")
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

        # Sinon, workload actif le plus chargé - les webviews passent en dernier
        # (un webview ne doit jamais primer sur une IA locale ou un jeu inconnu)
        non_webview = [g for g in self.detected_games if g.category != 'browser_webview']
        candidates = non_webview if non_webview else self.detected_games
        return max(candidates, key=lambda g: g.cpu_usage)

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
                'category': 'gaming',
                'optimization_mode': 'active',
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

        if game.category == 'local_ai':
            # IA locale (Ollama, LM Studio...) - charge GPU soutenue sans notion de FPS.
            # Priorité : refroidissement stable pour éviter le throttling pendant l'inférence.
            return {
                'name': game.custom_name,
                'category': 'local_ai',
                'optimization_mode': 'stable_cooling',
                'thermal_profile': 'medium',
                'target_temp': 70,
                'target_fps': 0,  # Pas de FPS pour l'inférence IA
                'supports_dlss': False,
                'supports_ray_tracing': False,
                'vram_requirement_gb': 6.0,
                'recommended_gpu_usage': 90.0,
                'optimization_hints': [
                    'Workload IA locale détecté',
                    'Priorité au refroidissement stable (anti-throttling)',
                    'Pas de cible FPS - débit de tokens privilégié'
                ],
                'is_known': False
            }

        if game.category == 'browser_webview':
            # WebView/navigateur embarqué - on observe sans intervenir.
            return {
                'name': game.custom_name,
                'category': 'browser_webview',
                'optimization_mode': 'observe_only',
                'thermal_profile': 'low',
                'target_temp': 75,
                'target_fps': 0,
                'supports_dlss': False,
                'supports_ray_tracing': False,
                'vram_requirement_gb': 1.0,
                'recommended_gpu_usage': 30.0,
                'optimization_hints': [
                    'WebView détecté - observation seulement',
                    'Aucune optimisation GPU appliquée'
                ],
                'is_known': False
            }

        # Workload GPU inconnu - profil par défaut conservateur
        return {
            'name': game.custom_name,
            'category': game.category,
            'optimization_mode': 'active',
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
                    'category': g.category,
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
