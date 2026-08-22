"""
3D block wordmark ("HAMNA"). The letters are the exact rasterized text mask drawn
as SOLID filled rectangles (run-length merged), so the name is always crisp and
unmistakable. A clean extruded edge behind the face gives depth, and the whole
group gently rocks (SMIL transform). Pure SVG -> animates inline in a README.
Space + girlie-tech palette.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os, sys

TEXT      = os.environ.get("WORDMARK_TEXT", "HAMNA")
FONT_PATH = os.environ.get("WORDMARK_FONT", "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf")
OUT       = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hamna/wordmark.svg"

COLS      = 108        # horizontal resolution of the letters (higher = crisper edges)
TRACKING  = 0.32       # gap between letters (fraction of font size)
CELL      = 7          # px per mask cell
DEPTH     = 6          # extrusion length in cells
DX, DY    = 1.0, 0.9   # per-step extrusion direction (down-right)

# palette
BG="#0b0e1a"; BG2="#141024"; FRAME="#ff5fa2"; TITLE="#8b93a7"
FACE_TOP="#ffc2e0"; FACE="#ff5fa2"; NEAR="#c02e86"; FAR="#5a1440"

# ---- 1. text -> clean binary mask with tracking ----
font = ImageFont.truetype(FONT_PATH, 220)
probe = ImageDraw.Draw(Image.new("L",(10,10)))
bb = probe.textbbox((0,0), TEXT, font=font)
pad = 24
cw = (bb[2]-bb[0]) + pad*2 + int(220*TRACKING)*(len(TEXT)-1)
ch = (bb[3]-bb[1]) + pad*2
img = Image.new("L",(cw,ch),0); d = ImageDraw.Draw(img); x = pad
for c in TEXT:
    cb = d.textbbox((0,0), c, font=font)
    d.text((x-cb[0], pad-bb[1]), c, font=font, fill=255)
    x += (cb[2]-cb[0]) + int(220*TRACKING)
img = img.crop(img.getbbox())
scale = COLS/img.width
mimg = img.resize((COLS, max(1,int(img.height*scale))), Image.LANCZOS)
mask = (np.array(mimg) > 110)
mh, mw = mask.shape

# ---- 2. run-length merge each row into (x0,x1) spans -> few rects ----
def row_spans(m):
    spans=[]
    for r in range(m.shape[0]):
        row=m[r]; c=0
        while c < len(row):
            if row[c]:
                s=c
                while c<len(row) and row[c]: c+=1
                spans.append((r,s,c))   # row, x_start, x_end(excl)
            else:
                c+=1
    return spans
spans = row_spans(mask)

# ---- 3. build SVG ----
PADX=26; PADY=16; TITLEBAR=30
ext_x = DEPTH*DX; ext_y = DEPTH*DY
art_w = (mw+ext_x+2)*CELL
art_h = (mh+ext_y+2)*CELL
W = int(art_w + PADX*2)
H = int(TITLEBAR + art_h + PADY)
ox0 = PADX; oy0 = TITLEBAR + PADY*0.4

def rects_for(spans, dx, dy, fill, op=1.0):
    out=[]
    for (r,s,e) in spans:
        x = ox0 + (s+dx)*CELL
        y = oy0 + (r+dy)*CELL
        w = (e-s)*CELL + 0.6   # tiny overlap kills seams
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{CELL+0.6:.1f}" fill="{fill}"'
                   + (f' opacity="{op}"' if op<1 else '') + '/>')
    return "".join(out)

p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
   f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">']
p.append(f'<defs><linearGradient id="wbg" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
         f'<linearGradient id="face" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{FACE_TOP}"/><stop offset="1" stop-color="{FACE}"/></linearGradient></defs>')
p.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#wbg)"/>')
p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-opacity="0.5"/>')
p.append(f'<line x1="0" y1="{TITLEBAR}" x2="{W}" y2="{TITLEBAR}" stroke="{FRAME}" stroke-opacity="0.3"/>')
for i,c in enumerate(["#ff5f8f","#ffbd2e","#27c93f"]):
    p.append(f'<circle cx="{26+i*16}" cy="{TITLEBAR/2}" r="5" fill="{c}"/>')
p.append(f'<text x="{W/2}" y="{TITLEBAR/2+4}" fill="{TITLE}" font-size="12" text-anchor="middle">hamna@dev: ~ $ ./wordmark.sh --3d</text>')

# reveal wipe on first play
p.append(f'<clipPath id="wipe"><rect x="{PADX}" y="{TITLEBAR}" height="{art_h}" width="0">'
         f'<animate attributeName="width" from="0" to="{art_w}" begin="0s" dur="1.2s" fill="freeze"/></rect></clipPath>')

# group that gently rocks (scaleX turn + tiny skew) about its own center
cx = W/2; cy = TITLEBAR + art_h/2
p.append(f'<g clip-path="url(#wipe)"><g transform="translate({cx:.1f},{cy:.1f})">'
         f'<animateTransform attributeName="transform" type="scale" additive="sum" '
         f'values="1 1;0.965 1;1 1;0.965 1;1 1" keyTimes="0;0.25;0.5;0.75;1" dur="7s" begin="1.2s" repeatCount="indefinite"/>'
         f'<animateTransform attributeName="transform" type="skewX" additive="sum" '
         f'values="0;-2.2;0;2.2;0" keyTimes="0;0.25;0.5;0.75;1" dur="7s" begin="1.2s" repeatCount="indefinite"/>'
         f'<g transform="translate({-cx:.1f},{-cy:.1f})">')

# extrusion: far -> near (draw behind, near on top of far)
for step in range(DEPTH, 0, -1):
    f = step/DEPTH
    # color lerp FAR->NEAR
    def lerp(a,b,t):
        a=[int(a[i:i+2],16) for i in (1,3,5)]; b=[int(b[i:i+2],16) for i in (1,3,5)]
        return "#%02x%02x%02x"%tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
    col = lerp(FAR, NEAR, 1-f)
    p.append(rects_for(spans, step*DX, step*DY, col))
# face on top
p.append(rects_for(spans, 0, 0, "url(#face)"))

p.append('</g></g></g>')
p.append("</svg>")
open(OUT,"w").write("".join(p))
print("wrote", OUT, len("".join(p)), "bytes;", W,"x",H,"; rects:", len(spans)*(DEPTH+1))
