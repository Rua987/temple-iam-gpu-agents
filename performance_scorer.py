"""
PERFORMANCE SCORER - SCORE GLOBAL DE PERFORMANCE GPU !
Objectif : Calculer un score unifie (0-100) combinant toutes les metriques

METRIQUES COMBINEES :
- Thermal Score (30%) : Temperature sous controle ?
- FPS Score (30%) : FPS stable et eleve ?
- Efficiency Score (20%) : GPU bien exploite ?
- Stability Score (20%) : Pas de stutters/drops ?

UTILISATION :
- Decisions automatiques basees sur le score global
- Comparaison entre sessions/jeux
- Dashboard unifie

PLUS ULTRA ! DATTEBAYO !
"""

import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PerformanceState(Enum):
    """Etat de performance base sur le score global"""
    EMERGENCY = "emergency"      # Score < 30 - Actions urgentes requises
    POOR = "poor"                # Score 30-50 - Performance degradee
    ACCEPTABLE = "acceptable"    # Score 50-70 - OK mais peut mieux faire
    GOOD = "good"                # Score 70-85 - Bonne performance
    EXCELLENT = "excellent"      # Score 85-95 - Excellente performance
    PEAK = "peak"                # Score > 95 - Performance optimale !


class OptimizationStrategy(Enum):
    """Strategie d'optimisation recommandee"""
    EMERGENCY_THROTTLE = "emergency_throttle"   # Throttle agressif immediat
    THERMAL_FOCUS = "thermal_focus"             # Priorite refroidissement
    BALANCED = "balanced"                       # Equilibre temp/FPS
    PERFORMANCE = "performance"                 # Priorite FPS
    BOOST = "boost"                             # Mode boost (GPU froid)


@dataclass
class ScoreBreakdown:
    """Detail des scores individuels"""
    thermal_score: float = 0.0          # 0-100
    fps_score: float = 0.0              # 0-100
    efficiency_score: float = 0.0       # 0-100
    stability_score: float = 0.0        # 0-100

    # Bonus/malus
    bonus_headroom: float = 0.0         # Bonus si marge thermique
    bonus_boost_active: float = 0.0     # Bonus si boost actif
    malus_throttle: float = 0.0         # Malus si throttle actif
    malus_bottleneck: float = 0.0       # Malus si bottleneck detecte

    # Details pour debug
    thermal_details: str = ""
    fps_details: str = ""
    efficiency_details: str = ""
    stability_details: str = ""


@dataclass
class PerformanceScore:
    """Resultat du scoring de performance"""
    overall_score: float                         # Score global 0-100
    state: PerformanceState                      # Etat de performance
    recommended_strategy: OptimizationStrategy   # Strategie recommandee
    breakdown: ScoreBreakdown                    # Details des scores
    timestamp: datetime = field(default_factory=datetime.now)

    # Contexte
    game_name: str = ""
    thermal_profile: str = "medium"

    # Tendance
    trend: str = "stable"              # rising, stable, falling
    score_delta: float = 0.0           # Variation vs derniere mesure

    # Recommandations
    recommendations: List[str] = field(default_factory=list)


