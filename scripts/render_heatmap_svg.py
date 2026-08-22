#!/usr/bin/env python3
"""
Render data/contributions.json as a GitHub-style contribution heatmap SVG in a
space/girlie-tech PINK ramp: rounded boxes in the 53-week x 7-day calendar,
revealed once with a diagonal top-left -> bottom-right cascade (CSS keyframes,
plays on load then freezes), a Less->More legend, and a real stats footer.
"""
import datetime, json, os
HERE = os.path.dirname(__file__)
IN_PATH  = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

# empty -> brightest, magenta/pink ramp with a neon top
PALETTE = ["#161225", "#3d1130", "#7a1e57", "#c02e86", "#ff5fa2", "#ff9ecb"]

CELL, GAP = 12, 3
STEP = CELL + GAP
PAD = 22; LEFT_LABEL_W = 30; TOP_LABEL_H = 20; TITLEBAR_H = 30
BG="#0a0a14"; BG2="#12101f"; FRAME="#ff5fa2"; MUTED="#8b93a7"
TEXT="#e9d8ee"; ACCENT="#22d3ee"; PINK="#ff5fa2"; GOLD="#f2cc60"
COL_T, ROW_T, CELL_DUR = 0.016, 0.045, 0.42

def level_for(c):
    if c==0: return 0
    if c<=2: return 1
    if c<=5: return 2
    if c<=10: return 3
    if c<=20: return 4
    return 5

def build_grid(days):
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday()+1)%7
    grid=[]; col=[None]*lead
    for d in days:
        wd=(datetime.date.fromisoformat(d["date"]).weekday()+1)%7
        while len(col)<wd: col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"])))
        if len(col)==7: grid.append(col); col=[]
    if col:
        while len(col)<7: col.append(None)
        grid.append(col)
    return grid

def render(data):
    days=data["days"]; grid=build_grid(days); ncol=len(grid)
    art_w=ncol*STEP; art_h=7*STEP
    months=[]; seen=set()
    for ci,column in enumerate(grid):
        for cell in column:
            if cell is None: continue
            dt=datetime.date.fromisoformat(cell[0]); k=(dt.year,dt.month)
            if k not in seen and dt.day<=7:
                seen.add(k); months.append((ci,dt.strftime("%b")))
            break
    canvas_w=PAD+LEFT_LABEL_W+art_w+PAD
    stats_h=88; canvas_h=TITLEBAR_H+TOP_LABEL_H+art_h+stats_h+PAD
    css=f"@keyframes cell{{0%{{opacity:0;transform:translateY(-6px)}}100%{{opacity:1;transform:translateY(0)}}}}.c{{opacity:0;animation:cell {CELL_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both}}"
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
       f'<style>{css}</style>',
       f'<defs><linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
       f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#hbg)"/>',
       f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{FRAME}" stroke-opacity="0.5"/>',
       f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.3"/>']
    for i,c in enumerate(["#ff5f8f","#ffbd2e","#27c93f"]):
        p.append(f'<circle cx="{PAD+i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{c}"/>')
    p.append(f'<text x="{canvas_w/2}" y="{TITLEBAR_H/2+4}" fill="{MUTED}" font-size="12" text-anchor="middle">hamna@github: ~/contributions --graph</text>')
    gtop=TITLEBAR_H+TOP_LABEL_H; gleft=PAD+LEFT_LABEL_W
    for ci,lab in months:
        p.append(f'<text x="{gleft+ci*STEP}" y="{TITLEBAR_H+14}" fill="{MUTED}" font-size="10">{lab}</text>')
    for wi,wn in [(1,"Mon"),(3,"Wed"),(5,"Fri")]:
        y=gtop+wi*STEP+CELL*0.78
        p.append(f'<text x="{PAD}" y="{y:.1f}" fill="{MUTED}" font-size="9">{wn}</text>')
    for ci,column in enumerate(grid):
        gx=gleft+ci*STEP
        for ri,cell in enumerate(column):
            if cell is None: continue
            ds,cnt,lvl=cell; gy=gtop+ri*STEP; delay=ci*COL_T+ri*ROW_T
            pl="s" if cnt!=1 else ""
            p.append(f'<rect class="c" x="{gx}" y="{gy}" width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s"><title>{ds}: {cnt} contribution{pl}</title></rect>')
    leg_y=gtop+art_h+6; leg_x=canvas_w-PAD-(len(PALETTE)*(CELL-1)+70)
    p.append(f'<text x="{leg_x}" y="{leg_y+CELL*0.8:.1f}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>')
    lx=leg_x+8
    for col in PALETTE:
        p.append(f'<rect x="{lx}" y="{leg_y}" width="{CELL-1}" height="{CELL-1}" rx="2.2" fill="{col}"/>'); lx+=CELL
    p.append(f'<text x="{lx+4}" y="{leg_y+CELL*0.8:.1f}" fill="{MUTED}" font-size="10">More</text>')
    sep=leg_y+CELL+14
    p.append(f'<line x1="0" y1="{sep}" x2="{canvas_w}" y2="{sep}" stroke="{FRAME}" stroke-opacity="0.2"/>')
    cs=data["current_streak"]["length"]; ls=data["longest_streak"]["length"]
    total=data["total_contributions"]; best=data["best_day"]; rng=data["range"]
    ly=sep+24
    p.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{PINK}"><tspan font-weight="700">{total:,}</tspan><tspan fill="{MUTED}"> contributions in the last year</tspan></text>')
    p.append(f'<text x="{canvas_w-PAD}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">{rng["start"]} &#8594; {rng["end"]}</text>')
    ly+=24
    p.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{MUTED}">current streak <tspan fill="{ACCENT}" font-weight="700">{cs} days</tspan><tspan fill="{MUTED}">   &#183;   longest </tspan><tspan fill="{ACCENT}" font-weight="700">{ls} days</tspan></text>')
    p.append(f'<text x="{canvas_w-PAD}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">best day <tspan fill="{GOLD}" font-weight="700">{best["count"]}</tspan> on {datetime.date.fromisoformat(best["date"]).strftime("%b %-d")}</text>')
    p.append("</svg>")
    return "".join(p)

if __name__=="__main__":
    data=json.load(open(IN_PATH))
    open(OUT_PATH,"w").write(render(data))
    print("wrote", OUT_PATH)
