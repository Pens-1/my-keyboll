#!/usr/bin/env python3
"""
nRF52840 (SuperMini) + PMW3360 Breakout + Battery  →  .kicad_pcb Generator
Board: 18mm × 33mm (Pro Micro footprint)

Layout:
  y=0.0  ─ board top edge
  y=1.27 ─ J1 (8-pin PMW3360 connector, horizontal)
  y=3.81 ─ U1 pin1 / pin13  (socket headers)
  y=6.35 ─ U1 pin2 / pin14
    ...   (2.54mm pitch, 12 pins per side)
  y=31.75─ U1 pin12 / pin24
  y=33.0 ─ board bottom edge

  x=1.27  ── left socket row  (pins 1-12)
  x=16.73 ── right socket row (pins 13-24)
  J2 battery connector: between rows at (8.0, 20.0) & (10.0, 20.0)

Routing strategy:
  B.Cu zone  : GND copper fill (entire board → connects all GND pads)
  F.Cu traces: MOSI, MISO, SCK, VCC   (short direct routes, no crossings)
  Ratsnest   : NCS, MOTION, BATIN     (displayed in KiCad, user routes manually)
"""

import uuid
import math

def uid():
    return str(uuid.uuid4())

# ─── Board ──────────────────────────────────────────────────────────────────
W, H = 18.0, 33.0       # mm

# KiCad A4ページ (297×210mm 横向き) 上のボード配置原点
# (0,0)のままだとページ左上隅に表示されるため中央付近にオフセット
ORIGIN_X = 135.0        # A4横(297mm): (297-18)/2 ≈ 139 → 135で左寄せ余裕
ORIGIN_Y =  85.0        # A4横(210mm): (210-33)/2 ≈  88 → 85でほぼ中央

# ─── Nets ───────────────────────────────────────────────────────────────────
NETS = {
    0: "",
    1: "GND",
    2: "VCC",
    3: "MOSI",
    4: "MISO",
    5: "SCK",
    6: "NCS",
    7: "MOTION",
    8: "BATIN",
}

# ─── U1 socket positions ─────────────────────────────────────────────────────
U1_LEFT_X  = 1.27
U1_RIGHT_X = 16.73
U1_Y_TOP   = 3.81
PITCH      = 2.54

def u1_y(n):        # n=1..12 for left, 1..12 for right
    return U1_Y_TOP + (n - 1) * PITCH

# Net assignments for U1 left pins (1-12)
U1_LEFT_NETS = {
    1: 0,           # TX/P0.06  (unused)
    2: 0,           # RX/P0.08  (unused)
    3: 1,           # GND
    4: 1,           # GND
    5: 0,           # SDA/P0.17 (unused)
    6: 0,           # SCL/P0.20 (unused)
    7: 0,           # P0.22     (unused)
    8: 0,           # P0.24     (unused)
    9: 0,           # P1.00     (unused)
    10: 0,          # P0.11     (unused)
    11: 7,          # MOTION/P1.04
    12: 6,          # NCS/P1.06
}

# Net assignments for U1 right pins (13-24)
U1_RIGHT_NETS = {
    13: 0,          # NFC1/P0.09 (unused)
    14: 4,          # MISO/P0.10 (swapped: nRF52840 SPI is software-configurable)
    15: 3,          # MOSI/P1.11 (swapped: avoids F.Cu track crossing)
    16: 5,          # SCK/P1.13
    17: 0,          # P1.15     (unused)
    18: 0,          # AIN0/P0.02 (unused)
    19: 0,          # AIN5/P0.29 (unused)
    20: 0,          # AIN7/P0.31 (unused)
    21: 2,          # VCC
    22: 0,          # RST       (unused)
    23: 1,          # GND
    24: 8,          # BATIN/P0.04
}

# ─── J1 (8-pin PMW3360 connector) ───────────────────────────────────────────
# 2.0mm pitch (JST-PH): 2*0.7 + 7*2.0 = 15.4mm < 18mm → fits within board
J1_PITCH  = 2.0
J1_Y      = 1.27
J1_X0     = (W - 7 * J1_PITCH) / 2    # = (18 - 14) / 2 = 2.0mm
J1_NETS   = {
    1: 1,   # GND
    2: 2,   # VCC
    3: 0,   # NC
    4: 7,   # MOTION
    5: 5,   # SCLK
    6: 3,   # MOSI
    7: 4,   # MISO
    8: 6,   # CS / NCS
}

