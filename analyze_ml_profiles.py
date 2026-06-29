"""
📊 ANALYSE DES PROFILS ML - INSIGHTS INTELLIGENTS ! 🏛️
Objectif : Analyser les données ML collectées et afficher les patterns appris

FONCTIONNALITÉS :
🎯 Profils par Jeu : Analyse complète de chaque jeu
🎯 Comparaisons : Compare les performances entre jeux
🎯 Recommandations : Suggestions d'optimisation basées sur les données
🎯 Visualisation : Affichage clair des tendances

PLUS ULTRA ! DATTEBAYO ! 🚀⚡🥷🏛️
"""

from gpu_ml_logger import GPUMLLogger
from pathlib import Path
import json
from typing import Dict, List, Any
from datetime import datetime

class MLProfileAnalyzer:
    """Analyseur de profils ML - ANALYSE DIVINE ! 📊"""

    def __init__(self, log_directory: str = "gpu_ml_data"):
        """
        Initialisation de l'analyseur

        Args:
            log_directory: Dossier contenant les données ML
        """
        self.log_directory = Path(log_directory)
        self.logger = GPUMLLogger(log_directory)

    def list_all_games(self) -> List[str]:
        """Liste tous les jeux qui ont des données ML"""
        games = set()

        if not self.log_directory.exists():
            print(f"⚠️  Dossier {self.log_directory} n'existe pas encore")
            return []

        for file in self.log_directory.glob("*.jsonl"):
            # Format: GameName_TIMESTAMP.jsonl
            game_name = "_".join(file.stem.split("_")[:-2])  # Retire le timestamp
            game_name = game_name.replace("_", " ")
            games.add(game_name)

        return sorted(list(games))

    def analyze_game(self, game_name: str):
        """Analyse complète d'un jeu"""
        print("\n" + "="*80)
        print(f"📊 ANALYSE ML - {game_name.upper()}")
        print("="*80)

        profile = self.logger.analyze_game_profile(game_name)

        if not profile:
            print(f"⚠️  Aucune donnée trouvée pour {game_name}")
            return

        # Infos générales
        print(f"\n📈 STATISTIQUES GÉNÉRALES:")
        print(f"  Sessions jouées:  {profile['sessions_analyzed']}")
        print(f"  Temps total:      {profile['total_playtime_minutes']:.1f} minutes ({profile['total_playtime_minutes']/60:.1f}h)")

        # Profil thermique
        thermal = profile['thermal_profile']
        print(f"\n🌡️  PROFIL THERMIQUE:")
        print(f"  Température moyenne:  {thermal['avg_temp']:.1f}°C")
        print(f"  Température max:      {thermal['max_temp']:.1f}°C")
        print(f"  Température min:      {thermal['min_temp']:.1f}°C")
        print(f"  Plage typique:        {thermal['typical_range']}")

        # Classification thermique
        avg_temp = thermal['avg_temp']
        if avg_temp < 65:
            thermal_class = "❄️  FROID (Très bon pour le GPU)"
        elif avg_temp < 72:
            thermal_class = "🟢 MODÉRÉ (Bon)"
        elif avg_temp < 78:
            thermal_class = "🟡 CHAUD (Acceptable)"
        else:
            thermal_class = "🔥 TRÈS CHAUD (Attention!)"

        print(f"  Classification:       {thermal_class}")

        # Profil performance
        perf = profile['performance_profile']
        print(f"\n⚡ PROFIL PERFORMANCE:")
        print(f"  GPU Load moyen:  {perf['avg_gpu_load']:.1f}%")

        if perf['avg_fps'] > 0:
            print(f"  FPS moyen:       {perf['avg_fps']:.1f}")

        # Classification charge
        if perf['avg_gpu_load'] < 70:
            load_class = "🟢 LÉGER (GPU pas poussé)"
        elif perf['avg_gpu_load'] < 85:
            load_class = "🟡 MODÉRÉ (Bon usage)"
        elif perf['avg_gpu_load'] < 95:
            load_class = "🟠 INTENSE (GPU bien utilisé)"
        else:
            load_class = "🔴 SATURÉ (GPU à fond)"

        print(f"  Classification:  {load_class}")

        # Stabilité
        stability = profile['stability']
        print(f"\n🎯 STABILITÉ:")
        print(f"  Spikes GPU totaux:  {stability['total_spikes']}")
        print(f"  Spikes par heure:   {stability['spikes_per_hour']:.1f}")

        if stability['spikes_per_hour'] < 2:
            stability_class = "🟢 EXCELLENT (Très stable)"
        elif stability['spikes_per_hour'] < 5:
            stability_class = "🟡 BON (Quelques variations)"
        else:
            stability_class = "🔴 INSTABLE (Beaucoup de variations)"

        print(f"  Classification:     {stability_class}")

        # Recommandations
        self._generate_recommendations(profile)

        print("\n" + "="*80)

    def _generate_recommendations(self, profile: Dict[str, Any]):
        """Génère des recommandations basées sur le profil"""
        print(f"\n💡 RECOMMANDATIONS INTELLIGENTES:")

        recommendations = []

        thermal = profile['thermal_profile']
        perf = profile['performance_profile']
        stability = profile['stability']

        # Recommandations thermiques
        if thermal['avg_temp'] > 75:
            recommendations.append("🌡️  Température élevée : Augmenter ventilation ou undervolt")
        elif thermal['avg_temp'] < 60:
            recommendations.append("❄️  Température basse : Peut réduire ventilateur (moins de bruit)")

        # Recommandations charge GPU
        if perf['avg_gpu_load'] > 95:
            recommendations.append("⚡ GPU saturé : Réduire qualité graphique ou activer DLSS")
        elif perf['avg_gpu_load'] < 60:
            recommendations.append("🎮 GPU peu utilisé : Peut augmenter qualité graphique")

        # Recommandations stabilité
        if stability['spikes_per_hour'] > 5:
            recommendations.append("📊 Beaucoup de spikes : Scènes/zones spécifiques exigeantes détectées")

        # Recommandations FPS
        if perf['avg_fps'] > 0 and perf['avg_fps'] < 45:
            recommendations.append("🎯 FPS bas : Activer DLSS ou réduire Ray Tracing")

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  ✅ Configuration optimale ! Aucune amélioration suggérée")

    def compare_games(self):
        """Compare tous les jeux analysés"""
        games = self.list_all_games()

        if len(games) < 2:
            print("⚠️  Pas assez de jeux pour comparaison (minimum 2)")
            return

        print("\n" + "="*80)
        print("📊 COMPARAISON DES JEUX")
        print("="*80)

        profiles = {}
        for game in games:
            profile = self.logger.analyze_game_profile(game)
            if profile:
                profiles[game] = profile

        if not profiles:
            print("⚠️  Aucune donnée à comparer")
            return

        # Tableau comparatif
        print(f"\n{'Jeu':<30} {'Temp Moy':<12} {'GPU Load':<12} {'FPS':<10} {'Spikes/h':<10}")
        print("-" * 80)

        for game, profile in profiles.items():
            temp_avg = profile['thermal_profile']['avg_temp']
            gpu_load = profile['performance_profile']['avg_gpu_load']
            fps = profile['performance_profile']['avg_fps']
            spikes_h = profile['stability']['spikes_per_hour']

            print(f"{game:<30} {temp_avg:>7.1f}°C     {gpu_load:>7.1f}%     {fps:>6.1f}     {spikes_h:>6.1f}")

        # Identifie les extrêmes
        print(f"\n🏆 CLASSEMENTS:")

        # Jeu le plus chaud
        hottest = max(profiles.items(), key=lambda x: x[1]['thermal_profile']['avg_temp'])
        print(f"  🔥 Plus chaud:     {hottest[0]} ({hottest[1]['thermal_profile']['avg_temp']:.1f}°C)")

        # Jeu le plus froid
        coolest = min(profiles.items(), key=lambda x: x[1]['thermal_profile']['avg_temp'])
        print(f"  ❄️  Plus frais:     {coolest[0]} ({coolest[1]['thermal_profile']['avg_temp']:.1f}°C)")

        # Jeu le plus gourmand GPU
        most_intensive = max(profiles.items(), key=lambda x: x[1]['performance_profile']['avg_gpu_load'])
        print(f"  ⚡ Plus intensif:  {most_intensive[0]} ({most_intensive[1]['performance_profile']['avg_gpu_load']:.1f}% GPU)")

        # Jeu le plus stable
        most_stable = min(profiles.items(), key=lambda x: x[1]['stability']['spikes_per_hour'])
        print(f"  🎯 Plus stable:    {most_stable[0]} ({most_stable[1]['stability']['spikes_per_hour']:.1f} spikes/h)")

        print("="*80)

    def show_summary(self):
        """Affiche un résumé de toutes les données ML"""
        games = self.list_all_games()

        print("\n" + "="*80)
        print("📊 RÉSUMÉ ML - TOUS LES JEUX")
        print("="*80)

        if not games:
            print("\n⚠️  Aucune donnée ML disponible")
            print("💡 Jouez quelques sessions avec le monitoring pour commencer l'apprentissage!")
            return

        print(f"\n🎮 {len(games)} jeu(x) avec données ML:")
        for i, game in enumerate(games, 1):
            print(f"  {i}. {game}")

        print(f"\n📂 Dossier données: {self.log_directory.absolute()}")

        # Compte total de fichiers
        total_files = len(list(self.log_directory.glob("*.jsonl")))
        print(f"📝 Sessions totales: {total_files}")


