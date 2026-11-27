import argparse
import re
import sys

from . import __version__
from .core import scan, FOUND
from .report import print_summary, write_html, write_json, use_color, paint
from .sites import S

BANNER = "UserScout %s - username investigation across social platforms" % __version__


def build_parser():
    p = argparse.ArgumentParser(prog="userscout", description=BANNER)
    p.add_argument("username", nargs="?", help="username to look up")
    p.add_argument("--top", type=int, metavar="N", help="only check the N most popular sites")
    p.add_argument("--category", action="append", metavar="NAME", help="only check this category (repeatable)")
    p.add_argument("--html", nargs="?", const="auto", metavar="FILE", help="write an HTML report (default: <username>.html)")
    p.add_argument("--json", nargs="?", const="auto", metavar="FILE", help="write a JSON report (default: <username>.json)")
    p.add_argument("--timeout", type=float, default=10, help="per-request timeout in seconds (default 10)")
    p.add_argument("--workers", type=int, default=20, help="concurrent requests (default 20)")
    p.add_argument("--calibrate", action="store_true", help="re-test hits with a random username and drop sites that report everything as found")
    p.add_argument("--include-fragile", action="store_true", help="also check sites behind login walls or bot protection (results are unverified)")
    p.add_argument("--all", action="store_true", help="also list missing, skipped and failed sites")
    p.add_argument("--no-color", action="store_true", help="disable colored output")
    p.add_argument("--list-sites", action="store_true", help="print the supported sites and exit")
    p.add_argument("--version", action="version", version=BANNER)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.list_sites:
        for s in S:
            tag = "  [limited]" if s["fragile"] else ""
            print(f"{s['rank']:>3}  {s['name']:<28} {s['category']}{tag}")
        return 0
    if not args.username:
        build_parser().print_usage()
        return 2
    user = args.username.strip().lstrip("@")
    if not re.match(r"^[\w.\-]{1,64}$", user):
        print("Invalid username: use letters, digits, dot, dash or underscore only.", file=sys.stderr)
        return 2
    sites = S if args.include_fragile else [s for s in S if not s["fragile"]]
    if args.category:
        wanted = {c.lower() for c in args.category}
        sites = [s for s in sites if s["category"] in wanted]
    if args.top:
        sites = sites[: args.top]
    if not sites:
        print("No sites selected.", file=sys.stderr)
        return 2
    color = use_color(args.no_color)
    print(paint(BANNER, "cyan", color))
    print(f"Checking {len(sites)} sites for '{user}'...")

    def progress(res, done, total):
        if sys.stdout.isatty():
            print(f"\r  {done}/{total}", end="", flush=True)

    results = scan(user, sites, args.workers, args.timeout, args.calibrate, progress)
    if sys.stdout.isatty():
        print("\r" + " " * 20 + "\r", end="")
    print_summary(user, results, args.all, color)
    if args.html:
        path = f"{user}.html" if args.html == "auto" else args.html
        write_html(path, user, results)
        print(f"HTML report: {path}")
    if args.json:
        path = f"{user}.json" if args.json == "auto" else args.json
        write_json(path, user, results)
        print(f"JSON report: {path}")
    return 0 if any(r.status == FOUND for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