def j1_x(n):
    return J1_X0 + (n - 1) * J1_PITCH

# ─── J2 (2-pin JST-PH battery) ──────────────────────────────────────────────
# Placed between SCK(x=10) and MOSI(x=12) traces, below their vertical sections
# pin1(B+) at x=10.5, pin2(B-) at x=12.5, y=14.0mm
J2_PITCH = 2.0          # JST-PH 2mm pitch
J2_CX    = 11.5         # centre x: between SCK(10.0) and MOSI(12.0) trace columns
J2_Y     = 14.0         # y: below all vertical F.Cu trace ends (SCK ends at y=11.43)

def j2_x(n):            # n=1 (B+), n=2 (B-)
    return J2_CX + (n - 1.5) * J2_PITCH   # pin1=3.5mm, pin2=5.5mm

J2_NETS = {1: 8, 2: 1}   # B+→BATIN, B-→GND

# ─── Helpers ────────────────────────────────────────────────────────────────
def net_ref(net_id):
    """(net N "name") reference string for pad declarations."""
    if net_id == 0:
        return ""
    return f'(net {net_id} "{NETS[net_id]}")'

def thru_pad(number, x, y, net_id,
             drill=1.0, pad_d=1.6, shape="circle"):
    """Standard through-hole pad (2.54mm header or similar)."""
    nr = net_ref(net_id)
    return (
        f'    (pad "{number}" thru_hole {shape} (at {x:.4f} {y:.4f}) '
        f'(size {pad_d:.4f} {pad_d:.4f}) (drill {drill:.4f}) '
        f'(layers "*.Cu" "*.Mask") {nr})\n'
    )

def smd_pad(number, x, y, net_id, w=1.6, h=1.6):
    """SMD pad."""
    nr = net_ref(net_id)
    return (
        f'    (pad "{number}" smd rect (at {x:.4f} {y:.4f}) '
        f'(size {w:.4f} {h:.4f}) (layers "F.Cu" "F.Paste" "F.Mask") {nr})\n'
    )

def fp_text(kind, text, x, y, layer="F.SilkS", size=0.8):
    return (
        f'  (fp_text {kind} "{text}" (at {x:.4f} {y:.4f}) (layer "{layer}") (uuid "{uid()}")\n'
        f'    (effects (font (size {size} {size}) (thickness 0.15))))\n'
    )

def fp_line(x1, y1, x2, y2, layer="F.SilkS", w=0.12):
    return (
        f'  (fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) '
        f'(stroke (width {w:.4f}) (type default)) (layer "{layer}"))\n'
    )

def segment(x1, y1, x2, y2, net_id, layer="F.Cu", width=0.25):
    return (
        f'(segment (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) '
        f'(width {width:.4f}) (layer "{layer}") (net {net_id}) (uuid "{uid()}"))\n'
    )

def gr_text(text, x, y, layer="F.SilkS", size=0.8, rot=0):
    return (
        f'(gr_text "{text}" (at {x:.4f} {y:.4f} {rot}) (layer "{layer}") (uuid "{uid()}")\n'
        f'  (effects (font (size {size} {size}) (thickness 0.15))))\n'
    )

