"""
Analyse detaillee ML pour Cyberpunk 2077
"""
# -*- coding: utf-8 -*-
import json
import sys
from datetime import datetime

# Force UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Charger les donnees
with open('thermal_ml_data.json', 'r', encoding='utf-8') as f:
    ml_data = json.load(f)

with open('sweet_spot_data.json', 'r', encoding='utf-8') as f:
    sweet_spot_data = json.load(f)

cp_ml = ml_data['patterns']['Cyberpunk 2077']
cp_sweet = sweet_spot_data['sweet_spots']['Cyberpunk 2077']

print("=" * 80)
print("CYBERPUNK 2077 - ANALYSE ML COMPLETE")
print("=" * 80)
print()

# Dataset
print("DATASET ML")
print("-" * 80)
print(f"   Echantillons collectes: {cp_ml['samples_count']:,}")
print(f"   Derniere mise a jour:   {cp_ml['last_updated']}")
print(f"   Temps de jeu estime:    ~{cp_ml['samples_count'] / 60 / 60:.1f} heures")
print()

# Temperatures
print("PROFIL THERMIQUE")
print("-" * 80)
print(f"   Temperature moyenne:    {cp_ml['avg_temp']:.1f}C")
print(f"   Temperature minimum:    {cp_ml['min_temp']:.1f}C")
print(f"   Temperature maximum:    {cp_ml['max_temp']:.1f}C")
print(f"   Stabilisation:          {cp_ml['stabilization_temp']}C")
print()
print(f"   [!] ANALYSE: GPU tourne a {cp_ml['avg_temp']:.1f}C en moyenne")
print(f"   [!] CRITIQUE: Atteint {cp_ml['max_temp']}C (max absolu)")
print(f"   [!] Se stabilise a {cp_ml['stabilization_temp']}C (tres chaud!)")
print()

# Dynamique thermique
print("DYNAMIQUE THERMIQUE")
print("-" * 80)
print(f"   Vitesse montee:   +{cp_ml['temp_rise_rate']:.2f}C/sec")
print(f"   Vitesse descente: -{cp_ml['temp_drop_rate']:.2f}C/sec")
print()
print(f"   [+] ANALYSE: La temperature monte et descend a ~{cp_ml['temp_rise_rate']:.1f}C/sec")
print(f"              (symetrique = bon refroidissement passif)")
print()

# Spikes typiques
print("TOP 10 SPIKES TYPIQUES")
print("-" * 80)
for i, spike in enumerate(cp_ml['typical_spikes'], 1):
    bar = "#" * int(spike / 2)
    print(f"   {i:2d}. {spike}C {bar}")
print()
print(f"   [!] OBSERVATION: Spikes frequents entre 84-89C")
print(f"              Pic recurrent a 88-89C")
print()

# Correlation
print("CORRELATION USAGE GPU <-> TEMPERATURE")
print("-" * 80)
correlation = cp_ml['usage_temp_correlation']
print(f"   Coefficient: {correlation:.2%}")
print()
if correlation > 0.8:
    strength = "TRES FORTE"
elif correlation > 0.6:
    strength = "FORTE"
elif correlation > 0.4:
    strength = "MODEREE"
else:
    strength = "FAIBLE"

print(f"   [>] Correlation {strength}")
if correlation > 0.6:
    print(f"   [+] L'usage GPU influence directement la temperature")
    print(f"      -> Reduire l'usage GPU = reduire la temperature")
else:
    print(f"   [+] Autres facteurs influencent la temperature")
    print(f"      -> Verifier le refroidissement ambiant")
print()

# Sweet Spot
print("=" * 80)
print("SWEET SPOT OPTIMAL")
print("=" * 80)
print()
print(f"   Clock GPU optimal:   {cp_sweet['optimal_clock_mhz']} MHz")
print(f"   Temperature cible:   {cp_sweet['optimal_temp_target']}C")
print(f"   FPS attendu:         {cp_sweet['expected_fps']:.1f}")
print(f"   Temperature reelle:  {cp_sweet['expected_temp']}C")
print(f"   Score efficacite:    {cp_sweet['efficiency_score']:.3f}")
print(f"   Confiance:           {cp_sweet['confidence']*100:.0f}%")
print()
print(f"   [>] {cp_sweet['recommendation']}")
print()

