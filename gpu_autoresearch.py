"""
GPU AUTORESEARCH - Autonomous per-workload clock/power auto-tuning.

Works for BOTH gaming and local AI inference (Ollama / LM Studio / etc.).
Instead of relying on fixed clock profiles, it runs an ACTIVE experiment:
it sweeps a set of GPU clock caps, holds each for a measurement window,
records the real temperature / utilisation / power / VRAM (nvidia-smi) and a
performance signal, then picks the most efficient cap and locks it in for the
current workload.

The performance signal is pluggable:
- games            -> FPS via RTSS shared memory (make_rtss_fps_provider)
- local LLMs       -> tokens/second via Ollama (make_ollama_provider)

This is the missing "active experimentation" piece: SweetSpotFinder only
analysed whatever clocks happened to occur during use; here we deliberately
drive each level so the data is balanced. LLM inference is memory-bound, so the
interesting trade-offs show at LOWER clock caps (and on power limit) - that is
why the default LLM levels differ from the gaming ones.

Reuses GPURealController for actuation/metrics.

Safety: a temperature guard aborts the sweep, and clocks are always reset (or
the chosen optimum applied) when the run ends.
"""

import time
import json
import logging
import os
import urllib.request
from dataclasses import dataclass, asdict
from typing import Callable, Dict, List, Optional

from gpu_real_controller import GPURealController, GPUControlCapability

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class LevelResult:
    """Averaged measurements for one clock cap during the sweep."""
    max_clock_mhz: int
    avg_temp: float
    avg_perf: float          # FPS or tokens/s, depending on the workload
    avg_util: float
    avg_power: float
    avg_vram_mb: float
    samples: int
    aborted: bool = False

    @property
    def efficiency(self) -> float:
        """Performance per degree above idle. Falls back to a utilisation-based
        proxy when no performance signal is available."""
        temp_delta = max(1.0, self.avg_temp - 40.0)
        if self.avg_perf > 0:
            return self.avg_perf / temp_delta
        return (self.avg_util * self.max_clock_mhz / 2100.0) / temp_delta


@dataclass
class SweepResult:
    workload: str
    optimal_clock_mhz: int
    reason: str
    perf_unit: str
    perf_signal: bool
    levels: List[LevelResult]


class GPUAutoResearch:
    """Autonomous clock/power tuner driven by real measurements."""

    GAMING_LEVELS = [1500, 1700, 1850, 1950, 2100]
    # LLM inference is memory-bound and runs at low core clocks; sweep lower so
    # the caps actually bite.
    LLM_LEVELS = [600, 855, 1200, 1950]

    def __init__(self,
                 controller: Optional[GPURealController] = None,
                 results_path: str = "autoresearch_results.json"):
        self.controller = controller or GPURealController()
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

    def best_for(self, workload: str) -> Optional[int]:
        """Return the previously discovered optimal clock for a workload."""
        entry = self.results.get(workload)
        return entry.get("optimal_clock_mhz") if entry else None

    # ---------- the experiment ----------
    def run_sweep(self,
                  workload: str,
                  perf_provider: Optional[Callable[[], float]] = None,
                  perf_unit: str = "fps",
                  levels: Optional[List[int]] = None,
                  window_s: float = 30.0,
                  samples: Optional[int] = None,
                  settle_s: float = 4.0,
                  sample_interval: float = 1.0,
                  temp_abort: int = 85) -> SweepResult:
        """Sweep each clock cap, measure, and lock in the most efficient one.

        perf_provider: callable returning the current performance value (FPS for
        games, tokens/s for LLMs). If None or it returns 0, the sweep still runs
        and uses the utilisation proxy, flagging perf_signal=False.
        samples: fixed number of measurements per level (use this for LLMs,
        where each sample is one generation). If None, use window_s/interval.
        """
        if self.controller.capabilities == GPUControlCapability.READ_ONLY:
            raise RuntimeError("Ce GPU est en lecture seule: auto-tuning impossible.")

        levels = sorted(levels or self.GAMING_LEVELS)
        logging.info(f"AUTORESEARCH demarre pour '{workload}' [{perf_unit}] - niveaux: {levels}")
        results: List[LevelResult] = []
        any_perf = False

        try:
            for cap in levels:
                self.controller.lock_gpu_clocks(300, cap)
                time.sleep(settle_s)

                temps, perfs, utils, powers, vrams = [], [], [], [], []
                n = samples if samples else max(1, int(window_s / sample_interval))
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
                    vrams.append(float(m.get("memory_used_mb", 0) or 0))
                    perf = float(perf_provider()) if perf_provider else 0.0
                    if perf > 0:
                        any_perf = True
                    perfs.append(perf)
                    if sample_interval > 0:
                        time.sleep(sample_interval)

                def avg(xs):
                    return sum(xs) / len(xs) if xs else 0.0

                lr = LevelResult(
                    max_clock_mhz=cap,
                    avg_temp=round(avg(temps), 1),
                    avg_perf=round(avg(perfs), 1),
                    avg_util=round(avg(utils), 1),
                    avg_power=round(avg(powers), 1),
                    avg_vram_mb=round(avg(vrams), 0),
                    samples=len(temps),
                    aborted=aborted,
                )
                results.append(lr)
                logging.info(
                    f"  cap {cap}MHz -> temp {lr.avg_temp}C, util {lr.avg_util}%, "
                    f"power {lr.avg_power}W, vram {lr.avg_vram_mb:.0f}MB, "
                    f"perf {lr.avg_perf}{perf_unit}, eff {lr.efficiency:.3f}"
                )

            optimal, reason = self._pick_optimal(results, any_perf)
            self.controller.lock_gpu_clocks(300, optimal)
            logging.info(f"AUTORESEARCH '{workload}': optimum {optimal}MHz applique ({reason})")

            self.results[workload] = {
                "optimal_clock_mhz": optimal,
                "reason": reason,
                "perf_unit": perf_unit,
                "perf_signal": any_perf,
                "levels": [asdict(r) for r in results],
                "timestamp": time.time(),
            }
            self._save()
            return SweepResult(workload, optimal, reason, perf_unit, any_perf, results)

        except Exception:
            # On any failure, never leave the GPU in a locked state.
            self.controller.reset_gpu_clocks()
            raise

    def _pick_optimal(self, results: List[LevelResult], any_perf: bool):
        """Pick the clock cap with the best efficiency among safe levels."""
        usable = [r for r in results if not r.aborted and r.samples > 0]
        if not usable:
            return self.GAMING_LEVELS[-1], "aucune mesure exploitable (fallback max)"

        best = max(usable, key=lambda r: r.efficiency)
        if any_perf:
            return best.max_clock_mhz, f"meilleure efficacite perf/degre ({best.efficiency:.3f})"
        return best.max_clock_mhz, "pas de signal perf - choix par proxy util/temp (donnees thermiques seules)"