# ─── Footprint builders ──────────────────────────────────────────────────────
def fp_u1():
    """SuperMini nRF52840 socket: two rows of 12 through-hole pads."""
    lines = []
    lines.append(f'(footprint "SuperMini_nRF52840_Socket" (layer "F.Cu") '
                 f'(at {ORIGIN_X:.4f} {ORIGIN_Y:.4f}) (uuid "{uid()}")\n')
    lines.append(fp_text("reference", "U1", W/2, U1_Y_TOP + 1.0))
    lines.append(fp_text("value", "SuperMini_nRF52840", W/2, u1_y(12) - 1.0))

    # Left row pads (pins 1-12)
    for n in range(1, 13):
        y = u1_y(n)
        lines.append(thru_pad(str(n), U1_LEFT_X, y, U1_LEFT_NETS[n]))

    # Right row pads (pins 13-24)
    for n in range(13, 25):
        row_n = n - 12
        y = u1_y(row_n)
        lines.append(thru_pad(str(n), U1_RIGHT_X, y, U1_RIGHT_NETS[n]))

    # Silkscreen outline around socket area (clamped inside board edges)
    margin = 1.5
    x1 = max(0.3, U1_LEFT_X - margin)
    x2 = min(W - 0.3, U1_RIGHT_X + margin)
    y1 = max(0.3, U1_Y_TOP - margin)
    y2 = min(H - 0.3, u1_y(12) + margin)
    for (ax, ay, bx, by) in [
        (x1, y1, x2, y1), (x2, y1, x2, y2),
        (x2, y2, x1, y2), (x1, y2, x1, y1)
    ]:
        lines.append(fp_line(ax, ay, bx, by))

    # Pin 1 marker
    lines.append(fp_text("user", "1", U1_LEFT_X + 1.8, U1_Y_TOP, size=0.8))
    lines.append(fp_text("user", "13", U1_RIGHT_X - 1.8, U1_Y_TOP, size=0.8))

    lines.append(")\n")
    return "".join(lines)


def fp_j1():
    """PMW3360 8-pin connector (horizontal, top of board). 2.0mm pitch JST-PH."""
    lines = []
    lines.append(f'(footprint "Connector_JST_PH_1x08" (layer "F.Cu") '
                 f'(at {ORIGIN_X:.4f} {ORIGIN_Y:.4f}) (uuid "{uid()}")\n')
    cx = (j1_x(1) + j1_x(8)) / 2
    lines.append(fp_text("reference", "J1", cx, 0.5))
    lines.append(fp_text("value", "PMW3360_Connector", cx, 2.6))

    for n in range(1, 9):
        # JST-PH: drill=0.75mm, pad=1.4mm → fits within 18mm board
        lines.append(thru_pad(str(n), j1_x(n), J1_Y, J1_NETS[n], drill=0.75, pad_d=1.4))

    # Silkscreen box
    x1, x2 = j1_x(1) - 1.0, j1_x(8) + 1.0
    y1, y2 = max(0.3, J1_Y - 1.0), J1_Y + 1.0
    for (ax, ay, bx, by) in [
        (x1, y1, x2, y1), (x2, y1, x2, y2),
        (x2, y2, x1, y2), (x1, y2, x1, y1)
    ]:
        lines.append(fp_line(ax, ay, bx, by))
    # F.CrtYd
    cyd_m = 0.25
    for (ax, ay, bx, by) in [
        (x1-cyd_m, y1-cyd_m, x2+cyd_m, y1-cyd_m),
        (x2+cyd_m, y1-cyd_m, x2+cyd_m, y2+cyd_m),
        (x2+cyd_m, y2+cyd_m, x1-cyd_m, y2+cyd_m),
        (x1-cyd_m, y2+cyd_m, x1-cyd_m, y1-cyd_m),
    ]:
        lines.append(fp_line(ax, ay, bx, by, layer="F.CrtYd", w=0.05))
    lines.append(")\n")
    return "".join(lines)


