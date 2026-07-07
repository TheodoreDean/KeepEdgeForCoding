#!/usr/bin/env python3
"""
Route A: Frida register-dense RAW trace -> DareDevil matrices (traces.bin, plaintext.bin).

INPUT (only this):
  Raw files from Tracer.py, glob name StalkerTrace[<32 hex>].trace, where the payload
  is a stream of fixed-size units (first byte 'Y' or 'N'):

  - 397-byte units from Stalker0-dense-entire.js or Stalker0-trailor.js / Stalker0-register.js: Y/N, PC, 4-byte insn, SP, x0–x28, FP, LR, V.

  - 393-byte legacy units (older entire.js without raw insn): still accepted for parsing.

NOT supported as input:
  - vStalkerTrace*.trace (Tracergrind binary from TracerGrindConvertor) — wrong format.
  - Legacy Stalker0 mixed 13-byte + 397-byte Frida traces.

Plaintext (guess) is parsed from the filename hex (same as send('start')).

One row per trace file, one column per time sample = Hamming weight of a chosen
byte in a chosen GPR after optional anchor alignment (--anchor-pc | --anchor-delta | --anchor-unit-index).

Example:
  python3 dense_trace_to_daredevil.py \\
    --glob 'StalkerTrace*.trace' \\
    --out-dir daredevil_pack \\
    --nsamples 3000 --reg 5 --byte 0 \\
    --anchor-pc 0x709012345678

ASLR / 多条 trace：绝对 VA 每条不同。请改用 **--anchor-delta** 或 **--anchor-unit-index**
（与 --anchor-pc 三选一）。delta = (锚点 PC − 文件中第 0 个 unit 的 PC)，有符号，可用 python 算一次。

If no anchor mode is set, sampling starts at unit index 0 in each file.
"""

from __future__ import annotations

import argparse
import binascii
import glob
import os
import re
import struct
import sys
from pathlib import Path

import numpy as np

# Stalker0-dense-entire.js / Stalker0-trailor.js / Stalker0-register.js: full 397-byte dense unit
# Older Stalker0-dense-entire: 393-byte (no raw insn after PC) — still parsed
UNIT_GPR393 = 393
UNIT_FULL = 397

PC_OFF = 1
X_STRIDE = 8
# 397: insn at 9..12, SP at 13, X at 21
X_OFF_FULL = 21
NUM_X_FULL = 29
# 393: no insn; SP at 9, X at 17
X_OFF_GPR393 = 17
NUM_X_GPR393 = 29

TRACE_NAME_RE = re.compile(r"StalkerTrace\[([0-9a-fA-F]{32})\]\.trace$")


def layout_x(unit_len: int) -> tuple[int, int]:
    """Return (x_off, num_x) for the given unit size."""
    if unit_len == UNIT_GPR393:
        return X_OFF_GPR393, NUM_X_GPR393
    if unit_len == UNIT_FULL:
        return X_OFF_FULL, NUM_X_FULL
    raise ValueError(f"unsupported dense unit length: {unit_len}")


def hw_u8(b: int) -> int:
    b &= 0xFF
    return int(b).bit_count()


def parse_units(raw: bytes, align_slack: int = 396) -> tuple[list[bytes], int]:
    """Split raw trace into 397-byte or 393-byte units; try small leading offsets for sync.

    Returns (units, unit_len). unit_len is UNIT_FULL or UNIT_GPR393.
    """
    best: list[bytes] = []
    best_len = UNIT_FULL
    for UNIT in (UNIT_FULL, UNIT_GPR393):
        if len(raw) < UNIT:
            continue
        slack = min(align_slack, UNIT - 1, max(0, len(raw) - 1))

        def valid_start(off: int) -> bool:
            if off + UNIT > len(raw):
                return False
            f = raw[off]
            return f in (0x59, 0x4E)

        for off in range(slack + 1):
            if not valid_start(off):
                continue
            units: list[bytes] = []
            p = off
            while p + UNIT <= len(raw):
                if not valid_start(p):
                    break
                units.append(raw[p : p + UNIT])
                p += UNIT
            if len(units) > len(best):
                best = units
                best_len = UNIT
    return best, best_len


def u64_le(b: bytes, off: int) -> int:
    return struct.unpack_from("<Q", b, off)[0]


