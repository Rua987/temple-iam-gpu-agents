"""
GPU AUTORESEARCH - Autonomous per-game clock/power auto-tuning.

Instead of relying on fixed clock profiles, this runs an ACTIVE experiment:
it sweeps a set of GPU clock caps, holds each for a measurement window,
records the real temperature / utilisation / power (nvidia-smi) and FPS
(RTSS/PresentMon when available), then picks the most efficient cap and
locks it in for the current game.

This is the missing "active experimentation" piece: the existing
SweetSpotFinder only analysed whatever clocks happened to occur during play;
here we deliberately drive each level so the data is balanced.

Reuses:
- GPURealController  -> actuation (lock_gpu_clocks / set_power_limit) + metrics
- SweetSpotFinder    -> efficiency analysis (optional)

Safety: a temperature guard aborts the sweep, and clocks are always reset
(or the chosen optimum applied) when the run ends.
"""

import time
import json
import logging
import os
from dataclasses import dataclass, asdict
from typing import Callable, Dict, List, Optional

from gpu_real_controller import GPURealController, GPUControlCapability

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class LevelResult:
    """Averaged measurements for one clock cap during the sweep."""
    max_clock_mhz: int
    avg_temp: float
    avg_fps: float
    avg_util: float
    avg_power: float
    samples: int
    aborted: bool = False

    @property
    def efficiency(self) -> float:
        """FPS per degree above idle. Falls back to a utilisation-based proxy
        when no FPS signal is available (e.g. no game / no RTSS)."""
        temp_delta = max(1.0, self.avg_temp - 40.0)
        if self.avg_fps > 0:
            return self.avg_fps / temp_delta
        # No real FPS: proxy = useful work (util * clock) per degree.
        return (self.avg_util * self.max_clock_mhz / 2100.0) / temp_delta


@dataclass
class SweepResult:
    game: str
    optimal_clock_mhz: int
    reason: str
    fps_signal: bool
    levels: List[LevelResult]