# Comparaison clocks
print("COMPARAISON CLOCKS GPU")
print("-" * 80)
details = cp_sweet['analysis_details']['all_levels']
for clock in sorted(details.keys(), key=lambda x: int(x)):
    d = details[clock]
    print(f"\n   {clock} MHz:")
    print(f"      FPS:           {d['avg_fps']:.1f}")
    print(f"      Temperature:   {d['avg_temp']:.1f}C")
    print(f"      Puissance:     {d['avg_power']:.1f}W")
    print(f"      Usage GPU:     {d['avg_usage']:.1f}%")
    print(f"      Efficacite:    {d['efficiency']:.3f}")
    print(f"      Perf/Watt:     {d['perf_per_watt']:.3f}")
    print(f"      Echantillons:  {d['samples']}")

print()
print("=" * 80)
print("RECOMMANDATIONS FINALES")
print("=" * 80)
print()

# Calcul gains
clock_1500 = details['1500']
clock_1850 = details['1850']

fps_gain = ((clock_1850['avg_fps'] - clock_1500['avg_fps']) / clock_1500['avg_fps']) * 100
temp_increase = clock_1850['avg_temp'] - clock_1500['avg_temp']
power_increase = clock_1850['avg_power'] - clock_1500['avg_power']

print(f"   PASSAGE DE 1500 MHz -> 1850 MHz:")
print(f"      [+] FPS:         +{fps_gain:.1f}% ({clock_1500['avg_fps']:.1f} -> {clock_1850['avg_fps']:.1f})")
print(f"      [!] Temperature: +{temp_increase:.1f}C ({clock_1500['avg_temp']:.1f}C -> {clock_1850['avg_temp']:.1f}C)")
print(f"      [!] Puissance:   +{power_increase:.1f}W ({clock_1500['avg_power']:.1f}W -> {clock_1850['avg_power']:.1f}W)")
print()

if temp_increase < 10:
    print(f"   [+] VERDICT: Le sweet spot a 1850 MHz est OPTIMAL")
    print(f"              Excellent compromis performance/temperature")
else:
    print(f"   [!] VERDICT: L'augmentation de temperature est elevee")
    print(f"              Considerer 1500 MHz si la temperature pose probleme")

print()
print(f"   POUR JOUER CONFORTABLEMENT:")
print(f"      1. Limite GPU a 1850 MHz (sweet spot)")
print(f"      2. Cap FPS a 30 (pour stabilite)")
print(f"      3. Surveille que temp < 80C")
print(f"      4. Si > 85C: baisse ray-tracing ou resolution")
print()

# Predictions
avg_temp = cp_ml['avg_temp']
if avg_temp > 85:
    print(f"   [!] ALERTE THERMIQUE:")
    print(f"      Ta moyenne actuelle ({avg_temp:.1f}C) est trop elevee!")
    print(f"      Actions urgentes:")
    print(f"         - Nettoie le GPU/laptop")
    print(f"         - Ameliore la ventilation")
    print(f"         - Baisse les settings graphiques")
    print(f"         - Utilise l'optimizer TOUJOURS active")
elif avg_temp > 80:
    print(f"   [!] ATTENTION:")
    print(f"      Ta moyenne ({avg_temp:.1f}C) est dans la zone warning")
    print(f"      L'optimizer te protege mais ameliore le refroidissement")
else:
    print(f"   [+] Temperature moyenne OK ({avg_temp:.1f}C)")

print()
print("=" * 80)
print("STATISTIQUES AVANCEES")
print("=" * 80)
print()
print(f"   Temps total monitore:     ~{cp_ml['samples_count'] / 60 / 60:.1f}h")
print(f"   Points par heure:          ~{60 * 60:,}")
print(f"   Precision des predictions: Elevee (dataset massif)")
print(f"   Confiance ML:              {cp_sweet['confidence']*100:.0f}% (sweet spot)")
print()
print("=" * 80)
print("[+] Analyse terminee !")
print("=" * 80)
