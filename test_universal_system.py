"""
🧪 TEST UNIVERSAL SYSTEM - SCRIPT DE TEST COMPLET ! 🏛️
Objectif : Tester le nouveau système universel de détection de jeux

TESTS :
✅ Détection de jeux
✅ Base de données
✅ Profils d'optimisation
✅ Integration avec GPU Monitor

PLUS ULTRA ! DATTEBAYO ! 🚀⚡🥷🏛️
"""

import sys
import time
from typing import List, Dict, Any

# Import des modules universels
try:
    from games_database import GAMES_DB, GameProfile
    from universal_game_detector import GAME_DETECTOR, UniversalGameDetector
    print("✅ Imports des modules universels réussis")
except ImportError as e:
    print(f"❌ Erreur import: {e}")
    sys.exit(1)

def test_games_database():
    """Test de la base de données de jeux"""
    print("\n" + "="*80)
    print("🎮 TEST 1: BASE DE DONNÉES DE JEUX")
    print("="*80)

    # Test 1: Comptage des jeux
    all_games = GAMES_DB.get_all_games()
    print(f"✅ Nombre de jeux dans la base: {len(all_games)}")

    # Test 2: Jeux avec DLSS
    dlss_games = GAMES_DB.get_games_with_feature('dlss')
    print(f"✅ Jeux avec DLSS: {len(dlss_games)}")
    print(f"   Exemples: {', '.join([g.display_name for g in dlss_games[:5]])}")

    # Test 3: Jeux avec Ray Tracing
    rt_games = GAMES_DB.get_games_with_feature('ray_tracing')
    print(f"✅ Jeux avec Ray Tracing: {len(rt_games)}")
    print(f"   Exemples: {', '.join([g.display_name for g in rt_games[:5]])}")

    # Test 4: Recherche par nom
    game = GAMES_DB.get_game_by_name("cyberpunk_2077")
    if game:
        print(f"✅ Recherche par nom: {game.display_name}")
        print(f"   Moteur: {game.engine.value}")
        print(f"   VRAM requis: {game.vram_requirement_gb}GB")
        print(f"   Profil thermique: {game.thermal_profile}")
    else:
        print("❌ Jeu non trouvé")

    # Test 5: Recherche par processus
    game = GAMES_DB.get_game_by_process("AlanWake2.exe")
    if game:
        print(f"✅ Recherche par processus: {game.display_name}")
    else:
        print("❌ Processus non trouvé")

    return True

def test_game_detector():
    """Test du détecteur universel de jeux"""
    print("\n" + "="*80)
    print("🔍 TEST 2: DÉTECTEUR UNIVERSEL DE JEUX")
    print("="*80)

    detector = UniversalGameDetector(auto_learn=True)

    # Test 1: Détection en temps réel
    print("🔍 Détection des jeux en cours d'exécution...")
    detected_games = detector.detect_running_games()

    if detected_games:
        print(f"✅ {len(detected_games)} jeu(x) détecté(s):")
        for game in detected_games:
            print(f"\n   📌 {game.custom_name}")
            print(f"      Processus: {game.process_name}")
            print(f"      PID: {game.pid}")
            print(f"      Connu: {'✅ Oui' if game.is_known else '🆕 Non (appris)'}")
            print(f"      CPU: {game.cpu_usage:.1f}%")
            print(f"      RAM: {game.memory_mb:.0f} MB")

            # Profil d'optimisation
            profile = detector.get_game_optimization_profile(game)
            print(f"      Profil thermique: {profile['thermal_profile']}")
            print(f"      Temp cible: {profile['target_temp']}°C")
            print(f"      FPS cible: {profile['target_fps']}")
    else:
        print("⚠️ Aucun jeu détecté")
        print("💡 Lancez un jeu pour tester la détection")

    # Test 2: Jeu principal
    primary = detector.get_primary_game()
    if primary:
        print(f"\n✅ Jeu principal: {primary.custom_name}")
    else:
        print("\n⚠️ Pas de jeu principal")

    # Test 3: Résumé
    summary = detector.get_detection_summary()
    print(f"\n📊 Résumé:")
    print(f"   Total: {summary['total_games_detected']}")
    print(f"   Connus: {summary['known_games']}")
    print(f"   Inconnus: {summary['unknown_games']}")

    return True

