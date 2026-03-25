#!/usr/bin/env python3
"""
Keyball39 Custom Schematic Generator
Output: keyball39_custom.kicad_sch

Components:
  U1         : SuperMini nRF52840 socket (24-pin 2.54mm)
  J1         : PMW3610 sensor (8-pin SPI, 3.3V)
  J2         : Battery JST-PH 2-pin
  C1, C2     : 100nF decoupling capacitors
  SW1-SW22   : Key switches MX-compatible
  D1-D22     : 1N4148 diodes SOD-123
  MH1, MH2   : M2 mounting holes (trackball case)

Pin assignments (SuperMini nRF52840):
  Left  col: COL0(P0.06) COL1(P0.08) GND GND COL2(P0.17) COL3(P0.20)
             COL4(P0.22) COL5(P0.24) ROW0(P1.00) ROW1(P0.11)
             MOTION(P1.04) NCS(P1.06)
  Right col: ROW2(P0.09) MOSI(P0.10) MISO(P1.11) SCK(P1.13) ROW3(P1.15)
             NC NC NC VCC RST GND BATIN(P0.04)

Key matrix (4 rows x 6 cols = 24 max, 22 populated):
  COLn -> SW -> D(1N4148) -> ROWn
  Row0: SW1-SW6    Row1: SW7-SW12
  Row2: SW13-SW18  Row3: SW19-SW22 (4 keys, thumb cluster)
"""

import uuid

def uid():
    return str(uuid.uuid4())

# ─── Layout constants ────────────────────────────────────────────────────────
# SuperMini U1: left side of schematic
U1_X,  U1_Y  = 35.0,  148.0
SM_BW, SM_PL  = 7.62,  2.54
SM_PX          = SM_BW + SM_PL   # 10.16 mm from centre to pin tip
SM_Y0, SM_STEP = 13.97, 2.54

# PMW3610 J1: upper right
J1_X,  J1_Y  = 385.0, 65.0
J1_BW, J1_PL  = 3.81,  5.08
J1_PX          = J1_BW + J1_PL   # 8.89
J1_Y0, J1_STEP = 8.89,  2.54

# Battery J2: lower left
J2_X,  J2_Y  = 35.0, 255.0
J2_BW, J2_PL  = 3.81,  5.08
J2_PX          = J2_BW + J2_PL
J2_Y0, J2_STEP = 1.27,  2.54

# Capacitors (vertical, VCC top / GND bottom)
C_BH = 1.016    # body half-height
C_PL = 1.524    # pin length
C_PY = C_BH + C_PL   # 2.54 mm centre-to-pin-tip
C1_X, C1_Y = 362.0, 118.0
C2_X, C2_Y = 382.0, 118.0

# Mounting holes
MH1_X, MH1_Y = 355.0, 252.0
MH2_X, MH2_Y = 380.0, 252.0

# Key matrix grid
MX0, MY0    = 85.0, 35.0   # origin of first cell (row0, col0)
CELL_DX     = 22.0          # horizontal cell spacing
CELL_DY     = 16.0          # vertical cell spacing

# In-cell offsets (SW + D in series, horizontal)
# SW pin1(COL) ── wire ── SW ── wire ── D_anode ── D ── D_cathode(ROW)
SW_PX  = 5.08   # SW pin-tip distance from SW centre (pin1 at -SW_PX, pin2 at +SW_PX)
D_DX   = 10.16  # diode centre offset from SW centre
D_PX   = 2.54   # diode pin-tip distance from D centre (A at -D_PX, K at +D_PX)

# Matrix definition: (row, col, sw_num, d_num)
MATRIX = [
    (0,0, 1, 1),(0,1, 2, 2),(0,2, 3, 3),(0,3, 4, 4),(0,4, 5, 5),(0,5, 6, 6),
    (1,0, 7, 7),(1,1, 8, 8),(1,2, 9, 9),(1,3,10,10),(1,4,11,11),(1,5,12,12),
    (2,0,13,13),(2,1,14,14),(2,2,15,15),(2,3,16,16),(2,4,17,17),(2,5,18,18),
    (3,0,19,19),(3,1,20,20),(3,2,21,21),(3,3,22,22),
]

