"""Core engine: sends the requests and decides whether an account exists."""

import random
import re
import string
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict

import requests

from .sites import S

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

FOUND, NOT_FOUND, ERROR, SKIPPED = "found", "not_found", "error", "skipped"


@dataclass
class Result:
    site: str
    category: str
    url: str
    status: str
    http_code: int = 0
    elapsed: float = 0.0
    note: str = ""

    def to_dict(self):
        return asdict(self)


def random_name(n=14):
    return "zq" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def _decide(site, username, resp):
    """Turn an HTTP response into FOUND / NOT_FOUND."""
    code, body = resp.status_code, resp.text or ""
    method = site["method"]
    markers = site["text"] or []
    if isinstance(markers, str):
        markers = [markers]
    markers = [m.replace("{u}", username) for m in markers]
    low = body.lower()

    if code in (404, 410):
        return NOT_FOUND, ""
    if code in (401, 403, 429, 999) or code >= 500:
        return ERROR, f"blocked or unavailable (HTTP {code})"
    if code != 200:
        return ERROR, f"unexpected HTTP {code}"
    if method == "status":
        return FOUND, ""
    if method == "absent":
        hit = any(m.lower() in low for m in markers)
        return (NOT_FOUND, "") if hit else (FOUND, "")
    if method == "present":
        hit = any(m.lower() in low for m in markers)
        return (FOUND, "") if hit else (NOT_FOUND, "")
    if method == "redirect":
        return (FOUND, "") if site["final"] in resp.url else (NOT_FOUND, "")
    return ERROR, "unknown method"


def check_site(site, username, session, timeout=10, retries=1):
    url = site["url"].format(u=username)
    if site["regex"] and not re.match(site["regex"], username):
        return Result(site["name"], site["category"], url, SKIPPED, note="username format not valid for this site")
    target = (site["check_url"] or site["url"]).format(u=username)
    headers = {"User-Agent": random.choice(USER_AGENTS), "Accept-Language": "en-US,en;q=0.9"}
    last_err = ""
    for attempt in range(retries + 1):
        start = time.time()
        try:
            resp = session.get(target, headers=headers, timeout=timeout, allow_redirects=True)
            status, note = _decide(site, username, resp)
            if status == FOUND and site.get("fragile"):
                note = "unverified: this site often gives misleading answers to scripts"
            return Result(site["name"], site["category"], url, status, resp.status_code, round(time.time() - start, 2), note)
        except requests.exceptions.Timeout:
            last_err = "timeout"
        except requests.exceptions.RequestException as exc:
            last_err = type(exc).__name__
    return Result(site["name"], site["category"], url, ERROR, 0, 0.0, last_err)


def scan(username, sites=None, workers=20, timeout=10, calibrate=False, progress=None):
    """Check `username` on every site concurrently. Returns a list of Result.

    With calibrate=True each site is also probed with a random username that
    cannot exist; a site that reports it as found is marked unreliable.
    """
    sites = sites if sites is not None else S
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=workers, pool_maxsize=workers)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    results = []

    def job(site):
        res = check_site(site, username, session, timeout)
        if calibrate and res.status == FOUND:
            probe = check_site(site, random_name(), session, timeout)
            if probe.status == FOUND:
                res.status = ERROR
                res.note = "unreliable: site reports random usernames as existing"
        return res

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(job, s): s for s in sites}
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            if progress:
                progress(res, len(results), len(sites))
    order = {s["name"]: s["rank"] for s in sites}
    results.sort(key=lambda r: order.get(r.site, 9999))
    return results
