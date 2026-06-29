# Contributing

Thanks for your interest! This project tunes real GPU clocks, so safety and
honest reporting matter more than feature count.

## Before you run it

- Use **`python diagnostic.py`** first (read-only) and check the report.
- Use **`python universal_gpu_monitor.py --dry-run`** to see what the agent *would*
  do without applying any real GPU action. Always sanity-check in dry-run before a
  live run on your main GPU.

## Reporting / testing

Open an issue using the **Bug report / Test feedback** template. Paste the
`diagnostic.py` output, the game/workload, and what you observed. Negative reports
("it throttled too hard", "fine control oscillated") are as valuable as positive ones.

## Code changes

1. Fork, branch from `main`.
2. Keep the gating intact: **gaming-only features** (RTSS FPS, upscaling advisor,
   Magpie orchestration, sweet-spot fine control, spike prediction) must never run
   on `local_ai` workloads (Ollama / training stay pure thermal).
3. Any new GPU actuation must respect `--dry-run` (no real action when simulating).
4. Run a quick smoke test: `python universal_gpu_monitor.py --dry-run` should start
   and render without applying anything.

## Architecture in one breath

`universal_gpu_monitor.py` is the loop. It detects the workload, scores it
(`performance_scorer`), and drives a 3-tier thermal control:

- **Tier 0 — anticipation** (`thermal_ml_predictor`): brake before a predicted spike.
- **Tier 1 — safety**: hard emergency cap (`workload_thermal_controller`).
- **Tier 2 — fine control** (`sweet_spot_finder`): converge to the learned per-game
  optimal clock (gaming only).

GPU actuation/metrics go through `gpu_real_controller` (nvidia-smi). External
upscaling is orchestrated, never reimplemented (`external_upscaler`).