class PerformanceScorer:
    """
    Calculateur de score de performance global - SCORING DIVIN !

    Combine toutes les metriques en un score unique (0-100)
    pour faciliter les decisions automatiques et le monitoring.
    """

    # Poids des differentes metriques
    WEIGHTS = {
        'thermal': 0.30,      # 30% - Temperature
        'fps': 0.30,          # 30% - FPS
        'efficiency': 0.20,   # 20% - Efficacite GPU
        'stability': 0.20     # 20% - Stabilite
    }

    # Seuils de score pour chaque etat
    STATE_THRESHOLDS = {
        PerformanceState.EMERGENCY: 30,
        PerformanceState.POOR: 50,
        PerformanceState.ACCEPTABLE: 70,
        PerformanceState.GOOD: 85,
        PerformanceState.EXCELLENT: 95
        # Au dessus de 95 = PEAK
    }

    def __init__(self):
        """Initialisation du scorer"""
        self.score_history: List[PerformanceScore] = []
        self.max_history = 500

        # Moyennes mobiles pour stabilite
        self.fps_samples: List[float] = []
        self.temp_samples: List[float] = []
        self.max_samples = 30  # 30 dernieres secondes

        # Configuration par defaut (sera mise a jour selon le jeu)
        self.config = {
            'target_temp': 75.0,
            'critical_temp': 88.0,
            'target_fps': 60.0,
            'min_acceptable_fps': 30.0,
            'optimal_gpu_usage': 85.0  # % usage GPU optimal
        }

        logging.info("Performance Scorer initialise - SCORING DIVIN ACTIF !")

    def configure_for_game(self, game_profile: Dict[str, Any]):
        """Configure le scorer selon le profil du jeu"""
        if not game_profile:
            return

        self.config['target_temp'] = game_profile.get('target_temp', 75.0)
        self.config['target_fps'] = game_profile.get('target_fps', 60.0)

        # Ajuster selon le profil thermique
        thermal_profile = game_profile.get('thermal_profile', 'medium')

        profile_adjustments = {
            'ultra': {'critical_temp': 78, 'optimal_gpu_usage': 95},
            'extreme': {'critical_temp': 80, 'optimal_gpu_usage': 95},
            'high': {'critical_temp': 85, 'optimal_gpu_usage': 90},
            'medium': {'critical_temp': 88, 'optimal_gpu_usage': 85},
            'low': {'critical_temp': 90, 'optimal_gpu_usage': 75},
            'esport': {'critical_temp': 90, 'optimal_gpu_usage': 90}
        }

        if thermal_profile in profile_adjustments:
            adj = profile_adjustments[thermal_profile]
            self.config['critical_temp'] = adj['critical_temp']
            self.config['optimal_gpu_usage'] = adj['optimal_gpu_usage']

        logging.info(f"Scorer configure pour profil: {thermal_profile} "
                    f"(cible: {self.config['target_temp']}C, "
                    f"FPS cible: {self.config['target_fps']})")

    def calculate_score(self,
                       temperature: float,
                       gpu_usage: float,
                       fps_current: float = 0,
                       fps_avg: float = 0,
                       fps_1_low: float = 0,
                       frametime_ms: float = 0,
                       clock_current: int = 0,
                       clock_max: int = 2100,
                       power_draw: float = 0,
                       vram_usage_percent: float = 0,
                       cpu_usage: float = 0,
                       is_throttling: bool = False,
                       is_boosting: bool = False,
                       game_name: str = "",
                       thermal_profile: str = "medium") -> PerformanceScore:
        """
        Calcule le score de performance global

        Args:
            temperature: Temperature GPU actuelle (C)
            gpu_usage: Utilisation GPU (%)
            fps_current: FPS actuel
            fps_avg: FPS moyen de la session
            fps_1_low: 1% low FPS
            frametime_ms: Frametime en ms
            clock_current: Clock GPU actuel (MHz)
            clock_max: Clock GPU max (MHz)
            power_draw: Puissance GPU (W)
            vram_usage_percent: Utilisation VRAM (%)
            cpu_usage: Utilisation CPU (%)
            is_throttling: Si le GPU est en throttle
            is_boosting: Si le mode boost est actif
            game_name: Nom du jeu
            thermal_profile: Profil thermique du jeu

        Returns:
            PerformanceScore avec le score global et les details
        """
        breakdown = ScoreBreakdown()

        # 1. THERMAL SCORE (0-100)
        breakdown.thermal_score, breakdown.thermal_details = self._calculate_thermal_score(
            temperature, self.config['target_temp'], self.config['critical_temp']
        )

        # 2. FPS SCORE (0-100)
        breakdown.fps_score, breakdown.fps_details = self._calculate_fps_score(
            fps_current, fps_avg, fps_1_low, frametime_ms,
            self.config['target_fps'], self.config['min_acceptable_fps']
        )

        # 3. EFFICIENCY SCORE (0-100)
        breakdown.efficiency_score, breakdown.efficiency_details = self._calculate_efficiency_score(
            gpu_usage, clock_current, clock_max, temperature,
            self.config['optimal_gpu_usage']
        )

        # 4. STABILITY SCORE (0-100)
        breakdown.stability_score, breakdown.stability_details = self._calculate_stability_score(
            fps_current, fps_avg, fps_1_low, frametime_ms, temperature
        )

        # 5. BONUS / MALUS

        # Bonus headroom thermique (si >10C sous la cible)
        thermal_headroom = self.config['target_temp'] - temperature
        if thermal_headroom > 10:
            breakdown.bonus_headroom = min(5.0, thermal_headroom - 10) * 0.5  # Max +2.5

        # Bonus mode boost actif
        if is_boosting and temperature < self.config['target_temp']:
            breakdown.bonus_boost_active = 3.0

        # Malus throttle actif
        if is_throttling:
            breakdown.malus_throttle = -10.0

        # Malus bottleneck (CPU > 85% et GPU < 60%)
        if cpu_usage > 85 and gpu_usage < 60:
            breakdown.malus_bottleneck = -5.0

        # 6. CALCUL SCORE GLOBAL
        weighted_score = (
            breakdown.thermal_score * self.WEIGHTS['thermal'] +
            breakdown.fps_score * self.WEIGHTS['fps'] +
            breakdown.efficiency_score * self.WEIGHTS['efficiency'] +
            breakdown.stability_score * self.WEIGHTS['stability']
        )

        # Appliquer bonus/malus
        total_bonus = (
            breakdown.bonus_headroom +
            breakdown.bonus_boost_active +
            breakdown.malus_throttle +
            breakdown.malus_bottleneck
        )

        overall_score = max(0, min(100, weighted_score + total_bonus))

        # 7. DETERMINER L'ETAT
        state = self._determine_state(overall_score)

        # 8. DETERMINER LA STRATEGIE RECOMMANDEE
        strategy = self._determine_strategy(
            overall_score, breakdown, temperature,
            is_throttling, is_boosting, thermal_headroom
        )

        # 9. CALCULER LA TENDANCE
        trend, score_delta = self._calculate_trend(overall_score)

        # 10. GENERER LES RECOMMANDATIONS
        recommendations = self._generate_recommendations(
            breakdown, state, temperature, fps_current, gpu_usage, cpu_usage
        )

        # Creer le resultat
        result = PerformanceScore(
            overall_score=round(overall_score, 1),
            state=state,
            recommended_strategy=strategy,
            breakdown=breakdown,
            game_name=game_name,
            thermal_profile=thermal_profile,
            trend=trend,
            score_delta=score_delta,
            recommendations=recommendations
        )

        # Sauvegarder dans l'historique
        self.score_history.append(result)
        if len(self.score_history) > self.max_history:
            self.score_history.pop(0)

        return result

    def _calculate_thermal_score(self, temp: float, target: float, critical: float) -> Tuple[float, str]:
        """Calcule le score thermique (0-100)"""
        # Ajouter a l'historique pour stabilite
        self.temp_samples.append(temp)
        if len(self.temp_samples) > self.max_samples:
            self.temp_samples.pop(0)

        if temp <= 0:
            return 50.0, "Pas de donnees temperature"

        # Score base sur la distance a la cible
        if temp <= target - 10:
            # Tres froid - score parfait
            score = 100.0
            details = f"Excellent ({temp:.0f}C << {target:.0f}C cible)"
        elif temp <= target:
            # Sous la cible - tres bien
            score = 85 + (target - temp) * 1.5
            details = f"Bon ({temp:.0f}C < {target:.0f}C cible)"
        elif temp <= target + 5:
            # Legerement au dessus - acceptable
            score = 70 - (temp - target) * 3
            details = f"Acceptable ({temp:.0f}C ~ {target:.0f}C cible)"
        elif temp <= critical:
            # Entre cible+5 et critique - attention
            range_size = critical - (target + 5)
            progress = (temp - (target + 5)) / range_size if range_size > 0 else 1
            score = 55 - progress * 35  # 55 -> 20
            details = f"Chaud ({temp:.0f}C > {target:.0f}C, attention!)"
        else:
            # Au dessus du critique - urgence
            overshoot = temp - critical
            score = max(0, 20 - overshoot * 2)
            details = f"CRITIQUE ({temp:.0f}C > {critical:.0f}C!)"

        return max(0, min(100, score)), details

    def _calculate_fps_score(self, fps_current: float, fps_avg: float,
                            fps_1_low: float, frametime_ms: float,
                            target_fps: float, min_fps: float) -> Tuple[float, str]:
        """Calcule le score FPS (0-100)"""
        # Ajouter a l'historique pour stabilite
        if fps_current > 0:
            self.fps_samples.append(fps_current)
            if len(self.fps_samples) > self.max_samples:
                self.fps_samples.pop(0)

        if fps_current <= 0 and fps_avg <= 0:
            return 50.0, "Pas de donnees FPS"

        # Utiliser la moyenne si FPS actuel non disponible
        fps = fps_avg if fps_current <= 0 else fps_current

        # Score base sur le FPS
        if fps >= target_fps:
            # Au dessus de la cible - parfait
            bonus = min(10, (fps - target_fps) / 10)  # Bonus si > cible
            score = 90 + bonus
            details = f"Excellent ({fps:.0f} >= {target_fps:.0f} cible)"
        elif fps >= target_fps * 0.8:
            # 80-100% de la cible - bien
            ratio = fps / target_fps
            score = 70 + (ratio - 0.8) * 100  # 70-90
            details = f"Bon ({fps:.0f} ~ {target_fps:.0f} cible)"
        elif fps >= min_fps:
            # Au dessus du minimum - acceptable
            range_size = target_fps * 0.8 - min_fps
            progress = (fps - min_fps) / range_size if range_size > 0 else 0
            score = 40 + progress * 30  # 40-70
            details = f"Acceptable ({fps:.0f} > {min_fps:.0f} min)"
        else:
            # Sous le minimum - probleme
            ratio = fps / min_fps if min_fps > 0 else 0
            score = max(0, ratio * 40)  # 0-40
            details = f"Faible ({fps:.0f} < {min_fps:.0f} min!)"

        # Malus frametime irregulier
        if frametime_ms > 0 and fps > 0:
            expected_frametime = 1000 / fps
            if frametime_ms > expected_frametime * 1.5:
                score -= 10
                details += " [Frametime irregulier]"

        # Malus si 1% low tres bas
        if fps_1_low > 0 and fps_1_low < fps * 0.5:
            score -= 5
            details += " [Stutters detectes]"

        return max(0, min(100, score)), details

    def _calculate_efficiency_score(self, gpu_usage: float, clock_current: int,
                                   clock_max: int, temperature: float,
                                   optimal_usage: float) -> Tuple[float, str]:
        """Calcule le score d'efficacite (0-100)"""
        if gpu_usage <= 0:
            return 50.0, "Pas de donnees GPU usage"

        # Calcul du ratio performance/chaleur
        clock_ratio = clock_current / clock_max if clock_max > 0 else 0

        # Score base sur l'utilisation GPU
        if gpu_usage >= optimal_usage - 10:
            # Usage optimal
            score = 85 + min(15, (gpu_usage - (optimal_usage - 10)) / 2)
            details = f"Optimal ({gpu_usage:.0f}% usage)"
        elif gpu_usage >= 60:
            # Usage correct
            score = 60 + (gpu_usage - 60) * (25 / (optimal_usage - 70))
            details = f"Bon ({gpu_usage:.0f}% usage)"
        elif gpu_usage >= 30:
            # Sous-utilise
            score = 30 + (gpu_usage - 30)
            details = f"Sous-utilise ({gpu_usage:.0f}% usage)"
        else:
            # Tres sous-utilise
            score = gpu_usage
            details = f"Tres sous-utilise ({gpu_usage:.0f}% usage)"

        # Bonus si clock eleve avec temperature basse
        if clock_ratio > 0.9 and temperature < 75:
            score += 5
            details += " [Efficace!]"

        return max(0, min(100, score)), details

    def _calculate_stability_score(self, fps_current: float, fps_avg: float,
                                  fps_1_low: float, frametime_ms: float,
                                  temperature: float) -> Tuple[float, str]:
        """Calcule le score de stabilite (0-100)"""
        score = 100.0
        issues = []

        # Stabilite FPS
        if len(self.fps_samples) >= 5:
            fps_variance = max(self.fps_samples) - min(self.fps_samples)
            fps_mean = sum(self.fps_samples) / len(self.fps_samples)

            if fps_mean > 0:
                variance_ratio = fps_variance / fps_mean
                if variance_ratio > 0.3:
                    score -= 20
                    issues.append("FPS instable")
                elif variance_ratio > 0.15:
                    score -= 10
                    issues.append("FPS variable")

        # 1% low vs moyenne
        if fps_1_low > 0 and fps_avg > 0:
            low_ratio = fps_1_low / fps_avg
            if low_ratio < 0.5:
                score -= 15
                issues.append("Gros drops FPS")
            elif low_ratio < 0.7:
                score -= 8
                issues.append("Drops FPS")

        # Stabilite temperature
        if len(self.temp_samples) >= 5:
            temp_variance = max(self.temp_samples) - min(self.temp_samples)
            if temp_variance > 10:
                score -= 10
                issues.append("Temp instable")
            elif temp_variance > 5:
                score -= 5
                issues.append("Temp variable")

        # Frametime consistency
        if frametime_ms > 0 and fps_current > 0:
            expected = 1000 / fps_current
            if frametime_ms > expected * 2:
                score -= 15
                issues.append("Frametime spike")

        if issues:
            details = f"Problemes: {', '.join(issues)}"
        else:
            details = "Stable"

        return max(0, min(100, score)), details

    def _determine_state(self, score: float) -> PerformanceState:
        """Determine l'etat de performance base sur le score"""
        if score < self.STATE_THRESHOLDS[PerformanceState.EMERGENCY]:
            return PerformanceState.EMERGENCY
        elif score < self.STATE_THRESHOLDS[PerformanceState.POOR]:
            return PerformanceState.POOR
        elif score < self.STATE_THRESHOLDS[PerformanceState.ACCEPTABLE]:
            return PerformanceState.ACCEPTABLE
        elif score < self.STATE_THRESHOLDS[PerformanceState.GOOD]:
            return PerformanceState.GOOD
        elif score < self.STATE_THRESHOLDS[PerformanceState.EXCELLENT]:
            return PerformanceState.EXCELLENT
        else:
            return PerformanceState.PEAK

    def _determine_strategy(self, score: float, breakdown: ScoreBreakdown,
                           temperature: float, is_throttling: bool,
                           is_boosting: bool, thermal_headroom: float) -> OptimizationStrategy:
        """Determine la strategie d'optimisation recommandee"""
        # Urgence si score tres bas ou temperature critique
        if score < 30 or temperature >= self.config['critical_temp']:
            return OptimizationStrategy.EMERGENCY_THROTTLE

        # Si le score thermique est le probleme principal
        if breakdown.thermal_score < 50 and breakdown.fps_score > 60:
            return OptimizationStrategy.THERMAL_FOCUS

        # Si on peut booster (score eleve + marge thermique)
        if score > 80 and thermal_headroom > 10 and not is_throttling:
            return OptimizationStrategy.BOOST

        # Si FPS OK mais pas optimal
        if score > 70 and breakdown.fps_score > 70:
            return OptimizationStrategy.PERFORMANCE

        # Par defaut - equilibre
        return OptimizationStrategy.BALANCED

    def _calculate_trend(self, current_score: float) -> Tuple[str, float]:
        """Calcule la tendance du score"""
        if len(self.score_history) < 5:
            return "stable", 0.0

        recent_scores = [s.overall_score for s in self.score_history[-5:]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        delta = current_score - avg_recent

        if delta > 3:
            return "rising", delta
        elif delta < -3:
            return "falling", delta
        else:
            return "stable", delta

    def _generate_recommendations(self, breakdown: ScoreBreakdown,
                                 state: PerformanceState,
                                 temperature: float, fps: float,
                                 gpu_usage: float, cpu_usage: float) -> List[str]:
        """Genere des recommandations basees sur l'analyse"""
        recommendations = []

        # Recommandations thermiques
        if breakdown.thermal_score < 50:
            recommendations.append("Reduire les clocks GPU pour baisser la temperature")
            if temperature > 85:
                recommendations.append("URGENT: Verifier le refroidissement du laptop")
        elif breakdown.thermal_score < 70:
            recommendations.append("Temperature elevee - surveiller l'evolution")

        # Recommandations FPS
        if breakdown.fps_score < 50:
            recommendations.append("FPS bas - baisser les parametres graphiques")
        elif breakdown.fps_score < 70:
            recommendations.append("FPS en dessous de la cible - ajuster les settings")

        # Recommandations efficacite
        if breakdown.efficiency_score < 50:
            if gpu_usage < 50:
                recommendations.append("GPU sous-utilise - augmenter les graphiques ou resoudre le bottleneck")
            if cpu_usage > 85 and gpu_usage < 60:
                recommendations.append("CPU bottleneck detecte - le CPU limite le GPU")

        # Recommandations stabilite
        if breakdown.stability_score < 70:
            if "FPS instable" in breakdown.stability_details:
                recommendations.append("FPS instable - verifier V-Sync ou limiter les FPS")
            if "Temp instable" in breakdown.stability_details:
                recommendations.append("Temperature instable - le GPU oscille entre throttle et normal")

        # Recommandation positive si tout va bien
        if state in [PerformanceState.EXCELLENT, PerformanceState.PEAK]:
            recommendations.append("Performance optimale ! Configuration ideale.")

        return recommendations

    def get_session_summary(self) -> Dict[str, Any]:
        """Retourne un resume de la session"""
        if not self.score_history:
            return {}

        scores = [s.overall_score for s in self.score_history]

        # Compter les etats
        state_counts = {}
        for s in self.score_history:
            state_name = s.state.value
            state_counts[state_name] = state_counts.get(state_name, 0) + 1

        return {
            'total_samples': len(scores),
            'avg_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'current_score': scores[-1],
            'state_distribution': state_counts,
            'time_in_optimal': state_counts.get('excellent', 0) + state_counts.get('peak', 0),
            'time_in_trouble': state_counts.get('emergency', 0) + state_counts.get('poor', 0)
        }

    def get_score_for_display(self) -> Dict[str, Any]:
        """Retourne le dernier score formate pour affichage"""
        if not self.score_history:
            return {
                'overall': 0,
                'state': 'unknown',
                'thermal': 0,
                'fps': 0,
                'efficiency': 0,
                'stability': 0,
                'trend': 'stable'
            }

        last = self.score_history[-1]
        return {
            'overall': last.overall_score,
            'state': last.state.value,
            'strategy': last.recommended_strategy.value,
            'thermal': last.breakdown.thermal_score,
            'fps': last.breakdown.fps_score,
            'efficiency': last.breakdown.efficiency_score,
            'stability': last.breakdown.stability_score,
            'trend': last.trend,
            'recommendations': last.recommendations
        }


# Instance globale
PERFORMANCE_SCORER = PerformanceScorer()


def test_performance_scorer():
    """Test du Performance Scorer"""
    print("=" * 60)
    print("PERFORMANCE SCORER - TEST")
    print("=" * 60)

    scorer = PerformanceScorer()

    # Test scenarios
    scenarios = [
        {
            'name': 'Performance Optimale',
            'temp': 68, 'gpu': 85, 'fps': 75, 'fps_avg': 72,
            'fps_1_low': 60, 'frametime': 13.3, 'clock': 1950, 'cpu': 60
        },
        {
            'name': 'Temperature Elevee',
            'temp': 86, 'gpu': 90, 'fps': 55, 'fps_avg': 52,
            'fps_1_low': 40, 'frametime': 18.2, 'clock': 1700, 'cpu': 70
        },
        {
            'name': 'CPU Bottleneck',
            'temp': 72, 'gpu': 45, 'fps': 45, 'fps_avg': 43,
            'fps_1_low': 35, 'frametime': 22.2, 'clock': 1600, 'cpu': 95
        },
        {
            'name': 'Mode Boost',
            'temp': 62, 'gpu': 75, 'fps': 90, 'fps_avg': 88,
            'fps_1_low': 75, 'frametime': 11.1, 'clock': 2100, 'cpu': 55,
            'boost': True
        },
        {
            'name': 'Urgence Thermique',
            'temp': 92, 'gpu': 70, 'fps': 35, 'fps_avg': 38,
            'fps_1_low': 20, 'frametime': 28.6, 'clock': 1200, 'cpu': 65,
            'throttle': True
        }
    ]

    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")

        result = scorer.calculate_score(
            temperature=scenario['temp'],
            gpu_usage=scenario['gpu'],
            fps_current=scenario['fps'],
            fps_avg=scenario['fps_avg'],
            fps_1_low=scenario['fps_1_low'],
            frametime_ms=scenario['frametime'],
            clock_current=scenario['clock'],
            cpu_usage=scenario['cpu'],
            is_throttling=scenario.get('throttle', False),
            is_boosting=scenario.get('boost', False)
        )

        print(f"Score Global: {result.overall_score}/100")
        print(f"Etat: {result.state.value}")
        print(f"Strategie: {result.recommended_strategy.value}")
        print(f"Scores: Thermal={result.breakdown.thermal_score:.0f}, "
              f"FPS={result.breakdown.fps_score:.0f}, "
              f"Efficiency={result.breakdown.efficiency_score:.0f}, "
              f"Stability={result.breakdown.stability_score:.0f}")

        if result.recommendations:
            print("Recommandations:")
            for rec in result.recommendations[:2]:
                print(f"  - {rec}")

    # Summary
    print("\n" + "=" * 60)
    print("RESUME SESSION")
    print("=" * 60)
    summary = scorer.get_session_summary()
    print(f"Echantillons: {summary['total_samples']}")
    print(f"Score moyen: {summary['avg_score']:.1f}")
    print(f"Score min/max: {summary['min_score']:.1f} / {summary['max_score']:.1f}")


if __name__ == "__main__":
    test_performance_scorer()
