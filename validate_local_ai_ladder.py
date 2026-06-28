"""Validation live de l'echelle thermique local_ai (caps sous le clock d'inference).

Reversible : reset garanti en finally. Usage : python validate_local_ai_ladder.py
"""

import io
import logging
import sys
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

logging.disable(logging.INFO)

from gpu_real_controller import GPURealController


def main():
    c = GPURealController()
    print('[SETUP] capacites:', c.capabilities.value)
    try:
        for t in range(8):
            m = c.get_gpu_metrics()
            temp = m.get('temperature', 0)
            clock = m.get('clock_current', 0)
            util = m.get('utilization', 0)
            before = c.current_profile
            applied = c.auto_adjust_for_temperature(temp, thermal_profile='local_ai')
            action = f'{before} -> {applied}' if applied != before else '-'
            print(f't={2*t:>2}s | temp {temp:>3}C | clock {clock:>4} MHz | util {util:>3}% | profil {str(applied):<12} | {action}')
            time.sleep(2)
    finally:
        c.reset_gpu_clocks()
        time.sleep(2)
        m = c.get_gpu_metrics()
        print(f"[RESET] clock {m.get('clock_current', 0)} MHz | temp {m.get('temperature', 0)}C")


if __name__ == '__main__':
    main()
