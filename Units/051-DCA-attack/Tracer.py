
"""
A instruction trace script based on Frida-Stalker.
"""

import argparse
import binascii
import json
import os
import frida
import sys
import subprocess


BUFFER_SIZE = 397*10*100
TRACE_NAME = "StalkerTrace"

class TraceMgr:

    def __init__(self):
        self.traceFile = None
        self.msgBuf = bytearray(BUFFER_SIZE) 
        self.size = 0
        pass

    def trace_symbol(self, lib, symbol):
        pass

    def trace_offset(self, lib, offset):
        pass

    def on_message(self, msg, data):
        if msg['type'] == 'error':
            print(msg)
            return
        if msg['type'] == 'send':
            if msg['payload'] == 'binTrace':
                if self.traceFile is None:
                    return
                # the first 4 bytes is the length of the data
                for x in range(4, int.from_bytes(data[:4], byteorder='little', signed=False)):
                    self.msgBuf[self.size] = data[x]
                    self.size = self.size + 1
                    if self.size == BUFFER_SIZE:
                        self.traceFile.write(self.msgBuf)
                        self.traceFile.flush()
                        self.size = 0
            elif msg['payload'] == 'start':
                print("start")
                self.traceFile = open(TRACE_NAME + "[" + data.hex() + "].trace", "wb")
            elif isinstance(msg.get('payload'), dict) and msg['payload'].get('type') == 'moduleInfo':
                p = msg['payload']
                sz = int(p.get("size", 0))
                print(
                    "[module] %s base=%s size=0x%x\n  path=%s"
                    % (p.get("libname", "?"), p.get("base", "?"), sz, p.get("path", ""))
                )
            elif isinstance(msg.get('payload'), dict) and msg['payload'].get('type') == 'traceFileFlush':
                if self.traceFile is not None and self.size > 0:
                    self.traceFile.write(self.msgBuf[0 : self.size])
                    self.traceFile.flush()
                    self.size = 0
                    for i in range(len(self.msgBuf)):
                        self.msgBuf[i] = 0
            elif isinstance(msg.get('payload'), dict) and msg['payload'].get('type') == 'fin':
                print("-------------------end-------------------")
                if self.traceFile is not None:
                    self.traceFile.write(self.msgBuf[0 : self.size])
                    self.traceFile.flush()
                    self.traceFile.close()
                    self.traceFile = None
                self.size = 0
                for i in range(len(self.msgBuf)):
                    self.msgBuf[i] = 0
            else:
                print(msg['payload'])
            return

def _parse_args():
    parser = argparse.ArgumentParser(usage="FridaTracer -l libname -i symbol|hexaddr target")
    parser.add_argument("-l", "--libname", required=True, 
                        help="Specify a native library like libnative-lib.so")
    parser.add_argument("-i", "--interceptor", required=True, 
                        help="Specity a function (symbol or a hex offset address) to trace.")
    parser.add_argument("target",
                        help="The name of the application to trace.")
    parser.add_argument(
        "--trace-rva-start",
        default=None,
        metavar="RVA",
        help="With Stalker0-dense-tailor.js: start of instrumented range as RVA from -l module base (hex or decimal).",
    )
    parser.add_argument(
        "--trace-rva-size",
        default=None,
        metavar="BYTES",
        help="With Stalker0-dense-tailor.js: length in bytes of instrumented range; use with --trace-rva-start.",
    )
    parser.add_argument(
        "--stop-rva-offset",
        default=None,
        metavar="RVA",
        help="With Stalker0-dense-tailor.js: unfollow when this RVA (module base+offset) is entered; "
        "place after round 1 to drop rounds 2-10.",
    )
    parser.add_argument(
        "--trace-sample-stride",
        type=int,
        default=1,
        metavar="N",
        help="With Stalker0-dense-entire.js / Stalker0-dense-tailor.js: emit one trace unit only every N-th "
        "instrumented in-range instruction (default 1 = all). N=2 roughly halves trace file size; "
        "execution is unchanged. Capped at 256.",
    )
    parser.add_argument(
        "--persist-stalk",
        action="store_true",
        help="With Stalker0-trailor.js: do not Stalker.unfollow on native hook onLeave; same thread skips "
        "re-follow on the next onEnter. Reduces Gum 'Unable to allocate code slab' / SIGTRAP when crypto is "
        "called often; the thread stays stalked between calls (overhead). If crypto uses multiple threads, omit this.",
    )
    args = parser.parse_args()

    return args



def main():
    # Register-dense path for Daredevil: STALKER_SCRIPT=Stalker0-dense-entire.js, Stalker0-dense-tailor.js, or Stalker0-trailor.js
    script_name = os.environ.get("STALKER_SCRIPT", "Stalker0.js")
    script_file = os.path.join(os.path.dirname(__file__), script_name)
    try:
        script = open(script_file, encoding='utf-8').read()
    except:
        raise Exception("Read script error.")

    trace_mgr = TraceMgr()

    args = _parse_args()

    config = {
        "type": "config",
        "payload": {}
    }

    config["payload"]["libname"] = args.libname

    if args.interceptor.startswith("0x") or args.interceptor.startswith("0X"):
        config["payload"]["offset"] = int(args.interceptor, 16)
    else:
        config["payload"]["symbol"] = args.interceptor

    if args.trace_rva_start is not None:
        config["payload"]["traceRvaStart"] = int(args.trace_rva_start, 0)
    if args.trace_rva_size is not None:
        config["payload"]["traceRvaSize"] = int(args.trace_rva_size, 0)
    if args.stop_rva_offset is not None:
        config["payload"]["stopRvaOffset"] = int(args.stop_rva_offset, 0)
    config["payload"]["traceSampleStride"] = max(1, min(256, int(args.trace_sample_stride)))
    if args.persist_stalk:
        config["payload"]["persistStalk"] = True

    device = frida.get_usb_device(1)
    pid = device.get_process(args.target).pid
    session = device.attach(pid)

    script = session.create_script(script)
    script.on("message", trace_mgr.on_message)
    script.load()
    script.post(config)

    print(
        f"Attached to '{args.target}' pid={pid}.\n"
        "  Hook is on the native function at -i; tracing runs only when that function is called "
        "(not when this script starts).\n"
        "  If you see 'start' immediately, the app already invoked crypto (e.g. startup/background).\n"
        "  Optional second session to force calls (pick one that matches your app):\n"
        f"    frida -U -l trigger.js -n '{args.target}' -p {pid}\n"
        f"    frida -U -l trigger-luckin.js -p {pid}"
    )
    print("Stalker script: %s" % (script_name,))
    print("Tracing. Press any key to quit...")

    try:
        input()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()






