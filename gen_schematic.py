#!/usr/bin/env python3
"""
nRF52840 (SuperMini) + PMW3360 Breakout KiCad Schematic Generator

Pin mapping:
  SuperMini nRF52840:
    Left  col: TX(P0.06), RX(P0.08), GND, GND, SDA(P0.17), SCL(P0.20),
               P0.22, P0.24, P1.00, P0.11, MOTION(P1.04), NCS(P1.06)
    Right col: NFC1(P0.09), MOSI(P0.10), MISO(P1.11), SCK(P1.13),
               P1.15, AIN0(P0.02), AIN5(P0.29), AIN7(P0.31),
               VCC, RST, GND, BATIN(P0.04)

  PMW3360 Breakout (8-pin):
    1:GND  2:VCC  3:NC  4:MOTION  5:SCLK  6:MOSI  7:MISO  8:CS

SPI connections:
  MOSI  : SuperMini pin14 (P0.10)  → PMW3360 pin6
  MISO  : SuperMini pin15 (P1.11)  → PMW3360 pin7
  SCK   : SuperMini pin16 (P1.13)  → PMW3360 pin5
  NCS   : SuperMini pin12 (P1.06)  → PMW3360 pin8
  MOTION: SuperMini pin11 (P1.04)  → PMW3360 pin4
"""

import uuid

def uid():
    return str(uuid.uuid4())

# ─── Layout ────────────────────────────────────────────────────────────────
U1_X, U1_Y = 100.0, 100.0   # SuperMini centre
J1_X, J1_Y = 162.0, 107.0   # PMW3360 connector centre

# SuperMini: body half-width / pin span
SM_BW   = 7.62              # body half-width (x)
SM_PL   = 2.54              # pin length
SM_PX   = SM_BW + SM_PL    # pin endpoint x-distance from centre = 10.16
SM_Y0   = 13.97             # top pin y (local, positive = up)
SM_STEP = 2.54              # pin pitch

# PMW3360 connector: all 8 pins on left side
J1_BW   = 3.81
J1_PL   = 5.08
J1_PX   = J1_BW + J1_PL    # = 8.89
J1_Y0   = 8.89
J1_STEP = 2.54


def sm_left_y(n):   # local y for SuperMini left-side pin n (1-12)
    return SM_Y0 - (n - 1) * SM_STEP

def sm_right_y(n):  # local y for SuperMini right-side pin n (13-24)
    return SM_Y0 - (n - 13) * SM_STEP

def j1_y(n):        # local y for PMW3360 pin n (1-8)
    return J1_Y0 - (n - 1) * J1_STEP


def pin(angle, x, y, length, name, number, ptype="bidirectional"):
    return (
        f'        (pin {ptype} line (at {x:.4f} {y:.4f} {angle}) (length {length:.4f})\n'
        f'          (name "{name}" (effects (font (size 1.016 1.016))))\n'
        f'          (number "{number}" (effects (font (size 1.016 1.016)))))\n'
    )


def lib_supermini():
    """Define SuperMini nRF52840 symbol in lib_symbols."""
    bh = SM_Y0 + SM_STEP / 2          # body half-height
    px = SM_PX

    left_pins = [
        (1,  "TX/P0.06",      "bidirectional"),
        (2,  "RX/P0.08",      "bidirectional"),
        (3,  "GND",           "power_in"),
        (4,  "GND",           "power_in"),
        (5,  "SDA/P0.17",     "bidirectional"),
        (6,  "SCL/P0.20",     "bidirectional"),
        (7,  "P0.22",         "bidirectional"),
        (8,  "P0.24",         "bidirectional"),
        (9,  "P1.00",         "bidirectional"),
        (10, "P0.11",         "bidirectional"),
        (11, "MOTION/P1.04",  "output"),
        (12, "NCS/P1.06",     "output"),
    ]
    right_pins = [
        (13, "NFC1/P0.09",   "bidirectional"),
        (14, "MOSI/P0.10",   "output"),
        (15, "MISO/P1.11",   "input"),
        (16, "SCK/P1.13",    "output"),
        (17, "P1.15",        "bidirectional"),
        (18, "AIN0/P0.02",   "input"),
        (19, "AIN5/P0.29",   "input"),
        (20, "AIN7/P0.31",   "input"),
        (21, "VCC",          "power_out"),
        (22, "RST",          "input"),
        (23, "GND",          "power_in"),
        (24, "BATIN/P0.04",  "input"),
    ]

    lines = []
    lines.append('    (symbol "SuperMini_nRF52840"\n')
    lines.append('      (in_bom yes) (on_board yes)\n')
    lines.append('      (property "Reference" "U" (at 0 0 0)\n')
    lines.append('        (effects (font (size 1.27 1.27))))\n')
    lines.append('      (property "Value" "SuperMini_nRF52840" (at 0 -2.54 0)\n')
    lines.append('        (effects (font (size 1.27 1.27))))\n')
    lines.append('      (property "Footprint" "Connector_PinSocket_2.54mm:PinSocket_1x24_P2.54mm_Vertical" (at 0 -5.08 0)\n')
    lines.append('        (effects (font (size 1.27 1.27)) (hide yes)))\n')
    lines.append('      (symbol "SuperMini_nRF52840_0_1"\n')
    lines.append(f'        (rectangle (start {-SM_BW:.4f} {-bh:.4f}) (end {SM_BW:.4f} {bh:.4f})\n')
    lines.append('          (stroke (width 0)) (fill (type background)))\n')

    for n, name, ptype in left_pins:
        y = sm_left_y(n)
        lines.append(pin(0, -px, y, SM_PL, name, str(n), ptype))

    for n, name, ptype in right_pins:
        y = sm_right_y(n)
        lines.append(pin(180, px, y, SM_PL, name, str(n), ptype))

    lines.append('      )\n')
    lines.append('    )\n')
    return "".join(lines)


