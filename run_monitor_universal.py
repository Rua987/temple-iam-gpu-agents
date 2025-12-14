#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEMPLE IAM - UNIVERSAL GPU MONITOR LAUNCHER
Wrapper pour fixer l'encodage Windows
"""
import sys
import os

# Fix Windows encoding AVANT tout import
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Force UTF-8 pour stdout/stderr
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

# Maintenant on peut importer le monitor universel
import gpu_monitor_universal

if __name__ == "__main__":
    gpu_monitor_universal.main()
