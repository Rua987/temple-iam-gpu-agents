"""Applique Profile1 stock (courbe vide) et Profile2 undervolt actif."""

from __future__ import annotations

import re
import shutil
import struct
import subprocess
import time
from pathlib import Path

PROFILE_CFG = Path(
    r"C:\Program Files (x86)\MSI Afterburner\Profiles"
    r"\VEN_10DE&DEV_1F10&SUBSYS_17111043&REV_A1&BUS_1&DEV_0&FN_0.cfg"
)
AFTERBURNER = Path(r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe")
HEADER = bytes.fromhex("0000020080000000")
POINT_COUNT = 128
RECORD_SIZE = 12


def read_points(data: bytes) -> list[tuple[int, float, float]]:
    points = []
    for i in range(POINT_COUNT):
        offset = 8 + i * RECORD_SIZE
        flags, mv, mhz = struct.unpack("<Iff", data[offset : offset + RECORD_SIZE])
        points.append((flags, mv, mhz))
    return points


def encode_curve(points: list[tuple[int, float, float]]) -> str:
    buf = bytearray(HEADER)
    for flags, mv, mhz in points:
        buf.extend(struct.pack("<Iff", flags, mv, mhz))
    while len(buf) < 3224:
        buf.append(0)
    return buf.hex().upper()


def build_efficient_curve(source_hex: str, plateau_mv: float, plateau_mhz: float) -> str:
    base = read_points(bytes.fromhex(source_hex))
    out = [(flags, mv, plateau_mhz if mv >= plateau_mv else mhz) for flags, mv, mhz in base]
    return encode_curve(out)


def replace_vfcurve_lines(text: str, profile1_hex: str, profile2_hex: str) -> str:
    current = None
    out_lines = []
    for line in text.splitlines():
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
        if line.startswith("VFCurve="):
            if current == "Profile1":
                out_lines.append(f"VFCurve={profile1_hex}")
                continue
            if current == "Profile2":
                out_lines.append(f"VFCurve={profile2_hex}")
                continue
        out_lines.append(line)
    return "\n".join(out_lines) + "\n"


def extract_profile2_hex(text: str) -> str:
    current = None
    for line in text.splitlines():
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
        if line.startswith("VFCurve=") and current == "Profile2":
            return line.split("=", 1)[1]
    raise RuntimeError("VFCurve Profile2 introuvable")


def patch_profile_cfg(plateau_mv: float = 600.0, plateau_mhz: float = 900.0) -> None:
    text = PROFILE_CFG.read_text(encoding="utf-8", errors="ignore")
    backup = PROFILE_CFG.with_suffix(".cfg.bak_curve")
    if not backup.exists():
        shutil.copy2(PROFILE_CFG, backup)

    source_text = backup.read_text(encoding="utf-8", errors="ignore")
    source_hex = extract_profile2_hex(source_text)
    efficient_hex = build_efficient_curve(source_hex, plateau_mv, plateau_mhz)
    text = replace_vfcurve_lines(text, profile1_hex="", profile2_hex=efficient_hex)
    PROFILE_CFG.write_text(text, encoding="utf-8")

    print(f"[OK] Backup: {backup}")
    print("[OK] Profile1: VFCurve vide (stock usine)")
    print(f"[OK] Profile2: plateau {plateau_mhz:.0f} MHz des {plateau_mv:.0f} mV")


def reload_profiles():
    for slot in (1, 2, 1):
        subprocess.run([str(AFTERBURNER), f"-profile{slot}"], capture_output=True, timeout=10)
        time.sleep(3)


def main():
    subprocess.run(["taskkill", "/IM", "MSIAfterburner.exe", "/F"], capture_output=True, text=True)
    time.sleep(2)
    patch_profile_cfg(plateau_mv=600.0, plateau_mhz=900.0)
    subprocess.Popen([str(AFTERBURNER)])
    time.sleep(5)
    reload_profiles()
    print("[OK] Profils recharges (fin sur profile1)")


if __name__ == "__main__":
    main()