def x_reg_bytes(unit: bytes, reg: int, unit_len: int) -> bytes:
    x_off, num_x = layout_x(unit_len)
    if not (0 <= reg < num_x):
        raise ValueError(f"reg must be in [0, {num_x - 1}] for this trace (unit_len={unit_len})")
    o = x_off + reg * X_STRIDE
    return unit[o : o + 8]


def leak_hw_byte(unit: bytes, reg: int, byte_idx: int, unit_len: int) -> float:
    """Hamming weight of byte_idx in little-endian AArch64 x<reg> (0..7)."""
    chunk = x_reg_bytes(unit, reg, unit_len)
    b = chunk[byte_idx & 7]
    return float(hw_u8(b))


def plaintext_from_path(path: Path) -> bytes | None:
    m = TRACE_NAME_RE.search(path.name)
    if not m:
        return None
    try:
        return binascii.unhexlify(m.group(1))
    except binascii.Error:
        return None


def find_anchor_index(units: list[bytes], anchor_pc: int | None) -> int:
    if anchor_pc is None:
        return 0
    for i, u in enumerate(units):
        if u64_le(u, PC_OFF) == anchor_pc:
            return i
    return -1


def find_anchor_index_delta(units: list[bytes], delta: int) -> int:
    """First i where PC[i] == (PC[0] + delta) mod 2**64. Stable across ASLR if prelude matches."""
    if not units:
        return -1
    p0 = u64_le(units[0], PC_OFF)
    target = (p0 + delta) % (1 << 64)
    for i, u in enumerate(units):
        if u64_le(u, PC_OFF) == target:
            return i
    return -1


def resolve_anchor_start(
    units: list[bytes],
    anchor_pc: int | None,
    anchor_delta: int | None,
    anchor_unit_index: int | None,
) -> int:
    if anchor_unit_index is not None:
        if 0 <= anchor_unit_index < len(units):
            return anchor_unit_index
        return -1
    if anchor_delta is not None:
        return find_anchor_index_delta(units, anchor_delta)
    return find_anchor_index(units, anchor_pc)


def build_row(
    units: list[bytes],
    start_idx: int,
    nsamples: int,
    reg: int,
    byte_idx: int,
    unit_len: int,
) -> np.ndarray:
    row = np.zeros(nsamples, dtype=np.float32)
    for c in range(nsamples):
        j = start_idx + c
        if j < len(units):
            row[c] = leak_hw_byte(units[j], reg, byte_idx, unit_len)
    return row