def fp_j2():
    """Battery JST-PH 2-pin connector."""
    lines = []
    cx = (j2_x(1) + j2_x(2)) / 2
    lines.append(f'(footprint "Connector_JST_PH_2pin" (layer "F.Cu") '
                 f'(at {ORIGIN_X:.4f} {ORIGIN_Y:.4f}) (uuid "{uid()}")\n')
    lines.append(fp_text("reference", "J2", cx, J2_Y - 2.0))
    lines.append(fp_text("value", "Battery_JST-PH", cx, J2_Y + 2.0))

    # JST-PH through-hole: 0.8mm drill, 1.6mm pad
    lines.append(thru_pad("1", j2_x(1), J2_Y, J2_NETS[1], drill=0.8, pad_d=1.6, shape="oval"))
    lines.append(thru_pad("2", j2_x(2), J2_Y, J2_NETS[2], drill=0.8, pad_d=1.6, shape="circle"))

    # Silkscreen + F.CrtYd
    x1, x2 = j2_x(1) - 1.2, j2_x(2) + 1.2
    y1, y2 = J2_Y - 1.2, J2_Y + 1.2
    cyd_m = 0.25
    for (ax, ay, bx, by) in [
        (x1-cyd_m, y1-cyd_m, x2+cyd_m, y1-cyd_m),
        (x2+cyd_m, y1-cyd_m, x2+cyd_m, y2+cyd_m),
        (x2+cyd_m, y2+cyd_m, x1-cyd_m, y2+cyd_m),
        (x1-cyd_m, y2+cyd_m, x1-cyd_m, y1-cyd_m),
    ]:
        lines.append(fp_line(ax, ay, bx, by, layer="F.CrtYd", w=0.05))
    for (ax, ay, bx, by) in [
        (x1, y1, x2, y1), (x2, y1, x2, y2),
        (x2, y2, x1, y2), (x1, y2, x1, y1)
    ]:
        lines.append(fp_line(ax, ay, bx, by))
    lines.append(fp_text("user", "B+", j2_x(1), J2_Y - 2.0, size=0.8))
    lines.append(fp_text("user", "B-", j2_x(2), J2_Y - 2.0, size=0.8))

    lines.append(")\n")
    return "".join(lines)


# ─── Copper traces ───────────────────────────────────────────────────────────
def traces():
    """
    Routes all signal and power traces.

    F.Cu signal traces:
      MOSI  : J1[6]  → U1R pin14  (right-side, short)
      MISO  : J1[7]  → U1R pin15  (right-side, short)
      SCK   : J1[5]  → U1R pin16  (right-side, medium)
      VCC   : J1[2]  → U1R pin21  (vertical + horizontal)
      BATIN : J2[1]  → U1R pin24  (down then right, between rows)

    B.Cu signal traces:
      NCS    : J1[8]  → U1L pin12  (right edge → bottom → left)
      MOTION : J1[4]  → U1L pin11  (vertical down then left)
    """
    segs = []
    W_SIG = 0.25    # signal trace width
    W_PWR = 0.4     # power trace width

    # フットプリント外の要素はボード相対座標にORIGINを加算
    ox, oy = ORIGIN_X, ORIGIN_Y

    def s(x1, y1, x2, y2, net, layer="F.Cu", w=W_SIG):
        return segment(ox+x1, oy+y1, ox+x2, oy+y2, net, layer, w)

    # ── MOSI: J1[6]=(12.0,1.27) → U1R15=(16.73,8.89) ──────────────────────
    mx1, my1 = j1_x(6), J1_Y
    mx2, my2 = U1_RIGHT_X, u1_y(3)     # row index 3 = global pin15
    segs.append(s(mx1, my1, mx1, my2, 3))   # vertical
    segs.append(s(mx1, my2, mx2, my2, 3))   # horizontal

    # ── MISO: J1[7]=(14.0,1.27) → U1R14=(16.73,6.35) ──────────────────────
    ix1, iy1 = j1_x(7), J1_Y
    ix2, iy2 = U1_RIGHT_X, u1_y(2)     # row index 2 = global pin14
    segs.append(s(ix1, iy1, ix1, iy2, 4))
    segs.append(s(ix1, iy2, ix2, iy2, 4))

    # ── SCK: J1[5]=(10.27,1.27) → U1R16=(16.73,11.43) ──────────────────────
    sx1, sy1 = j1_x(5), J1_Y
    sx2, sy2 = U1_RIGHT_X, u1_y(4)     # row index 4 = global pin16
    segs.append(s(sx1, sy1, sx1, sy2, 5))
    segs.append(s(sx1, sy2, sx2, sy2, 5))

    # ── VCC: J1[2]=(2.65,1.27) → U1R21=(16.73,24.13) ───────────────────────
    vx1, vy1 = j1_x(2), J1_Y
    vx2, vy2 = U1_RIGHT_X, u1_y(9)     # row index 9 = global pin21
    segs.append(s(vx1, vy1, vx1, vy2, 2, w=W_PWR))
    segs.append(s(vx1, vy2, vx2, vy2, 2, w=W_PWR))

    # ── BATIN: J2[1]=(10.5,14.0) → U1R24=(16.73,31.75)  [B.Cu] ────────────
    # B.Cu avoids crossing VCC horizontal trace (F.Cu at y=24.13)
    bx1, by1 = j2_x(1), J2_Y           # J2 pin1 (B+)
    bx2, by2 = U1_RIGHT_X, u1_y(12)    # U1R pin24 = row index 12
    segs.append(s(bx1, by1, bx1, by2, 8, "B.Cu"))   # vertical down
    segs.append(s(bx1, by2, bx2, by2, 8, "B.Cu"))   # horizontal right

    # ── NCS: J1[8]=(16.0,1.27) → U1L12=(1.27,31.75)  [B.Cu] ──────────────
    # Route: left from J1[8], down between rows, left below MOTION, down to pin12
    nx1, ny1 = j1_x(8), J1_Y           # J1 pin8 (CS) = (16.0, 1.27)
    nx2, ny2 = U1_LEFT_X, u1_y(12)     # U1L pin12 = (1.27, 31.75)
    segs.append(s(nx1, ny1, 15.1, ny1, 6, "B.Cu"))         # left to x=15.1
    segs.append(s(15.1, ny1, 15.1, 12.7, 6, "B.Cu"))       # down to y=12.7
    segs.append(s(15.1, 12.7, 9.0, 12.7, 6, "B.Cu"))       # left to x=9.0
    segs.append(s(9.0, 12.7, 9.0, 30.5, 6, "B.Cu"))        # down to y=30.5
    segs.append(s(9.0, 30.5, nx2, 30.5, 6, "B.Cu"))         # left to x=1.27
    segs.append(s(nx2, 30.5, nx2, ny2, 6, "B.Cu"))          # down to pin12

    # ── MOTION: J1[4]=(7.73,1.27) → U1L11=(1.27,29.21)  [B.Cu] ────────────
    mot_x = j1_x(4)                     # x = 7.73
    mot_y = u1_y(11)                    # y = 29.21 (row index 11 = global pin11)
    segs.append(s(mot_x, J1_Y, mot_x, mot_y, 7, "B.Cu"))   # vertical down
    segs.append(s(mot_x, mot_y, U1_LEFT_X, mot_y, 7, "B.Cu"))  # left

    return "".join(segs)


