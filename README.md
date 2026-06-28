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

# Dependencies (no requirements file yet — these are the ones that matter)
pip install GPUtil psutil pynvml

# Start the adaptive monitor (auto-detects the active game)
python universal_gpu_monitor.py

# Optional: thermal optimizer with per-game profiles
python temple_iam_thermal_optimizer.py
```

## Quick start (Docker)

Requires the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

```bash
docker compose -f docker-compose.gpu.yml up -d universal-gpu-monitor
docker compose -f docker-compose.gpu.yml logs -f universal-gpu-monitor
```

Full Docker details: [README-DOCKER.md](README-DOCKER.md).

---

## Autonomous tuning (experimental)

`gpu_autoresearch.py` runs an **active experiment** instead of relying on fixed
profiles: it sweeps a set of GPU clock caps, holds each for a measurement
window, records the real temperature / utilisation / power (nvidia-smi) and FPS
(RTSS/PresentMon when available), then locks in the most efficient cap for the
current game and remembers it.

```bash
# Quick idle demo of the sweep mechanics (no game needed)
python gpu_autoresearch.py
```

For a real run, call `run_sweep(game, fps_provider=...)` with an FPS source
while the game runs. Notes:

- A temperature guard aborts the sweep, and clocks are always reset (or the
  chosen optimum applied) when it ends.
- Without an FPS signal (no game / no RTSS) it still sweeps and reports the
  thermal data, but picks a cap by a utilisation proxy and flags
  `fps_signal=False` — the meaningful FPS-vs-temperature trade-off only appears
  under real gameplay.

## Configuration

Optional `.env` file:

```bash
GAME_NAME=auto        # or AlanWake2, Cyberpunk2077, ...
TARGET_TEMP=75        # °C
CRITICAL_TEMP=85      # °C emergency cutoff
MONITOR_INTERVAL=1.0  # seconds
```

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
