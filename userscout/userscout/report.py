"""Terminal and HTML output."""

import html
import json
import sys
from datetime import datetime

from .core import FOUND, NOT_FOUND, ERROR, SKIPPED

_COLORS = {"green": "32", "red": "31", "yellow": "33", "cyan": "36", "grey": "90", "bold": "1"}


def paint(text, color, enabled=True):
    if not enabled:
        return text
    return f"\033[{_COLORS[color]}m{text}\033[0m"


def use_color(flag):
    return sys.stdout.isatty() and not flag


def print_summary(username, results, show_all=False, color=True):
    found = [r for r in results if r.status == FOUND]
    missing = [r for r in results if r.status == NOT_FOUND]
    errors = [r for r in results if r.status == ERROR]
    skipped = [r for r in results if r.status == SKIPPED]
    print()
    print(paint(f"Results for '{username}'", "bold", color))
    print("-" * 60)
    for r in found:
        flag = paint("  (unverified)", "yellow", color) if r.note.startswith("unverified") else ""
        print(f"{paint('[+]', 'green', color)} {r.site:<26} {r.url}{flag}")
    if show_all:
        for r in missing:
            print(f"{paint('[-]', 'grey', color)} {paint(r.site, 'grey', color)}")
        for r in skipped:
            print(f"{paint('[~]', 'grey', color)} {paint(r.site + ' (skipped: ' + r.note + ')', 'grey', color)}")
    for r in errors:
        if show_all:
            print(f"{paint('[!]', 'yellow', color)} {r.site:<26} {r.note}")
    print("-" * 60)
    print(
        f"{paint(str(len(found)), 'green', color)} found, {len(missing)} not found, "
        f"{paint(str(len(errors)), 'yellow', color)} errors, {len(skipped)} skipped "
        f"({len(results)} sites checked)"
    )
    if errors and not show_all:
        print(paint("Use --all to see which sites were blocked or timed out.", "grey", color))


def write_json(path, username, results):
    data = {
        "username": username,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "results": [r.to_dict() for r in results],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def write_html(path, username, results):
    found = [r for r in results if r.status == FOUND]
    cats = {}
    for r in found:
        cats.setdefault(r.category, []).append(r)
    rows = []
    for cat in sorted(cats):
        rows.append(f"<h2>{html.escape(cat.title())} <span>{len(cats[cat])}</span></h2><ul>")
        for r in cats[cat]:
            u = html.escape(r.url, quote=True)
            rows.append(f'<li><a href="{u}" target="_blank" rel="noopener noreferrer">{html.escape(r.site)}</a><small>{u}</small></li>')
        rows.append("</ul>")
    body = "\n".join(rows) or "<p>No profiles found.</p>"
    errors = sum(1 for r in results if r.status == ERROR)
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>UserScout report: {html.escape(username)}</title>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;background:#0f1419;color:#e6e6e6;margin:0;padding:2rem}}
main{{max-width:820px;margin:auto}}
h1{{margin-bottom:.2rem}} .meta{{color:#8b98a5;margin-bottom:2rem}}
h2{{border-bottom:1px solid #2a3340;padding-bottom:.3rem;margin-top:2rem;font-size:1.1rem}}
h2 span{{background:#1d9bf0;color:#fff;border-radius:10px;padding:0 .5rem;font-size:.8rem;margin-left:.4rem}}
ul{{list-style:none;padding:0}} li{{padding:.5rem 0;border-bottom:1px solid #1b222b}}
a{{color:#4cc2ff;font-weight:600;text-decoration:none}} a:hover{{text-decoration:underline}}
small{{display:block;color:#8b98a5;word-break:break-all}}
</style></head><body><main>
<h1>Username: {html.escape(username)}</h1>
<div class="meta">{len(found)} profiles found across {len(results)} sites checked
({errors} errors). Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}.
A match means a page exists at that address, not that it belongs to the same person.</div>
{body}
</main></body></html>"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
