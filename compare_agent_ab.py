"""
COMPARAISON A/B : SANS agent GPU  vs  AVEC agent GPU.

But: prouver, chiffres a l'appui, la difference entre les deux strategies sur
un meme workload (jeu ou LLM).

  Phase A - SANS agent : on remet le GPU aux reglages d'usine (driver libre) et
                         on mesure fps/temp/power/util pendant une fenetre.
  Phase B - AVEC agent : l'agent (GPUAutoResearch) sweep les clocks, trouve et
                         applique l'optimum, puis on remesure dans les memes
                         conditions.

A la fin on affiche le delta (perf identique ? moins chaud ? moins gourmand ?)
et un verdict efficacite (perf par watt et perf par degre).

Usage:
    python compare_agent_ab.py game cyberpunk
    python compare_agent_ab.py game            (jeu actif le plus rapide)
    python compare_agent_ab.py llm  dolphin-trinity-nano:latest
"""

import sys
import time
import logging

from gpu_real_controller import GPURealController, GPUControlCapability
from gpu_autoresearch import (
    GPUAutoResearch,
    make_rtss_fps_provider,
    make_ollama_provider,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def measure(controller, perf_provider, label, window_s=20.0, interval=1.0):
    """Echantillonne metriques + perf pendant window_s, retourne les moyennes."""
    temps, perfs, utils, powers, vrams = [], [], [], [], []
    n = max(1, int(window_s / interval))
    logging.info(f"[{label}] mesure sur {window_s:.0f}s ({n} echantillons)...")
    for _ in range(n):
        m = controller.get_gpu_metrics()
        temps.append(float(m.get("temperature", 0) or 0))
        utils.append(float(m.get("utilization", 0) or 0))
        powers.append(float(m.get("power_draw", 0) or 0))
        vrams.append(float(m.get("memory_used_mb", 0) or 0))
        perfs.append(float(perf_provider()) if perf_provider else 0.0)
        if interval > 0:
            time.sleep(interval)

    def avg(xs):
        return sum(xs) / len(xs) if xs else 0.0

    return {
        "label": label,
        "perf": round(avg(perfs), 1),
        "temp": round(avg(temps), 1),
        "util": round(avg(utils), 1),
        "power": round(avg(powers), 1),
        "vram": round(avg(vrams), 0),
    }


def perf_per_watt(r):
    return r["perf"] / r["power"] if r["power"] > 0 else 0.0


def perf_per_degree(r):
    delta = max(1.0, r["temp"] - 40.0)
    return r["perf"] / delta


def pct(before, after):
    if before == 0:
        return 0.0
    return (after - before) / before * 100.0


def main():
    mode = sys.argv[1] if len(sys.argv) >= 2 else "game"
    target = sys.argv[2] if len(sys.argv) > 2 else None
    unit = "fps"

    controller = GPURealController()
    if controller.capabilities == GPUControlCapability.READ_ONLY:
        print("ERREUR: GPU en lecture seule, impossible de comparer (pas d'actuation).")
        return

    # Provider de perf selon le workload
    if mode == "llm":
        model = target or "dolphin-trinity-nano:latest"
        provider = make_ollama_provider(model, num_predict=64)
        unit = "tok/s"
        is_gaming = False
        workload = f"ollama:{model}"
        levels = GPUAutoResearch.LLM_LEVELS
    else:
        provider = make_rtss_fps_provider(target)
        unit = "fps"
        is_gaming = True
        workload = f"game:{target or 'active'}"
        levels = GPUAutoResearch.GAMING_LEVELS

    print("=" * 70)
    print(f"COMPARAISON A/B  -  workload: {workload}")
    print("=" * 70)

    try:
        # ----- PHASE A : SANS agent (clocks d'usine) -----
        print("\n--- PHASE A : SANS agent (reglages d'usine du driver) ---")
        controller.reset_gpu_clocks()
        time.sleep(4)  # laisser le driver reprendre la main
        baseline = measure(controller, provider, "SANS agent",
                           window_s=20 if is_gaming else 0, interval=1.0)

        # Pour le LLM, la fenetre fixe ne marche pas (chaque sample = 1 generation);
        # on prend 2 generations a la place.
        if not is_gaming:
            baseline = _measure_llm(controller, provider, "SANS agent", n=2)

        # ----- PHASE B : AVEC agent (sweep + optimum applique) -----
        print("\n--- PHASE B : AVEC agent (sweep autonome + optimum verrouille) ---")
        tuner = GPUAutoResearch(controller=controller)
        if is_gaming:
            sweep = tuner.run_sweep(workload, provider, unit, levels=levels,
                                    window_s=20, settle_s=4, sample_interval=1.0)
        else:
            sweep = tuner.run_sweep(workload, provider, unit, levels=levels,
                                    samples=2, settle_s=2, sample_interval=0)

        # l'optimum est deja applique par run_sweep ; on remesure a ce clock
        if is_gaming:
            optimized = measure(controller, provider, f"AVEC agent ({sweep.optimal_clock_mhz}MHz)",
                               window_s=20, interval=1.0)
        else:
            optimized = _measure_llm(controller, provider,
                                    f"AVEC agent ({sweep.optimal_clock_mhz}MHz)", n=2)

        # ----- VERDICT -----
        _print_verdict(baseline, optimized, unit, sweep.optimal_clock_mhz)

    finally:
        controller.reset_gpu_clocks()
        logging.info("GPU clocks remis aux valeurs par defaut.")


def _measure_llm(controller, provider, label, n=2):
    """Mesure LLM: chaque sample est une generation complete (fournit son temps)."""
    temps, perfs, powers = [], [], []
    logging.info(f"[{label}] mesure LLM ({n} generations)...")
    for _ in range(n):
        m = controller.get_gpu_metrics()
        temps.append(float(m.get("temperature", 0) or 0))
        powers.append(float(m.get("power_draw", 0) or 0))
        perfs.append(float(provider()))

    def avg(xs):
        return sum(xs) / len(xs) if xs else 0.0

    return {
        "label": label,
        "perf": round(avg(perfs), 1),
        "temp": round(avg(temps), 1),
        "util": 0.0,
        "power": round(avg(powers), 1),
        "vram": 0.0,
    }


def _print_verdict(a, b, unit, optimal_mhz):
    print("\n" + "=" * 70)
    print("RESULTAT A/B")
    print("=" * 70)
    rows = [
        ("Strategie", a["label"], b["label"]),
        (f"Perf ({unit})", a["perf"], b["perf"]),
        ("Temp (C)", a["temp"], b["temp"]),
        ("Power (W)", a["power"], b["power"]),
        ("Perf/Watt", round(perf_per_watt(a), 3), round(perf_per_watt(b), 3)),
        ("Perf/degre", round(perf_per_degree(a), 3), round(perf_per_degree(b), 3)),
    ]
    w = 22
    for name, va, vb in rows:
        print(f"{name:<14}{str(va):<{w}}{str(vb):<{w}}")

    print("-" * 70)
    print(f"Clock optimal trouve par l'agent : {optimal_mhz} MHz")
    print(f"Delta perf   : {pct(a['perf'], b['perf']):+.1f}%")
    print(f"Delta temp   : {b['temp'] - a['temp']:+.1f} C")
    print(f"Delta power  : {pct(a['power'], b['power']):+.1f}%")
    print(f"Delta perf/W : {pct(perf_per_watt(a), perf_per_watt(b)):+.1f}%")

    # Verdict lisible
    same_perf = abs(pct(a["perf"], b["perf"])) < 5.0
    cooler = b["temp"] < a["temp"]
    less_power = b["power"] < a["power"]
    print("-" * 70)
    if same_perf and (cooler or less_power):
        print("VERDICT: l'agent garde la MEME perf en consommant moins / plus froid.")
        print("         -> meme resultat, meilleure efficacite. Strategie agent gagnante.")
    elif b["perf"] > a["perf"]:
        print("VERDICT: l'agent ameliore la perf brute. Strategie agent gagnante.")
    else:
        print("VERDICT: a analyser (voir deltas ci-dessus).")


if __name__ == "__main__":
    main()