def lib_pmw3360():
    """Define PMW3360 Breakout connector symbol."""
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

    lines = []
    lines.append('    (symbol "PMW3360_Breakout"\n')
    lines.append('      (in_bom yes) (on_board yes)\n')
    lines.append('      (property "Reference" "J" (at 0 0 0)\n')
    lines.append('        (effects (font (size 1.27 1.27))))\n')
    lines.append('      (property "Value" "PMW3360_Breakout" (at 0 -2.54 0)\n')
    lines.append('        (effects (font (size 1.27 1.27))))\n')
    lines.append('      (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" (at 0 -5.08 0)\n')
    lines.append('        (effects (font (size 1.27 1.27)) (hide yes)))\n')
    lines.append('      (symbol "PMW3360_Breakout_0_1"\n')
    lines.append(f'        (rectangle (start {-J1_BW:.4f} {-bh:.4f}) (end {J1_BW:.4f} {bh:.4f})\n')
    lines.append('          (stroke (width 0)) (fill (type background)))\n')

    for n, name, ptype in pins_def:
        y = j1_y(n)
        lines.append(pin(0, -px, y, J1_PL, name, str(n), ptype))

    lines.append('      )\n')
    lines.append('    )\n')
    return "".join(lines)


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


def instance_supermini(x, y):
    """Place SuperMini U1 on the schematic."""
    bh = SM_Y0 + SM_STEP / 2
    ref_y = y - bh - 2.0
    val_y = y + bh + 1.5
    return f"""  (symbol (lib_id "SuperMini_nRF52840") (at {x:.4f} {y:.4f} 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid()}")
    (property "Reference" "U1" (at {x:.4f} {ref_y:.4f} 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "SuperMini_nRF52840" (at {x:.4f} {val_y:.4f} 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_PinSocket_2.54mm:PinSocket_1x24_P2.54mm_Vertical" (at {x:.4f} {y:.4f} 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
  )
"""


def instance_pmw3360(x, y):
    """Place PMW3360 Breakout J1 on the schematic."""
    bh = J1_Y0 + J1_STEP / 2
    ref_y = y - bh - 2.0
    val_y = y + bh + 1.5
    return f"""  (symbol (lib_id "PMW3360_Breakout") (at {x:.4f} {y:.4f} 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid()}")
    (property "Reference" "J1" (at {x:.4f} {ref_y:.4f} 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "PMW3360_Breakout" (at {x:.4f} {val_y:.4f} 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" (at {x:.4f} {y:.4f} 0)
      (effects (font (size 1.27 1.27)) (hide yes)))
  )
"""


def power_sym(x, y, value, sym_id, rotation=0):
    return f"""  (symbol (lib_id "power:{value}") (at {x:.4f} {y:.4f} {rotation}) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid()}")
    (property "Reference" "{sym_id}" (at {x:.4f} {y:.4f} {rotation})
      (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "{value}" (at {x:.4f} {y:.4f} {rotation})
      (effects (font (size 1.27 1.27))))
  )
"""


def wire(x1, y1, x2, y2):
    return (
        f'  (wire (pts (xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f}))\n'
        f'    (stroke (width 0) (type default))\n'
        f'    (uuid "{uid()}"))\n'
    )


