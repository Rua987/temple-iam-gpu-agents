# Temple IAM GPU Agents

Adaptive GPU monitoring and thermal tuning for NVIDIA gaming PCs.

It detects the game you're running, watches GPU temperature / VRAM / power / estimated FPS in real time, and adjusts thermal targets and fan behavior. The longer you play, the more session data it collects and the better its per-game profiles get.

> **Status: works for me, looking for more testers.**
> Validated by the author on an **RTX 2070** and an **RTX 4060** (see [Tested hardware](#tested-hardware)). It very likely runs on other NVIDIA GPUs, but that isn't confirmed yet — **that's exactly what I need help with.** See [Call for testers](#call-for-testers).

---

## What it actually does

- **Auto-detects the running game** and loads a matching profile, or learns a new one.
- **Real-time monitoring**: GPU temperature, VRAM usage, power draw, clocks, estimated FPS.
- **Thermal control**: keeps the GPU around a target temperature (default 75 °C) with automatic fan adjustment and an emergency cutoff at 85 °C.
- **Adaptive profiles**: tuning decisions improve after several hours of real play, because there's more representative data to learn from.
- **Non-destructive**: changes are reversible; stop the tool and the GPU returns to default behavior.

It does **not** overclock blindly or promise fixed FPS gains. Results depend on your GPU, driver, cooling, and the game.

---

## Tested hardware

| GPU | Games tested in real sessions |
|-----|-------------------------------|
| **RTX 2070** | Alan Wake 2, Cyberpunk 2077, Elden Ring |
| **RTX 4060** | Arma 4, Teardown, latest Hitman |

Anything not in this table is **untested**. It may work — please tell me if it does.

---

## Requirements

- NVIDIA GPU with working `nvidia-smi`
- NVIDIA driver 525.x or newer
- Python 3.10+ (or Docker)

---

## Quick start (Python)

```bash
git clone https://github.com/Rua987/temple-iam-gpu-agents.git
cd temple-iam-gpu-agents

# Dependencies
pip install -r requirements.txt

# 1) Read-only diagnostic FIRST (modifies nothing, writes diagnostic_report.txt)
python diagnostic.py

# 2) Dry-run: see what the agent WOULD do, with no real GPU action
python universal_gpu_monitor.py --dry-run

# 3) Live run (auto-detects the active game/workload)
python universal_gpu_monitor.py
```

### Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | Simulate everything (detection, scoring, display) — **no real GPU action**. Use this first. |
| `--gpu-index N` | Target a specific GPU (multi-GPU). Default `0`. |
| `--interval S` | Polling interval in seconds (or env `MONITOR_INTERVAL`). Default `1.0`. |

## Quick start (Docker)

Requires the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

```bash
docker compose -f docker-compose.gpu.yml up -d universal-gpu-monitor
docker compose -f docker-compose.gpu.yml logs -f universal-gpu-monitor
```

Full Docker details: [README-DOCKER.md](README-DOCKER.md).

---

## How the thermal control works

The monitor scores the live workload every second (`performance_scorer`) and
drives a **3-tier thermal control**:

- **Tier 0 — anticipation** (`thermal_ml_predictor`): a short linear-regression
  forecast of temperature. If a spike is predicted (e.g. >88 °C within ~10 s) it
  brakes *before* the threshold instead of reacting after the fact.
- **Tier 1 — safety**: a hard emergency cap (`workload_thermal_controller`) that
  takes absolute priority whenever temperature actually derails.
- **Tier 2 — fine control** (`sweet_spot_finder`): in the normal range it converges
  the clock cap continuously toward the learned per-game optimal (efficiency =
  FPS / temperature-rise), instead of jumping between discrete steps.

Real FPS come from **RTSS shared memory** (needs MSI Afterburner / RTSS running and
hooking the game). Without RTSS it falls back to a utilisation-based estimate,
clearly labelled `(estimated)` — no crash.

### Gaming vs AI gating

Gaming-only features — RTSS FPS, the upscaling advisor, Magpie orchestration, the
sweet-spot fine control and spike prediction — **never run on `local_ai` workloads**.
When the agent detects Ollama or a training process it stays **pure thermal**: no
upscaling, no FPS-based logic, just the safety brake. The dashboard switches to an
AI view (power / clock instead of FPS).

### Upscaling (gaming only)

The agent does **not** reimplement DLSS (it can't — DLSS needs per-frame motion
vectors only the game engine has). Instead, when it detects a game it can
**orchestrate an external upscaler** (Magpie / Lossless Scaling) if one is installed,
and advise enabling in-game DLSS when it has to throttle for heat. It launches the
tool; you trigger scaling with the tool's own hotkey.

---

## Configuration

The polling interval can be set via the `--interval` flag or the
`MONITOR_INTERVAL` environment variable:

```bash
MONITOR_INTERVAL=2.0 python universal_gpu_monitor.py
# or
python universal_gpu_monitor.py --interval 2.0
```

Per-game **target / critical temperatures and FPS targets** are not global — they
live in the game profiles (`games_database.py`, plus the profiles the agent learns
per game). The workload is auto-detected; there is no `GAME_NAME` to set.

---

## Call for testers

I built this for my own machine and it's been stable through hours of AAA gameplay on an RTX 2070 and an RTX 4060. I'd like to know whether it holds up on **other GPUs and other games** — that's the only way to know what's real versus what just happens to work on my hardware.

If you try it, please [open an issue](https://github.com/Rua987/temple-iam-gpu-agents/issues) with:

- **GPU** and driver version
- **OS** (Windows / Linux)
- **Game(s)** and resolution / preset
- What you observed: temperatures, stability, FPS feel, anything that broke
- The session log if you can attach it

Honest negative reports are just as useful as positive ones. Thanks for trying it.

---

## License

MIT — see [LICENSE](LICENSE).
