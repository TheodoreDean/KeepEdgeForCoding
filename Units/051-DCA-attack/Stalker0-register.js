/*
 * Stalker0.js — register-dense / low-mem-emphasis trace (Luckin workflow)
 *
 * Every instrumented instruction inside the hooked module range emits one
 * full 397-byte unit: block marker (Y/N), PC, raw opcode, SP, X0–X28, FP, LR,
 * and 128 bytes of SIMD/FP state (same layout as the legacy “memory” path).
 *
 * There is no special ld/st pairing or last_load_flag chain — less branching
 * in the transform, smaller conceptual surface for “mem vs non-mem”, and a
 * single record shape for offline analysis that correlates on register values.
 *
 * Trade-off: higher bytes/sec than the legacy mix of 13-byte + 397-byte units.
 * TracerGrindConvertor.py expects the legacy stream — use Stalker0-original.js
 * with that pipeline; for register-centric work, parse the fixed 397-byte
 * records directly (or extend the convertor).
 */
"use strict";

const BUFFER_SIZE = 397 * 10;
const msg_buf = Memory.alloc(BUFFER_SIZE);
const index_buf = Memory.alloc(4);
index_buf.writeUInt(4);
const target_addr = Memory.alloc(8);
target_addr.writeU64(0);

const arm64CM = new CModule(
  `
#include <gum/gumstalker.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define BUFFER_SIZE 397*10
#define MAX_UNIT_SIZE 397
#define END_OFFSET 60

extern void on_message(int end_flag);
static void onExecution(GumCpuContext* cpu_context, gpointer user_data);
extern char msg_buf[BUFFER_SIZE];
extern volatile gint index_buf;
extern volatile guint64 target_addr;

/* bit0: 1 = new basic block (write 'Y'), 0 = continuation ('N') */
static char flag_block = 1;
static char flag_cont = 0;

/*
 * Binary unit (397 bytes), repeated per instruction in range:
 *   1: 'Y'(0x59) or 'N'(0x4e) — basic-block boundary marker
 *   8: PC
 *   4: instruction word at PC
 *   8: SP
 *   8*29: x0..x28
 *   8: FP
 *   8: LR
 * 128: V registers (as in legacy full path)
 */

void transform(GumStalkerIterator* iterator,
    GumStalkerOutput* output,
    gpointer user_data)
{
    cs_insn* insn;
    bool newblock = true;

    gpointer base = *(gpointer*) user_data;
    gpointer end = *(gpointer*) (user_data + sizeof(gpointer));

    while (gum_stalker_iterator_next(iterator, &insn))
    {
        gboolean in_target = (gpointer) insn->address >= base && (gpointer) insn->address < end;
        if (in_target)
        {
            gum_stalker_iterator_put_callout(
                iterator,
                onExecution,
                newblock ? &flag_block : &flag_cont,
                NULL);
            newblock = false;
        }
        gum_stalker_iterator_keep(iterator);
    }
}

static void
onExecution(GumCpuContext* cpu_context,
    gpointer user_data)
{
    char flags = *(char*) user_data;

    if (index_buf > BUFFER_SIZE - MAX_UNIT_SIZE)
    {
        memcpy(msg_buf, &(int) index_buf, 4);
        on_message(0);
        index_buf = 4;
    }

    if ((flags & 1) > 0)
        msg_buf[index_buf] = 'Y';
    else
        msg_buf[index_buf] = 'N';
    index_buf++;

    memcpy(msg_buf + index_buf, &(cpu_context->pc), 8);
    index_buf = index_buf + 8;

    memcpy(msg_buf + index_buf, (gpointer) (cpu_context->pc), 4);
    index_buf = index_buf + 4;

    memcpy(msg_buf + index_buf, &(cpu_context->sp), 8);
    index_buf = index_buf + 8;

    memcpy(msg_buf + index_buf, cpu_context->x, 8 * 29);
    index_buf = index_buf + 8 * 29;

    memcpy(msg_buf + index_buf, &(cpu_context->fp), 8);
    index_buf = index_buf + 8;

    memcpy(msg_buf + index_buf, &(cpu_context->lr), 8);
    index_buf = index_buf + 8;

    memcpy(msg_buf + index_buf, cpu_context->v, 128);
    index_buf = index_buf + 128;

    if (target_addr + END_OFFSET == cpu_context->pc)
    {
        memcpy(msg_buf, &(int) index_buf, 4);
        on_message(1);
        index_buf = 4;
    }
}
`,
  {
    on_message: new NativeCallback(
      function (end_flag) {
        send("binTrace", msg_buf.readByteArray(BUFFER_SIZE));
        if (end_flag) {
          console.log("________________________end_flag____________________");
        }
      },
      "void",
      ["int"]
    ),
    msg_buf,
    index_buf,
    target_addr,
  }
);

const userData = Memory.alloc(Process.pageSize);
function stalkerTraceRangeC(tid, base, size) {
  userData.writePointer(base);
  const pointerSize = Process.pointerSize;
  userData.add(pointerSize).writePointer(base.add(size));

  Stalker.follow(tid, {
    transform: arm64CM.transform,
    data: userData,
  });
}

function hex(arrayBuffer) {
  const byteToHex = [];
  for (let n = 0; n <= 0xff; ++n) byteToHex.push(n.toString(16).padStart(2, "0"));
  const buff = new Uint8Array(arrayBuffer);
  const hexOctets = [];
  for (let i = 0; i < buff.length; ++i) hexOctets.push(byteToHex[buff[i]]);
  return hexOctets.join("");
}

function traceAddr(addr) {
  const moduleMap = new ModuleMap();
  const targetModule = moduleMap.find(addr);
  console.log(JSON.stringify(targetModule));

  Interceptor.attach(addr, {
    onEnter: function (args) {
      console.log("input===" + hex(args[0].readByteArray(0x10)));
      send("start", args[0].readByteArray(0x10));
      this.tid = Process.getCurrentThreadId();
      stalkerTraceRangeC(this.tid, targetModule.base, targetModule.size);
    },
    onLeave: function () {
      Stalker.unfollow(this.tid);
      Stalker.flush();
      Stalker.garbageCollect();
      send({
        type: "fin",
        tid: this.tid,
      });
    },
  });
}

(() => {
  console.log("----- start trace (register-dense Stalker0) -----");

  recv("config", (msg) => {
    const payload = msg.payload;
    console.log(JSON.stringify(payload));
    const libname = payload.libname;
    console.log(`libname:${libname}`);
    if (payload.spawn) {
      console.error("todo: not implemented");
    } else {
      const targetModule = Process.getModuleByName(libname);
      const baseStr = targetModule.base.toString();
      console.log(
        "[Tracer] " +
          libname +
          " base=" +
          baseStr +
          " size=0x" +
          targetModule.size.toString(16) +
          " path=" +
          targetModule.path
      );
      send({
        type: "moduleInfo",
        libname: libname,
        base: baseStr,
        size: targetModule.size,
        path: targetModule.path,
      });
      let targetAddress = null;
      if ("symbol" in payload) {
        targetAddress = targetModule.findExportByName(payload.symbol);
      } else if ("offset" in payload) {
        targetAddress = targetModule.base.add(ptr(payload.offset));
        console.log(`------targetAddress---------:` + targetAddress);
      }
      target_addr.writePointer(targetAddress);
      traceAddr(targetAddress);
    }
  });
})();