# ─── Coordinate helpers ──────────────────────────────────────────────────────
def sm_left_y(n):    return SM_Y0 - (n - 1) * SM_STEP
def sm_right_y(n):   return SM_Y0 - (n - 13) * SM_STEP
def u1L(n):          return U1_X - SM_PX, U1_Y - sm_left_y(n)
def u1R(n):          return U1_X + SM_PX, U1_Y - sm_right_y(n)
def j1y(n):          return J1_Y0 - (n - 1) * J1_STEP
def j1L(n):          return J1_X - J1_PX, J1_Y - j1y(n)
def j2y(n):          return J2_Y0 - (n - 1) * J2_STEP
def j2L(n):          return J2_X - J2_PX, J2_Y - j2y(n)
def cell_sw(row, col):
    cx = MX0 + col * CELL_DX
    cy = MY0 + row * CELL_DY
    return cx, cy
def cell_d(row, col):
    cx, cy = cell_sw(row, col)
    return cx + D_DX, cy

# ─── Symbol helpers ──────────────────────────────────────────────────────────
def pin(angle, x, y, length, name, number, ptype="passive"):
    return (
        f'        (pin {ptype} line (at {x:.4f} {y:.4f} {angle}) (length {length:.4f})\n'
        f'          (name "{name}" (effects (font (size 1.016 1.016))))\n'
        f'          (number "{number}" (effects (font (size 1.016 1.016)))))\n'
    )

def wire(x1, y1, x2, y2):
    return (f'  (wire (pts (xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f}))\n'
            f'    (stroke (width 0) (type default)) (uuid "{uid()}"))\n')

def label(text, x, y, rot=0):
    return (f'  (label "{text}" (at {x:.4f} {y:.4f} {rot})\n'
            f'    (effects (font (size 1.27 1.27))) (uuid "{uid()}"))\n')

def no_connect(x, y):
    return f'  (no_connect (at {x:.4f} {y:.4f}) (uuid "{uid()}"))\n'

def junction(x, y):
    return f'  (junction (at {x:.4f} {y:.4f}) (diameter 0) (color 0 0 0 0) (uuid "{uid()}"))\n'