class GPUAutoResearch:
    """Autonomous clock/power tuner driven by real measurements."""

    DEFAULT_LEVELS = [1500, 1700, 1850, 1950, 2100]

    def __init__(self,
                 controller: Optional[GPURealController] = None,
                 sweet_spot_finder=None,
                 results_path: str = "autoresearch_results.json"):
        self.controller = controller or GPURealController()
        self.sweet_spot_finder = sweet_spot_finder
        self.results_path = results_path
        self.results: Dict[str, dict] = self._load()

    # ---------- persistence ----------
    def _load(self) -> Dict[str, dict]:
        if os.path.exists(self.results_path):
            try:
                with open(self.results_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Lecture {self.results_path} echouee: {e}")
        return {}

    def _save(self):
        try:
            with open(self.results_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2)
        except Exception as e:
            logging.error(f"Ecriture {self.results_path} echouee: {e}")

    def best_for(self, game: str) -> Optional[int]:
        """Return the previously discovered optimal clock for a game, if any."""
        entry = self.results.get(game)
        return entry.get("optimal_clock_mhz") if entry else None

    # ---------- the experiment ----------
    def run_sweep(self,
                  game: str,
                  fps_provider: Optional[Callable[[], float]] = None,
                  levels: Optional[List[int]] = None,
                  window_s: float = 30.0,
                  settle_s: float = 4.0,
                  sample_interval: float = 1.0,
                  temp_abort: int = 85) -> SweepResult:
        """Sweep each clock cap, measure, and lock in the most efficient one.

        fps_provider: callable returning current FPS (e.g. from RTSS). If None
        or it returns 0, the sweep still runs and uses the utilisation proxy,
        but the result is flagged fps_signal=False (thermal data only).
        """
        if self.controller.capabilities == GPUControlCapability.READ_ONLY:
            raise RuntimeError("Ce GPU est en lecture seule: auto-tuning impossible.")

        levels = sorted(levels or self.DEFAULT_LEVELS)
        logging.info(f"AUTORESEARCH demarre pour '{game}' - niveaux: {levels}")
        results: List[LevelResult] = []
        any_fps = False

        try:
            for cap in levels:
                self.controller.lock_gpu_clocks(300, cap)
                time.sleep(settle_s)

                temps, fpss, utils, powers = [], [], [], []
                n = max(1, int(window_s / sample_interval))
                aborted = False
                for _ in range(n):
                    m = self.controller.get_gpu_metrics()
                    temp = float(m.get("temperature", 0) or 0)
                    if temp >= temp_abort:
                        logging.warning(f"Garde thermique: {temp}C >= {temp_abort}C, niveau {cap} interrompu")
                        aborted = True
                        break
                    temps.append(temp)
                    utils.append(float(m.get("utilization", 0) or 0))
                    powers.append(float(m.get("power_draw", 0) or 0))
                    fps = float(fps_provider()) if fps_provider else 0.0
                    if fps > 0:
                        any_fps = True
                    fpss.append(fps)
                    time.sleep(sample_interval)

                def avg(xs):
                    return sum(xs) / len(xs) if xs else 0.0

                lr = LevelResult(
                    max_clock_mhz=cap,
                    avg_temp=round(avg(temps), 1),
                    avg_fps=round(avg(fpss), 1),
                    avg_util=round(avg(utils), 1),
                    avg_power=round(avg(powers), 1),
                    samples=len(temps),
                    aborted=aborted,
                )
                results.append(lr)
                logging.info(
                    f"  cap {cap}MHz -> temp {lr.avg_temp}C, util {lr.avg_util}%, "
                    f"power {lr.avg_power}W, fps {lr.avg_fps}, eff {lr.efficiency:.3f}"
                )

                # Feed the existing analyser too, when present and we have FPS.
                if self.sweet_spot_finder is not None and lr.avg_fps > 0:
                    try:
                        self.sweet_spot_finder.add_data_point(
                            clock_mhz=cap, temperature=lr.avg_temp,
                            fps=lr.avg_fps, gpu_usage=lr.avg_util,
                            power_draw=lr.avg_power,
                        )
                    except Exception as e:
                        logging.error(f"sweet_spot add_data_point: {e}")

            optimal, reason = self._pick_optimal(results, any_fps)
            self.controller.lock_gpu_clocks(300, optimal)
            logging.info(f"AUTORESEARCH '{game}': optimum {optimal}MHz applique ({reason})")

            self.results[game] = {
                "optimal_clock_mhz": optimal,
                "reason": reason,
                "fps_signal": any_fps,
                "levels": [asdict(r) for r in results],
                "timestamp": time.time(),
            }
            self._save()
            return SweepResult(game, optimal, reason, any_fps, results)

        except Exception:
            # On any failure, never leave the GPU in a locked state.
            self.controller.reset_gpu_clocks()
            raise

    def _pick_optimal(self, results: List[LevelResult], any_fps: bool):
        """Pick the clock cap with the best efficiency among non-aborted, safe
        levels. Returns (clock_mhz, reason)."""
        usable = [r for r in results if not r.aborted and r.samples > 0]
        if not usable:
            return self.DEFAULT_LEVELS[-1], "aucune mesure exploitable (fallback max)"

        best = max(usable, key=lambda r: r.efficiency)
        if any_fps:
            return best.max_clock_mhz, f"meilleure efficacite FPS/degre ({best.efficiency:.3f})"
        return best.max_clock_mhz, "pas de signal FPS - choix par proxy util/temp (donnees thermiques seules)"


def _demo():
    """Short idle sweep to demonstrate the mechanics with REAL nvidia-smi
    metrics (no game required). Differences are small at idle - the point is to
    prove the sweep drives each cap, measures, picks one, and resets cleanly."""
    tuner = GPUAutoResearch(results_path="autoresearch_results.json")
    res = tuner.run_sweep(
        game="_demo_idle",
        levels=[1500, 1950, 2100],
        window_s=4, settle_s=2, sample_interval=1.0,
    )
    print("\n=== DEMO RESULT ===")
    print(f"game={res.game} optimal={res.optimal_clock_mhz}MHz fps_signal={res.fps_signal}")
    print(f"reason: {res.reason}")
    for lr in res.levels:
        print(f"  {lr.max_clock_mhz}MHz: temp={lr.avg_temp} util={lr.avg_util} "
              f"power={lr.avg_power} fps={lr.avg_fps} eff={lr.efficiency:.3f}")
    tuner.controller.reset_gpu_clocks()


if __name__ == "__main__":
    _demo()
