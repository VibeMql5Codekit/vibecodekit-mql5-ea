#!/usr/bin/env python3
"""Compatibility wrapper for the package-based RRI CLI."""
from __future__ import annotations

import sys

from vibecodekit_mql5.rri.cli import main


if __name__ == "__main__":
    sys.exit(main())
