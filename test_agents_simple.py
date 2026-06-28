#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TEST SIMPLE DES AGENTS - Temple IAM
======================================
"""

import sys
from pathlib import Path

print("=" * 80)
print("🧪 TEST DES AGENTS - TEMPLE IAM")
print("=" * 80)
print()

# Test 1: BeachPatrol
print("1️⃣ TEST BEACHPATROL")
print("-" * 80)
try:
    sys.path.insert(0, str(Path("agents/beachpatrol_web")))
    from beachpatrol_agent_direct import BeachPatrolAgentDirect
    
    print("   ✅ Import réussi")
    agent = BeachPatrolAgentDirect(headless=True, incognito=True)
    print("   ✅ Agent créé")
    
    if agent._start_browser():
        print("   ✅ Navigateur démarré")
        agent._stop_browser()
        print("   ✅ Navigateur fermé")
        print("   ✅ BEACHPATROL : OK")
        beachpatrol_ok = True
    else:
        print("   ❌ Erreur navigateur")
        beachpatrol_ok = False
except Exception as e:
    print(f"   ❌ Erreur : {e}")
    beachpatrol_ok = False

print()

# Test 2: Farming System
print("2️⃣ TEST FARMING SYSTEM")
print("-" * 80)
try:
    sys.path.insert(0, str(Path("agents/beachpatrol_web")))
    from farming_system import FarmingSystem
    
    print("   ✅ Import réussi")
    system = FarmingSystem()
    print("   ✅ Système créé")
    tasks = system.load_tasks()
    print(f"   ✅ {len(tasks)} tâche(s) chargée(s)")
    print("   ✅ FARMING SYSTEM : OK")
    farming_ok = True
except Exception as e:
    print(f"   ❌ Erreur : {e}")
    farming_ok = False

print()

# Test 3: Download System
print("3️⃣ TEST DOWNLOAD SYSTEM")
print("-" * 80)
try:
    sys.path.insert(0, str(Path("agents/beachpatrol_web")))
    from farming_download_direct import format_file_size
    
    print("   ✅ Import réussi")
    size = format_file_size(1024 * 1024)
    print(f"   ✅ Format test : {size}")
    print("   ✅ DOWNLOAD SYSTEM : OK")
    download_ok = True
except Exception as e:
    print(f"   ❌ Erreur : {e}")
    download_ok = False

print()

# Résumé
print("=" * 80)
print("📊 RÉSUMÉ")
print("=" * 80)
print(f"   BeachPatrol    : {'✅ OK' if beachpatrol_ok else '❌ ÉCHEC'}")
print(f"   Farming System : {'✅ OK' if farming_ok else '❌ ÉCHEC'}")
print(f"   Download System: {'✅ OK' if download_ok else '❌ ÉCHEC'}")
print()

total = 3
passed = sum([beachpatrol_ok, farming_ok, download_ok])

print(f"Total : {passed}/{total} test(s) réussi(s)")

if passed == total:
    print("\n🎉 Tous les tests sont passés !")
else:
    print(f"\n⚠️ {total - passed} test(s) ont échoué")

