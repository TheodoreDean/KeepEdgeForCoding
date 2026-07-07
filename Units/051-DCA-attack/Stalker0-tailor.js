/*
 * Stalker0-trailor.js — register-dense trace (same 397-byte units as Stalker0-register.js).
 *
 * Hit detection: (pc - trace_mod_base) == STOP_RVA; trace_mod_base matches Stalker user_data[0].
 * Hit counter is extern volatile gint stop_visit_count (same binding style as index_buf), not gint* —
 * exporting gint* onto a 4-byte slot corrupts memory and SIGSEGVs in Gum.
 * On the 2nd hit at base+STOP_RVA: C only sets trace_active=0 (no on_message from that callout — avoids
 * back-to-back send in Gum). Poller flushes msg_buf/index_buf via send(binTrace) then traceFileFlush for disk.
 * Narrow stalk range (recommended after profiling): Tracer.py --trace-rva-start RVA --trace-rva-size BYTES
 * (same as Stalker0-dense-tailor.js). Derive RVA window from a prior trace: min/max PC in the .so → RVAs,
 * subtract module base, add padding, align start down / end up to 4; ensure STOP_RVA lies inside [start,start+size).
 * Optional: Tracer.py --persist-stalk — skip Stalker.unfollow on hook onLeave for the same thread (reduces Gum
 * "Unable to allocate code slab" / SIGTRAP when crypto is invoked many times; thread stays instrumented between calls).
 */
"use strict";

/** Stop-instruction RVA for hit counting / logging only (default 0xd50). */
const STOP_RVA = 0xd50;

const BUFFER_SIZE = 397 * 10;
const msg_buf = Memory.alloc(BUFFER_SIZE);
const index_buf = Memory.alloc(4);
index_buf.writeUInt(4);
const target_addr = Memory.alloc(8);
target_addr.writeU64(0);
/** Bumped in C when (pc - trace_mod_base) == STOP_RVA; reset on hook onEnter. */
const stop_visit_count_buf = Memory.alloc(4);
stop_visit_count_buf.writeUInt(0);
/** Same as Stalker transform range base[0]; used for RVA hit test in C. */
const trace_mod_base_buf = Memory.alloc(8);
trace_mod_base_buf.writeU64(0);
/** Bumped on each hook onEnter so poller resets its last-seen stop count. */
const hook_epoch_buf = Memory.alloc(4);
hook_epoch_buf.writeU32(0);
/** 1 = record trace units; 0 after 2nd hit at base+STOP_RVA (same export pattern as index_buf). */
const trace_active_buf = Memory.alloc(4);
trace_active_buf.writeUInt(1);

let flushPollerStarted = false;
let pollerHookEpoch = -1;
let pollerLastStopCount = 0;
/** When persist-stalk: tid we last Stalker.follow'd without unfollowing (see traceAddr onLeave). */
let trailorStalkingTid = null;

function flushCmsgBufPartialToHost() {
  const idx = index_buf.readU32();
  if (idx <= 4) {
    return;
  }
  msg_buf.writeU32(idx);
  send("binTrace", msg_buf.readByteArray(BUFFER_SIZE));
  index_buf.writeUInt(4);
}

function ensureFlushPoller() {
  if (flushPollerStarted) {
    return;
  }
  flushPollerStarted = true;
  setInterval(function () {
    const ep = hook_epoch_buf.readU32();
    if (ep !== pollerHookEpoch) {
      pollerHookEpoch = ep;
      pollerLastStopCount = 0;
    }
    const cur = stop_visit_count_buf.readU32();
    if (cur > pollerLastStopCount) {
      if (pollerLastStopCount < 1 && cur >= 1) {
        console.log("[Stalker0-trailor] hit 第一次");
      }
      if (pollerLastStopCount < 2 && cur >= 2) {
        console.log("[Stalker0-trailor] hit 第二次 — stop trace + flush C buffer + traceFileFlush");
        flushCmsgBufPartialToHost();
        send({ type: "traceFileFlush" });
      }
      pollerLastStopCount = cur;
    }
  }, 50);
}

