#!/usr/bin/env python3
"""macOS notification helper. Usage: python tools/notify.py "title" "message" """
import subprocess
import sys


def notify(title: str, message: str) -> None:
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{message}" with title "{title}" sound name "Submarine"'],
            check=False, capture_output=True, timeout=10)
    except Exception:
        pass  # notifications are best-effort


if __name__ == "__main__":
    notify(sys.argv[1] if len(sys.argv) > 1 else "money-os",
           sys.argv[2] if len(sys.argv) > 2 else "")
