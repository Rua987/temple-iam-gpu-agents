# Cleanup Plan: Keep Essential, Remove Marketing Noise

## Keep (Core Functionality)

### Documentation
- `README.md` — Main project docs (updated with 3 features)
- `README-DOCKER.md` — Docker setup
- `INT4_VALIDATION.md` — Quantization validation results
- `CHANGELOG.md` — Version history

### Python Core (GPU Monitoring & Optimization)
- `universal_gpu_monitor.py` — Main monitor with auto-tuning
- `gpu_autoresearch.py` — Auto-tuning algorithm
- `gpu_benchmark.py` — Synthetic GPU benchmark (no game needed)
- `fps_monitor.py` — Real FPS via RTSS
- `rtss_reader.py` — RTSS shared memory reader
- `bench_ollama_multi.py` — Multi-model LLM benchmarking
- `test_quantization_demo.py` — INT4 theoretical demo

### Optional Utilities
- `afterburner_profile_controller.py` — MSI Afterburner control (keep if useful)

### Config & Infrastructure
- `.gitignore`
- `LICENSE`
- `.github/` (CI/CD if present)
- `docker-compose.gpu.yml` — Docker compose

## Delete (Marketing Noise & Experiments)

### Directories to Remove
- `agents/beachpatrol_web/` — **Entire directory** (~1000s of files)
  - Guides, marketing docs, video farming experiments
  - Node modules, dependencies
  - Not related to GPU optimization

- `tools/` — Check if empty or unrelated

### Files to Remove
- `afterburner_profile_controller.py` — If unused
- Any `test_*.py` files that aren't core to the project
- `.pytest_cache/` — Build artifacts

## Action Items

1. Delete `agents/beachpatrol_web/` recursively
2. Review and delete unrelated files
3. Keep only the 7 core Python files + docs
4. Final size should be ~100 KB vs current 100+ MB

## Result

Focused, clean repo with:
- 1 main README with clear examples
- 7 production Python modules
- 2 integration demo scripts
- Docker support
- Clear use cases: gaming FPS tuning + LLM inference optimization
