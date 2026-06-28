"""
🎯 SWEET SPOT FINDER - TROUVER L'ÉQUILIBRE PARFAIT FPS/TEMPÉRATURE ! 🔥
Objectif : Trouver automatiquement le meilleur compromis performance/thermique

CONCEPT :
Le "Sweet Spot" est le point où :
- Les FPS sont maximisés
- La température reste contrôlée
- Le GPU n'est ni sous-exploité ni en throttle

ALGORITHME :
1. Collecter données FPS + Température sur plusieurs niveaux de clocks
2. Calculer le score Efficacité = FPS / (Temp - Temp_idle)
3. Trouver le point où l'efficacité diminue (rendements décroissants)
4. Recommander les paramètres optimaux

PLUS ULTRA ! DATTEBAYO ! 🚀⚡
"""

import time
import logging
import json
import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import threading

logging.basicConfig(level=logging.INFO, format='🎯 %(asctime)s - %(levelname)s - %(message)s')


@dataclass
class PerformancePoint:
    """Point de données performance pour l'analyse"""
    timestamp: float
    clock_mhz: int
    temperature: float
    fps: float
    gpu_usage: float
    power_draw: float
    frametime_ms: float = 0.0

    @property
    def efficiency(self) -> float:
        """Score d'efficacité = FPS par degré au-dessus de l'idle"""
        temp_delta = max(1, self.temperature - 40)  # 40°C = idle approximatif
        return self.fps / temp_delta if self.fps > 0 else 0

    @property
    def perf_per_watt(self) -> float:
        """Performance par Watt"""
        return self.fps / self.power_draw if self.power_draw > 0 else 0


@dataclass
class SweetSpotResult:
    """Résultat de l'analyse Sweet Spot"""
    optimal_clock_mhz: int
    optimal_temp_target: float
    expected_fps: float
    expected_temp: float
    efficiency_score: float
    confidence: float
    recommendation: str
    analysis_details: Dict[str, Any] = field(default_factory=dict)


