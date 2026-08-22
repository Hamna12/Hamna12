#!/usr/bin/env python3
"""
Scrape a full year of GitHub contribution data for a user WITHOUT auth, by
reading the public contributions calendar HTML. Writes data/contributions.json
(days[], totals, streaks, best day, range) for render_heatmap_svg.py.
"""
import datetime, json, os, sys, re
import requests
from bs4 import BeautifulSoup

USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER", "Hamna12")
HERE = os.path.dirname(__file__)
OUT  = os.path.join(HERE, "..", "data", "contributions.json")

url = f"https://github.com/users/{USER}/contributions"
r = requests.get(url, headers={"User-Agent": "profile-art-bot", "X-Requested-With": "XMLHttpRequest"}, timeout=30)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

days = []
# modern layout: <td data-date="YYYY-MM-DD" data-level="0-4"> with a tooltip count
for td in soup.select("td[data-date]"):
    date = td.get("data-date")
    if not date:
        continue
    # count: from the <tool-tip> text or aria-label, fall back to level*heuristic
    count = 0
    aria = td.get("aria-label") or ""
    m = re.search(r"(\d+)\s+contribution", aria)
    if m:
        count = int(m.group(1))
    else:
        cid = td.get("id")
        if cid:
            tip = soup.find("tool-tip", {"for": cid})
            if tip:
                mm = re.search(r"(\d+)\s+contribution", tip.get_text())
                count = int(mm.group(1)) if mm else 0
    days.append({"date": date, "count": count})

# fallback for the older <rect data-date data-count> SVG layout
if not days:
    for rect in soup.select("rect[data-date]"):
        days.append({"date": rect.get("data-date"),
                     "count": int(rect.get("data-count", 0))})

days = [d for d in days if d["date"]]
days.sort(key=lambda d: d["date"])
if not days:
    raise SystemExit("no contribution data parsed — GitHub markup may have changed")

# --- streaks / totals ---
def streaks(days):
    cur = longest = 0; cur_start = longest_start = longest_end = None
    for d in days:
        if d["count"] > 0:
            if cur == 0: cur_start = d["date"]
            cur += 1
            if cur > longest:
                longest, longest_start, longest_end = cur, cur_start, d["date"]
        else:
            cur = 0
    # current streak = trailing run
    c = 0; cstart = None
    for d in reversed(days):
        if d["count"] > 0:
            c += 1; cstart = d["date"]
        else:
            break
    return ({"length": c, "start": cstart or days[-1]["date"], "end": days[-1]["date"]},
            {"length": longest, "start": longest_start, "end": longest_end})

current, longest = streaks(days)
total = sum(d["count"] for d in days)
best = max(days, key=lambda d: d["count"])

data = {
    "user": USER,
    "days": days,
    "total_contributions": total,
    "current_streak": current,
    "longest_streak": longest,
    "best_day": best,
    "range": {"start": days[0]["date"], "end": days[-1]["date"]},
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z",
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, "w"), indent=2)
print(f"wrote {OUT}: {len(days)} days, {total} contributions, streak {current['length']}")
