"""
🧠 THERMAL ML PREDICTOR - PRÉDICTION THERMIQUE PAR MACHINE LEARNING ! 🔥
Objectif : Apprendre les patterns thermiques par jeu et prédire les pics

FONCTIONNALITÉS :
1. Collecte de données thermiques par jeu
2. Apprentissage des patterns (montée en temp, stabilisation, pics)
3. Prédiction des pics thermiques AVANT qu'ils arrivent
4. Ajustement préventif des clocks

ALGORITHMES :
- Moving Average pour tendance
- Linear Regression pour prédiction court terme
- Pattern Matching pour scénarios connus

PLUS ULTRA ! DATTEBAYO ! 🚀⚡
"""

import os
import json
import time
import logging
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import deque
import threading

logging.basicConfig(level=logging.INFO, format='🧠 %(asctime)s - %(levelname)s - %(message)s')


@dataclass
class ThermalDataPoint:
    """Point de données thermique"""
    timestamp: float
    temperature: float
    gpu_usage: float
    clock_speed: int
    power_draw: float
    fps: float = 0.0
    game_scene: str = "unknown"  # menu, gameplay, cutscene, loading


@dataclass
class ThermalPattern:
    """Pattern thermique appris pour un jeu"""
    game_name: str
    avg_temp: float = 0.0
    max_temp: float = 0.0
    min_temp: float = 0.0
    temp_rise_rate: float = 0.0  # °C par seconde en montée
    temp_drop_rate: float = 0.0  # °C par seconde en descente
    stabilization_temp: float = 0.0  # Température de stabilisation
    typical_spikes: List[float] = field(default_factory=list)  # Pics typiques
    usage_temp_correlation: float = 0.0  # Corrélation usage GPU / temp
    samples_count: int = 0
    last_updated: str = ""


@dataclass
class ThermalPrediction:
    """Prédiction thermique"""
    current_temp: float
    predicted_temp_5s: float  # Prédiction dans 5 secondes
    predicted_temp_10s: float  # Prédiction dans 10 secondes
    predicted_temp_30s: float  # Prédiction dans 30 secondes
    trend: str  # 'rising', 'stable', 'falling'
    spike_probability: float  # Probabilité de pic (0-1)
    recommended_action: str  # 'none', 'prepare_throttle', 'throttle_now'
    confidence: float  # Confiance de la prédiction (0-1)


