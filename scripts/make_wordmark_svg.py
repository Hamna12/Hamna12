"""
Build a 3D ASCII wordmark ("HAMNA") that wipes in left->right then gently rocks
on its vertical axis. Pure SVG + SMIL flipbook (no JS) so it animates inline in
a GitHub README <img>. Space + girlie-in-tech palette.

Technique: rasterize bold text -> binary mask -> extrude to a surface point
cloud (front/back caps + side walls with normals) -> for each frame rotate,
back-face cull, perspective divide, Lambert shade + depth fog, z-buffer splat
into a char grid -> emit every frame as SVG text, cycled by discrete opacity.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import html, os, sys

TEXT       = os.environ.get("WORDMARK_TEXT", "HAMNA")
FONT_PATH  = os.environ.get("WORDMARK_FONT", "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf")
OUT        = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hamna/wordmark.svg"

COLS       = 72
ROW_MARGIN = 4
DEPTH_FRAC = 0.16     # extrusion depth as fraction of mask width
TRACKING   = 0.22     # extra gap between letters
CAM_DIST   = 6.0
TILT_DEG   = 4.0
SWING_DEG  = 12.0
N_FRAMES   = 22
LIGHT      = np.array([-0.15, -0.42, -1.0]); LIGHT = LIGHT/np.linalg.norm(LIGHT)

RAMP = " .`:-=+*csS#%@"        # sparse/dim -> dense/bright
CELL_W, CELL_H = 9, 9

# --- palette (deep space + magenta/cyan) ---
BG   = "#0b0e1a"
BG2  = "#141024"
FRAME= "#ff5fa2"
INK  = "#ffd6ec"     # letter faces glow pink-white
TITLE= "#8b93a7"

# ---- 1. text -> binary mask ------------------------------------------------
font = ImageFont.truetype(FONT_PATH, 220)
tmp  = Image.new("L", (10, 10))
d    = ImageDraw.Draw(tmp)
# add tracking by drawing letters spaced out
spaced = (" " * 0).join(list(TEXT))
bbox = d.textbbox((0, 0), TEXT, font=font)
tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
pad = 40
img = Image.new("L", (tw + pad*2 + int(tw*TRACKING), th + pad*2), 0)
d   = ImageDraw.Draw(img)
# draw each glyph with tracking
x = pad
for ch in TEXT:
    cb = d.textbbox((0,0), ch, font=font)
    d.text((x - cb[0], pad - bbox[1]), ch, font=font, fill=255)
    x += (cb[2]-cb[0]) + int(220*TRACKING)
img = img.crop(img.getbbox())
mask = (np.array(img) > 128)
mh, mw = mask.shape

# downsample mask to a working resolution keyed off COLS
scale = COLS / mw
work_w = COLS
work_h = max(1, int(mh * scale))
mimg = Image.fromarray((mask*255).astype(np.uint8)).resize((work_w, work_h), Image.LANCZOS)
mask = (np.array(mimg) > 110)
mh, mw = mask.shape
depth = max(2.0, mw * DEPTH_FRAC)

# ---- 2. build surface point cloud -----------------------------------------
pts, norms = [], []
ys, xs = np.where(mask)
cx, cy = mw/2.0, mh/2.0
# front + back caps
for zc, nz in [(-0.6, -1.0), (depth, 1.0)]:
    for (yy, xx) in zip(ys, xs):
        pts.append((xx-cx, yy-cy, zc)); norms.append((0,0,nz))
# side walls (boundary pixels through depth)
def empty(yy, xx):
    if yy<0 or yy>=mh or xx<0 or xx>=mw: return True
    return not mask[yy, xx]
nz_steps = np.linspace(0, depth, max(3, int(depth)))
for (yy, xx) in zip(ys, xs):
    nx = ny = 0.0
    if empty(yy, xx-1): nx -= 1
    if empty(yy, xx+1): nx += 1
    if empty(yy-1, xx): ny -= 1
    if empty(yy+1, xx): ny += 1
    if nx==0 and ny==0: continue
    n = np.array([nx, ny, 0.0]); n = n/np.linalg.norm(n)
    for zc in nz_steps:
        pts.append((xx-cx, yy-cy, zc)); norms.append(tuple(n))
pts = np.array(pts, float); norms = np.array(norms, float)

# ---- 3. project + shade one frame -> char grid -----------------------------
tilt = np.radians(TILT_DEG)
Rx = np.array([[1,0,0],[0,np.cos(tilt),-np.sin(tilt)],[0,np.sin(tilt),np.cos(tilt)]])

def frame_grid(yaw_deg):
    yaw = np.radians(yaw_deg)
    Ry = np.array([[np.cos(yaw),0,np.sin(yaw)],[0,1,0],[-np.sin(yaw),0,np.cos(yaw)]])
    R  = Rx @ Ry
    P  = pts @ R.T
    Nr = norms @ R.T
    view = np.array([0,0,-1.0])
    facing = Nr @ view > 0.02                       # back-face cull
    P, Nr = P[facing], Nr[facing]
    z = P[:,2]
    f = CAM_DIST / (CAM_DIST + (z - z.min())/max(1,(z.max()-z.min())) * 3.0 + 1e-6)
    sx = P[:,0]*f; sy = P[:,1]*f
    lam = np.clip(Nr @ LIGHT, 0, 1)
    fog = np.clip(1.0 - (z - z.min())/max(1,(z.max()-z.min()))*0.55, 0, 1)
    bright = np.clip(lam*0.75 + 0.35, 0, 1) * fog
    return sx, sy, z, bright

# global fit across all frames
allx=[]; ally=[]
frames_raw=[]
yaws = [(-SWING_DEG + 2*SWING_DEG* (i/(N_FRAMES-1))) for i in range(N_FRAMES)]
# rock: go there and back
half = yaws
yaws = half + half[::-1][1:-1]
N = len(yaws)
for yaw in yaws:
    sx, sy, z, b = frame_grid(yaw)
    frames_raw.append((sx, sy, z, b)); allx.append(sx); ally.append(sy)
allx=np.concatenate(allx); ally=np.concatenate(ally)
minx,maxx=allx.min(),allx.max(); miny,maxy=ally.min(),ally.max()
gcols = COLS
gscale = (gcols-1)/(maxx-minx)
grows = int((maxy-miny)*gscale)+1 + ROW_MARGIN*2

def rasterize(sx, sy, z, b):
    col = np.round((sx-minx)*gscale).astype(int)
    row = np.round((sy-miny)*gscale).astype(int)+ROW_MARGIN
    grid = np.zeros((grows, gcols), int)
    order = np.argsort(-z)                            # far->near, nearest wins
    idx = np.clip((b*(len(RAMP)-1)).astype(int),0,len(RAMP)-1)
    c=col[order]; r=row[order]; ii=idx[order]
    ok=(c>=0)&(c<gcols)&(r>=0)&(r<grows)
    grid[r[ok], c[ok]] = ii[ok]
    return grid

grids = [rasterize(*fr) for fr in frames_raw]

# ---- 4. emit SVG flipbook --------------------------------------------------
PAD=18; TITLEBAR=30
art_w = gcols*CELL_W; art_h = grows*CELL_H
W = art_w + PAD*2
H = TITLEBAR + art_h + PAD
DUR = 6.0

p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
   f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">']
p.append(f'<defs><linearGradient id="wbg" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>')
p.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#wbg)"/>')
p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-opacity="0.5"/>')
p.append(f'<line x1="0" y1="{TITLEBAR}" x2="{W}" y2="{TITLEBAR}" stroke="{FRAME}" stroke-opacity="0.3"/>')
for i,c in enumerate(["#ff5f8f","#ffbd2e","#27c93f"]):
    p.append(f'<circle cx="{PAD+i*16}" cy="{TITLEBAR/2}" r="5" fill="{c}"/>')
p.append(f'<text x="{W/2}" y="{TITLEBAR/2+4}" fill="{TITLE}" font-size="12" text-anchor="middle">hamna@dev: ~ $ ./wordmark.sh</text>')

def rows_to_text(grid, gid, begin, hidden):
    out=[f'<g id="{gid}" opacity="{0 if hidden else 1}">']
    for ry in range(grows):
        line="".join(RAMP[v] for v in grid[ry])
        if not line.strip(): continue
        y = TITLEBAR + PAD*0.3 + ry*CELL_H + CELL_H*0.8
        out.append(f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
                   f'font-size="{CELL_H*0.95:.1f}" textLength="{art_w}" lengthAdjust="spacing">{html.escape(line)}</text>')
    out.append("</g>")
    return "".join(out)

# intro: frame 0 wipes in via clipPath, then flipbook takes over
intro_dur=1.4
p.append(f'<clipPath id="wipe"><rect x="{PAD}" y="{TITLEBAR}" height="{art_h}" width="0">'
         f'<animate attributeName="width" from="0" to="{art_w}" begin="0s" dur="{intro_dur}s" fill="freeze"/></rect></clipPath>')
p.append(f'<g clip-path="url(#wipe)">{rows_to_text(grids[0],"introframe",0,False)}</g>')
# hide intro once flipbook starts
p.append(f'<set xlink:href="#introframe" attributeName="opacity" to="0" begin="{intro_dur}s"/>')

# flipbook: each frame owns [i/N,(i+1)/N] of DUR, discrete
for i,g in enumerate(grids):
    gid=f"f{i}"
    p.append(rows_to_text(g, gid, 0, True))
    kt=f"{i/N:.4f};{(i+0.9)/N:.4f};{(i+1)/N:.4f}"
    p.append(f'<animate xlink:href="#{gid}" attributeName="opacity" calcMode="discrete" '
             f'values="0;1;0" keyTimes="{kt}" dur="{DUR}s" begin="{intro_dur}s" repeatCount="indefinite"/>')

p.append("</svg>")
svg="".join(p)
open(OUT,"w").write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", H, "; frames:", N)
