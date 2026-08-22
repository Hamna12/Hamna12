#!/usr/bin/env python3
"""
Collect accurate GitHub stats for the profile cards. Uses GITHUB_TOKEN when present
(the Action provides it) to avoid rate limits and to sum real language bytes.
Writes data/github_stats.json and data/languages.json.
Pulls total_contributions + longest_streak from data/contributions.json if present.
"""
import json, os, sys, urllib.request
from collections import Counter

USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER","Hamna12")
TOKEN = os.environ.get("GITHUB_TOKEN","")
HERE = os.path.dirname(__file__); D = os.path.join(HERE,"..","data")

def gh(url):
    req=urllib.request.Request(url, headers={
        "User-Agent":"profile-bot","Accept":"application/vnd.github+json",
        **({"Authorization":f"Bearer {TOKEN}"} if TOKEN else {})})
    return json.load(urllib.request.urlopen(req, timeout=45))

u = gh(f"https://api.github.com/users/{USER}")
repos=[]; page=1
while True:
    b = gh(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner")
    repos += b
    if len(b) < 100: break
    page += 1

stars = sum(r["stargazers_count"] for r in repos)

langs = Counter()
for r in repos:
    if r.get("fork"): continue
    try:
        for lang, byts in gh(r["languages_url"]).items():
            langs[lang] += byts
    except Exception as e:
        print("lang skip", r["name"], e)

# contributions + streak from the contributions scrape (if available)
total_contrib = longest = 0
cpath = os.path.join(D,"contributions.json")
if os.path.exists(cpath):
    c = json.load(open(cpath))
    total_contrib = c.get("total_contributions",0)
    longest = c.get("longest_streak",{}).get("length",0)

stats = {"user":USER, "repos":u["public_repos"], "followers":u["followers"],
         "following":u["following"], "stars":stars,
         "total_contributions":total_contrib, "longest_streak":longest}
os.makedirs(D, exist_ok=True)
json.dump(stats, open(os.path.join(D,"github_stats.json"),"w"), indent=2)
json.dump(dict(langs), open(os.path.join(D,"languages.json"),"w"), indent=2)
print("stats:", stats)
print("languages:", dict(langs.most_common(8)))
