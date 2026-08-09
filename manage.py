#!/usr/bin/env python
"""
Lightweight manage.py at repository root to forward commands to the inner
Django project `matoleo_system` so `python manage.py <cmd>` works from repo root.
"""
import os
import sys
from pathlib import Path


def main():
    # Ensure the inner project package is importable when running from repo root.
    repo_root = Path(__file__).resolve().parent
    inner_project = repo_root / "matoleo_system"
    # Add inner project directory to sys.path so `matoleo_system` (the inner package)
    # becomes importable as a top-level package.
    sys.path.insert(0, str(inner_project))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "matoleo_system.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        raise
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
