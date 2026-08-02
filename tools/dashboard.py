#!/usr/bin/env python3
"""Generate a static HTML dashboard: equity curves, positions, journals, sentinel events.

Output: logs/dashboard.html (local file; open it in a browser).
Usage:  python tools/dashboard.py
"""
import html
import json
from datetime import datetime, timezone
from pathlib import Path

from alpaca.trading.client import TradingClient

import stats
from common import REPO

OUT = REPO / "logs" / "dashboard.html"


def svg_curves(curves: dict) -> str:
    if not curves or all(len(c) < 2 for c in curves.values()):
        return "<p>(equity curves appear once a few days of snapshots accumulate)</p>"
    W, H, PAD = 720, 260, 40
    all_pts = [(d, e) for c in curves.values() for d, e in c]
    dates = sorted({d for d, _ in all_pts})
    lo = min(e for _, e in all_pts) * 0.995
    hi = max(e for _, e in all_pts) * 1.005
    colors = {"scholar": "#4c8dd8", "momentum": "#4caf7d", "intuition": "#d88a4c"}
    x = lambda d: PAD + dates.index(d) / max(len(dates) - 1, 1) * (W - 2 * PAD)
    y = lambda e: H - PAD - (e - lo) / (hi - lo) * (H - 2 * PAD)
    parts = [f'<svg viewBox="0 0 {W} {H}" style="max-width:100%;background:#fafafa;border:1px solid #ddd">']
    for gy in (lo, (lo + hi) / 2, hi):
        parts.append(f'<line x1="{PAD}" y1="{y(gy)}" x2="{W - PAD}" y2="{y(gy)}" stroke="#e5e5e5"/>'
                     f'<text x="4" y="{y(gy) + 4}" font-size="10" fill="#888">${gy:,.0f}</text>')
    for agent, curve in curves.items():
        if len(curve) < 2:
            continue
        pts = " ".join(f"{x(d):.1f},{y(e):.1f}" for d, e in curve)
        col = colors.get(agent, "#999")
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2"/>')
        d, e = curve[-1]
        parts.append(f'<text x="{x(d) + 3:.0f}" y="{y(e):.0f}" font-size="11" fill="{col}">{agent}</text>')
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    live = stats.snapshot()
    curves = stats.curves()
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")

    rows = []
    for agent in sorted(curves):
        envf = Path.home() / ".config" / "money-os" / f"{agent}.env"
        e = stats.parse_env(envf) if envf.exists() else {}
        positions_html = "<em>—</em>"
        if e.get("ALPACA_API_KEY"):
            try:
                client = TradingClient(e["ALPACA_API_KEY"], e["ALPACA_SECRET_KEY"], paper=True)
                ps = client.get_all_positions()
                if ps:
                    positions_html = ", ".join(
                        f"{p.symbol} {float(p.qty):g} ({float(p.unrealized_plpc) * 100:+.1f}%)" for p in ps)
                else:
                    positions_html = "all cash"
            except Exception:
                positions_html = "<em>api error</em>"
        curve = curves[agent]
        ret = (live.get(agent, curve[-1][1]) / curve[0][1] - 1) * 100
        # latest journal line
        jf = REPO / "agents" / agent / "journal" / "journal.jsonl"
        latest = ""
        if jf.exists():
            lines = jf.read_text().strip().splitlines()
            if lines:
                d = json.loads(lines[-1])
                acts = ", ".join(f"{x['action']} {x['symbol']}" for x in d.get("decisions", [])[:5])
                latest = f"{d.get('ts', '')[:16]} [{d.get('session', '')}] {html.escape(acts)}"
        rows.append(f"<tr><td><b>{agent}</b></td><td>${live.get(agent, 0):,.2f}</td>"
                    f"<td>{ret:+.2f}%</td><td>{positions_html}</td><td>{latest}</td></tr>")

    events_html = ""
    ev = REPO / "logs" / "sentinel-events.jsonl"
    if ev.exists():
        lines = ev.read_text().strip().splitlines()[-10:]
        for line in reversed(lines):
            r = json.loads(line)
            events_html += f"<li><code>{r.get('ts', '')[:16]}</code> {r.get('type')} — {html.escape(str(r.get('agent', '')))} {html.escape(str(r.get('detail', r.get('session', ''))))}</li>"
    if not events_html:
        events_html = "<li><em>no sentinel events</em></li>"

    OUT.write_text(f"""<!doctype html><meta charset="utf-8">
<title>money-os dashboard</title>
<style>body{{font:14px -apple-system,sans-serif;max-width:860px;margin:2em auto;padding:0 1em;color:#222}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:6px 10px;text-align:left}}
th{{background:#f5f5f5}}h1{{font-size:1.4em}}</style>
<h1>money-os — {now}</h1>
{svg_curves(curves)}
<table><tr><th>agent</th><th>equity</th><th>return</th><th>positions</th><th>latest decision</th></tr>
{''.join(rows)}</table>
<h3>sentinel events (last 10)</h3><ul>{events_html}</ul>
""")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
