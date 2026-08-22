"""
Animated dev-console hero for the profile README. Pure SVG + SMIL (types
line-by-line, blinking cursor) with a LIGHT space touch: a faint starfield and a
small orbiting planet in the corner. No Mars/mission text. Girlie-tech palette.
"""
import html, os, sys, random
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hamna/hero.svg"

# palette
BG="#0b0e1a"; BG2="#141024"; FRAME="#ff5fa2"; PINK="#ff8fc7"; CYAN="#22d3ee"
INK="#e9d8ee"; MUTE="#8b93a7"; GREEN="#5ef2b0"; GOLD="#f2cc60"
W, H = 860, 300
PAD, TITLEBAR = 22, 32
LEFT = PAD + 6
mono = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

# (prompt color, prompt, text color, text)
lines = [
    (CYAN,  "hamna@dev:~$ ", INK,  "whoami"),
    (None,  "", PINK,  "Hamna Qaseem  //  AI Engineer & Researcher"),
    (None,  "", MUTE,  "Data Scientist · Pakistan · learning in public"),
    (CYAN,  "hamna@dev:~$ ", INK,  "./focus --now"),
    (GREEN, "  [ok] ", MUTE, "AI agents & multi-agent systems"),
    (GREEN, "  [ok] ", MUTE, "RAG · LLMs · backend"),
    (GREEN, "  [ok] ", MUTE, "robotics learning · Webots simulation"),
    (GREEN, "  [ok] ", MUTE, "data science · ML · analytics"),
    (GOLD,  "  >> ",   INK,  "status: building & sharing as I go"),
]

LINE_H = 22; CHARW = 8.4
start_y = TITLEBAR + 26
TYPE = 0.9; GAP = 0.35

p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{mono}">']
p.append(f'<defs><linearGradient id="hbg" x1="0" y1="0" x2="1" y2="1">'
         f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
         f'<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
         f'<stop offset="0" stop-color="{PINK}" stop-opacity="0.18"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>'
         f'<radialGradient id="planet" cx="0.35" cy="0.30" r="0.75">'
         f'<stop offset="0" stop-color="{PINK}"/><stop offset="0.6" stop-color="#b23a7a"/><stop offset="1" stop-color="#5a1440"/></radialGradient></defs>')
p.append(f'<rect width="{W}" height="{H}" rx="14" fill="url(#hbg)"/>')

# --- faint starfield (subtle space touch), a few twinkle ---
random.seed(7)
star_layer=['<g>']
for i in range(46):
    x=random.randint(6,W-6); y=random.randint(TITLEBAR+6,H-6)
    r=random.choice([0.6,0.8,1.0,1.0,1.4]); op=random.choice([0.25,0.35,0.5,0.7])
    tw=random.random()<0.30
    if tw:
        dur=random.choice([2.4,3.1,3.8,4.5])
        star_layer.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#cbd5e1" opacity="{op}">'
                          f'<animate attributeName="opacity" values="{op};{op*0.15};{op}" dur="{dur}s" repeatCount="indefinite"/></circle>')
    else:
        star_layer.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#cbd5e1" opacity="{op}"/>')
star_layer.append('</g>')
p.append("".join(star_layer))

p.append(f'<circle cx="{W-110}" cy="{H-30}" r="150" fill="url(#glow)"/>')
p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{FRAME}" stroke-opacity="0.55"/>')
# title bar
p.append(f'<line x1="0" y1="{TITLEBAR}" x2="{W}" y2="{TITLEBAR}" stroke="{FRAME}" stroke-opacity="0.3"/>')
for i,c in enumerate(["#ff5f8f","#ffbd2e","#27c93f"]):
    p.append(f'<circle cx="{PAD+i*16}" cy="{TITLEBAR/2}" r="5" fill="{c}"/>')
p.append(f'<text x="{W/2}" y="{TITLEBAR/2+4}" fill="{MUTE}" font-size="12.5" text-anchor="middle">~/hamna12 — dev console</text>')

# --- small orbiting planet (top-right), pure decoration: subtle space touch ---
cxh, cyh = W-92, TITLEBAR+92
p.append(f'<g transform="translate({cxh},{cyh})">')
# orbit path
p.append(f'<ellipse rx="52" ry="20" fill="none" stroke="{CYAN}" stroke-opacity="0.22" stroke-width="1" transform="rotate(-18)"/>')
# planet body + a ring
p.append(f'<circle r="17" fill="url(#planet)"/>')
p.append(f'<ellipse rx="30" ry="9" fill="none" stroke="{GOLD}" stroke-opacity="0.55" stroke-width="2" transform="rotate(-18)"/>')
p.append(f'<ellipse rx="30" ry="9" fill="none" stroke="{PINK}" stroke-opacity="0.30" stroke-width="4" transform="rotate(-18)"/>')
# highlight
p.append(f'<circle cx="-6" cy="-6" r="4.5" fill="#ffd6ec" opacity="0.6"/>')
# orbiting moon along the tilted orbit
p.append(f'<g transform="rotate(-18)"><g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="7s" repeatCount="indefinite"/>'
         f'<circle cx="52" cy="0" r="3" fill="{CYAN}"/></g></g>')
p.append('</g>')

# --- typed lines ---
t=0.6
for i,(pc,prompt,tc,txt) in enumerate(lines):
    y=start_y+i*LINE_H
    full=prompt+txt; n=max(1,len(full)); dur=TYPE*(n/40+0.3)
    cid=f"ln{i}"; total_w=n*CHARW
    p.append(f'<clipPath id="{cid}"><rect x="{LEFT}" y="{y-14}" height="{LINE_H}" width="0">'
             f'<animate attributeName="width" from="0" to="{total_w:.0f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
    seg=f'<g clip-path="url(#{cid})">'
    if prompt:
        seg+=f'<text x="{LEFT}" y="{y}" font-size="14" fill="{pc}" xml:space="preserve">{html.escape(prompt)}</text>'
    seg+=(f'<text x="{LEFT+len(prompt)*CHARW:.0f}" y="{y}" font-size="14" fill="{tc}" '
          f'font-weight="{700 if i==1 else 400}" xml:space="preserve">{html.escape(txt)}</text></g>')
    p.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s"/>{seg}</g>')
    p.append(f'<rect x="{LEFT}" y="{y-12}" width="8" height="15" fill="{PINK}" opacity="0">'
             f'<set attributeName="opacity" to="0.9" begin="{t:.2f}s"/>'
             f'<animate attributeName="x" from="{LEFT}" to="{LEFT+total_w:.0f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
             f'<set attributeName="opacity" to="0" begin="{t+dur:.2f}s"/></rect>')
    t+=dur+GAP

fy=start_y+len(lines)*LINE_H
p.append(f'<rect x="{LEFT}" y="{fy-12}" width="8" height="15" fill="{PINK}" opacity="0">'
         f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/>'
         f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" begin="{t:.2f}s" repeatCount="indefinite"/></rect>')
p.append("</svg>")
open(OUT,"w").write("".join(p))
print("wrote", OUT, len("".join(p)), "bytes")
