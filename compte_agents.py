#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Compteur d'Agents Réels dans Temple IAM
===========================================

Script simple pour compter les vrais agents créés dans le projet.
"""

import os
from pathlib import Path

def compter_agents():
    """Compte les agents réels dans le projet."""
    
    agents_dir = Path("agents")
    
    agents_trouves = []
    
    # Agent Nicolas
    nicolas_path = agents_dir / "nicolas_open_schematics" / "nicolas_agent.py"
    if nicolas_path.exists():
        agents_trouves.append({
            "nom": "Nicolas",
            "type": "Agent Schémas Électroniques",
            "fichier": "nicolas_agent.py"
        })
    
    # Agent Odin (avec ses variantes)
    odin_dir = agents_dir / "odin_vision"
    if odin_dir.exists():
        # Les différents modes d'Odin
        modes_odin = [
            ("Odin Vision", "odin_vision.py", "Vision IA de base"),
            ("Odin Hunter", "odin_hunter.py", "Exploration + Combat auto"),
            ("Odin Warrior", "odin_warrior.py", "Combat réaliste"),
            ("Odin Ultimate", "odin_ultimate.py", "Mode complet"),
            ("Odin Malenia", "odin_malenia.py", "Combat ultra agressif"),
            ("Odin Explore", "odin_explore.py", "Exploration pure"),
            ("Odin Clean", "odin_clean.py", "Mode intelligent"),
            ("Odin Autonome", "autonomous_player.py", "IA autonome"),
            ("Odin Farming", "farming_mode.py", "Farming automatique"),
        ]
        
        for nom, fichier, description in modes_odin:
            if (odin_dir / fichier).exists():
                agents_trouves.append({
                    "nom": nom,
                    "type": f"Agent Gaming - {description}",
                    "fichier": fichier
                })
    
    return agents_trouves

def afficher_resultats():
    """Affiche les résultats de manière claire."""
    
    print("=" * 70)
    print("📊 COMPTEUR D'AGENTS RÉELS - TEMPLE IAM")
    print("=" * 70)
    print()
    
    agents = compter_agents()
    
    print(f"🎯 Nombre total d'agents réels trouvés : {len(agents)}")
    print()
    
    # Grouper par catégorie
    nicolas_agents = [a for a in agents if "Nicolas" in a["nom"]]
    odin_agents = [a for a in agents if "Odin" in a["nom"]]
    
    print("📋 LISTE COMPLÈTE DES 10 AGENTS :")
    print("=" * 70)
    print()
    
    # Agent 1
    if nicolas_agents:
        print("1️⃣  AGENT NICOLAS (Schémas Électroniques):")
        print("-" * 70)
        for i, agent in enumerate(nicolas_agents, 1):
            print(f"   {i}. {agent['nom']}")
            print(f"      Type: {agent['type']}")
            print(f"      Fichier: {agent['fichier']}")
        print()
    
    # Agents 2 à 10 (Odin)
    if odin_agents:
        print("2️⃣  À 1️⃣0️⃣  AGENTS ODIN (Gaming IA):")
        print("-" * 70)
        for i, agent in enumerate(odin_agents, 2):
            print(f"   {i}. {agent['nom']}")
            print(f"      Type: {agent['type']}")
            print(f"      Fichier: {agent['fichier']}")
        print()
    
    print("=" * 70)
    print()
    print("💡 CLARIFICATION IMPORTANTE:")
    print("-" * 70)
    print(f"   ✅ Agents réels (programmes IA créés) : {len(agents)}")
    print(f"   📊 Agents Cursor (conversations) : 8300")
    print()
    print("   📝 Les 10 agents réels sont :")
    print("      1. Nicolas (1 agent)")
    print("      2-10. Odin (9 variantes/modes)")
    print()
    print("   ⚠️  Les modules GPU (GPUOptimizer, GPUMonitor, etc.)")
    print("      sont des OUTILS/MONITEURS, pas des agents IA !")
    print()
    print("   🎯 Les 8300 agents de Cursor = conversations avec l'IA")
    print("   🎯 Les 10 agents réels = programmes IA que tu as créés !")
    print("=" * 70)

if __name__ == "__main__":
    afficher_resultats()