# --------------------------------------------------------------------------
# Performance providers
# --------------------------------------------------------------------------
def make_ollama_provider(model: str,
                         prompt: str = "Write a detailed paragraph about the ocean.",
                         num_predict: int = 64,
                         host: str = "http://localhost:11434") -> Callable[[], float]:
    """Return a perf_provider that runs one Ollama generation and reports the
    eval throughput in tokens/second."""
    url = host.rstrip("/") + "/api/generate"

    def provider() -> float:
        body = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": num_predict},
        }).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read())
            ec, ed = d.get("eval_count", 0), d.get("eval_duration", 0)
            return ec / (ed / 1e9) if ed else 0.0
        except Exception as e:
            logging.error(f"ollama provider: {e}")
            return 0.0

    return provider


# --------------------------------------------------------------------------
# FPS provider via RTSS (RivaTuner Statistics Server, ships with MSI Afterburner)
# --------------------------------------------------------------------------
class _RTSSReader:
    """Reads real per-application FPS from RTSS shared memory.

    RTSS (bundled with MSI Afterburner) publishes a shared block named
    'RTSSSharedMemoryV2' with one entry per hooked app, each holding a frame
    counter and a time window: FPS = dwFrames * 1000 / (dwTime1 - dwTime0).
    Requires RTSS to be running and the game to be hooked by it. We attach to
    the EXISTING mapping via OpenFileMapping (not mmap(-1), which would create
    a fresh empty block), and read the documented entry layout.
    """
    _FILE_MAP_READ = 0x0004
    _SIGNATURE = 0x52545353  # 'RTSS'
    # byte offsets inside RTSS_SHARED_MEMORY_APP_ENTRY
    _OFF_TIME0, _OFF_TIME1, _OFF_FRAMES = 268, 272, 276

    def __init__(self):
        self._addr = None
        self._entry_size = self._arr_off = self._arr_size = 0
        try:
            import ctypes
            from ctypes import wintypes
            k = ctypes.windll.kernel32
            k.OpenFileMappingW.restype = wintypes.HANDLE
            k.OpenFileMappingW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
            k.MapViewOfFile.restype = ctypes.c_void_p
            k.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                        wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
            h = k.OpenFileMappingW(self._FILE_MAP_READ, False, "RTSSSharedMemoryV2")
            if not h:
                logging.info("RTSS non detecte (lancez MSI Afterburner/RTSS) - pas de FPS reelle")
                return
            addr = k.MapViewOfFile(h, self._FILE_MAP_READ, 0, 0, 0)
            if not addr:
                return
            hdr = (ctypes.c_uint32 * 8).from_address(addr)
            if hdr[0] != self._SIGNATURE:
                logging.info(f"RTSS signature inattendue: {hex(hdr[0])}")
                return
            self._ctypes = ctypes
            self._addr = addr
            self._entry_size, self._arr_off, self._arr_size = hdr[2], hdr[3], hdr[4]
            logging.info(f"RTSS detecte: {self._arr_size} slots d'app")
        except Exception as e:
            logging.info(f"RTSS indisponible: {e}")

    @property
    def available(self) -> bool:
        return self._addr is not None

    def read_max_fps(self, name_filter: Optional[str] = None) -> float:
        """Highest FPS among currently hooked apps (0.0 if none/unavailable)."""
        if not self._addr:
            return 0.0
        c = self._ctypes
        best = 0.0
        for i in range(self._arr_size):
            base = self._addr + self._arr_off + i * self._entry_size
            if c.c_uint32.from_address(base).value == 0:  # dwProcessID
                continue
            if name_filter:
                nm = c.string_at(base + 4, 260).split(b"\x00")[0].decode("ascii", "replace")
                if name_filter.lower() not in nm.lower():
                    continue
            t0 = c.c_uint32.from_address(base + self._OFF_TIME0).value
            t1 = c.c_uint32.from_address(base + self._OFF_TIME1).value
            frames = c.c_uint32.from_address(base + self._OFF_FRAMES).value
            if t1 > t0:
                fps = frames * 1000.0 / (t1 - t0)
                best = max(best, fps)
        return best


