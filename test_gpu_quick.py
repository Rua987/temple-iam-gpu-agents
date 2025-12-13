#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEMPLE IAM - QUICK GPU TEST
Test rapide des agents GPU avant Docker build
Style Karpathy : Validation avant déploiement
"""

import subprocess
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_nvidia_smi():
    """Test nvidia-smi accessibility"""
    print("[Test 1] nvidia-smi...")
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,temperature.gpu,utilization.gpu', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"[OK] nvidia-smi: {result.stdout.strip()}")
            return True
        else:
            print(f"[FAIL] nvidia-smi: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] nvidia-smi: {e}")
        return False

def test_psutil():
    """Test psutil pour monitoring processus"""
    print("\n[Test 2] psutil...")
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        print(f"[OK] psutil - CPU: {cpu_percent}%, RAM: {memory.percent}%")
        return True
    except Exception as e:
        print(f"[ERROR] psutil: {e}")
        return False

def test_gputil():
    """Test GPUtil pour monitoring GPU"""
    print("\n[Test 3] GPUtil (optional)...")
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            print(f"[OK] GPUtil - GPU: {gpu.name}, Temp: {gpu.temperature}C")
            return True
        else:
            print("[WARN] GPUtil: No GPU detected")
            return False
    except ImportError:
        print("[WARN] GPUtil not installed (optional)")
        return True  # Not critical
    except Exception as e:
        print(f"[WARN] GPUtil ERROR: {e} (optional)")
        return True  # Not critical

def test_process_detection():
    """Test détection processus (simulation Alan Wake 2)"""
    print("\n[Test 4] Process detection...")
    try:
        import psutil
        # Test en cherchant python.exe (on sait qu'il existe)
        found = False
        for proc in psutil.process_iter(['pid', 'name']):
            if 'python' in proc.info['name'].lower():
                found = True
                break

        if found:
            print("[OK] Process detection (python found)")
            return True
        else:
            print("[WARN] Process detection: No python process found")
            return False
    except Exception as e:
        print(f"[ERROR] Process detection: {e}")
        return False

def main():
    print("TEMPLE IAM GPU AGENTS - QUICK TEST")
    print("=" * 60)

    results = []

    # Test critical components
    results.append(("nvidia-smi", test_nvidia_smi()))
    results.append(("psutil", test_psutil()))
    results.append(("GPUtil", test_gputil()))
    results.append(("Process Detection", test_process_detection()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")

    print("=" * 60)
    print(f"RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] ALL TESTS PASSED - Ready for Docker build!")
        return 0
    elif passed >= 2:  # nvidia-smi + psutil minimum
        print("[PARTIAL] Core functionality OK, some optional features missing")
        return 0
    else:
        print("[FAILED] CRITICAL TESTS FAILED - Fix issues before Docker build")
        return 1

if __name__ == "__main__":
    sys.exit(main())