class ThermalMLPredictor:
    """
    Prédicteur thermique ML - INTELLIGENCE DIVINE ! 🧠
    Apprend les patterns et prédit les pics thermiques
    """

    def __init__(self, data_path: str = "thermal_ml_data.json"):
        self.data_path = data_path

        # Données en mémoire
        self.current_buffer = deque(maxlen=300)  # 5 minutes à 1Hz
        self.game_patterns: Dict[str, ThermalPattern] = {}

        # État actuel
        self.current_game: Optional[str] = None
        self.is_learning = True

        # Paramètres ML
        self.prediction_window = 30  # Secondes de données pour prédire
        self.spike_threshold = 5.0  # °C de montée = spike
        self.trend_samples = 10  # Échantillons pour calculer la tendance

        # Charger les données existantes
        self._load_data()

        logging.info("🧠 Thermal ML Predictor initialisé")
        logging.info(f"   Jeux appris: {len(self.game_patterns)}")

    def _load_data(self):
        """Charge les données d'apprentissage"""
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for game_name, pattern_data in data.get('patterns', {}).items():
                    self.game_patterns[game_name] = ThermalPattern(
                        game_name=game_name,
                        avg_temp=pattern_data.get('avg_temp', 0),
                        max_temp=pattern_data.get('max_temp', 0),
                        min_temp=pattern_data.get('min_temp', 100),
                        temp_rise_rate=pattern_data.get('temp_rise_rate', 0),
                        temp_drop_rate=pattern_data.get('temp_drop_rate', 0),
                        stabilization_temp=pattern_data.get('stabilization_temp', 0),
                        typical_spikes=pattern_data.get('typical_spikes', []),
                        usage_temp_correlation=pattern_data.get('usage_temp_correlation', 0),
                        samples_count=pattern_data.get('samples_count', 0),
                        last_updated=pattern_data.get('last_updated', '')
                    )

                logging.info(f"✅ Données ML chargées: {len(self.game_patterns)} jeux")
        except Exception as e:
            logging.warning(f"⚠️ Erreur chargement données ML: {e}")

    def _save_data(self):
        """Sauvegarde les données d'apprentissage"""
        try:
            data = {
                'patterns': {},
                'version': '1.0',
                'last_save': datetime.now().isoformat()
            }

            for game_name, pattern in self.game_patterns.items():
                data['patterns'][game_name] = {
                    'avg_temp': pattern.avg_temp,
                    'max_temp': pattern.max_temp,
                    'min_temp': pattern.min_temp,
                    'temp_rise_rate': pattern.temp_rise_rate,
                    'temp_drop_rate': pattern.temp_drop_rate,
                    'stabilization_temp': pattern.stabilization_temp,
                    'typical_spikes': pattern.typical_spikes[-10:],  # Garder les 10 derniers
                    'usage_temp_correlation': pattern.usage_temp_correlation,
                    'samples_count': pattern.samples_count,
                    'last_updated': pattern.last_updated
                }

            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logging.info(f"💾 Données ML sauvegardées: {len(self.game_patterns)} jeux")
        except Exception as e:
            logging.error(f"❌ Erreur sauvegarde données ML: {e}")

    def set_current_game(self, game_name: Optional[str]):
        """Définit le jeu actuel pour l'apprentissage"""
        if game_name != self.current_game:
            # Sauvegarder les données du jeu précédent
            if self.current_game and len(self.current_buffer) > 30:
                self._update_pattern(self.current_game)
                self._save_data()

            self.current_game = game_name
            self.current_buffer.clear()

            if game_name:
                logging.info(f"🎮 ML: Apprentissage actif pour {game_name}")

                # Créer le pattern si nouveau jeu
                if game_name not in self.game_patterns:
                    self.game_patterns[game_name] = ThermalPattern(game_name=game_name)

    def add_data_point(self, temp: float, gpu_usage: float, clock_speed: int,
                       power_draw: float, fps: float = 0.0):
        """Ajoute un point de données pour l'apprentissage"""
        point = ThermalDataPoint(
            timestamp=time.time(),
            temperature=temp,
            gpu_usage=gpu_usage,
            clock_speed=clock_speed,
            power_draw=power_draw,
            fps=fps
        )

        self.current_buffer.append(point)

        # Mettre à jour le pattern toutes les 60 secondes
        if len(self.current_buffer) % 60 == 0 and self.current_game:
            self._update_pattern(self.current_game)

    def _update_pattern(self, game_name: str):
        """Met à jour le pattern d'un jeu avec les nouvelles données"""
        if game_name not in self.game_patterns:
            return

        pattern = self.game_patterns[game_name]
        temps = [p.temperature for p in self.current_buffer]
        usages = [p.gpu_usage for p in self.current_buffer]

        if not temps:
            return

        # Statistiques de base
        pattern.avg_temp = np.mean(temps)
        pattern.max_temp = max(pattern.max_temp, max(temps))
        pattern.min_temp = min(pattern.min_temp, min(temps))

        # Calcul du taux de montée/descente
        if len(temps) > 10:
            diffs = np.diff(temps)
            rises = diffs[diffs > 0]
            drops = diffs[diffs < 0]

            if len(rises) > 0:
                pattern.temp_rise_rate = np.mean(rises)
            if len(drops) > 0:
                pattern.temp_drop_rate = abs(np.mean(drops))

        # Température de stabilisation (mode)
        temp_rounded = [round(t) for t in temps]
        if temp_rounded:
            pattern.stabilization_temp = max(set(temp_rounded), key=temp_rounded.count)

        # Détection des spikes (augmentation > 5°C en 10 secondes)
        for i in range(10, len(temps)):
            delta = temps[i] - temps[i-10]
            if delta >= self.spike_threshold:
                pattern.typical_spikes.append(temps[i])

        # Corrélation usage/température
        if len(temps) == len(usages) and len(temps) > 10:
            try:
                correlation = np.corrcoef(temps, usages)[0, 1]
                pattern.usage_temp_correlation = correlation if not np.isnan(correlation) else 0
            except:
                pass

        pattern.samples_count += len(temps)
        pattern.last_updated = datetime.now().isoformat()

        logging.info(f"🧠 Pattern mis à jour pour {game_name}: avg={pattern.avg_temp:.1f}°C, max={pattern.max_temp:.1f}°C")

    def predict(self) -> ThermalPrediction:
        """Prédit la température future basée sur les données actuelles"""
        if len(self.current_buffer) < 10:
            # Pas assez de données
            return ThermalPrediction(
                current_temp=self.current_buffer[-1].temperature if self.current_buffer else 0,
                predicted_temp_5s=0,
                predicted_temp_10s=0,
                predicted_temp_30s=0,
                trend='unknown',
                spike_probability=0,
                recommended_action='none',
                confidence=0
            )

        temps = [p.temperature for p in self.current_buffer]
        current_temp = temps[-1]

        # Calculer la tendance (régression linéaire simple sur les derniers points)
        recent_temps = temps[-self.trend_samples:]
        x = np.arange(len(recent_temps))

        # Régression linéaire: y = mx + b
        n = len(recent_temps)
        sum_x = np.sum(x)
        sum_y = np.sum(recent_temps)
        sum_xy = np.sum(x * recent_temps)
        sum_xx = np.sum(x * x)

        # Pente (m) = taux de changement par seconde (si sampling 1Hz)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x) if (n * sum_xx - sum_x * sum_x) != 0 else 0
        intercept = (sum_y - slope * sum_x) / n

        # Prédictions
        current_x = len(recent_temps) - 1
        pred_5s = current_temp + slope * 5
        pred_10s = current_temp + slope * 10
        pred_30s = current_temp + slope * 30

        # Tendance
        if slope > 0.1:
            trend = 'rising'
        elif slope < -0.1:
            trend = 'falling'
        else:
            trend = 'stable'

        # Probabilité de spike
        spike_prob = 0.0
        if self.current_game and self.current_game in self.game_patterns:
            pattern = self.game_patterns[self.current_game]

            # Basé sur la proximité du max connu
            if pattern.max_temp > 0:
                proximity = current_temp / pattern.max_temp
                spike_prob = min(1.0, proximity * slope * 10) if slope > 0 else 0

            # Ajuster avec l'historique des spikes
            if pattern.typical_spikes:
                avg_spike_temp = np.mean(pattern.typical_spikes)
                if current_temp > avg_spike_temp - 5:
                    spike_prob = min(1.0, spike_prob + 0.3)

        # Si montée rapide, augmenter la probabilité
        if slope > 0.5:  # Plus de 0.5°C par seconde
            spike_prob = min(1.0, spike_prob + 0.4)

        # Action recommandée
        if spike_prob > 0.7 or pred_10s > 88:
            action = 'throttle_now'
        elif spike_prob > 0.4 or pred_10s > 83:
            action = 'prepare_throttle'
        else:
            action = 'none'

        # Confiance basée sur la quantité de données
        confidence = min(1.0, len(self.current_buffer) / 100)
        if self.current_game and self.current_game in self.game_patterns:
            pattern = self.game_patterns[self.current_game]
            if pattern.samples_count > 1000:
                confidence = min(1.0, confidence + 0.3)

        return ThermalPrediction(
            current_temp=current_temp,
            predicted_temp_5s=pred_5s,
            predicted_temp_10s=pred_10s,
            predicted_temp_30s=pred_30s,
            trend=trend,
            spike_probability=spike_prob,
            recommended_action=action,
            confidence=confidence
        )

    def get_pattern_summary(self, game_name: str = None) -> Dict[str, Any]:
        """Retourne le résumé du pattern d'un jeu"""
        if game_name is None:
            game_name = self.current_game

        if not game_name or game_name not in self.game_patterns:
            return {}

        pattern = self.game_patterns[game_name]

        return {
            'game': game_name,
            'avg_temp': round(pattern.avg_temp, 1),
            'max_temp': round(pattern.max_temp, 1),
            'min_temp': round(pattern.min_temp, 1),
            'temp_rise_rate': round(pattern.temp_rise_rate, 2),
            'temp_drop_rate': round(pattern.temp_drop_rate, 2),
            'stabilization_temp': round(pattern.stabilization_temp, 1),
            'usage_correlation': round(pattern.usage_temp_correlation, 2),
            'samples': pattern.samples_count,
            'spike_temps': pattern.typical_spikes[-5:] if pattern.typical_spikes else [],
            'last_updated': pattern.last_updated
        }

    def get_all_games_summary(self) -> List[Dict[str, Any]]:
        """Retourne le résumé de tous les jeux appris"""
        summaries = []
        for game_name in self.game_patterns:
            summaries.append(self.get_pattern_summary(game_name))
        return summaries

    def should_preemptive_throttle(self, current_temp: float, target_temp: float) -> Tuple[bool, str]:
        """
        Détermine si on devrait throttle de manière préventive
        basé sur la prédiction ML
        """
        prediction = self.predict()

        # Si on prédit qu'on va dépasser la cible dans 10 secondes
        if prediction.predicted_temp_10s > target_temp:
            return True, f"Prédiction: {prediction.predicted_temp_10s:.1f}°C dans 10s (cible: {target_temp}°C)"

        # Si spike probable
        if prediction.spike_probability > 0.6:
            return True, f"Spike probable ({prediction.spike_probability*100:.0f}%) - Action préventive"

        # Si montée rapide
        if prediction.trend == 'rising' and current_temp > target_temp - 5:
            return True, f"Montée rapide détectée, proche de la cible"

        return False, ""


