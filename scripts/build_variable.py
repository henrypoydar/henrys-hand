"""Build a variable-weight Henry's Hand from the single SemiBold TTF.

Usage: python3 build_variable.py SRC.ttf OUT_DIR
"""
import math
import sys
from pathlib import Path

from fontTools.designspaceLib import (
    AxisDescriptor,
    DesignSpaceDocument,
    InstanceDescriptor,
    SourceDescriptor,
)
from fontTools.ttLib import TTFont
from fontTools import varLib

VERSION = "3.000"

# Offset in font units applied to each side of every stroke.
# Stems in the source are ~90-126 units at 1024 UPM.
MASTERS = {
    "Light": (300, -20),
    "SemiBold": (600, 0),
    "Bold": (700, 7),
}
INSTANCES = {"Light": 300, "Regular": 400, "SemiBold": 600, "Bold": 700}
MAX_MITER = 2.0


def unit(x, y):
    length = math.hypot(x, y)
    return (x / length, y / length) if length else (0.0, 0.0)


def offset_contour(pts, d):
    """Move each point away from the ink by d (outlines are clockwise)."""
    n = len(pts)
    out = []
    for i, (x, y) in enumerate(pts):
        # Nearest distinct neighbours, so duplicate points don't zero the normal.
        j = (i - 1) % n
        while pts[j] == (x, y) and j != i:
            j = (j - 1) % n
        k = (i + 1) % n
        while pts[k] == (x, y) and k != i:
            k = (k + 1) % n
        e1 = unit(x - pts[j][0], y - pts[j][1])
        e2 = unit(pts[k][0] - x, pts[k][1] - y)
        # Away-from-ink normal of a clockwise edge (dx, dy) is (-dy, dx).
        n1 = (-e1[1], e1[0])
        n2 = (-e2[1], e2[0])
        bx, by = unit(n1[0] + n2[0], n1[1] + n2[1])
        cos = bx * n1[0] + by * n1[1]
        scale = min(1 / cos, MAX_MITER) if cos > 0 else 1.0
        out.append((x + bx * d * scale, y + by * d * scale))
    return out


def make_master(src, d, weight, style, path):
    font = TTFont(src)
    glyf, hmtx = font["glyf"], font["hmtx"]
    for name in font.getGlyphOrder():
        glyph = glyf[name]
        advance, lsb = hmtx[name]
        if glyph.numberOfContours > 0 and d:
            coords, ends, _ = glyph.getCoordinates(glyf)
            new, start = [], 0
            for end in ends:
                new += offset_contour(list(coords[start : end + 1]), d)
                start = end + 1
            # Shift right by d so the side bearing holds; widen the advance by 2d.
            for i, (x, y) in enumerate(new):
                coords[i] = (round(x + d), round(y))
            glyph.recalcBounds(glyf)
            lsb = glyph.xMin
        hmtx[name] = (max(0, advance + 2 * d), lsb)
    os2 = font["OS/2"]
    if os2.version < 2:
        # varLib needs the v2+ fields; measure heights from the default glyphs.
        src_glyf = TTFont(src)["glyf"]
        os2.version = 4
        os2.ulCodePageRange1, os2.ulCodePageRange2 = 1, 0
        os2.sxHeight = src_glyf["x"].yMax
        os2.sCapHeight = src_glyf["H"].yMax
        os2.usDefaultChar, os2.usBreakChar, os2.usMaxContext = 0, 32, 0
    os2.usWeightClass = weight
    name = font["name"]
    name.setName(style, 17, 3, 1, 0x409)
    name.setName("Henry's Hand", 16, 3, 1, 0x409)
    font.save(path)


def main(src, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.tag, axis.name = "wght", "Weight"
    axis.minimum, axis.default, axis.maximum = 300, 600, 700
    doc.addAxis(axis)

    for style, (weight, d) in MASTERS.items():
        path = out_dir / f"master-{style}.ttf"
        make_master(src, d, weight, style, path)
        source = SourceDescriptor()
        source.path, source.styleName = str(path), style
        source.location = {"Weight": weight}
        doc.addSource(source)

    for style, weight in INSTANCES.items():
        inst = InstanceDescriptor()
        inst.familyName, inst.styleName = "Henry's Hand", style
        inst.location = {"Weight": weight}
        doc.addInstance(inst)

    vf, _, _ = varLib.build(doc)
    vf["head"].fontRevision = float(VERSION)
    name = vf["name"]
    # Drop the stale Unicode and Mac records from the source; Windows records suffice.
    name.removeNames(platformID=0)
    name.removeNames(platformID=1)
    name.setName(f"{VERSION};HenrysHand-Variable", 3, 3, 1, 0x409)
    name.setName(f"Version {VERSION}", 5, 3, 1, 0x409)
    name.setName("HenrysHand-SemiBold", 6, 3, 1, 0x409)
    vf.save(out_dir / "henrys-hand-variable.ttf")


if __name__ == "__main__":
    main(*sys.argv[1:])
