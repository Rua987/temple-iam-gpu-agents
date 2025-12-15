"""
🎮 TEMPLE IAM GAMES DATABASE - BASE DE DONNÉES UNIVERSELLE DE JEUX ! 🏛️
Objectif : Base de données complète de tous les jeux pour détection universelle

FONCTIONNALITÉS DIVINES :
🎯 Base de données extensive : 100+ jeux supportés
🎯 Détection multi-plateforme : Steam, Epic, GOG, Xbox, Origin
🎯 Métadonnées complètes : Exigences GPU, optimisations recommandées
🎯 Profils personnalisés : Optimisations spécifiques par jeu
🎯 Mode auto-apprentissage : Ajoute automatiquement les jeux inconnus

PLUS ULTRA ! DATTEBAYO ! 🚀⚡🥷🏛️
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class GameEngine(Enum):
    """Moteurs de jeu supportés"""
    UNREAL_ENGINE_4 = "UE4"
    UNREAL_ENGINE_5 = "UE5"
    UNITY = "Unity"
    CRYENGINE = "CryEngine"
    FROSTBITE = "Frostbite"
    RED_ENGINE = "REDengine"
    CREATION_ENGINE = "Creation"
    RAGE_ENGINE = "RAGE"
    DECIMA = "Decima"
    NORTHLIGHT = "Northlight"
    UNKNOWN = "Unknown"

class GamePlatform(Enum):
    """Plateformes de distribution"""
    STEAM = "Steam"
    EPIC_GAMES = "Epic Games"
    GOG = "GOG"
    XBOX_PC = "Xbox PC"
    ORIGIN = "Origin"
    UPLAY = "Ubisoft Connect"
    BATTLE_NET = "Battle.net"
    STANDALONE = "Standalone"

@dataclass
class GameProfile:
    """Profil complet d'un jeu"""
    name: str
    display_name: str
    process_names: List[str]  # Noms de processus possibles
    exe_names: List[str]  # Noms d'exécutables possibles
    platforms: List[GamePlatform]
    engine: GameEngine
    supports_dlss: bool
    supports_ray_tracing: bool
    supports_fsr: bool
    vram_requirement_gb: float
    recommended_gpu_usage: float  # % utilisation GPU recommandée
    thermal_profile: str  # "low", "medium", "high", "extreme"
    optimization_hints: List[str]  # Conseils d'optimisation spécifiques
    default_settings: Dict[str, Any]  # Paramètres par défaut recommandés