# Instance globale
THERMAL_PREDICTOR = ThermalMLPredictor()


def test_ml_predictor():
    """Test du prédicteur ML"""
    print("=" * 60)
    print("🧠 TEST THERMAL ML PREDICTOR - TEMPLE IAM")
    print("=" * 60)

    predictor = ThermalMLPredictor()

    # Simuler un jeu
    predictor.set_current_game("Test Game")

    print("\n📊 Simulation de données thermiques...")

    # Simuler une montée de température
    base_temp = 60
    for i in range(60):
        # Simulation: température qui monte puis se stabilise
        if i < 30:
            temp = base_temp + i * 0.5  # Montée
        else:
            temp = base_temp + 15 + np.random.normal(0, 1)  # Stabilisation avec bruit

        gpu_usage = 70 + np.random.normal(0, 10)
        clock = 1800
        power = 100 + np.random.normal(0, 10)

        predictor.add_data_point(temp, gpu_usage, clock, power)

        if i % 10 == 0:
            prediction = predictor.predict()
            print(f"   [{i}s] Temp: {temp:.1f}°C | Prédit 10s: {prediction.predicted_temp_10s:.1f}°C | "
                  f"Trend: {prediction.trend} | Spike prob: {prediction.spike_probability*100:.0f}%")

    # Résumé du pattern
    print(f"\n📈 Pattern appris:")
    summary = predictor.get_pattern_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")

    # Test prédiction
    print(f"\n🔮 Prédiction finale:")
    pred = predictor.predict()
    print(f"   Temp actuelle: {pred.current_temp:.1f}°C")
    print(f"   Prédit 5s: {pred.predicted_temp_5s:.1f}°C")
    print(f"   Prédit 10s: {pred.predicted_temp_10s:.1f}°C")
    print(f"   Prédit 30s: {pred.predicted_temp_30s:.1f}°C")
    print(f"   Tendance: {pred.trend}")
    print(f"   Action recommandée: {pred.recommended_action}")
    print(f"   Confiance: {pred.confidence*100:.0f}%")

    print("\n" + "=" * 60)
    print("✅ TEST ML TERMINÉ")
    print("=" * 60)


if __name__ == "__main__":
    test_ml_predictor()
