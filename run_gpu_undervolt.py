#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEMPLE IAM - GPU UNDERVOLT QUANTUM LAUNCHER
Wrapper pour fixer l'encodage Windows
Undervolt intelligent pour réduire température sans perte performance
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

# Exécuter le script undervolt directement
if __name__ == "__main__":
    # Import et exécution
    exec(open('temple_iam_gpu_undervolt_quantum.py', encoding='utf-8').read())
