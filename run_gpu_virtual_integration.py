#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEMPLE IAM - GPU VIRTUAL INTEGRATION LAUNCHER
Wrapper pour fixer l'encodage Windows
Lance Alan Wake 2 avec optimisations GPU
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

# Importer le GPU virtual integration
import temple_iam_alan_wake2_gpu_virtual_integration

if __name__ == "__main__":
    temple_iam_alan_wake2_gpu_virtual_integration.main()
