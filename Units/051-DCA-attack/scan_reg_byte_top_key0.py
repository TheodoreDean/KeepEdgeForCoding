#!/usr/bin/env python3
"""
For each (reg, byte) with reg in 0..28 (x0..x28) and byte in 0..7, regenerate traces +
config and run Daredevil; report whether the top-ranked key byte #0 candidate equals
the expected value (default 0x6C). Matches dense_trace_to_daredevil NUM_X=29 GPR slots.

Run from waa-master (or any cwd; script dir is used for dense_trace_to_daredevil.py).

Example:
  python3 scan_reg_byte_top_key0.py \\
    --daredevil /Users/pengyi/gitDir/Daredevil/daredevil \\
    --glob 'StalkerTrace*.trace' \\
    --work-dir ./daredevil_scan_rb \\
    --expected 0x6c
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Must match dense_trace_to_daredevil.NUM_X (GPR slots x0 .. x28 in each unit).
TRACE_NUM_REGS = 29


def parse_daredevil_top_key_byte0(text: str) -> int | None:
    """First '1: 0x..' line after 'Key byte number 0' (sum block)."""
    idx = text.lower().find("key byte number 0")
    if idx < 0:
        return None
    tail = text[idx:]
    m = re.search(r"^\s*1:\s*0x([0-9a-fA-F]+)\b", tail, re.MULTILINE | re.IGNORECASE)
    if not m:
        return None
    return int(m.group(1), 16)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scan reg x0-x28 and byte 0-7; check Daredevil top key byte #0 vs expected."
    )
    ap.add_argument(
        "--daredevil",
        required=True,
        type=Path,
        help="Path to daredevil executable",
    )
    ap.add_argument(
        "--glob",
        default="StalkerTrace*.trace",
        help="Trace glob passed to dense_trace_to_daredevil.py",
    )
    ap.add_argument(
        "--work-dir",
        type=Path,
        default=Path("./daredevil_scan_rb"),
        help="Parent directory for per-(reg,byte) output packs",
    )
    ap.add_argument(
        "--expected",
        type=lambda s: int(s, 0),
        default=0x6C,
        help="Expected top-1 key byte #0 candidate (default: 0x6C)",
    )
    ap.add_argument("--nsamples", type=int, default=120000)
    anchor = ap.add_mutually_exclusive_group()
    anchor.add_argument("--anchor-pc", type=lambda s: int(s, 0), default=None)
    anchor.add_argument("--anchor-delta", type=lambda s: int(s, 0), default=None)
    anchor.add_argument("--anchor-unit-index", type=int, default=None)
    ap.add_argument("--skip-units", type=int, default=0)
    ap.add_argument(
        "--daredevil-transpose",
        action="store_true",
        help="Pass --daredevil-transpose to dense_trace_to_daredevil.py",
    )
    ap.add_argument(
        "--keep-packs",
        action="store_true",
        help="Do not delete per-(reg,byte) output directories after each run",
    )
    args = ap.parse_args()

    script_dir = Path(__file__).resolve().parent
    dense = script_dir / "dense_trace_to_daredevil.py"
    if not dense.is_file():
        print(f"Missing {dense}", file=sys.stderr)
        return 1
    if not args.daredevil.is_file():
        print(f"Missing daredevil: {args.daredevil}", file=sys.stderr)
        return 1

    args.work_dir = args.work_dir.resolve()
    args.work_dir.mkdir(parents=True, exist_ok=True)

    exp = args.expected & 0xFF
    anchor_args: list[str] = []
    if args.anchor_pc is not None:
        anchor_args.extend(["--anchor-pc", hex(args.anchor_pc)])
    elif args.anchor_delta is not None:
        anchor_args.extend(["--anchor-delta", hex(args.anchor_delta)])
    elif args.anchor_unit_index is not None:
        anchor_args.extend(["--anchor-unit-index", str(args.anchor_unit_index)])

    transpose_args = ["--daredevil-transpose"] if args.daredevil_transpose else []

    print(
        f"expected_top_key0=0x{exp:02x}  glob={args.glob!r}  nsamples={args.nsamples}  "
        f"work_dir={args.work_dir}  trace_regs=x0..x{TRACE_NUM_REGS - 1} (NUM_X={TRACE_NUM_REGS})"
    )
    print("reg  byte  top0  match")
    any_match = False

    for reg in range(TRACE_NUM_REGS):
        for byte_idx in range(8):
            pack = args.work_dir / f"r{reg}_b{byte_idx}"
            if pack.exists():
                shutil.rmtree(pack)

            r1 = subprocess.run(
                [
                    sys.executable,
                    str(dense),
                    "--glob",
                    args.glob,
                    "--out-dir",
                    str(pack),
                    "--bytenum",
                    "0",
                    "--nsamples",
                    str(args.nsamples),
                    "--reg",
                    str(reg),
                    "--byte",
                    str(byte_idx),
                    "--skip-units",
                    str(args.skip_units),
                ]
                + anchor_args
                + transpose_args,
                cwd=str(script_dir),
                capture_output=True,
                text=True,
            )
            if r1.returncode != 0:
                print(
                    f"{reg:3d}  {byte_idx:4d}  ERR dense_trace rc={r1.returncode}",
                    file=sys.stderr,
                )
                if r1.stderr:
                    print(r1.stderr[:2000], file=sys.stderr)
                top = None
            else:
                cfg = pack / "daredevil.config"
                if not cfg.is_file():
                    print(f"{reg:3d}  {byte_idx:4d}  ERR no config", file=sys.stderr)
                    top = None
                else:
                    r2 = subprocess.run(
                        [str(args.daredevil), "-c", str(cfg)],
                        capture_output=True,
                        text=True,
                    )
                    blob = (r2.stdout or "") + "\n" + (r2.stderr or "")
                    top = parse_daredevil_top_key_byte0(blob)
                    if r2.returncode != 0 and top is None:
                        print(
                            f"{reg:3d}  {byte_idx:4d}  ERR daredevil rc={r2.returncode}",
                            file=sys.stderr,
                        )
                        print(blob[:1500], file=sys.stderr)

            if top is None:
                print(f"{reg:3d}  {byte_idx:4d}  ---   no")
            else:
                ok = top == exp
                if ok:
                    any_match = True
                print(f"{reg:3d}  {byte_idx:4d}  0x{top:02x}  {'yes' if ok else 'no'}")

            if not args.keep_packs and pack.exists():
                shutil.rmtree(pack)

    print(f"\nany_match_expected= {any_match}")
    return 0 if any_match else 1


if __name__ == "__main__":
    raise SystemExit(main())