const arm64CM = new CModule(
  `
#include <gum/gumstalker.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define BUFFER_SIZE 397*10
#define MAX_UNIT_SIZE 397
#define END_OFFSET 60
#define STOP_RVA_CONST 0x${STOP_RVA.toString(16)}

extern void on_message(int end_flag);
static void onExecution(GumCpuContext* cpu_context, gpointer user_data);
extern char msg_buf[BUFFER_SIZE];
extern volatile gint index_buf;
extern volatile guint64 target_addr;
extern volatile guint64 trace_mod_base;
extern volatile gint stop_visit_count;
extern volatile gint trace_active;

static char flag_block = 1;
static char flag_cont = 0;

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

    if (trace_active == 0)
        return;

    if (trace_mod_base != 0)
    {
        guintptr cur = (guintptr) (gpointer) cpu_context->pc;
        guintptr mod = (guintptr) trace_mod_base;
        if (cur >= mod && cur - mod == (guintptr) STOP_RVA_CONST)
            stop_visit_count++;
    }

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

    if (trace_mod_base != 0)
    {
        guintptr cur2 = (guintptr) (gpointer) cpu_context->pc;
        guintptr mod2 = (guintptr) trace_mod_base;
        if (cur2 >= mod2 && cur2 - mod2 == (guintptr) STOP_RVA_CONST && stop_visit_count >= 2)
            trace_active = 0;
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
    trace_mod_base: trace_mod_base_buf,
    stop_visit_count: stop_visit_count_buf,
    trace_active: trace_active_buf,
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

function traceAddr(addr, targetModule, opts) {
  opts = opts || {};
  const moduleMap = new ModuleMap();
  const tracedModule = moduleMap.find(addr);
  const baseMod = tracedModule !== null ? tracedModule.base : targetModule.base;
  const tracedSize = tracedModule !== null ? tracedModule.size : targetModule.size;

  let stalkBase = baseMod;
  let stalkSpan = tracedSize;
  const useNarrow =
    typeof opts.traceRvaStart === "number" &&
    typeof opts.traceRvaSize === "number" &&
    opts.traceRvaSize > 0;
  if (useNarrow) {
    stalkBase = baseMod.add(opts.traceRvaStart);
    stalkSpan = opts.traceRvaSize;
    console.log(
      "[Stalker0-trailor] narrow stalk rva=0x" +
        opts.traceRvaStart.toString(16) +
        " size=0x" +
        opts.traceRvaSize.toString(16) +
        " -> " +
        stalkBase +
        " .. " +
        stalkBase.add(stalkSpan)
    );
  } else {
    console.log("[Stalker0-trailor] full-module stalk (heavy on Gum); pass --trace-rva-start/--trace-rva-size to narrow.");
  }

  const persistStalk = opts.persistStalk === true;
  if (persistStalk) {
    console.log(
      "[Stalker0-trailor] persist-stalk: onLeave will not Stalker.unfollow (same tid skips re-follow); " +
        "if crypto runs on different threads, omit --persist-stalk or expect extra slab use per tid."
    );
  }

  const stopAddr = baseMod.add(STOP_RVA);
  const stalkEnd = stalkBase.add(stalkSpan);
  const stopInStalkRange =
    stopAddr.compare(stalkBase) >= 0 && stopAddr.compare(stalkEnd) < 0;
  const stopInModule =
    stopAddr.compare(baseMod) >= 0 && stopAddr.compare(baseMod.add(tracedSize)) < 0;
  if (stopInModule && stopInStalkRange) {
    console.log(
      "[Stalker0-trailor] stop PC at " +
        stopAddr +
        " (rva=0x" +
        STOP_RVA.toString(16) +
        "); 2nd hit stops trace + mid flush; 1st/2nd logged via poller"
    );
  } else if (stopInModule && useNarrow && !stopInStalkRange) {
    console.error(
      "[Stalker0-trailor] STOP_RVA 0x" +
        STOP_RVA.toString(16) +
        " not inside narrow [rva,rva+size); widen --trace-rva-* or hits will never count."
    );
  } else if (!stopInModule) {
    console.error(
      "[Stalker0-trailor] stop RVA 0x" +
        STOP_RVA.toString(16) +
        " outside module; stop logic disabled."
    );
  }

  console.log(JSON.stringify(targetModule));

  Interceptor.attach(addr, {
    onEnter: function (args) {
      hook_epoch_buf.writeU32(hook_epoch_buf.readU32() + 1);
      stop_visit_count_buf.writeUInt(0);
      trace_active_buf.writeUInt(1);
      trace_mod_base_buf.writePointer(baseMod);
      console.log("input===" + hex(args[0].readByteArray(0x10)));
      send("start", args[0].readByteArray(0x10));
      this.tid = Process.getCurrentThreadId();
      if (persistStalk && trailorStalkingTid === this.tid) {
        /* Already following this thread; avoid follow/unfollow churn (Gum code slabs). */
      } else {
        if (persistStalk && trailorStalkingTid !== null && trailorStalkingTid !== this.tid) {
          console.warn(
            "[Stalker0-trailor] persist-stalk: tid changed " + trailorStalkingTid + " -> " + this.tid + "; unfollow old"
          );
          Stalker.unfollow(trailorStalkingTid);
          Stalker.flush();
          Stalker.garbageCollect();
        }
        stalkerTraceRangeC(this.tid, stalkBase, stalkSpan);
        if (persistStalk) {
          trailorStalkingTid = this.tid;
        }
      }
    },
    onLeave: function () {
      Stalker.flush();
      Stalker.garbageCollect();
      if (!persistStalk) {
        Stalker.unfollow(this.tid);
        trailorStalkingTid = null;
      }
      send({
        type: "fin",
        tid: this.tid,
      });
    },
  });
}

(() => {
  ensureFlushPoller();
  console.log("----- start trace (Stalker0-trailor.js) -----");

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
      traceAddr(targetAddress, targetModule, {
        traceRvaStart: payload.traceRvaStart,
        traceRvaSize: payload.traceRvaSize,
        persistStalk: payload.persistStalk === true,
      });
    }
  });
})();