class SweetSpotFinder:
    """
    Sweet Spot Finder - OPTIMISATION DIVINE ! 🎯
    Trouve automatiquement l'équilibre parfait FPS/Température
    """

    # Niveaux de clocks à tester (RTX 2070)
    CLOCK_LEVELS = [
        1500,  # Power Save
        1700,  # Quiet
        1850,  # Balanced Low
        1950,  # Balanced
        2000,  # Performance Low
        2100,  # Performance Max
    ]

    def __init__(self, data_path: str = "sweet_spot_data.json"):
        self.data_path = data_path

        # Données par jeu
        self.game_data: Dict[str, Dict[int, List[PerformancePoint]]] = {}

        # Résultats sauvegardés
        self.sweet_spots: Dict[str, SweetSpotResult] = {}

        # État de l'analyse
        self.is_analyzing = False
        self.current_game: Optional[str] = None
        self.analysis_buffer: List[PerformancePoint] = []

        # Paramètres
        self.min_samples_per_level = 30  # 30 secondes par niveau de clock
        self.target_temp_max = 85  # Température max acceptable
        self.fps_threshold = 0.95  # 95% des FPS max acceptables

        # Charger les données existantes
        self._load_data()

        logging.info("🎯 Sweet Spot Finder initialisé")
        logging.info(f"   Jeux analysés: {len(self.sweet_spots)}")

    def _load_data(self):
        """Charge les données d'analyse précédentes"""
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for game_name, spot_data in data.get('sweet_spots', {}).items():
                    self.sweet_spots[game_name] = SweetSpotResult(
                        optimal_clock_mhz=spot_data.get('optimal_clock_mhz', 1950),
                        optimal_temp_target=spot_data.get('optimal_temp_target', 75),
                        expected_fps=spot_data.get('expected_fps', 0),
                        expected_temp=spot_data.get('expected_temp', 0),
                        efficiency_score=spot_data.get('efficiency_score', 0),
                        confidence=spot_data.get('confidence', 0),
                        recommendation=spot_data.get('recommendation', ''),
                        analysis_details=spot_data.get('analysis_details', {})
                    )

                logging.info(f"✅ Données Sweet Spot chargées: {len(self.sweet_spots)} jeux")
        except Exception as e:
            logging.warning(f"⚠️ Erreur chargement données Sweet Spot: {e}")

    def _save_data(self):
        """Sauvegarde les données d'analyse"""
        try:
            data = {
                'sweet_spots': {},
                'version': '1.0',
                'last_save': datetime.now().isoformat()
            }

            for game_name, spot in self.sweet_spots.items():
                data['sweet_spots'][game_name] = {
                    'optimal_clock_mhz': spot.optimal_clock_mhz,
                    'optimal_temp_target': spot.optimal_temp_target,
                    'expected_fps': spot.expected_fps,
                    'expected_temp': spot.expected_temp,
                    'efficiency_score': spot.efficiency_score,
                    'confidence': spot.confidence,
                    'recommendation': spot.recommendation,
                    'analysis_details': spot.analysis_details
                }

            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logging.info(f"💾 Données Sweet Spot sauvegardées")
        except Exception as e:
            logging.error(f"❌ Erreur sauvegarde données Sweet Spot: {e}")

    def set_current_game(self, game_name: Optional[str]):
        """Définit le jeu actuel pour l'analyse"""
        if game_name != self.current_game:
            self.current_game = game_name
            self.analysis_buffer.clear()

            if game_name:
                if game_name not in self.game_data:
                    self.game_data[game_name] = {level: [] for level in self.CLOCK_LEVELS}
                logging.info(f"🎮 Sweet Spot: Analyse active pour {game_name}")

    def add_data_point(self, clock_mhz: int, temperature: float, fps: float,
                       gpu_usage: float, power_draw: float, frametime_ms: float = 0.0):
        """Ajoute un point de données pour l'analyse"""
        if not self.current_game:
            return

        # 🛡️ VALIDATION: Ignorer les points de données invalides
        # Température doit être > 30°C (sinon c'est une erreur de lecture)
        # Clock doit être > 0
        # FPS doit être > 0
        if temperature < 30 or clock_mhz <= 0 or fps <= 0:
            return

        point = PerformancePoint(
            timestamp=time.time(),
            clock_mhz=clock_mhz,
            temperature=temperature,
            fps=fps,
            gpu_usage=gpu_usage,
            power_draw=power_draw,
            frametime_ms=frametime_ms
        )

        self.analysis_buffer.append(point)

        # Classifier par niveau de clock le plus proche
        closest_level = min(self.CLOCK_LEVELS, key=lambda x: abs(x - clock_mhz))

        if self.current_game in self.game_data:
            self.game_data[self.current_game][closest_level].append(point)

            # Limiter la taille des données
            if len(self.game_data[self.current_game][closest_level]) > 600:  # 10 min max
                self.game_data[self.current_game][closest_level].pop(0)

    def analyze_sweet_spot(self, game_name: str = None) -> Optional[SweetSpotResult]:
        """
        Analyse les données et trouve le Sweet Spot optimal

        Algorithme :
        1. Pour chaque niveau de clock, calculer FPS moyen et Temp moyenne
        2. Calculer l'efficacité (FPS/°C) pour chaque niveau
        3. Trouver le point de rendements décroissants
        4. Recommander le clock optimal
        """
        if game_name is None:
            game_name = self.current_game

        if not game_name or game_name not in self.game_data:
            return None

        game_points = self.game_data[game_name]

        # Collecter les statistiques par niveau
        level_stats: Dict[int, Dict[str, float]] = {}

        for clock_level, points in game_points.items():
            if len(points) < 10:  # Minimum 10 points
                continue

            fps_list = [p.fps for p in points if p.fps > 0]
            temp_list = [p.temperature for p in points if p.temperature > 30]  # Filtrer températures invalides
            power_list = [p.power_draw for p in points if p.power_draw > 0]
            usage_list = [p.gpu_usage for p in points]

            if not fps_list or not temp_list:
                continue

            avg_fps = sum(fps_list) / len(fps_list)
            avg_temp = sum(temp_list) / len(temp_list)

            # 🛡️ Si température moyenne invalide, skip ce niveau
            if avg_temp < 30:
                logging.warning(f"⚠️ Sweet Spot: Température invalide pour {clock_level}MHz ({avg_temp}°C)")
                continue
            avg_power = sum(power_list) / len(power_list) if power_list else 0
            avg_usage = sum(usage_list) / len(usage_list)

            # Calculer l'efficacité
            temp_delta = max(1, avg_temp - 40)  # 40°C idle
            efficiency = avg_fps / temp_delta

            # Performance par watt
            perf_per_watt = avg_fps / avg_power if avg_power > 0 else 0

            level_stats[clock_level] = {
                'avg_fps': avg_fps,
                'avg_temp': avg_temp,
                'avg_power': avg_power,
                'avg_usage': avg_usage,
                'efficiency': efficiency,
                'perf_per_watt': perf_per_watt,
                'samples': len(points)
            }

        if len(level_stats) < 2:
            logging.warning(f"⚠️ Pas assez de données pour analyser {game_name}")
            return None

        # Trouver le Sweet Spot
        # Critères :
        # 1. FPS >= 95% du FPS max
        # 2. Température <= target_temp_max
        # 3. Meilleure efficacité

        max_fps = max(s['avg_fps'] for s in level_stats.values())
        fps_threshold = max_fps * self.fps_threshold

        candidates = []
        for clock, stats in level_stats.items():
            if stats['avg_fps'] >= fps_threshold and stats['avg_temp'] <= self.target_temp_max:
                candidates.append((clock, stats))

        if not candidates:
            # Fallback : prendre celui avec la meilleure efficacité sous le seuil de temp
            candidates = [
                (clock, stats) for clock, stats in level_stats.items()
                if stats['avg_temp'] <= self.target_temp_max
            ]

        if not candidates:
            # Dernier recours : prendre le plus froid
            candidates = [(clock, stats) for clock, stats in level_stats.items()]
            candidates.sort(key=lambda x: x[1]['avg_temp'])

        # Trier par efficacité décroissante
        candidates.sort(key=lambda x: x[1]['efficiency'], reverse=True)

        # Le Sweet Spot est le premier candidat
        optimal_clock, optimal_stats = candidates[0]

        # Calculer la confiance basée sur le nombre d'échantillons
        total_samples = sum(s['samples'] for s in level_stats.values())
        confidence = min(1.0, total_samples / 500)  # 500 samples = confiance max

        # Générer la recommandation
        if optimal_stats['avg_temp'] < 70:
            recommendation = f"🚀 GPU sous-exploité ! Tu peux augmenter les graphiques du jeu."
        elif optimal_stats['avg_temp'] > 80:
            recommendation = f"🔥 GPU chaud - Équilibre atteint, évite d'augmenter les clocks."
        else:
            recommendation = f"✅ Sweet Spot trouvé ! Équilibre optimal performance/température."

        # Ajouter analyse détaillée
        analysis_details = {
            'all_levels': {str(k): v for k, v in level_stats.items()},
            'max_fps_observed': max_fps,
            'fps_threshold_used': fps_threshold,
            'candidates_count': len(candidates),
            'analysis_date': datetime.now().isoformat()
        }

        result = SweetSpotResult(
            optimal_clock_mhz=optimal_clock,
            optimal_temp_target=min(optimal_stats['avg_temp'] + 5, 85),  # +5°C marge
            expected_fps=optimal_stats['avg_fps'],
            expected_temp=optimal_stats['avg_temp'],
            efficiency_score=optimal_stats['efficiency'],
            confidence=confidence,
            recommendation=recommendation,
            analysis_details=analysis_details
        )

        # Sauvegarder le résultat
        self.sweet_spots[game_name] = result
        self._save_data()

        logging.info(f"🎯 Sweet Spot trouvé pour {game_name}:")
        logging.info(f"   Clock optimal: {optimal_clock} MHz")
        logging.info(f"   FPS attendu: {optimal_stats['avg_fps']:.1f}")
        logging.info(f"   Temp attendue: {optimal_stats['avg_temp']:.1f}°C")
        logging.info(f"   Efficacité: {optimal_stats['efficiency']:.2f}")

        return result

    def get_sweet_spot(self, game_name: str = None) -> Optional[SweetSpotResult]:
        """Retourne le Sweet Spot pour un jeu (depuis le cache ou analyse)"""
        if game_name is None:
            game_name = self.current_game

        if not game_name:
            return None

        # Vérifier si on a déjà analysé ce jeu
        if game_name in self.sweet_spots:
            return self.sweet_spots[game_name]

        # Sinon, tenter une analyse
        return self.analyze_sweet_spot(game_name)

    def get_real_time_recommendation(self, current_temp: float, current_fps: float,
                                     current_clock: int) -> Dict[str, Any]:
        """
        Donne une recommandation en temps réel basée sur les données actuelles
        et le Sweet Spot connu (si disponible)
        """
        recommendation = {
            'action': 'none',
            'reason': '',
            'target_clock': current_clock,
            'confidence': 0.0
        }

        if not self.current_game:
            return recommendation

        sweet_spot = self.get_sweet_spot()

        if not sweet_spot:
            # Pas de Sweet Spot connu - recommandations basiques
            if current_temp > 85:
                recommendation['action'] = 'reduce_clock'
                recommendation['reason'] = f"Température élevée ({current_temp}°C)"
                recommendation['target_clock'] = max(1500, current_clock - 100)
            elif current_temp < 65 and current_fps > 0:
                recommendation['action'] = 'increase_clock'
                recommendation['reason'] = f"Marge thermique disponible ({65 - current_temp}°C)"
                recommendation['target_clock'] = min(2100, current_clock + 100)

            recommendation['confidence'] = 0.3
            return recommendation

        # Avec Sweet Spot connu
        recommendation['confidence'] = sweet_spot.confidence

        # Comparer avec les valeurs attendues
        temp_delta = current_temp - sweet_spot.expected_temp
        fps_ratio = current_fps / sweet_spot.expected_fps if sweet_spot.expected_fps > 0 else 1.0

        if current_temp > sweet_spot.optimal_temp_target + 5:
            # Trop chaud - réduire vers le sweet spot
            recommendation['action'] = 'reduce_clock'
            recommendation['reason'] = f"Dépasse Sweet Spot temp ({current_temp}°C > {sweet_spot.optimal_temp_target}°C)"
            recommendation['target_clock'] = sweet_spot.optimal_clock_mhz

        elif current_temp < sweet_spot.optimal_temp_target - 10 and fps_ratio < 0.9:
            # Froid mais FPS bas - augmenter
            recommendation['action'] = 'increase_clock'
            recommendation['reason'] = f"Marge thermique ({sweet_spot.optimal_temp_target - current_temp}°C) et FPS bas"
            recommendation['target_clock'] = min(2100, current_clock + 100)

        elif current_clock != sweet_spot.optimal_clock_mhz:
            # Pas au clock optimal
            if abs(current_clock - sweet_spot.optimal_clock_mhz) > 100:
                recommendation['action'] = 'adjust_clock'
                recommendation['reason'] = f"Ajustement vers Sweet Spot ({sweet_spot.optimal_clock_mhz}MHz)"
                recommendation['target_clock'] = sweet_spot.optimal_clock_mhz

        return recommendation

    def get_game_summary(self, game_name: str = None) -> Dict[str, Any]:
        """Retourne le résumé de l'analyse pour un jeu"""
        if game_name is None:
            game_name = self.current_game

        if not game_name:
            return {}

        sweet_spot = self.get_sweet_spot(game_name)

        if not sweet_spot:
            # Retourner les données brutes si pas de sweet spot
            if game_name in self.game_data:
                total_points = sum(len(points) for points in self.game_data[game_name].values())
                return {
                    'game': game_name,
                    'status': 'collecting',
                    'total_points': total_points,
                    'message': f"Collecte en cours... ({total_points} points)"
                }
            return {}

        return {
            'game': game_name,
            'status': 'analyzed',
            'optimal_clock_mhz': sweet_spot.optimal_clock_mhz,
            'optimal_temp_target': sweet_spot.optimal_temp_target,
            'expected_fps': round(sweet_spot.expected_fps, 1),
            'expected_temp': round(sweet_spot.expected_temp, 1),
            'efficiency_score': round(sweet_spot.efficiency_score, 2),
            'confidence': round(sweet_spot.confidence * 100, 0),
            'recommendation': sweet_spot.recommendation
        }

    def get_all_games_summary(self) -> List[Dict[str, Any]]:
        """Retourne le résumé de tous les jeux analysés"""
        summaries = []
        for game_name in self.sweet_spots:
            summaries.append(self.get_game_summary(game_name))
        return summaries


