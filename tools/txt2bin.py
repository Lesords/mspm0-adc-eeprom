#!/usr/bin/env python3
"""TI-TXT -> flat binary converter for MSPM0 PCU firmware.

Usage: txt2bin.py <input.txt> [output.bin]

Pads gaps with 0xFF (erased-flash state), page-aligns the image size,
prints vector table and the ad7291 channel LUT found in the image.
"""
import hashlib
import sys

# Known channel LUT byte sequences (searched in order, first hit reported)
KNOWN_LUTS = [
    (bytes([1, 2, 3, 4, 6, 8, 9, 7]), "bbw2 v2: ch0-7 = A1 A2 A3 A4 A6 A8 A9 A7"),
    (bytes([1, 2, 3, 4, 7, 6, 8, 9]), "bbw2 v1: ch0-7 = A1 A2 A3 A4 A7 A6 A8 A9"),
    (bytes([1, 2, 3, 4, 5, 6, 8, 9]), "stock TI v0.13.1"),
]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src.rsplit(".", 1)[0] + ".bin"

    mem, addr, maxa = {}, 0, 0
    for ln in open(src):
        ln = ln.strip()
        if not ln or ln == "q":
            continue
        if ln.startswith("@"):
            addr = int(ln[1:], 16)
        else:
            for i in range(0, len(ln), 3):
                b = ln[i:i + 2]
                if b.strip():
                    mem[addr] = int(b, 16)
                    addr += 1
                    maxa = max(maxa, addr)

    size = (maxa + 0xFF) & ~0xFF
    buf = bytearray([0xFF] * size)
    for a, v in mem.items():
        buf[a] = v
    open(dst, "wb").write(buf)

    sp = int.from_bytes(buf[0:4], "little")
    rv = int.from_bytes(buf[4:8], "little")
    print(f"{src}: 0x{maxa:X} -> {dst} ({size} bytes)")
    print(f"  vectors SP=0x{sp:08X} RESET=0x{rv:08X}")
    for seq, name in KNOWN_LUTS:
        pos = buf.find(seq)
        if pos >= 0:
            print(f"  LUT [{seq.hex(' ')}] @ 0x{pos:x}  ({name})")
            break
    else:
        print("  !! no known LUT sequence found - verify channel table manually")
    print(f"  md5 {hashlib.md5(buf).hexdigest()}")


if __name__ == "__main__":
    main()