def write_config(
    path: Path,
    n_traces: int,
    nsamples: int,
    transpose: bool,
    algorithm: str,
    position: str,
    bytenum: str,
    bitnum: str,
    trace_bin: Path,
    plaintext_bin: Path,
) -> None:
    # Absolute paths so Daredevil finds files when -c points into out-dir but CWD is elsewhere.
    tb = trace_bin.resolve().as_posix()
    pb = plaintext_bin.resolve().as_posix()
    text = f"""# DareDevil experiment — generated by dense_trace_to_daredevil.py
[Traces]
files=1
trace_type=f
transpose={'true' if transpose else 'false'}
index=0
nsamples={nsamples}
trace={tb} {n_traces} {nsamples}

[Guesses]
files=1
guess_type=u
transpose={'true' if transpose else 'false'}
guess={pb} {n_traces} 16

[General]
threads=8
order=1
return_type=double
window=3
algorithm={algorithm}
position={position}
round=0
bytenum={bytenum}
bitnum={bitnum}
top=20
"""
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Dense Frida trace -> DareDevil (route A)")
    ap.add_argument(
        "--glob",
        default="StalkerTrace*.trace",
        help="Glob for .trace files (cwd default: waa-master)",
    )
    ap.add_argument(
        "--out-dir",
        required=True,
        help="Output directory (traces.bin, plaintext.bin, daredevil.config)",
    )
    ap.add_argument("--nsamples", type=int, default=3000, help="Columns / time samples")
    ap.add_argument("--reg", type=int, default=5, help="GPR index 0..28 (397-byte or 393-byte dense traces)")
    ap.add_argument("--byte", type=int, default=0, dest="byte_idx", help="Byte index 0..7 in x<reg>")
    anchor = ap.add_mutually_exclusive_group()
    anchor.add_argument(
        "--anchor-pc",
        type=lambda s: int(s, 0),
        default=None,
        help="Start at first unit whose PC equals this absolute VA (breaks across ASLR batches)",
    )
    anchor.add_argument(
        "--anchor-delta",
        type=lambda s: int(s, 0),
        default=None,
        help="Start at first unit where PC == (PC of unit 0 + delta) mod 2**64; "
        "delta = signed offset from first sampled PC to anchor (ASLR-safe if unit 0 aligns)",
    )
    anchor.add_argument(
        "--anchor-unit-index",
        type=int,
        default=None,
        help="Start at this unit index in every file (0=first unit; ASLR-safe if traces share prelude)",
    )
    ap.add_argument(
        "--skip-units",
        type=int,
        default=0,
        help="After anchor, skip this many additional units before first column",
    )
    ap.add_argument(
        "--plaintext-file",
        default=None,
        help="Raw uint8 file length M*16 (row-major); row order must match "
        "successful traces in sorted --glob order after skips",
    )
    ap.add_argument(
        "--daredevil-transpose",
        action="store_true",
        help="Set transpose=true in CONFIG (try if correlations look wrong)",
    )
    ap.add_argument("--algorithm", default="AES", help="DareDevil [General] algorithm")
    ap.add_argument(
        "--position",
        default="LUT/AES_AFTER_SBOX",
        help="DareDevil position= path (under DareDevil install) or documented token",
    )
    ap.add_argument("--bytenum", default="0", help="Key byte index or 'all'")
    ap.add_argument("--bitnum", default="none", help="none | all | 0..7")
    args = ap.parse_args()

    paths = sorted(glob.glob(args.glob))
    if not paths:
        print("No files matched --glob", file=sys.stderr)
        return 1

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows: list[np.ndarray] = []
    plains: list[bytes] = []

    for fp in paths:
        p = Path(fp)
        raw = p.read_bytes()
        units, unit_len = parse_units(raw)
        if not units:
            print(f"skip (no units): {p}", file=sys.stderr)
            continue

        _x_off, num_x = layout_x(unit_len)
        if not (0 <= args.reg < num_x):
            print(
                f"skip (--reg {args.reg} out of range for unit_len={unit_len}, max {num_x - 1}): {p}",
                file=sys.stderr,
            )
            continue

        ai = resolve_anchor_start(
            units,
            args.anchor_pc,
            args.anchor_delta,
            args.anchor_unit_index,
        )
        if (
            args.anchor_pc is not None
            or args.anchor_delta is not None
            or args.anchor_unit_index is not None
        ) and ai < 0:
            print(f"skip (anchor not resolved): {p}", file=sys.stderr)
            continue

        start = ai + args.skip_units
        if start >= len(units):
            print(f"skip (start past end): {p}", file=sys.stderr)
            continue

        if not args.plaintext_file:
            pt = plaintext_from_path(p)
            if pt is None or len(pt) != 16:
                print(f"skip (no 16B plaintext in name): {p}", file=sys.stderr)
                continue
            plains.append(pt)

        row = build_row(units, start, args.nsamples, args.reg, args.byte_idx, unit_len)
        rows.append(row)

    if not rows:
        print("No valid traces after filtering.", file=sys.stderr)
        return 1

    M = len(rows)
    traces = np.vstack(rows).astype(np.float32)

    if args.plaintext_file:
        guess = np.fromfile(args.plaintext_file, dtype=np.uint8)
        if guess.size != M * 16:
            print(
                f"--plaintext-file must contain exactly {M*16} bytes ({M}x16), got {guess.size}",
                file=sys.stderr,
            )
            return 1
        guess = guess.reshape(M, 16)
    else:
        guess = np.stack([np.frombuffer(pt, dtype=np.uint8) for pt in plains])

    traces.tofile(out / "traces.bin")
    guess.tofile(out / "plaintext.bin")

    write_config(
        out / "daredevil.config",
        n_traces=M,
        nsamples=args.nsamples,
        transpose=args.daredevil_transpose,
        algorithm=args.algorithm,
        position=args.position,
        bytenum=str(args.bytenum),
        bitnum=str(args.bitnum),
        trace_bin=out / "traces.bin",
        plaintext_bin=out / "plaintext.bin",
    )

    print(f"Wrote {out}/ traces.bin ({M}x{args.nsamples}) float32")
    print(f"Wrote {out}/ plaintext.bin ({M}x16) uint8")
    print(f"Wrote {out}/ daredevil.config")
    return 0


if __name__ == "__main__":
    sys.exit(main())