# Instance globale
SWEET_SPOT_FINDER = SweetSpotFinder()


def test_sweet_spot_finder():
    """Test du Sweet Spot Finder"""
    import numpy as np

    print("=" * 60)
    print("🎯 TEST SWEET SPOT FINDER - TEMPLE IAM")
    print("=" * 60)

    finder = SweetSpotFinder()
    finder.set_current_game("Test Game")

    print("\n📊 Simulation de données performance...")

    # Simuler différents niveaux de clock avec des comportements réalistes
    for clock in [1500, 1700, 1850, 1950, 2100]:
        print(f"\n   Simulation {clock}MHz...")

        for i in range(50):
            # Plus le clock est élevé, plus les FPS sont hauts mais plus ça chauffe
            base_fps = 60 + (clock - 1500) * 0.05
            fps = base_fps + np.random.normal(0, 3)

            # Température proportionnelle au clock
            base_temp = 50 + (clock - 1500) * 0.02
            temp = base_temp + np.random.normal(0, 2)

            # Puissance aussi proportionnelle
            power = 80 + (clock - 1500) * 0.05 + np.random.normal(0, 5)

            usage = 70 + np.random.normal(0, 10)

            finder.add_data_point(clock, temp, fps, usage, power)

    # Analyser
    print("\n🔍 Analyse Sweet Spot...")
    result = finder.analyze_sweet_spot()

    if result:
        print(f"\n🎯 RÉSULTAT SWEET SPOT:")
        print(f"   Clock optimal: {result.optimal_clock_mhz} MHz")
        print(f"   Temp cible: {result.optimal_temp_target}°C")
        print(f"   FPS attendu: {result.expected_fps:.1f}")
        print(f"   Temp attendue: {result.expected_temp:.1f}°C")
        print(f"   Efficacité: {result.efficiency_score:.2f}")
        print(f"   Confiance: {result.confidence*100:.0f}%")
        print(f"   {result.recommendation}")

    # Test recommandation temps réel
    print(f"\n🔮 Test recommandation temps réel:")
    rec = finder.get_real_time_recommendation(current_temp=75, current_fps=70, current_clock=2000)
    print(f"   Action: {rec['action']}")
    print(f"   Raison: {rec['reason']}")
    print(f"   Clock cible: {rec['target_clock']}MHz")

    print("\n" + "=" * 60)
    print("✅ TEST SWEET SPOT TERMINÉ")
    print("=" * 60)


if __name__ == "__main__":
    test_sweet_spot_finder()