def make_rtss_fps_provider(name_filter: Optional[str] = None) -> Callable[[], float]:
    """Return a perf_provider that reads real FPS from RTSS shared memory.

    name_filter: optional substring of the game's exe name (e.g. 'cyberpunk');
    if None, uses the fastest-rendering hooked app.
    """
    reader = _RTSSReader()

    def provider() -> float:
        return reader.read_max_fps(name_filter)

    return provider


# --------------------------------------------------------------------------
# Demos / CLI
# --------------------------------------------------------------------------
def _print(res: SweepResult):
    print("\n=== AUTORESEARCH RESULT ===")
    print(f"workload={res.workload} optimal={res.optimal_clock_mhz}MHz "
          f"perf_signal={res.perf_signal} ({res.perf_unit})")
    print(f"reason: {res.reason}")
    for lr in res.levels:
        print(f"  {lr.max_clock_mhz}MHz: temp={lr.avg_temp} util={lr.avg_util} "
              f"power={lr.avg_power} vram={lr.avg_vram_mb:.0f}MB "
              f"perf={lr.avg_perf}{res.perf_unit} eff={lr.efficiency:.3f}")


def _demo_idle():
    """Short idle sweep (no game/model needed) - proves the mechanics."""
    tuner = GPUAutoResearch()
    res = tuner.run_sweep("_demo_idle", levels=[1500, 1950, 2100],
                          window_s=4, settle_s=2, sample_interval=1.0)
    _print(res)
    tuner.controller.reset_gpu_clocks()


def _demo_llm(model: str):
    """Real LLM auto-tuning: sweep clock caps while benchmarking tokens/s."""
    tuner = GPUAutoResearch()
    provider = make_ollama_provider(model, num_predict=64)
    res = tuner.run_sweep(
        workload=f"ollama:{model}",
        perf_provider=provider,
        perf_unit="tok/s",
        levels=GPUAutoResearch.LLM_LEVELS,
        samples=2,            # 2 generations per level
        settle_s=2,
        sample_interval=0,    # the generation itself provides the time
    )
    _print(res)
    tuner.controller.reset_gpu_clocks()


def _demo_game(name_filter: Optional[str] = None):
    """Real gaming auto-tuning: sweep clock caps while reading FPS from RTSS.

    Launch your game first, with MSI Afterburner / RTSS running and its FPS
    overlay active, then start this. Pass a name filter (e.g. 'cyberpunk') to
    lock onto a specific process instead of the fastest-rendering app.
    """
    tuner = GPUAutoResearch()
    provider = make_rtss_fps_provider(name_filter)
    res = tuner.run_sweep(
        workload=f"game:{name_filter or 'active'}",
        perf_provider=provider,
        perf_unit="fps",
        levels=GPUAutoResearch.GAMING_LEVELS,
        window_s=20, settle_s=4, sample_interval=1.0,
    )
    _print(res)
    tuner.controller.reset_gpu_clocks()


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) >= 2 else ""
    if mode == "llm":
        _demo_llm(sys.argv[2] if len(sys.argv) > 2 else "dolphin-trinity-nano:latest")
    elif mode == "game":
        _demo_game(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        _demo_idle()
