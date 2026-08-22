#!/usr/bin/env python3
"""
Render two self-contained SVG cards (no external services) themed to match the
profile: data/github_stats.json -> stats-card.svg, data/languages.json -> langs-card.svg
"""
import json, os
HERE=os.path.dirname(__file__); D=os.path.join(HERE,"..","data")
BG="#0b0e1a"; BG2="#141024"; FRAME="#ff5fa2"; TITLE="#8b93a7"
PINK="#ff5fa2"; PINKB="#ff9ecb"; CYAN="#22d3ee"; GOLD="#f2cc60"; INK="#e9d8ee"; MUTE="#8b93a7"
mono="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

def frame(W,H,title):
    s=[f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
       f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
       f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
       f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-opacity="0.5"/>',
       f'<line x1="0" y1="30" x2="{W}" y2="30" stroke="{FRAME}" stroke-opacity="0.3"/>']
    for i,c in enumerate(["#ff5f8f","#ffbd2e","#27c93f"]):
        s.append(f'<circle cx="{18+i*15}" cy="15" r="4.5" fill="{c}"/>')
    s.append(f'<text x="{W/2}" y="19" fill="{TITLE}" font-size="11.5" text-anchor="middle" font-family="{mono}">{title}</text>')
    return s

def stats_card():
    d=json.load(open(os.path.join(D,"github_stats.json")))
    W,H=430,220
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{mono}">']
    s+=frame(W,H,"hamna@github: ~ $ ./stats.sh")
    s.append(f'<text x="24" y="60" fill="{PINKB}" font-size="15" font-weight="700">Hamna\u2019s GitHub, at a glance</text>')
    rows=[("Contributions (last year)", f'{d["total_contributions"]:,}', CYAN)]
    if d.get("stars",0)>0: rows.append(("Stars earned", f'{d["stars"]:,}', GOLD))
    rows += [
          ("Public repositories", f'{d["repos"]:,}', GOLD),
          ("Followers", f'{d["followers"]:,}', PINK),
          ("Following", f'{d["following"]:,}', PINK),
          ("Longest streak", f'{d["longest_streak"]} days', CYAN)]
    y=90
    for label,val,col in rows:
        s.append(f'<text x="24" y="{y}" fill="{MUTE}" font-size="13">{label}</text>')
        s.append(f'<text x="{W-24}" y="{y}" fill="{col}" font-size="15" font-weight="700" text-anchor="end">{val}</text>')
        s.append(f'<line x1="24" y1="{y+9}" x2="{W-24}" y2="{y+9}" stroke="{FRAME}" stroke-opacity="0.12"/>')
        y+=25
    s.append("</svg>")
    open(os.path.join(HERE,"..","stats-card.svg"),"w").write("".join(s))

LANG_COLORS={"Python":"#3572A5","Jupyter Notebook":"#DA5B0B","HTML":"#e34c26",
 "JavaScript":"#f1e05a","CSS":"#563d7c","C++":"#f34b7d","TeX":"#3D6117","C":"#555555",
 "TypeScript":"#3178c6","Java":"#b07219","Shell":"#89e051","Dart":"#00B4AB"}

def langs_card():
    d=json.load(open(os.path.join(D,"languages.json")))
    items=sorted(d.items(), key=lambda kv: -kv[1])
    top=items[:6]; total=sum(v for _,v in items) or 1
    W,H=430,220
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{mono}">']
    s+=frame(W,H,"hamna@github: ~ $ ./languages.sh")
    s.append(f'<text x="24" y="60" fill="{PINKB}" font-size="15" font-weight="700">Most used languages</text>')
    # stacked bar
    bx,by,bw,bh=24,74,W-48,16; x=bx
    for name,val in top:
        w=bw*val/total; col=LANG_COLORS.get(name,"#8b93a7")
        s.append(f'<rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="{bh}" fill="{col}"/>')
        x+=w
    s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="4" fill="none" stroke="{FRAME}" stroke-opacity="0.25"/>')
    # legend two columns
    y=115; col_x=[24, 24+ (W-48)//2]
    for i,(name,val) in enumerate(top):
        cx=col_x[i%2]; row=i//2
        yy=y+row*26
        c=LANG_COLORS.get(name,"#8b93a7"); pct=100*val/total
        s.append(f'<circle cx="{cx+5}" cy="{yy-4}" r="5" fill="{c}"/>')
        s.append(f'<text x="{cx+16}" y="{yy}" fill="{INK}" font-size="12.5">{name}</text>')
        s.append(f'<text x="{cx+(W-48)//2-8}" y="{yy}" fill="{MUTE}" font-size="12" text-anchor="end">{pct:.1f}%</text>')
    s.append("</svg>")
    open(os.path.join(HERE,"..","langs-card.svg"),"w").write("".join(s))

if __name__=="__main__":
    stats_card(); langs_card(); print("wrote stats-card.svg and langs-card.svg")
