#!/usr/bin/env python3
"""
Convert Frida *dense* Stalker traces to Tracergrind binary vStalkerTrace*.trace.

Requires fixed 397-byte dense units (Stalker0-dense-entire.js or register-style dense scripts: PC + raw insn + SP + x0–x28 + FP + LR + V).

Usage:
  python3 TracerGrindConvertor-Dense.py
  python3 TracerGrindConvertor-Dense.py --glob 'StalkerTrace*.trace'
  # Filenames with literal [...] (UUID in brackets): use a wildcard or pass the path;
  #   plain glob treats [...] as a character class and matches nothing.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
import traceback
from multiprocessing import Process
from pathlib import Path

from capstone import Cs, CsError, CS_ARCH_ARM64, CS_MODE_ARM

from TracerGrindHelper import clear_global, header, hook_block, hook_code, hook_mem_access

TRACE_UNIT = 397
MIN_UNIT_SIZE = 13


def resolve_stalker_trace_paths(pattern: str, script_dir: Path) -> list[Path]:
    """Resolve input paths next to this script. Glob ``[...]`` in trace names is a character class;
    use ``glob.escape`` when the pattern has brackets but no ``*``/``?``."""
    p = Path(pattern).expanduser()
    cand = p if p.is_absolute() else (script_dir / p)
    if cand.is_file():
        return [cand.resolve()]

    if "*" in pattern or "?" in pattern:
        return sorted(
            x.resolve()
            for x in script_dir.glob(pattern)
            if x.is_file() and x.name.startswith("StalkerTrace") and x.suffix == ".trace"
        )

    if "[" in pattern or "]" in pattern:
        esc = glob.escape(pattern)
        hits = sorted(script_dir.glob(esc))
        return [x.resolve() for x in hits if x.is_file()]

    lit = script_dir / pattern
    if lit.is_file():
        return [lit.resolve()]
    return []


def parse_dense_units(raw: bytes, align_slack: int = 396) -> list[bytes]:
    """Split dense payload into 397-byte units (same heuristic as dense_trace_to_daredevil)."""
    if len(raw) < TRACE_UNIT:
        return []

    def valid_start(off: int) -> bool:
        if off + TRACE_UNIT > len(raw):
            return False
        f = raw[off]
        return f in (0x59, 0x4E)

    best: list[bytes] = []
    for off in range(min(align_slack + 1, len(raw))):
        if not valid_start(off):
            continue
        units: list[bytes] = []
        p = off
        while p + TRACE_UNIT <= len(raw):
            if not valid_start(p):
                break
            units.append(raw[p : p + TRACE_UNIT])
            p += TRACE_UNIT
        if len(units) > len(best):
            best = units
    return best


def _emit_one_instruction(
    trace_output,
    trace_unit: bytes,
    nexttrace_unit: bytes | None,
) -> None:
    """One dense unit = one AArch64 instruction snapshot (full 397 bytes)."""
    if len(trace_unit) < TRACE_UNIT:
        return

    if trace_unit[0] == 0x59:
        hook_block(trace_output)

    try:
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        md.detail = False
        pc = int.from_bytes(trace_unit[1:9], byteorder="little", signed=False)
        insn = next(md.disasm(trace_unit[9:13], pc), None)
        if insn is None:
            print(
                "WARN: undisassemblable bytes %s at pc %#x"
                % (trace_unit[9:13].hex(), pc),
                file=sys.stderr,
            )
            return

        hook_code(trace_unit[9:13], trace_unit[1:9], 4)

        mne_str = insn.mnemonic
        op_list = insn.op_str.split()
        op_len = len(op_list)
        size = 8
        access = 3
        addr_op = 1
        dest_reg1 = 0
        dest_reg2 = 0
        base_reg = 0
        ext_reg = 0
        float_flag = 0

        if mne_str.startswith("ld"):
            if mne_str[2] not in ("1", "2", "3", "4"):
                access = 0
        elif mne_str.startswith("st"):
            if mne_str[2] not in ("1", "2", "3", "4"):
                access = 1

        if access not in (0, 1):
            return

        if access == 0 and nexttrace_unit is None:
            # Load value would come from following snapshot; skip mem message.
            return

        next_u = nexttrace_unit if nexttrace_unit is not None else trace_unit

        if "w" in mne_str[2:]:
            size = 4
        elif "h" in mne_str[2:]:
            size = 2
        elif "b" in mne_str[2:]:
            size = 1
        if op_list[0].startswith("w") and size > 4:
            size = 4

        if op_list[0].startswith("xzr"):
            dest_reg1 = b"\x00\x00\x00\x00\x00\x00\x00\x00"
        elif op_list[0].startswith("wzr"):
            dest_reg1 = b"\x00\x00\x00\x00"
        else:
            dest_reg_num1 = int(op_list[0][1:-1])
            if op_list[0].startswith("b"):
                size = 1
                float_flag = 1
            elif op_list[0].startswith("h"):
                size = 2
                float_flag = 1
            elif op_list[0].startswith("s"):
                size = 4
                float_flag = 1
            elif op_list[0].startswith("d"):
                size = 8
                float_flag = 1
            elif op_list[0].startswith("q"):
                size = 16
                float_flag = 1
            else:
                if access == 0:
                    dest_reg1 = next_u[21 + 8 * dest_reg_num1 : 21 + 8 * dest_reg_num1 + size]
                elif access == 1:
                    dest_reg1 = trace_unit[21 + 8 * dest_reg_num1 : 21 + 8 * dest_reg_num1 + size]
            if float_flag == 1:
                if access == 0:
                    dest_reg1 = next_u[269 + 16 * dest_reg_num1 : 269 + 16 * dest_reg_num1 + size]
                elif access == 1:
                    dest_reg1 = trace_unit[269 + 16 * dest_reg_num1 : 269 + 16 * dest_reg_num1 + size]

        if "p" in mne_str[2:]:
            if op_list[1].startswith("xzr"):
                dest_reg2 = b"\x00\x00\x00\x00\x00\x00\x00\x00"
            elif op_list[1].startswith("wzr"):
                dest_reg2 = b"\x00\x00\x00\x00"
            else:
                dest_reg_num2 = int(op_list[1][1:-1])
                if float_flag == 1:
                    if access == 0:
                        dest_reg2 = next_u[269 + 16 * dest_reg_num2 : 269 + 16 * dest_reg_num2 + size]
                    elif access == 1:
                        dest_reg2 = trace_unit[269 + 16 * dest_reg_num2 : 269 + 16 * dest_reg_num2 + size]
                else:
                    if access == 0:
                        dest_reg2 = next_u[21 + 8 * dest_reg_num2 : 21 + 8 * dest_reg_num2 + size]
                    elif access == 1:
                        dest_reg2 = trace_unit[21 + 8 * dest_reg_num2 : 21 + 8 * dest_reg_num2 + size]
            size = size * 2
            addr_op = addr_op + 1

        if op_list[addr_op].startswith("#"):
            address = int(op_list[addr_op][1:], 16)
        else:
            if op_list[addr_op].startswith("[x"):
                if op_list[addr_op].endswith("],"):
                    base_reg_num = int(op_list[addr_op][2:-2])
                else:
                    base_reg_num = int(op_list[addr_op][2:-1])
                base_reg = trace_unit[21 + 8 * base_reg_num : 21 + 8 + 8 * base_reg_num]
            elif op_list[addr_op].startswith("[s"):
                base_reg = trace_unit[13:21]
            else:
                return
            address = int.from_bytes(base_reg, byteorder="little", signed=False)

            if op_len > addr_op + 1:
                if op_list[addr_op + 1].startswith("#"):
                    tmp = op_list[addr_op + 1].split("]")
                    address = address + int(tmp[0][1:], 16)
                else:
                    if op_list[addr_op + 1].endswith(","):
                        ext_reg_num = op_list[addr_op + 1].split(",")
                    else:
                        ext_reg_num = op_list[addr_op + 1].split("]")
                    ext_reg_num = int(ext_reg_num[0][1:])
                    if op_list[addr_op + 1].startswith("x"):
                        ext_reg = trace_unit[21 + 8 * ext_reg_num : 21 + 8 + 8 * ext_reg_num]
                    elif op_list[addr_op + 1].startswith("w"):
                        ext_reg = trace_unit[21 + 8 * ext_reg_num : 21 + 4 + 8 * ext_reg_num]
                    else:
                        return
                    ext_reg = int.from_bytes(ext_reg, byteorder="little", signed=True)
                    if op_list[addr_op + 1].endswith(","):
                        if op_len > addr_op + 3:
                            num = op_list[addr_op + 3].split("]")
                            num = int(num[0][1:], 16)
                            ext_reg = ext_reg << num
                    address = address + ext_reg

        hook_mem_access(trace_unit[1:9], access, address, size, dest_reg1, dest_reg2)

    except (CsError, ValueError, IndexError, KeyError) as e:
        print("WARN: skip unit: %s" % e, file=sys.stderr)


def _parse_dense_trace(trace_input, trace_output) -> None:
    raw = trace_input.read()
    units = parse_dense_units(raw)
    if not units:
        raise ValueError("No dense 397-byte units found (wrong format or empty file).")
    for i, unit in enumerate(units):
        nxt = units[i + 1] if i + 1 < len(units) else None
        _emit_one_instruction(trace_output, unit, nxt)


def convertsub(input_path: str, exec_only: bool = False) -> None:
    name = os.path.basename(input_path)
    output_file = os.path.join(os.path.dirname(__file__), "v" + name)
    trace_output = None
    trace_input = None
    try:
        print(name, flush=True)
        if exec_only:

            def _noop_mem(*_a, **_k):
                return

            globals()["hook_mem_access"] = _noop_mem

        clear_global()
        trace_output = open(output_file, "wb", buffering=4096)
        trace_input = open(input_path, "rb")
        header(trace_output)
        _parse_dense_trace(trace_input, trace_output)
    except Exception as e:
        print("%s: %s" % (name, e), file=sys.stderr, flush=True)
        traceback.print_exc()
        if trace_output is not None:
            try:
                trace_output.close()
            except OSError:
                pass
            trace_output = None
            try:
                os.remove(output_file)
            except OSError:
                pass
    finally:
        if trace_input is not None:
            try:
                trace_input.close()
            except OSError:
                pass
        if trace_output is not None:
            try:
                trace_output.close()
            except OSError:
                pass


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Dense StalkerTrace (397-byte units) -> Tracergrind vStalkerTrace*.trace"
    )
    ap.add_argument(
        "--glob",
        default="StalkerTrace*.trace",
        help="Input glob (default: all StalkerTrace*.trace in this directory)",
    )
    ap.add_argument(
        "--exec-only",
        action="store_true",
        help="Omit Tracergrind memory (type 3) messages (same idea as TracerGrindConvertor-luckin).",
    )
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    paths = resolve_stalker_trace_paths(args.glob, here)
    if not paths:
        print(
            "No StalkerTrace*.trace matched %r under %s.\n"
            "  Hint: names like StalkerTrace[uuid].trace need --glob 'StalkerTrace*.trace' "
            "or an explicit path; unescaped [...] is a glob character class."
            % (args.glob, here),
            file=sys.stderr,
        )
        return 1

    procs: list[Process] = []
    for path in paths:
        if not path.name.startswith("StalkerTrace") or not path.name.endswith(".trace"):
            continue
        output_file = os.path.join(os.path.dirname(__file__), "v" + path.name)
        if os.path.exists(output_file):
            print("skip (exists): %s" % output_file, flush=True)
            continue
        p = Process(target=convertsub, args=(str(path), args.exec_only))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()

    return 0


if __name__ == "__main__":
    sys.exit(main())
