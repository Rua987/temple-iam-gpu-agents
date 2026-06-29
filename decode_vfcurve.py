"""Decode MSI Afterburner VFCurve hex from profile cfg."""
import re
import struct
from pathlib import Path

PROFILE = Path(
    r"C:\Program Files (x86)\MSI Afterburner\Profiles"
    r"\VEN_10DE&DEV_1F10&SUBSYS_17111043&REV_A1&BUS_1&DEV_0&FN_0.cfg"
)


def decode_curve(hexstr: str):
    data = bytes.fromhex(hexstr.strip())
    print(f"total bytes: {len(data)}")
    print(f"header: {data[:8].hex()}")
    offset = 8
    points = []
    while offset + 12 <= len(data):
        chunk = data[offset : offset + 12]
        if chunk == b"\x00" * 12:
            offset += 12
            continue
        # try: 4 pad + 4 voltage + 4 freq OR 4 freq + 4 voltage
        a, b, c = struct.unpack("<III", chunk)
        f1, f2, f3 = struct.unpack("<fff", chunk)
        if f2 > 100 and f2 < 2000 and f3 > 100 and f3 < 4000:
            points.append((f2, f3, offset))
        elif f1 > 100 and f1 < 2000 and f2 > 100 and f2 < 4000:
            points.append((f1, f2, offset))
        offset += 12
    return points


def extract_profile2():
    text = PROFILE.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"\[Profile2\].*?VFCurve=([0-9A-Fa-f]+)", text, re.S)
    if not m:
        print("Profile2 not found")
        return
    hexstr = m.group(1)
    # try 16-byte stride after 8-byte header
    data = bytes.fromhex(hexstr)
    print("=== 16-byte stride ===")
    for i in range(8, min(len(data), 8 + 16 * 20), 16):
        chunk = data[i : i + 16]
        if chunk == b"\x00" * 16:
            continue
        parts = [struct.unpack("<f", chunk[j : j + 4])[0] for j in range(0, 16, 4)]
        print(i, parts)

    print("=== search 800mV / 1526MHz patterns ===")
    for mv in [750, 775, 800, 825]:
        for mhz in [1400, 1450, 1526, 1900]:
            h = struct.pack("<f", float(mhz)).hex()
            print(mv, mhz, h)


if __name__ == "__main__":
    extract_profile2()