def main():
    """Point d'entrée principal"""
    print("="*80)
    print("📊 GPU ML PROFILE ANALYZER - ANALYSE INTELLIGENTE")
    print("="*80)

    analyzer = MLProfileAnalyzer()

    # Résumé
    analyzer.show_summary()

    games = analyzer.list_all_games()

    if not games:
        print("\n💡 Lancez le monitoring GPU et jouez pour générer des données!")
        return

    # Menu interactif
    while True:
        print("\n" + "="*80)
        print("MENU:")
        print("  1. Analyser un jeu spécifique")
        print("  2. Comparer tous les jeux")
        print("  3. Afficher résumé")
        print("  0. Quitter")
        print("="*80)

        choice = input("\nChoix: ").strip()

        if choice == "0":
            print("\n✅ Au revoir!")
            break

        elif choice == "1":
            print(f"\nJeux disponibles:")
            for i, game in enumerate(games, 1):
                print(f"  {i}. {game}")

            try:
                game_idx = int(input("\nNuméro du jeu: ").strip()) - 1
                if 0 <= game_idx < len(games):
                    analyzer.analyze_game(games[game_idx])
                else:
                    print("⚠️  Numéro invalide")
            except ValueError:
                print("⚠️  Entrée invalide")

        elif choice == "2":
            analyzer.compare_games()

        elif choice == "3":
            analyzer.show_summary()

        else:
            print("⚠️  Choix invalide")


if __name__ == "__main__":
    main()
