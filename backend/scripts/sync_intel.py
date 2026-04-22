#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.swarm.vuln_intel import run_sync

if __name__ == '__main__':
    force = '--force' in sys.argv
    print('Syncing threat intelligence...')
    run_sync(force=force)
    print('Done.')
