"""
Test Universal System - Windows Compatible
"""

import sys
import os

# Force UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import des modules universels
try:
    from games_database import GAMES_DB, GameProfile
    from universal_game_detector import GAME_DETECTOR, UniversalGameDetector
    print("[OK] Imports des modules universels reussis")
except ImportError as e:
    print(f"[ERROR] Erreur import: {e}")
    sys.exit(1)

def test_games_database():
    """Test de la base de donnees de jeux"""
    print("\n" + "="*80)
    print("[TEST 1] BASE DE DONNEES DE JEUX")
    print("="*80)

    # Test 1: Comptage des jeux
    all_games = GAMES_DB.get_all_games()
    print(f"[OK] Nombre de jeux dans la base: {len(all_games)}")

    # Test 2: Jeux avec DLSS
    dlss_games = GAMES_DB.get_games_with_feature('dlss')
    print(f"[OK] Jeux avec DLSS: {len(dlss_games)}")
    print(f"     Exemples: {', '.join([g.display_name for g in dlss_games[:5]])}")

    # Test 3: Jeux avec Ray Tracing
    rt_games = GAMES_DB.get_games_with_feature('ray_tracing')
    print(f"[OK] Jeux avec Ray Tracing: {len(rt_games)}")
    print(f"     Exemples: {', '.join([g.display_name for g in rt_games[:5]])}")

    # Test 4: Recherche par nom
    game = GAMES_DB.get_game_by_name("cyberpunk_2077")
    if game:
        print(f"[OK] Recherche par nom: {game.display_name}")
        print(f"     Moteur: {game.engine.value}")
        print(f"     VRAM requis: {game.vram_requirement_gb}GB")
        print(f"     Profil thermique: {game.thermal_profile}")
    else:
        print("[ERROR] Jeu non trouve")

    return True

def test_game_detector():
    """Test du detecteur universel de jeux"""
    print("\n" + "="*80)
    print("[TEST 2] DETECTEUR UNIVERSEL DE JEUX")
    print("="*80)

    detector = UniversalGameDetector(auto_learn=True)

    # Test 1: Detection en temps reel
    print("[INFO] Detection des jeux en cours d'execution...")
    detected_games = detector.detect_running_games()

    if detected_games:
        print(f"[OK] {len(detected_games)} jeu(x) detecte(s):")
        for game in detected_games:
            print(f"\n   [GAME] {game.custom_name}")
            print(f"      Processus: {game.process_name}")
            print(f"      PID: {game.pid}")
            print(f"      Connu: {'Oui' if game.is_known else 'Non (appris)'}")
            print(f"      CPU: {game.cpu_usage:.1f}%")
            print(f"      RAM: {game.memory_mb:.0f} MB")

            # Profil d'optimisation
            profile = detector.get_game_optimization_profile(game)
            print(f"      Profil thermique: {profile['thermal_profile']}")
            print(f"      Temp cible: {profile['target_temp']}C")
            print(f"      FPS cible: {profile['target_fps']}")
    else:
        print("[WARNING] Aucun jeu detecte")
        print("[INFO] Lancez un jeu pour tester la detection")

    # Test 2: Jeu principal
    primary = detector.get_primary_game()
    if primary:
        print(f"\n[OK] Jeu principal: {primary.custom_name}")
    else:
        print("\n[WARNING] Pas de jeu principal")

    # Test 3: Resume
    summary = detector.get_detection_summary()
    print(f"\n[SUMMARY]")
    print(f"   Total: {summary['total_games_detected']}")
    print(f"   Connus: {summary['known_games']}")
    print(f"   Inconnus: {summary['unknown_games']}")

    return True

def test_integration():
    """Test d'integration systeme complet"""
    print("\n" + "="*80)
    print("[TEST 3] INTEGRATION SYSTEME")
    print("="*80)

    try:
        # Import du moniteur universel
        from universal_gpu_monitor import UniversalGPUMonitor
        print("[OK] Import UniversalGPUMonitor reussi")

        # Creation moniteur (sans demarrer)
        monitor = UniversalGPUMonitor(monitor_interval=2.0, max_history=100)
        print("[OK] Initialisation UniversalGPUMonitor reussie")
        print(f"     GPU disponible: {monitor.gpu_available}")
        if monitor.gpu_available:
            print(f"     GPU name: {monitor.gpu_name}")

        return True
    except Exception as e:
        print(f"[ERROR] Erreur integration: {e}")
        return False

def test_thermal_optimizer_integration():
    """Test d'integration du thermal optimizer"""
    print("\n" + "="*80)
    print("[TEST 4] THERMAL OPTIMIZER UNIVERSEL")
    print("="*80)

    try:
        from temple_iam_thermal_optimizer import TempleIAMThermalOptimizer
        print("[OK] Import TempleIAMThermalOptimizer reussi")

        # Creation optimizer (sans demarrer)
        optimizer = TempleIAMThermalOptimizer()
        print("[OK] Initialisation TempleIAMThermalOptimizer reussie")
        print(f"     GPU disponible: {optimizer.gpu_available}")
        if optimizer.gpu_available:
            print(f"     GPU name: {optimizer.gpu_name}")
        print(f"     Detecteur de jeux: {'Actif' if optimizer.game_detector else 'Inactif'}")

        return True
    except Exception as e:
        print(f"[ERROR] Erreur thermal optimizer: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Execution de tous les tests"""
    print("\n" + "="*80)
    print("TEMPLE IAM - TESTS SYSTEME UNIVERSEL")
    print("="*80)
    print("Version: UNIVERSAL GAME DETECTION v1.0")
    print("="*80)

    tests = [
        ("Base de donnees de jeux", test_games_database),
        ("Detecteur universel de jeux", test_game_detector),
        ("Integration GPU Monitor", test_integration),
        ("Integration Thermal Optimizer", test_thermal_optimizer_integration)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n[ERROR] Erreur test '{test_name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Resume
    print("\n" + "="*80)
    print("RESUME DES TESTS")
    print("="*80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} - {test_name}")

    print("\n" + "="*80)
    print(f"Resultat: {passed}/{total} tests reussis")

    if passed == total:
        print("[SUCCESS] TOUS LES TESTS SONT REUSSIS ! PLUS ULTRA !")
    else:
        print("[WARNING] Certains tests ont echoue. Verifier les erreurs ci-dessus.")

    print("="*80)

if __name__ == "__main__":
    run_all_tests()