# ─── GND copper fill on B.Cu ─────────────────────────────────────────────────
def gnd_zone():
    """Fill entire board with GND on B.Cu (connects all GND pads)."""
    ox, oy = ORIGIN_X, ORIGIN_Y
    return f"""(zone (net 1) (net_name "GND") (layer "B.Cu") (uuid "{uid()}")
  (hatch edge 0.508)
  (connect_pads (clearance 0.2))
  (min_thickness 0.25)
  (filled_areas_thickness no)
  (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
  (polygon (pts
    (xy {ox:.4f} {oy:.4f}) (xy {ox+W:.4f} {oy:.4f})
    (xy {ox+W:.4f} {oy+H:.4f}) (xy {ox:.4f} {oy+H:.4f})))
)
"""


# ─── Silkscreen labels ───────────────────────────────────────────────────────
def silkscreen():
    ox, oy = ORIGIN_X, ORIGIN_Y
    parts = []
    # Board title
    parts.append(gr_text("nRF52840+PMW3360", ox + W/2, oy + H - 1.5, size=0.8))
    return "".join(parts)


# ─── Main generator ──────────────────────────────────────────────────────────
def generate():
    parts = []

    # ── KiCad PCB header ────────────────────────────────────────────────────
    parts.append(f"""(kicad_pcb (version 20240108) (generator pcbnew) (generator_version "9.0")
  (general (thickness 1.6))
  (paper "A4")
  (title_block
    (title "nRF52840 + PMW3360 PCB (Pro Micro form factor)")
    (date "2026-03-21")
    (rev "1.0")
    (comment 1 "Board size: {W}mm x {H}mm")
    (comment 2 "SPI: MOSI=P0.10 MISO=P1.11 SCK=P1.13 NCS=P1.06 MOTION=P1.04")
  )
""")

    # ── Layers (KiCad 9 standard layer numbers) ─────────────────────────────
    parts.append("""  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user)
    (37 "F.SilkS" user)
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user)
    (47 "F.CrtYd" user)
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
""")

    # ── Setup (KiCad 9 minimal) ──────────────────────────────────────────────
    parts.append("""  (setup
    (copper_edge_clearance 0.25)
    (pad_to_mask_clearance 0)
    (allow_soldermask_bridges_in_footprints no)
    (pcbplotparams
      (layerselection 0x00010fc_ffffffff)
      (plot_on_all_layers_selection 0x0000000_00000000)
      (disableapertmacros no)
      (usegerberextensions no)
      (usegerberattributes yes)
      (usegerberadvancedattributes yes)
      (creategerberjobfile yes)
      (dashed_line_dash_ratio 12.000000)
      (dashed_line_gap_ratio 3.000000)
      (svgprecision 4)
      (plotframeref no)
      (viasonmask no)
      (mode 1)
      (useauxorigin no)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15.000000)
      (dxfpolygonmode yes)
      (dxfimperialunits yes)
      (dxfusepcbnewfont yes)
      (psnegative no)
      (psa4output no)
      (plotreference yes)
      (plotvalue yes)
      (plotinvisibletext no)
      (sketchpadsonfab no)
      (subtractmaskfromsilk no)
      (outputformat 1)
      (mirror no)
      (drillshape 1)
      (scaleselection 1)
      (outputdirectory "gerber/"))
  )
""")

    # ── Net definitions ──────────────────────────────────────────────────────
    for net_id, net_name in NETS.items():
        parts.append(f'  (net {net_id} "{net_name}")\n')
    parts.append("\n")

    # ── Board outline (Edge.Cuts) ────────────────────────────────────────────
    ox, oy = ORIGIN_X, ORIGIN_Y
    parts.append(f'  (gr_rect (start {ox:.4f} {oy:.4f}) (end {ox+W:.4f} {oy+H:.4f}) '
                 f'(stroke (width 0.05) (type default)) (layer "Edge.Cuts") (uuid "{uid()}"))\n\n')

    # ── Footprints ───────────────────────────────────────────────────────────
    parts.append(fp_u1())
    parts.append(fp_j1())
    parts.append(fp_j2())

    # ── Traces ───────────────────────────────────────────────────────────────
    parts.append(traces())

    # ── GND zone ─────────────────────────────────────────────────────────────
    parts.append(gnd_zone())

    # ── Silkscreen ───────────────────────────────────────────────────────────
    parts.append(silkscreen())

    # ── Footer ───────────────────────────────────────────────────────────────
    parts.append(")\n")
    return "".join(parts)