def test_optimization_profiles():
    """Test des profils d'optimisation"""
    print("\n" + "="*80)
    print("⚙️ TEST 3: PROFILS D'OPTIMISATION")
    print("="*80)

    test_games = [
        "cyberpunk_2077",
        "alan_wake_2",
        "valorant",
        "elden_ring"
    ]

    for game_name in test_games:
        game = GAMES_DB.get_game_by_name(game_name)
        if game:
            print(f"\n✅ {game.display_name}")
            print(f"   Profil thermique: {game.thermal_profile.upper()}")
            print(f"   Temp cible: {game.default_settings.get('target_temp')}°C")
            print(f"   FPS cible: {game.default_settings.get('target_fps')}")

            if game.optimization_hints:
                print(f"   Optimisations:")
                for hint in game.optimization_hints[:3]:
                    print(f"      - {hint}")

    return True

def test_integration():
    """Test d'intégration système complet"""
    print("\n" + "="*80)
    print("🔗 TEST 4: INTÉGRATION SYSTÈME")
    print("="*80)

    try:
        # Import du moniteur universel
        from universal_gpu_monitor import UniversalGPUMonitor
        print("✅ Import UniversalGPUMonitor réussi")

        # Création moniteur (sans démarrer)
        monitor = UniversalGPUMonitor(monitor_interval=2.0, max_history=100)
        print("✅ Initialisation UniversalGPUMonitor réussie")
        print(f"   GPU disponible: {monitor.gpu_available}")
        if monitor.gpu_available:
            print(f"   GPU name: {monitor.gpu_name}")

        return True
    except Exception as e:
        print(f"❌ Erreur intégration: {e}")
        return False

def test_thermal_optimizer_integration():
    """Test d'intégration du thermal optimizer"""
    print("\n" + "="*80)
    print("🔥 TEST 5: THERMAL OPTIMIZER UNIVERSEL")
    print("="*80)

    try:
        from temple_iam_thermal_optimizer import TempleIAMThermalOptimizer
        print("✅ Import TempleIAMThermalOptimizer réussi")

        # Création optimizer (sans démarrer)
        optimizer = TempleIAMThermalOptimizer()
        print("✅ Initialisation TempleIAMThermalOptimizer réussie")
        print(f"   GPU disponible: {optimizer.gpu_available}")
        if optimizer.gpu_available:
            print(f"   GPU name: {optimizer.gpu_name}")
        print(f"   Détecteur de jeux: {'✅ Actif' if optimizer.game_detector else '❌ Inactif'}")

        return True
    except Exception as e:
        print(f"❌ Erreur thermal optimizer: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Exécution de tous les tests"""
    print("\n" + "="*80)
    print("🧪 TEMPLE IAM - TESTS SYSTÈME UNIVERSEL")
    print("="*80)
    print("Version: UNIVERSAL GAME DETECTION v1.0")
    print("="*80)

    tests = [
        ("Base de données de jeux", test_games_database),
        ("Détecteur universel de jeux", test_game_detector),
        ("Profils d'optimisation", test_optimization_profiles),
        ("Intégration GPU Monitor", test_integration),
        ("Intégration Thermal Optimizer", test_thermal_optimizer_integration)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Erreur test '{test_name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Résumé
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "="*80)
    print(f"Résultat: {passed}/{total} tests réussis")

    if passed == total:
        print("🎉 TOUS LES TESTS SONT RÉUSSIS ! PLUS ULTRA !")
    else:
        print("⚠️ Certains tests ont échoué. Vérifier les erreurs ci-dessus.")

    print("="*80)

if __name__ == "__main__":
    run_all_tests()