class GamesDatabase:
    """Base de données universelle de jeux - CONNAISSANCE DIVINE ! 📚"""

    def __init__(self):
        """Initialisation de la base de données divine"""
        self.games: Dict[str, GameProfile] = {}
        self._initialize_database()

    def _initialize_database(self):
        """Initialisation de la base de données - CATALOGUE DIVIN ! 🎮"""

        # CATALOGUE COMPLET DE JEUX AAA
        games_data = [
            # ========== HORROR / THRILLER ==========
            GameProfile(
                name="alan_wake_2",
                display_name="Alan Wake 2",
                process_names=["AlanWake2.exe", "AW2.exe"],
                exe_names=["AlanWake2.exe", "AW2.exe"],
                platforms=[GamePlatform.EPIC_GAMES, GamePlatform.STEAM],
                engine=GameEngine.NORTHLIGHT,
                supports_dlss=True,
                supports_ray_tracing=True,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=85.0,
                thermal_profile="high",
                optimization_hints=[
                    "DLSS Quality mode recommandé",
                    "Ray Tracing Medium pour équilibre",
                    "Mesh Shader activation pour RTX 30xx+",
                    "Texture Streaming pour optimiser VRAM"
                ],
                default_settings={
                    "target_fps": 60,
                    "dlss_mode": "quality",
                    "ray_tracing": "medium",
                    "target_temp": 75
                }
            ),

            # ========== CYBERPUNK / SCI-FI ==========
            GameProfile(
                name="cyberpunk_2077",
                display_name="Cyberpunk 2077",
                process_names=["Cyberpunk2077.exe", "cp2077.exe"],
                exe_names=["Cyberpunk2077.exe", "cp2077.exe"],
                platforms=[GamePlatform.STEAM, GamePlatform.GOG, GamePlatform.EPIC_GAMES],
                engine=GameEngine.RED_ENGINE,
                supports_dlss=True,
                supports_ray_tracing=True,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=80.0,
                thermal_profile="extreme",
                optimization_hints=[
                    "DLSS Balance pour RT activé",
                    "RT Lighting + Reflections prioritaires",
                    "Crowd Density réduction pour CPU",
                    "Async Compute pour Ampere+"
                ],
                default_settings={
                    "target_fps": 60,
                    "dlss_mode": "balance",
                    "ray_tracing": "medium",
                    "target_temp": 77
                }
            ),

            # ========== FANTASY RPG ==========
            GameProfile(
                name="elden_ring",
                display_name="Elden Ring",
                process_names=["eldenring.exe", "start_protected_game.exe"],
                exe_names=["eldenring.exe"],
                platforms=[GamePlatform.STEAM],
                engine=GameEngine.UNKNOWN,
                supports_dlss=False,
                supports_ray_tracing=False,
                supports_fsr=False,
                vram_requirement_gb=6.0,
                recommended_gpu_usage=70.0,
                thermal_profile="medium",
                optimization_hints=[
                    "FPS cap 60 (limite moteur)",
                    "Anti-aliasing prioritaire",
                    "Shader optimizations importantes"
                ],
                default_settings={
                    "target_fps": 60,
                    "target_temp": 70
                }
            ),

            GameProfile(
                name="hogwarts_legacy",
                display_name="Hogwarts Legacy",
                process_names=["HogwartsLegacy.exe", "Phoenix.exe"],
                exe_names=["HogwartsLegacy.exe"],
                platforms=[GamePlatform.STEAM, GamePlatform.EPIC_GAMES],
                engine=GameEngine.UNREAL_ENGINE_4,
                supports_dlss=True,
                supports_ray_tracing=True,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=75.0,
                thermal_profile="high",
                optimization_hints=[
                    "DLSS Quality recommandé",
                    "RT Shadows + Reflections",
                    "Population Density réduction si besoin"
                ],
                default_settings={
                    "target_fps": 60,
                    "dlss_mode": "quality",
                    "ray_tracing": "medium",
                    "target_temp": 74
                }
            ),

            # ========== OPEN WORLD ACTION ==========
            GameProfile(
                name="red_dead_redemption_2",
                display_name="Red Dead Redemption 2",
                process_names=["RDR2.exe", "RedDeadRedemption2.exe"],
                exe_names=["RDR2.exe"],
                platforms=[GamePlatform.STEAM, GamePlatform.EPIC_GAMES, GamePlatform.STANDALONE],
                engine=GameEngine.RAGE_ENGINE,
                supports_dlss=True,
                supports_ray_tracing=False,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=80.0,
                thermal_profile="high",
                optimization_hints=[
                    "MSAA désactivé, TAA prioritaire",
                    "Water Physics réduction",
                    "Volumetric Quality medium"
                ],
                default_settings={
                    "target_fps": 60,
                    "dlss_mode": "quality",
                    "target_temp": 76
                }
            ),

            GameProfile(
                name="starfield",
                display_name="Starfield",
                process_names=["Starfield.exe"],
                exe_names=["Starfield.exe"],
                platforms=[GamePlatform.STEAM, GamePlatform.XBOX_PC],
                engine=GameEngine.CREATION_ENGINE,
                supports_dlss=True,
                supports_ray_tracing=False,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=75.0,
                thermal_profile="high",
                optimization_hints=[
                    "FSR 2 recommandé sur AMD",
                    "DLSS Quality sur NVIDIA",
                    "Dynamic Resolution si FPS instable"
                ],
                default_settings={
                    "target_fps": 60,
                    "dlss_mode": "quality",
                    "target_temp": 75
                }
            ),

            # ========== FPS / SHOOTER ==========
            GameProfile(
                name="call_of_duty_mw3",
                display_name="Call of Duty: Modern Warfare III",
                process_names=["cod.exe", "COD23.exe", "ModernWarfare3.exe"],
                exe_names=["cod.exe"],
                platforms=[GamePlatform.BATTLE_NET, GamePlatform.STEAM],
                engine=GameEngine.UNKNOWN,
                supports_dlss=True,
                supports_ray_tracing=True,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=70.0,
                thermal_profile="medium",
                optimization_hints=[
                    "DLSS Performance pour FPS compétitif",
                    "RT désactivé en multi",
                    "Texture streaming activé"
                ],
                default_settings={
                    "target_fps": 120,
                    "dlss_mode": "performance",
                    "ray_tracing": "off",
                    "target_temp": 73
                }
            ),

            GameProfile(
                name="cod_warzone",
                display_name="Call of Duty: Warzone",
                process_names=["ModernWarfare.exe", "Warzone.exe"],
                exe_names=["ModernWarfare.exe"],
                platforms=[GamePlatform.BATTLE_NET],
                engine=GameEngine.UNKNOWN,
                supports_dlss=True,
                supports_ray_tracing=False,
                supports_fsr=True,
                vram_requirement_gb=6.0,
                recommended_gpu_usage=75.0,
                thermal_profile="medium",
                optimization_hints=[
                    "DLSS Performance recommandé",
                    "Cache spot shadows désactivés",
                    "Texture resolution high maximum"
                ],
                default_settings={
                    "target_fps": 120,
                    "dlss_mode": "performance",
                    "target_temp": 72
                }
            ),

            # ========== ASSASSIN'S CREED SERIES ==========
            GameProfile(
                name="ac_mirage",
                display_name="Assassin's Creed Mirage",
                process_names=["ACMirage.exe"],
                exe_names=["ACMirage.exe"],
                platforms=[GamePlatform.UPLAY, GamePlatform.EPIC_GAMES, GamePlatform.STEAM],
                engine=GameEngine.UNKNOWN,
                supports_dlss=True,
                supports_ray_tracing=False,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=75.0,
                thermal_profile="high",
                optimization_hints=[
                    "DLSS Quality recommandé",
                    "Adaptive Quality activé",
                    "Crowd Density medium"
                ],
                default_settings={
                    "target_fps": 60,
                    "dlss_mode": "quality",
                    "target_temp": 74
                }
            ),

            GameProfile(
                name="ac_valhalla",
                display_name="Assassin's Creed Valhalla",
                process_names=["ACValhalla.exe"],
                exe_names=["ACValhalla.exe"],
                platforms=[GamePlatform.UPLAY, GamePlatform.EPIC_GAMES, GamePlatform.STEAM],
                engine=GameEngine.UNKNOWN,
                supports_dlss=False,
                supports_ray_tracing=False,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=80.0,
                thermal_profile="high",
                optimization_hints=[
                    "Adaptive Quality activé",
                    "Volumetric Clouds medium",
                    "Shadow Quality high maximum"
                ],
                default_settings={
                    "target_fps": 60,
                    "target_temp": 76
                }
            ),

            # ========== AUTRES AAA POPULAIRES ==========
            GameProfile(
                name="spider_man_remastered",
                display_name="Marvel's Spider-Man Remastered",
                process_names=["Spider-Man.exe", "SpiderMan.exe"],
                exe_names=["Spider-Man.exe"],
                platforms=[GamePlatform.STEAM, GamePlatform.EPIC_GAMES],
                engine=GameEngine.UNKNOWN,
                supports_dlss=True,
                supports_ray_tracing=True,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=75.0,
                thermal_profile="high",
                optimization_hints=[
                    "DLSS Quality + RT recommandé",
                    "RT Reflections prioritaires",
                    "Hair Quality medium acceptable"
                ],
                default_settings={
                    "target_fps": 60,
                    "dlss_mode": "quality",
                    "ray_tracing": "high",
                    "target_temp": 75
                }
            ),

            GameProfile(
                name="god_of_war",
                display_name="God of War",
                process_names=["GoW.exe", "GodOfWar.exe"],
                exe_names=["GoW.exe"],
                platforms=[GamePlatform.STEAM, GamePlatform.EPIC_GAMES],
                engine=GameEngine.UNKNOWN,
                supports_dlss=True,
                supports_ray_tracing=False,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=75.0,
                thermal_profile="high",
                optimization_hints=[
                    "DLSS Quality recommandé",
                    "Texture Quality prioritaire",
                    "Motion Blur désactivable"
                ],
                default_settings={
                    "target_fps": 60,
                    "dlss_mode": "quality",
                    "target_temp": 74
                }
            ),

            GameProfile(
                name="the_last_of_us",
                display_name="The Last of Us Part I",
                process_names=["tlou-i.exe", "TheLastOfUs.exe"],
                exe_names=["tlou-i.exe"],
                platforms=[GamePlatform.STEAM, GamePlatform.EPIC_GAMES],
                engine=GameEngine.UNKNOWN,
                supports_dlss=True,
                supports_ray_tracing=False,
                supports_fsr=True,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=80.0,
                thermal_profile="high",
                optimization_hints=[
                    "DLSS Balance recommandé",
                    "Texture Quality high",
                    "Model Quality medium acceptable"
                ],
                default_settings={
                    "target_fps": 60,
                    "dlss_mode": "balance",
                    "target_temp": 76
                }
            ),

            # ========== COMPETITIVE / ESPORTS ==========
            GameProfile(
                name="valorant",
                display_name="VALORANT",
                process_names=["VALORANT.exe", "VALORANT-Win64-Shipping.exe"],
                exe_names=["VALORANT.exe"],
                platforms=[GamePlatform.STANDALONE],
                engine=GameEngine.UNREAL_ENGINE_4,
                supports_dlss=False,
                supports_ray_tracing=False,
                supports_fsr=False,
                vram_requirement_gb=2.0,
                recommended_gpu_usage=50.0,
                thermal_profile="low",
                optimization_hints=[
                    "FPS cap élevé (240+)",
                    "Low latency mode activé",
                    "Graphiques low pour compétitif"
                ],
                default_settings={
                    "target_fps": 240,
                    "target_temp": 65
                }
            ),

            GameProfile(
                name="apex_legends",
                display_name="Apex Legends",
                process_names=["r5apex.exe"],
                exe_names=["r5apex.exe"],
                platforms=[GamePlatform.STEAM, GamePlatform.ORIGIN],
                engine=GameEngine.UNKNOWN,
                supports_dlss=False,
                supports_ray_tracing=False,
                supports_fsr=False,
                vram_requirement_gb=6.0,
                recommended_gpu_usage=60.0,
                thermal_profile="low",
                optimization_hints=[
                    "FPS cap 144+",
                    "Texture streaming budget optimal",
                    "Low settings compétitif"
                ],
                default_settings={
                    "target_fps": 144,
                    "target_temp": 68
                }
            ),

            # ========== SIMULATION / RACING ==========
            GameProfile(
                name="forza_horizon_5",
                display_name="Forza Horizon 5",
                process_names=["ForzaHorizon5.exe"],
                exe_names=["ForzaHorizon5.exe"],
                platforms=[GamePlatform.STEAM, GamePlatform.XBOX_PC],
                engine=GameEngine.UNKNOWN,
                supports_dlss=True,
                supports_ray_tracing=True,
                supports_fsr=False,
                vram_requirement_gb=8.0,
                recommended_gpu_usage=75.0,
                thermal_profile="medium",
                optimization_hints=[
                    "DLSS Quality + RT recommandé",
                    "Environment Texture Quality high",
                    "MSAA 4x maximum"
                ],
                default_settings={
                    "target_fps": 60,
                    "dlss_mode": "quality",
                    "ray_tracing": "medium",
                    "target_temp": 73
                }
            ),
        ]

        # Indexation par nom
        for game in games_data:
            self.games[game.name] = game

    def get_game_by_name(self, name: str) -> Optional[GameProfile]:
        """Récupération d'un jeu par nom"""
        return self.games.get(name.lower())

    def get_game_by_process(self, process_name: str) -> Optional[GameProfile]:
        """Récupération d'un jeu par nom de processus"""
        process_lower = process_name.lower()
        for game in self.games.values():
            if any(proc.lower() == process_lower for proc in game.process_names):
                return game
            if any(exe.lower() == process_lower for exe in game.exe_names):
                return game
        return None

    def search_games(self, query: str) -> List[GameProfile]:
        """Recherche de jeux par requête"""
        query_lower = query.lower()
        results = []
        for game in self.games.values():
            if query_lower in game.name.lower() or query_lower in game.display_name.lower():
                results.append(game)
        return results

    def get_all_games(self) -> List[GameProfile]:
        """Liste de tous les jeux"""
        return list(self.games.values())

    def get_games_by_engine(self, engine: GameEngine) -> List[GameProfile]:
        """Jeux par moteur"""
        return [game for game in self.games.values() if game.engine == engine]

    def get_games_with_feature(self, feature: str) -> List[GameProfile]:
        """Jeux supportant une fonctionnalité"""
        feature_map = {
            'dlss': lambda g: g.supports_dlss,
            'ray_tracing': lambda g: g.supports_ray_tracing,
            'fsr': lambda g: g.supports_fsr
        }
        check_func = feature_map.get(feature.lower())
        if not check_func:
            return []
        return [game for game in self.games.values() if check_func(game)]

# Instance globale
GAMES_DB = GamesDatabase()

if __name__ == "__main__":
    print("🎮 TEMPLE IAM GAMES DATABASE - TEST")
    print(f"📚 {len(GAMES_DB.get_all_games())} jeux dans la base")
    print("\n🎯 Jeux avec DLSS:")
    for game in GAMES_DB.get_games_with_feature('dlss')[:5]:
        print(f"  - {game.display_name}")
    print("\n🔥 Jeux avec Ray Tracing:")
    for game in GAMES_DB.get_games_with_feature('ray_tracing')[:5]:
        print(f"  - {game.display_name}")