if __name__ == "__main__":
    output_path = "/home/user/repos/make-keybord/nrf52840_pmw3360.kicad_pcb"
    content = generate()
    with open(output_path, "w") as f:
        f.write(content)
    print(f"PCB written to: {output_path}")
    print(f"File size: {len(content):,} bytes")
    print()
    print("Board:  18.0 mm × 33.0 mm  (Pro Micro form factor)")
    print()
    print("Component placement:")
    print(f"  U1 socket  left row : x={U1_LEFT_X:.2f}mm, y={U1_Y_TOP:.2f}..{u1_y(12):.2f}mm (pins 1-12)")
    print(f"  U1 socket  right row: x={U1_RIGHT_X:.2f}mm, y={U1_Y_TOP:.2f}..{u1_y(12):.2f}mm (pins 13-24)")
    print(f"  J1 PMW3360  8-pin  : y={J1_Y:.2f}mm, x={j1_x(1):.2f}..{j1_x(8):.2f}mm (horizontal)")
    print(f"  J2 Battery  2-pin  : ({j2_x(1):.2f},{J2_Y:.2f}) & ({j2_x(2):.2f},{J2_Y:.2f})mm")
    print()
    print("Routed traces (F.Cu): MOSI, MISO, SCK, VCC")
    print("Routed traces (B.Cu): NCS (right edge→bottom), MOTION (vertical→left), BATIN")
    print("GND copper fill     : B.Cu (entire board)")