def net_label(text, x, y, rotation=0):
    return (
        f'  (label "{text}" (at {x:.4f} {y:.4f} {rotation})\n'
        f'    (effects (font (size 1.27 1.27)))\n'
        f'    (uuid "{uid()}"))\n'
    )


def no_connect(x, y):
    return f'  (no_connect (at {x:.4f} {y:.4f}) (uuid "{uid()}"))\n'


def junction(x, y):
    return f'  (junction (at {x:.4f} {y:.4f}) (diameter 0) (color 0 0 0 0) (uuid "{uid()}"))\n'


# ─── Pin absolute positions ─────────────────────────────────────────────────
def u1_left_abs(n):
    """Absolute position of SuperMini left-side pin endpoint (n=1..12)."""
    return U1_X - SM_PX, U1_Y - sm_left_y(n)

def u1_right_abs(n):
    """Absolute position of SuperMini right-side pin endpoint (n=13..24)."""
    return U1_X + SM_PX, U1_Y - sm_right_y(n)

def j1_left_abs(n):
    """Absolute position of PMW3360 pin endpoint (n=1..8)."""
    return J1_X - J1_PX, J1_Y - j1_y(n)


def generate():
    parts = []

    # ── Header ──────────────────────────────────────────────────────────────
    parts.append(f"""(kicad_sch (version 20230121) (generator eeschema)
  (paper "A4")
  (title_block
    (title "nRF52840 + PMW3360 Trackball Interface")
    (date "2026-03-21")
    (rev "1.0")
    (comment 1 "SuperMini nRF52840 (nice!nano v2 compatible)")
    (comment 2 "PMW3360 Breakout Board (monkeypad/pmw3360-breakout)")
    (comment 3 "SPI: MOSI=P0.10  MISO=P1.11  SCK=P1.13  NCS=P1.06")
    (comment 4 "MOTION=P1.04  VCC=3.3V from SuperMini pin21")
  )
""")

    # ── lib_symbols ──────────────────────────────────────────────────────────
    parts.append("  (lib_symbols\n")
    parts.append(lib_supermini())
    parts.append(lib_pmw3360())
    parts.append(lib_power_vcc())
    parts.append(lib_power_gnd())
    parts.append("  )\n\n")

    # ── Component instances ──────────────────────────────────────────────────
    parts.append(instance_supermini(U1_X, U1_Y))
    parts.append(instance_pmw3360(J1_X, J1_Y))

    # ── Power symbols & wires for VCC ────────────────────────────────────────
    # U1 pin21 = VCC (right side)
    vcc_u1x, vcc_u1y = u1_right_abs(21)
    parts.append(power_sym(vcc_u1x + 2.54, vcc_u1y, "VCC", "#PWR01"))
    parts.append(wire(vcc_u1x, vcc_u1y, vcc_u1x + 2.54, vcc_u1y))

    # J1 pin2 = VCC
    vcc_j1x, vcc_j1y = j1_left_abs(2)
    parts.append(power_sym(vcc_j1x - 2.54, vcc_j1y, "VCC", "#PWR02"))
    parts.append(wire(vcc_j1x - 2.54, vcc_j1y, vcc_j1x, vcc_j1y))

    # ── Power symbols & wires for GND ────────────────────────────────────────
    # U1 pin3 GND (left side)
    gnd3x, gnd3y = u1_left_abs(3)
    parts.append(power_sym(gnd3x - 2.54, gnd3y, "GND", "#PWR03"))
    parts.append(wire(gnd3x - 2.54, gnd3y, gnd3x, gnd3y))

    # U1 pin4 GND (left side) - merge with junction
    gnd4x, gnd4y = u1_left_abs(4)
    parts.append(power_sym(gnd4x - 2.54, gnd4y, "GND", "#PWR04"))
    parts.append(wire(gnd4x - 2.54, gnd4y, gnd4x, gnd4y))

    # U1 pin23 GND (right side)
    gnd23x, gnd23y = u1_right_abs(23)
    parts.append(power_sym(gnd23x + 2.54, gnd23y, "GND", "#PWR05"))
    parts.append(wire(gnd23x, gnd23y, gnd23x + 2.54, gnd23y))

    # J1 pin1 GND
    gnd_j1x, gnd_j1y = j1_left_abs(1)
    parts.append(power_sym(gnd_j1x - 2.54, gnd_j1y, "GND", "#PWR06"))
    parts.append(wire(gnd_j1x - 2.54, gnd_j1y, gnd_j1x, gnd_j1y))

    # ── SPI signal wiring via net labels ─────────────────────────────────────
    SPI_LABEL_LEN = 5.08   # stub wire from pin to label

    # --- MOSI: U1 pin14 (right) → label → J1 pin6 ---
    mx_u1, my_u1 = u1_right_abs(14)
    parts.append(wire(mx_u1, my_u1, mx_u1 + SPI_LABEL_LEN, my_u1))
    parts.append(net_label("MOSI", mx_u1 + SPI_LABEL_LEN, my_u1, 0))

    mx_j1, my_j1 = j1_left_abs(6)
    parts.append(wire(mx_j1 - SPI_LABEL_LEN, my_j1, mx_j1, my_j1))
    parts.append(net_label("MOSI", mx_j1 - SPI_LABEL_LEN, my_j1, 180))

    # --- MISO: U1 pin15 (right) → label → J1 pin7 ---
    mix_u1, miy_u1 = u1_right_abs(15)
    parts.append(wire(mix_u1, miy_u1, mix_u1 + SPI_LABEL_LEN, miy_u1))
    parts.append(net_label("MISO", mix_u1 + SPI_LABEL_LEN, miy_u1, 0))

    mix_j1, miy_j1 = j1_left_abs(7)
    parts.append(wire(mix_j1 - SPI_LABEL_LEN, miy_j1, mix_j1, miy_j1))
    parts.append(net_label("MISO", mix_j1 - SPI_LABEL_LEN, miy_j1, 180))

    # --- SCK: U1 pin16 (right) → label → J1 pin5 ---
    sx_u1, sy_u1 = u1_right_abs(16)
    parts.append(wire(sx_u1, sy_u1, sx_u1 + SPI_LABEL_LEN, sy_u1))
    parts.append(net_label("SCK", sx_u1 + SPI_LABEL_LEN, sy_u1, 0))

    sx_j1, sy_j1 = j1_left_abs(5)
    parts.append(wire(sx_j1 - SPI_LABEL_LEN, sy_j1, sx_j1, sy_j1))
    parts.append(net_label("SCK", sx_j1 - SPI_LABEL_LEN, sy_j1, 180))

    # --- NCS: U1 pin12 (left) → label → J1 pin8 ---
    ncx_u1, ncy_u1 = u1_left_abs(12)
    parts.append(wire(ncx_u1 - SPI_LABEL_LEN, ncy_u1, ncx_u1, ncy_u1))
    parts.append(net_label("NCS", ncx_u1 - SPI_LABEL_LEN, ncy_u1, 180))

    ncx_j1, ncy_j1 = j1_left_abs(8)
    parts.append(wire(ncx_j1 - SPI_LABEL_LEN, ncy_j1, ncx_j1, ncy_j1))
    parts.append(net_label("NCS", ncx_j1 - SPI_LABEL_LEN, ncy_j1, 180))

    # --- MOTION: U1 pin11 (left) → label → J1 pin4 ---
    motx_u1, moty_u1 = u1_left_abs(11)
    parts.append(wire(motx_u1 - SPI_LABEL_LEN, moty_u1, motx_u1, moty_u1))
    parts.append(net_label("MOTION", motx_u1 - SPI_LABEL_LEN, moty_u1, 180))

    motx_j1, moty_j1 = j1_left_abs(4)
    parts.append(wire(motx_j1 - SPI_LABEL_LEN, moty_j1, motx_j1, moty_j1))
    parts.append(net_label("MOTION", motx_j1 - SPI_LABEL_LEN, moty_j1, 180))

    # ── No-connects for unused pins ──────────────────────────────────────────
    unused_left  = [1, 2, 5, 6, 7, 8, 9, 10]   # U1 left
    unused_right = [13, 17, 18, 19, 20, 22, 24]  # U1 right

    for n in unused_left:
        x, y = u1_left_abs(n)
        parts.append(no_connect(x, y))

    for n in unused_right:
        x, y = u1_right_abs(n)
        parts.append(no_connect(x, y))

    # J1 pin3 NC
    nc3x, nc3y = j1_left_abs(3)
    parts.append(no_connect(nc3x, nc3y))

    # ── Footer ──────────────────────────────────────────────────────────────
    parts.append(")\n")

    return "".join(parts)


if __name__ == "__main__":
    output_path = "/home/user/repos/make-keybord/nrf52840_pmw3360.kicad_sch"
    content = generate()
    with open(output_path, "w") as f:
        f.write(content)
    print(f"Schematic written to: {output_path}")
    print(f"File size: {len(content):,} bytes")