def power_sym(x, y, value, pwr_id, rot=0):
    return (f'  (symbol (lib_id "power:{value}") (at {x:.4f} {y:.4f} {rot}) (unit 1)\n'
            f'    (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")\n'
            f'    (property "Reference" "{pwr_id}" (at {x:.4f} {y:.4f} {rot})\n'
            f'      (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'    (property "Value" "{value}" (at {x:.4f} {y:.4f} {rot})\n'
            f'      (effects (font (size 1.27 1.27))))\n'
            f'  )\n')

# ─── Library symbol definitions ──────────────────────────────────────────────

def lib_supermini():
    bh = SM_Y0 + SM_STEP / 2
    px = SM_PX
    left_pins = [
        (1,  "COL0/P0.06",   "bidirectional"),
        (2,  "COL1/P0.08",   "bidirectional"),
        (3,  "GND",          "power_in"),
        (4,  "GND",          "power_in"),
        (5,  "COL2/P0.17",   "bidirectional"),
        (6,  "COL3/P0.20",   "bidirectional"),
        (7,  "COL4/P0.22",   "bidirectional"),
        (8,  "COL5/P0.24",   "bidirectional"),
        (9,  "ROW0/P1.00",   "bidirectional"),
        (10, "ROW1/P0.11",   "bidirectional"),
        (11, "MOTION/P1.04", "output"),
        (12, "NCS/P1.06",    "output"),
    ]
    right_pins = [
        (13, "ROW2/P0.09",  "bidirectional"),
        (14, "MOSI/P0.10",  "output"),
        (15, "MISO/P1.11",  "input"),
        (16, "SCK/P1.13",   "output"),
        (17, "ROW3/P1.15",  "bidirectional"),
        (18, "P0.02",       "bidirectional"),
        (19, "P0.29",       "bidirectional"),
        (20, "P0.31",       "bidirectional"),
        (21, "VCC",         "power_out"),
        (22, "RST",         "input"),
        (23, "GND",         "power_in"),
        (24, "BATIN/P0.04", "input"),
    ]
    L = []
    L.append('    (symbol "SuperMini_nRF52840"\n')
    L.append('      (in_bom yes) (on_board yes)\n')
    L.append('      (property "Reference" "U" (at 0 0 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Value" "SuperMini_nRF52840" (at 0 -2.54 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Footprint" "" (at 0 0 0)\n'
             '        (effects (font (size 1.27 1.27)) (hide yes)))\n')
    L.append('      (symbol "SuperMini_nRF52840_0_1"\n')
    L.append(f'        (rectangle (start {-SM_BW:.4f} {-bh:.4f}) (end {SM_BW:.4f} {bh:.4f})\n'
              '          (stroke (width 0)) (fill (type background)))\n')
    for n, name, ptype in left_pins:
        L.append(pin(0, -px, sm_left_y(n), SM_PL, name, str(n), ptype))
    for n, name, ptype in right_pins:
        L.append(pin(180, px, sm_right_y(n), SM_PL, name, str(n), ptype))
    L.append('      )\n    )\n')
    return "".join(L)


def lib_pmw3610():
    bh = J1_Y0 + J1_STEP / 2
    px = J1_PX
    pins_def = [
        (1, "GND",    "power_in"),
        (2, "VCC",    "power_in"),
        (3, "NC",     "no_connect"),
        (4, "MOTION", "output"),
        (5, "SCLK",   "input"),
        (6, "MOSI",   "input"),
        (7, "MISO",   "output"),
        (8, "CS",     "input"),
    ]
    L = []
    L.append('    (symbol "PMW3610"\n')
    L.append('      (in_bom yes) (on_board yes)\n')
    L.append('      (property "Reference" "J" (at 0 0 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Value" "PMW3610" (at 0 -2.54 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Footprint" "" (at 0 0 0)\n'
             '        (effects (font (size 1.27 1.27)) (hide yes)))\n')
    L.append('      (symbol "PMW3610_0_1"\n')
    L.append(f'        (rectangle (start {-J1_BW:.4f} {-bh:.4f}) (end {J1_BW:.4f} {bh:.4f})\n'
              '          (stroke (width 0)) (fill (type background)))\n')
    for n, name, ptype in pins_def:
        L.append(pin(0, -px, j1y(n), J1_PL, name, str(n), ptype))
    L.append('      )\n    )\n')
    return "".join(L)


def lib_battery():
    bh = J2_Y0 + J2_STEP / 2
    px = J2_PX
    L = []
    L.append('    (symbol "Battery_Connector"\n')
    L.append('      (in_bom yes) (on_board yes)\n')
    L.append('      (property "Reference" "J" (at 0 0 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Value" "JST-PH_2pin" (at 0 -2.54 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Footprint" "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical" (at 0 0 0)\n'
             '        (effects (font (size 1.27 1.27)) (hide yes)))\n')
    L.append('      (symbol "Battery_Connector_0_1"\n')
    L.append(f'        (rectangle (start {-J2_BW:.4f} {-bh:.4f}) (end {J2_BW:.4f} {bh:.4f})\n'
              '          (stroke (width 0)) (fill (type background)))\n')
    L.append(pin(0, -px, j2y(1), J2_PL, "B+", "1", "passive"))
    L.append(pin(0, -px, j2y(2), J2_PL, "B-", "2", "passive"))
    L.append('      )\n    )\n')
    return "".join(L)


def lib_sw_push():
    """Simple key switch symbol (2-pin passive, horizontal)."""
    BW, PL = 1.524, 3.556
    px = BW + PL   # 5.08mm
    L = []
    L.append('    (symbol "SW_Push"\n')
    L.append('      (in_bom yes) (on_board yes)\n')
    L.append('      (property "Reference" "SW" (at 0 2.032 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Value" "SW_Push" (at 0 -2.032 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Footprint" "MX_Alps_Hybrid:MX-1U-NoLED" (at 0 0 0)\n'
             '        (effects (font (size 1.27 1.27)) (hide yes)))\n')
    L.append('      (symbol "SW_Push_0_1"\n')
    # Switch body: two contacts as circles + actuator line
    L.append('        (circle (center -1.524 0) (radius 0.508)\n'
             '          (stroke (width 0)) (fill (type none)))\n')
    L.append('        (circle (center 1.524 0) (radius 0.508)\n'
             '          (stroke (width 0)) (fill (type none)))\n')
    # Actuator bar slightly above contacts
    L.append('        (polyline (pts (xy -1.524 1.524) (xy 1.524 1.524))\n'
             '          (stroke (width 0.254)) (fill (type none)))\n')
    # Lines from pin stubs to circles
    L.append('        (polyline (pts (xy -3.556 0) (xy -2.032 0))\n'
             '          (stroke (width 0)) (fill (type none)))\n')
    L.append('        (polyline (pts (xy 2.032 0) (xy 3.556 0))\n'
             '          (stroke (width 0)) (fill (type none)))\n')
    L.append(pin(0,   -px, 0, PL, "A", "1", "passive"))
    L.append(pin(180,  px, 0, PL, "B", "2", "passive"))
    L.append('      )\n    )\n')
    return "".join(L)


def lib_diode():
    """1N4148 diode symbol (A anode left, K cathode right)."""
    PL = 2.54
    BW = 1.27
    px = BW + PL   # 3.81mm
    L = []
    L.append('    (symbol "D_1N4148"\n')
    L.append('      (in_bom yes) (on_board yes)\n')
    L.append('      (property "Reference" "D" (at 0 2.032 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Value" "1N4148" (at 0 -2.032 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Footprint" "Diode_SMD:D_SOD-123" (at 0 0 0)\n'
             '        (effects (font (size 1.27 1.27)) (hide yes)))\n')
    L.append('      (symbol "D_1N4148_0_1"\n')
    # Diode triangle (anode side) and bar (cathode)
    L.append('        (polyline (pts (xy -1.27 1.27) (xy -1.27 -1.27) (xy 1.27 0) (xy -1.27 1.27))\n'
             '          (stroke (width 0.254)) (fill (type background)))\n')
    # Cathode bar
    L.append('        (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27))\n'
             '          (stroke (width 0.254)) (fill (type none)))\n')
    # Connecting lines to pins
    L.append('        (polyline (pts (xy -3.81 0) (xy -1.27 0))\n'
             '          (stroke (width 0)) (fill (type none)))\n')
    L.append('        (polyline (pts (xy 1.27 0) (xy 3.81 0))\n'
             '          (stroke (width 0)) (fill (type none)))\n')
    L.append(pin(0,   -px, 0, PL, "A", "A", "passive"))
    L.append(pin(180,  px, 0, PL, "K", "K", "passive"))
    L.append('      )\n    )\n')
    return "".join(L)


def lib_capacitor():
    """100nF capacitor symbol (vertical, pin1 top / pin2 bottom)."""
    PL = 1.524
    BH = 1.016
    py = BH + PL   # 2.54mm
    L = []
    L.append('    (symbol "C_100nF"\n')
    L.append('      (in_bom yes) (on_board yes)\n')
    L.append('      (property "Reference" "C" (at 1.905 0.508 0)\n'
             '        (effects (font (size 1.27 1.27)) (hjustify left)))\n')
    L.append('      (property "Value" "100nF" (at 1.905 -0.508 0)\n'
             '        (effects (font (size 1.27 1.27)) (hjustify left)))\n')
    L.append('      (property "Footprint" "Capacitor_SMD:C_0402_1005Metric" (at 0 0 0)\n'
             '        (effects (font (size 1.27 1.27)) (hide yes)))\n')
    L.append('      (symbol "C_100nF_0_1"\n')
    # Two parallel lines (capacitor plates)
    L.append('        (polyline (pts (xy -2.032 0.508) (xy 2.032 0.508))\n'
             '          (stroke (width 0.508)) (fill (type none)))\n')
    L.append('        (polyline (pts (xy -2.032 -0.508) (xy 2.032 -0.508))\n'
             '          (stroke (width 0.508)) (fill (type none)))\n')
    # Lines to pins
    L.append('        (polyline (pts (xy 0 0.508) (xy 0 2.54))\n'
             '          (stroke (width 0)) (fill (type none)))\n')
    L.append('        (polyline (pts (xy 0 -0.508) (xy 0 -2.54))\n'
             '          (stroke (width 0)) (fill (type none)))\n')
    L.append(pin(90,  0,  py, PL, "+", "1", "passive"))
    L.append(pin(270, 0, -py, PL, "-", "2", "passive"))
    L.append('      )\n    )\n')
    return "".join(L)


def lib_mounting_hole():
    """M2 mounting hole symbol (1 passive pin)."""
    L = []
    L.append('    (symbol "MountingHole_M2"\n')
    L.append('      (in_bom yes) (on_board yes)\n')
    L.append('      (property "Reference" "MH" (at 0 3.556 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Value" "MountingHole_M2" (at 0 -3.556 0)\n'
             '        (effects (font (size 1.27 1.27))))\n')
    L.append('      (property "Footprint" "MountingHole:MountingHole_2mm_M2" (at 0 0 0)\n'
             '        (effects (font (size 1.27 1.27)) (hide yes)))\n')
    L.append('      (symbol "MountingHole_M2_0_1"\n')
    L.append('        (circle (center 0 0) (radius 2.0)\n'
             '          (stroke (width 0.254)) (fill (type none)))\n')
    L.append('        (circle (center 0 0) (radius 1.0)\n'
             '          (stroke (width 0.254)) (fill (type none)))\n')
    L.append(pin(270, 0, 2.54, 0, "M", "1", "passive"))
    L.append('      )\n    )\n')
    return "".join(L)


def lib_power_vcc():
    return """    (symbol "power:VCC"
      (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -1.905 0)
        (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Value" "VCC" (at 0 1.905 0)
        (effects (font (size 1.27 1.27))))
      (symbol "VCC_0_1"
        (pin power_in line (at 0 0 270) (length 0)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))))
      (symbol "VCC_1_1"
        (polyline (pts (xy -0.762 0.508) (xy 0 1.778) (xy 0.762 0.508))
          (stroke (width 0)) (fill (type none)))
        (polyline (pts (xy 0 0) (xy 0 1.016))
          (stroke (width 0)) (fill (type none))))
    )
"""

def lib_power_gnd():
    return """    (symbol "power:GND"
      (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -1.905 0)
        (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Value" "GND" (at 0 -3.81 0)
        (effects (font (size 1.27 1.27))))
      (symbol "GND_0_1"
        (pin power_in line (at 0 0 90) (length 0)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))))
      (symbol "GND_1_1"
        (polyline (pts (xy 0 0) (xy 0 -1.016) (xy 1.016 -1.016)
                       (xy 0 -2.54) (xy -1.016 -1.016) (xy 0 -1.016))
          (stroke (width 0)) (fill (type none))))
    )
"""

# ─── Component instance helpers ──────────────────────────────────────────────

def inst(lib_id, ref, value, x, y, rot=0, ref_dy=-2.54, val_dy=2.54,
         footprint="", extra_props=""):
    return (f'  (symbol (lib_id "{lib_id}") (at {x:.4f} {y:.4f} {rot}) (unit 1)\n'
            f'    (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")\n'
            f'    (property "Reference" "{ref}" (at {x:.4f} {y+ref_dy:.4f} {rot})\n'
            f'      (effects (font (size 1.27 1.27))))\n'
            f'    (property "Value" "{value}" (at {x:.4f} {y+val_dy:.4f} {rot})\n'
            f'      (effects (font (size 1.27 1.27))))\n'
            f'    (property "Footprint" "{footprint}" (at {x:.4f} {y:.4f} {rot})\n'
            f'      (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'{extra_props}'
            f'  )\n')


# ─── Main generate ───────────────────────────────────────────────────────────

def generate():
    P = []

    # ── Header ───────────────────────────────────────────────────────────────
    P.append("""(kicad_sch (version 20231120) (generator eeschema) (generator_version "9.0")
  (paper "A3")
  (title_block
    (title "Keyball39 Custom PCB")
    (date "2026-03-25")
    (rev "1.0")
    (comment 1 "SuperMini nRF52840 + PMW3610 + 22-key matrix (right half)")
    (comment 2 "SPI: MOSI=P0.10  MISO=P1.11  SCK=P1.13  NCS=P1.06  MOTION=P1.04")
    (comment 3 "Matrix: 4x6 (row3=4 keys).  Diode: 1N4148 SOD-123 (COL->SW->D->ROW)")
    (comment 4 "Battery: JST-PH 2pin  B+=BATIN/P0.04  B-=GND")
  )
""")

    # ── lib_symbols ───────────────────────────────────────────────────────────
    P.append("  (lib_symbols\n")
    P.append(lib_supermini())
    P.append(lib_pmw3610())
    P.append(lib_battery())
    P.append(lib_sw_push())
    P.append(lib_diode())
    P.append(lib_capacitor())
    P.append(lib_mounting_hole())
    P.append(lib_power_vcc())
    P.append(lib_power_gnd())
    P.append("  )\n\n")

    # ── U1: SuperMini nRF52840 ────────────────────────────────────────────────
    bh = SM_Y0 + SM_STEP / 2
    P.append(inst("SuperMini_nRF52840", "U1", "SuperMini_nRF52840",
                  U1_X, U1_Y, ref_dy=-(bh+2.0), val_dy=(bh+1.5)))

    # ── J1: PMW3610 ──────────────────────────────────────────────────────────
    j1bh = J1_Y0 + J1_STEP / 2
    P.append(inst("PMW3610", "J1", "PMW3610",
                  J1_X, J1_Y, ref_dy=-(j1bh+2.0), val_dy=(j1bh+1.5)))

    # ── J2: Battery connector ─────────────────────────────────────────────────
    j2bh = J2_Y0 + J2_STEP / 2
    P.append(inst("Battery_Connector", "J2", "JST-PH_2pin",
                  J2_X, J2_Y, ref_dy=-(j2bh+2.0), val_dy=(j2bh+1.5),
                  footprint="Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical"))

    # ── C1, C2: decoupling capacitors ────────────────────────────────────────
    P.append(inst("C_100nF", "C1", "100nF", C1_X, C1_Y, ref_dy=-0.5, val_dy=0.5,
                  footprint="Capacitor_SMD:C_0402_1005Metric"))
    P.append(inst("C_100nF", "C2", "100nF", C2_X, C2_Y, ref_dy=-0.5, val_dy=0.5,
                  footprint="Capacitor_SMD:C_0402_1005Metric"))

    # ── MH1, MH2: mounting holes ──────────────────────────────────────────────
    P.append(inst("MountingHole_M2", "MH1", "MountingHole_M2",
                  MH1_X, MH1_Y, ref_dy=-4.0, val_dy=4.0,
                  footprint="MountingHole:MountingHole_2mm_M2"))
    P.append(inst("MountingHole_M2", "MH2", "MountingHole_M2",
                  MH2_X, MH2_Y, ref_dy=-4.0, val_dy=4.0,
                  footprint="MountingHole:MountingHole_2mm_M2"))

    # ── SW1-SW22 and D1-D22 ──────────────────────────────────────────────────
    pwr_idx = 10
    for row, col, sn, dn in MATRIX:
        cx, cy = cell_sw(row, col)
        dx, dy = cell_d(row, col)
        sw_ref = f"SW{sn}"
        d_ref  = f"D{dn}"

        # Switch instance
        P.append(inst("SW_Push", sw_ref, "SW_Push", cx, cy,
                      ref_dy=-2.0, val_dy=2.0,
                      footprint="MX_Alps_Hybrid:MX-1U-NoLED"))

        # Diode instance (rotation=0, horizontal)
        P.append(inst("D_1N4148", d_ref, "1N4148", dx, dy,
                      ref_dy=-2.0, val_dy=2.0,
                      footprint="Diode_SMD:D_SOD-123"))

        # Wire: SW pin2 (cx+SW_PX, cy) → D pinA (dx-D_PX, dy)
        P.append(wire(cx + SW_PX, cy, dx - D_PX, dy))

        # COL net label on SW pin1 (left side, rotation=180)
        col_name = f"COL{col}"
        P.append(label(col_name, cx - SW_PX, cy, 180))

        # ROW net label on D pinK (right side, rotation=0)
        row_name = f"ROW{row}"
        P.append(label(row_name, dx + D_PX, dy, 0))

    # ── U1 pin connections ────────────────────────────────────────────────────
    SL = 5.08   # stub wire length

    # Left-side pins
    left_conns = {
        1:  ("COL0",   "label"),
        2:  ("COL1",   "label"),
        3:  ("GND",    "power"),
        4:  ("GND",    "power"),
        5:  ("COL2",   "label"),
        6:  ("COL3",   "label"),
        7:  ("COL4",   "label"),
        8:  ("COL5",   "label"),
        9:  ("ROW0",   "label"),
        10: ("ROW1",   "label"),
        11: ("MOTION", "label"),
        12: ("NCS",    "label"),
    }
    right_conns = {
        13: ("ROW2",   "label"),
        14: ("MOSI",   "label"),
        15: ("MISO",   "label"),
        16: ("SCK",    "label"),
        17: ("ROW3",   "label"),
        18: (None,     "nc"),
        19: (None,     "nc"),
        20: (None,     "nc"),
        21: ("VCC",    "power"),
        22: (None,     "nc"),
        23: ("GND",    "power"),
        24: ("BATIN",  "label"),
    }

    pwr_count = [1]

    def add_left(n, net, kind):
        px, py = u1L(n)
        if kind == "power":
            pid = f"#PWR0{pwr_count[0]:02d}"
            pwr_count[0] += 1
            P.append(power_sym(px - 2.54, py, net, pid))
            P.append(wire(px - 2.54, py, px, py))
        elif kind == "label":
            P.append(wire(px - SL, py, px, py))
            P.append(label(net, px - SL, py, 180))
        else:  # nc
            P.append(no_connect(px, py))

    def add_right(n, net, kind):
        px, py = u1R(n)
        if kind == "power":
            pid = f"#PWR0{pwr_count[0]:02d}"
            pwr_count[0] += 1
            P.append(power_sym(px + 2.54, py, net, pid))
            P.append(wire(px, py, px + 2.54, py))
        elif kind == "label":
            P.append(wire(px, py, px + SL, py))
            P.append(label(net, px + SL, py, 0))
        else:
            P.append(no_connect(px, py))

    for n, (net, kind) in left_conns.items():
        add_left(n, net, kind)
    for n, (net, kind) in right_conns.items():
        add_right(n, net, kind)

    # ── J1 PMW3610 connections ────────────────────────────────────────────────
    j1_conns = {
        1: ("GND",    "power"),
        2: ("VCC",    "power"),
        3: (None,     "nc"),
        4: ("MOTION", "label"),
        5: ("SCK",    "label"),
        6: ("MOSI",   "label"),
        7: ("MISO",   "label"),
        8: ("NCS",    "label"),
    }
    for n, (net, kind) in j1_conns.items():
        px, py = j1L(n)
        if kind == "power":
            pid = f"#PWR0{pwr_count[0]:02d}"
            pwr_count[0] += 1
            P.append(power_sym(px - 2.54, py, net, pid))
            P.append(wire(px - 2.54, py, px, py))
        elif kind == "label":
            P.append(wire(px - SL, py, px, py))
            P.append(label(net, px - SL, py, 180))
        else:
            P.append(no_connect(px, py))

    # ── C1 connections: VCC (top) + GND (bottom) ─────────────────────────────
    for cx, cy, ci in [(C1_X, C1_Y, "11"), (C2_X, C2_Y, "12")]:
        # pin1 (top) = VCC
        P.append(power_sym(cx, cy - C_PY - 2.54, "VCC", f"#PWR0{pwr_count[0]:02d}"))
        pwr_count[0] += 1
        P.append(wire(cx, cy - C_PY - 2.54, cx, cy - C_PY))
        # pin2 (bottom) = GND
        P.append(power_sym(cx, cy + C_PY + 2.54, "GND", f"#PWR0{pwr_count[0]:02d}", rot=180))
        pwr_count[0] += 1
        P.append(wire(cx, cy + C_PY, cx, cy + C_PY + 2.54))

    # ── J2 battery connections ────────────────────────────────────────────────
    # pin1 B+ → BATIN net label
    bp_x, bp_y = j2L(1)
    P.append(wire(bp_x - SL, bp_y, bp_x, bp_y))
    P.append(label("BATIN", bp_x - SL, bp_y, 180))
    # pin2 B- → GND
    bm_x, bm_y = j2L(2)
    P.append(power_sym(bm_x - 2.54, bm_y, "GND", f"#PWR0{pwr_count[0]:02d}"))
    pwr_count[0] += 1
    P.append(wire(bm_x - 2.54, bm_y, bm_x, bm_y))

    # ── MH1, MH2: no-connect on mounting pin ─────────────────────────────────
    P.append(no_connect(MH1_X, MH1_Y + 2.54))
    P.append(no_connect(MH2_X, MH2_Y + 2.54))

    # ── Footer ───────────────────────────────────────────────────────────────
    P.append(")\n")
    return "".join(P)


if __name__ == "__main__":
    out = "/home/user/repos/make-keybord/keyball39_custom.kicad_sch"
    content = generate()
    with open(out, "w") as f:
        f.write(content)
    print(f"Schematic written to: {out}")
    print(f"File size: {len(content):,} bytes")
    print()
    print("Components:")
    print("  U1  SuperMini nRF52840 socket")
    print("  J1  PMW3610 (8-pin SPI sensor)")
    print("  J2  Battery JST-PH 2-pin")
    print("  C1,C2  100nF decoupling capacitors")
    print("  SW1-SW22  Key switches (MX-compatible)")
    print("  D1-D22   1N4148 diodes (SOD-123)")
    print("  MH1,MH2  M2 mounting holes")
    print()
    print("Key matrix net labels:")
    print("  COL0-5  column lines (from SuperMini left-side pins 1,2,5,6,7,8)")
    print("  ROW0-3  row lines    (from SuperMini pins 9,10,13,17)")
    print("  MOTION/NCS/MOSI/MISO/SCK  SPI signals to PMW3610")
    print("  BATIN   battery positive (J2 pin1 → SuperMini pin24)")
