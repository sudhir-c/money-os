#!/usr/bin/env python3
"""Notification helpers: macOS banner + iMessage-to-self.

iMessage config: ~/.config/money-os/notify.conf with
    IMESSAGE_TO="+15551234567"     # or an Apple ID email
Unconfigured -> texts silently skip; banners still fire.

Usage:
  python tools/notify.py "title" "banner message"
  python tools/notify.py --text "message that goes to your phone"
"""
import subprocess
import sys
from pathlib import Path

CONF = Path.home() / ".config" / "money-os" / "notify.conf"


def _imessage_to() -> str | None:
    if not CONF.exists():
        return None
    for line in CONF.read_text().splitlines():
        line = line.strip()
        if line.startswith("IMESSAGE_TO"):
            _, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            return v or None
    return None


def notify(title: str, message: str) -> None:
    """macOS banner. Best-effort."""
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{message}" with title "{title}" sound name "Submarine"'],
            check=False, capture_output=True, timeout=10)
    except Exception:
        pass


def send_text(message: str) -> bool:
    """iMessage the configured handle (yourself). Returns True on apparent success."""
    to = _imessage_to()
    if not to:
        return False
    # escape for AppleScript string literal
    msg = message.replace("\\", "\\\\").replace('"', '\\"')
    # NB: "buddy" is a reserved Messages class name — never use it as a variable
    script = (
        'tell application "Messages"\n'
        '  set svc to 1st account whose service type = iMessage\n'
        f'  set dest to participant "{to}" of svc\n'
        f'  send "{msg}" to dest\n'
        'end tell'
    )
    try:
        r = subprocess.run(["osascript", "-e", script],
                           check=False, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            notify("money-os", f"text send failed: {r.stderr.strip()[:120]}")
            return False
        return True
    except Exception:
        return False


def alert(title: str, message: str, text: bool = False) -> None:
    """Banner always; text too when asked."""
    notify(title, message)
    if text:
        send_text(f"[{title}] {message}")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--text":
        ok = send_text(" ".join(sys.argv[2:]))
        print("sent" if ok else "NOT sent (notify.conf unconfigured or Messages error)")
    else:
        notify(sys.argv[1] if len(sys.argv) > 1 else "money-os",
               sys.argv[2] if len(sys.argv) > 2 else "")
