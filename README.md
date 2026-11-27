# UserScout

UserScout is a command-line tool for username investigation. Give it a username and it checks, concurrently, whether a profile with that name exists on dozens of public sites, then prints a colored summary and can write an HTML or JSON report.

It is written in pure Python 3 with a single dependency (`requests`).

## Features

- Concurrent checks across 80+ site definitions (45 enabled by default, the rest opt-in)
- Existence detection by HTTP status code, page-content markers, and public JSON APIs where a site offers one
- Calibration mode that re-tests each hit with a random username and drops sites that answer "found" for everything
- Colored terminal summary
- HTML report grouped by category, and JSON output for scripting
- Username format validation per site, so impossible names are skipped instead of reported as missing

## Install

```bash
git clone https://github.com/mohamedhanyegdm-sudo/userscout.git
cd userscout
pip install -r requirements.txt
```

Python 3.8 or newer is required.

## Usage

```bash
python -m userscout <username> [options]
```

| Option | Description |
| --- | --- |
| `--html [FILE]` | Write an HTML report (default `<username>.html`) |
| `--json [FILE]` | Write a JSON report (default `<username>.json`) |
| `--timeout SECONDS` | Per-request timeout, default 10 |
| `--workers N` | Concurrent requests, default 20 |
| `--top N` | Only check the N most popular sites |
| `--category NAME` | Only check one category, repeatable (for example `coding`, `social`, `gaming`) |
| `--calibrate` | Verify hits against a random username to remove false positives |
| `--include-fragile` | Also check sites behind login walls or bot protection (results are unverified) |
| `--all` | List missing, skipped and failed sites too |
| `--no-color` | Disable colors |
| `--list-sites` | Print supported sites |

Examples:

```bash
python -m userscout octocat --html --json
python -m userscout octocat --calibrate --category coding
python -m userscout octocat --top 20 --all
```

The exit code is 0 when at least one profile was found and 1 otherwise.

## Sample output

```
Results for 'octocat'
------------------------------------------------------------
[+] GitHub                     https://github.com/octocat
[+] Telegram                   https://t.me/octocat
[+] TikTok                     https://www.tiktok.com/@octocat
[+] YouTube                    https://www.youtube.com/@octocat
...
------------------------------------------------------------
32 found, 10 not found, 3 errors, 0 skipped (45 sites checked)
```

## How detection works

Each site in `userscout/sites.py` declares one of four methods:

- `status`: HTTP 200 means the profile exists, 404 means it does not
- `absent`: HTTP 200 and a known "user not found" text is missing from the page
- `present`: HTTP 200 and a known profile marker is in the page
- `redirect`: the final URL after redirects still contains the profile path

Some sites use a different URL for the check, such as an official JSON API, which is more stable than scraping HTML. HTTP 401, 403, 429 and 5xx responses are reported as errors, never as "not found", so a blocked request does not hide a real account.

## Limitations

Several large platforms (Instagram, X, Facebook, LinkedIn, Reddit and others) hide profiles behind a login or block scripted requests. They are marked as limited, skipped by default, and any hit from them is labelled unverified. Results can also vary by network location. A match only shows that a page exists at that address, not that it belongs to the person you are investigating. Site layouts change, so definitions may need updating over time.

## Adding a site

Add one line to `userscout/sites.py`:

```python
add("Example", "https://example.com/u/{u}", "social", method="absent", text=["User not found"])
```

Then run `python -m userscout --calibrate somename` to confirm it behaves.

## Responsible use

Use this tool only for lawful purposes such as checking your own online footprint, security research you are authorized to perform, and journalism. Respect each site's terms of service and applicable law.

## License

MIT License. Copyright (c) 2026 Mohamed Hany.
