#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 UNIVERSAL GPU MONITOR V2 - LAUNCHER (UTF-8 Safe)
Système avancé avec base de données de jeux et profils adaptatifs

IMPORTANT: Ce launcher fixe l'encodage UTF-8 sur Windows AVANT d'importer
           le module principal qui contient des emojis

Version: 2.0
Compatibilité: Windows UTF-8 Safe (basé sur le fix d'Eugène)
"""

import sys
import os

# ========================================================================
# FIX ENCODAGE UTF-8 WINDOWS (Crédit: Eugène Villant @evillant08)
# ========================================================================
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ========================================================================
# IMPORT DU MONITEUR UNIVERSEL V2
# ========================================================================

try:
    print("="*80)
    print("UNIVERSAL GPU MONITOR V2 - ENHANCED SYSTEM")
    print("="*80)
    print("Features:")
    print("  - 16+ AAA games with complete profiles")
    print("  - Auto-learning for unknown games")
    print("  - Adaptive thermal profiles per game")
    print("  - DLSS/RT/FSR detection")
    print("  - Comprehensive games database")
    print("="*80)
    print()

    # Import le moniteur universel v2
    from universal_gpu_monitor import UniversalGPUMonitor, main

    print("[OK] Universal GPU Monitor V2 loaded successfully")
    print("[OK] UTF-8 encoding active (Windows compatible)")
    print()

    # Lance le moniteur
    main()

except ImportError as e:
    print(f"[ERROR] Failed to import universal_gpu_monitor: {e}")
    print()
    print("Make sure you have:")
    print("  - universal_gpu_monitor.py")
    print("  - universal_game_detector.py")
    print("  - games_database.py")
    print()
    print("Fallback: You can use run_gpu_monitor.py (Eugene's version) instead")
    sys.exit(1)

except KeyboardInterrupt:
    print()
    print("[INFO] Universal GPU Monitor V2 stopped by user")
    sys.exit(0)

except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
