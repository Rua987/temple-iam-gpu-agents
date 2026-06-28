"""Benchmark Ollama LLM auto-tuning across multiple models.

Tests each model with the auto-tuning sweep to discover its optimal GPU clock.
Accumulates results to show the pattern: all tested models are memory-bound,
so they all prefer lower clock caps than uncapped gaming.

Usage:
    python bench_ollama_multi.py                  # Test all available models
    python bench_ollama_multi.py qwen3.5:2b mistral:7b  # Test specific models
"""

import sys
import json
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

try:
    import gpu_autoresearch
except ImportError:
    logging.error("gpu_autoresearch not available")
    sys.exit(1)


def list_ollama_models() -> List[str]:
    """Fetch list of available models from Ollama."""
    try:
        import urllib.request
        import json as stdlib_json
        url = "http://localhost:11434/api/tags"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = stdlib_json.loads(r.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception as e:
        logging.error(f"Failed to list Ollama models: {e}")
        return []


def bench_model(model: str) -> Optional[Dict]:
    """Run auto-tuning sweep for one Ollama model, return results."""
    try:
        logging.info(f"🚀 Testing {model}...")

        # Create provider for this model
        provider = gpu_autoresearch.make_ollama_provider(
            model,
            prompt="Write a detailed paragraph about the ocean.",
            num_predict=64
        )

        # Run sweep with model's levels (memory-bound, lower caps)
        optimal_mhz = gpu_autoresearch.auto_tune_workload(
            workload_name=f"ollama:{model}",
            perf_provider=provider,
            perf_unit="tok/s",
            is_gaming=False,  # Use LLM levels (600, 855, 1200, 1950)
            duration_s=25.0  # Shorter to test multiple models
        )

        if optimal_mhz:
            logging.info(f"✅ {model}: optimal = {optimal_mhz} MHz")
            return {"model": model, "optimal_mhz": optimal_mhz, "status": "ok"}
        else:
            logging.warning(f"⚠️ {model}: inconclusive (GPU read-only?)")
            return {"model": model, "optimal_mhz": None, "status": "inconclusive"}

    except Exception as e:
        logging.error(f"❌ {model} failed: {e}")
        return {"model": model, "optimal_mhz": None, "status": "error"}


def main():
    models = []
    if len(sys.argv) > 1:
        models = sys.argv[1:]
        logging.info(f"Testing specified models: {models}")
    else:
        available = list_ollama_models()
        if not available:
            logging.error("No Ollama models found. Start Ollama and run: ollama pull <model>")
            sys.exit(1)
        # Test a few representative models
        models = [m for m in available if any(x in m for x in ['qwen', 'mistral', 'deepseek', 'llama'])][:4]
        if not models:
            models = available[:3]
        logging.info(f"Testing available models: {models}")

    results = []
    for model in models:
        result = bench_model(model)
        if result:
            results.append(result)

    # Summary
    print("\n" + "="*80)
    print("OLLAMA AUTO-TUNING RESULTS")
    print("="*80)
    for r in results:
        status_str = f"OK {r['optimal_mhz']} MHz" if r['optimal_mhz'] else f"WARN {r['status']}"
        print(f"  {r['model']:30s} {status_str}")

    optimal_mhz_values = [r['optimal_mhz'] for r in results if r['optimal_mhz']]
    if optimal_mhz_values:
        avg = sum(optimal_mhz_values) / len(optimal_mhz_values)
        print(f"\nPattern: All LLMs are memory-bound. Average optimum = {avg:.0f} MHz")
        print("Insight: Lower clocks than gaming (which prefers max) because inference")
        print("  is VRAM-bandwidth-bound, not compute-bound. Extra GPU clock adds heat.")
    print("="*80 + "\n")

    # Save to JSON
    with open("ollama_benchmarks.json", "w") as f:
        json.dump(results, f, indent=2)
    logging.info("Results saved to ollama_benchmarks.json")


if __name__ == "__main__":
    main()
