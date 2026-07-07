const BUFFER_SIZE = 397*10
const msg_buf = Memory.alloc(BUFFER_SIZE)
const index_buf = Memory.alloc(4)
index_buf.writeUInt(4)
const last_load_flag = Memory.alloc(4)
last_load_flag.writeUInt(0)
const target_addr = Memory.alloc(8)
target_addr.writeU64(0)


const arm64CM = new CModule(`
#include <gum/gumstalker.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define BUFFER_SIZE 397*10
#define MAX_UNIT_SIZE 397
#define MIN_UNIT_SIZE 13
#define END_OFFSET 60  //0x3c, the length of the target function

extern void on_message(int end_flag);
static void onExecution(GumCpuContext* cpu_context, gpointer user_data);
extern char msg_buf[BUFFER_SIZE];
extern volatile gint index_buf;
extern volatile gint last_load_flag;
extern volatile guint64  target_addr;

char flag3 = 3;
char flag1 = 1;
char flag2 = 2;
char flag0 = 0;

/*
 message buffer format : unit of 397 bytes
    1: new blocl flag
    8: instruction address = pc 
    4: instruction bytes
  if memeory access ins:
    8: sp;
    8*29: x[29];
    8: fp;
    8: lr;
	1*128: q[128]
 */

void transform(GumStalkerIterator* iterator,
    GumStalkerOutput* output,
    gpointer user_data)
{
    cs_insn* insn;
    bool newblock = true;
	
	bool mem_ins = false; 
	char* mne = NULL;

    gpointer base = *(gpointer*)user_data;
    gpointer end = *(gpointer*)(user_data + sizeof(gpointer));

    while (gum_stalker_iterator_next(iterator, &insn))
    {
        gboolean in_target = (gpointer)insn->address >= base && (gpointer)insn->address < end;
        if (in_target)
        {
			mne = insn->mnemonic;
			mem_ins = false;
			if ((mne[0] == 's' && mne[1] == 't' ) || (mne[0] == 'l' && mne[1] == 'd') || (last_load_flag == 1)){
				mem_ins = true;
			}

			if (newblock && mem_ins){			
				gum_stalker_iterator_put_callout(iterator, onExecution, &flag3, NULL);
            }
            else if (newblock && !mem_ins){			
				gum_stalker_iterator_put_callout(iterator, onExecution, &flag1, NULL);
            }
			else if (!newblock && mem_ins){				
				gum_stalker_iterator_put_callout(iterator, onExecution, &flag2, NULL);
            }
			else {				
				gum_stalker_iterator_put_callout(iterator, onExecution, &flag0, NULL);
            }
            if(last_load_flag==1){
                last_load_flag = 0;
            }
			if (mne[0] == 'l' && mne[1] == 'd'){
				last_load_flag = 1; // if last instruction is load, msg for the next instruction should send registers too, to compute data loaded
			}
			newblock = false;
        }
        gum_stalker_iterator_keep(iterator);
    }
}

static void
onExecution(GumCpuContext* cpu_context,
    gpointer user_data)
{
    int i = 0;
	char flags = 0;
    //static GMutex msg_lock;
    //g_mutex_lock(&msg_lock);
    flags = *(char*)user_data;
	
	if((flags&2) > 0){
		if(index_buf > BUFFER_SIZE - MAX_UNIT_SIZE){
			memcpy(msg_buf, &(int)index_buf, 4);
			on_message(0);
			index_buf = 4;
		}
		if ((flags&1) > 0) {
			msg_buf[index_buf] = 'Y';
		}
		else {
			msg_buf[index_buf] = 'N';
		}
		index_buf++;

		memcpy(msg_buf + index_buf, &(cpu_context->pc), 8);
		index_buf = index_buf + 8;

		memcpy(msg_buf + index_buf, (gpointer)(cpu_context->pc), 4);
		index_buf = index_buf + 4;

		memcpy(msg_buf + index_buf, &(cpu_context->sp), 8);
		index_buf = index_buf + 8;

		memcpy(msg_buf + index_buf, cpu_context->x, 8*29);
		index_buf = index_buf + 8*29;
			
		memcpy(msg_buf + index_buf, &(cpu_context->fp), 8);
		index_buf = index_buf + 8;

		memcpy(msg_buf + index_buf, &(cpu_context->lr), 8);
		index_buf = index_buf + 8;
		
		memcpy(msg_buf + index_buf, cpu_context->v, 128);
		index_buf = index_buf + 128;	
		
	} else{
		if (index_buf > BUFFER_SIZE - MIN_UNIT_SIZE) {
			memcpy(msg_buf, &(int)index_buf, 4);
			on_message(0);
			index_buf = 4;					
		}
				   
		if ((flags & 1) > 0) {
			msg_buf[index_buf] = 'Y';
		}
		else {
			msg_buf[index_buf] = 'N';
		}
		index_buf++;

		memcpy(msg_buf + index_buf, &(cpu_context->pc), 8);
		index_buf = index_buf + 8;

		memcpy(msg_buf + index_buf, (gpointer)(cpu_context->pc), 4);
		index_buf = index_buf + 4;
	}
	if(target_addr + END_OFFSET == cpu_context->pc){
		memcpy(msg_buf, &(int)index_buf, 4);   // first 4 bytes is for the length of the data
		on_message(1);  // end flag is not really useful for the moment
		index_buf = 4;
	}
    //g_mutex_unlock(&msg_lock);
}
`, {
    on_message: new NativeCallback(function (end_flag) {
		//console.log( msg_buf.readByteArray(200))
		//console.log("js: " + index_buf.readInt());
		send('binTrace', msg_buf.readByteArray(BUFFER_SIZE));
		if(end_flag){
		    console.log("________________________end_flag____________________");
			//console.log(msg_buf.readByteArray(BUFFER_SIZE));
			/**
		    send({
                type: "fin",
                tid: this.tid
            }) **/
		}
	}, 'void', ['int']),
	msg_buf, index_buf, last_load_flag, target_addr
});

const userData = Memory.alloc(Process.pageSize);
function stalkerTraceRangeC(tid, base, size) {
    // const hello = new NativeFunction(cm.hello, 'void', []);
    // hello();
    userData.writePointer(base)
    const pointerSize = Process.pointerSize;
    userData.add(pointerSize).writePointer(base.add(size))
    
    Stalker.follow(tid, {
        transform: arm64CM.transform,
        // onEvent: cm.process,
        data: userData /* user_data */
    })
}


function hex(arrayBuffer)
{
	const byteToHex = [];

	for (let n = 0; n <= 0xff; ++n)
	{
		const hexOctet = n.toString(16).padStart(2, "0");
		byteToHex.push(hexOctet);
	}
    const buff = new Uint8Array(arrayBuffer);
    const hexOctets = []; 

    for (let i = 0; i < buff.length; ++i)
        hexOctets.push(byteToHex[buff[i]]);

    return hexOctets.join("");
}

function traceAddr(addr) {
    let moduleMap = new ModuleMap();
    let targetModule = moduleMap.find(addr);
    console.log(JSON.stringify(targetModule))

    Interceptor.attach(addr, {
        onEnter: function(args) {
			console.log("input===" + hex(args[0].readByteArray(0x10)))
			send('start', args[0].readByteArray(0x10));        // encrypt/decrypt input data: args[1].readByteArray(0x10)
            this.tid = Process.getCurrentThreadId();
            stalkerTraceRangeC(this.tid, targetModule.base, targetModule.size);
        },
        onLeave: function(ret) {
            Stalker.unfollow(this.tid);
			Stalker.flush();
            Stalker.garbageCollect();
            //Thread.sleep(3);
            
            send({
                type: "fin",
                tid: this.tid
            })  
        }
    })
}



(() => {

    console.log(`----- start trace -----`);

    recv("config", (msg) => {
        const payload = msg.payload;
        console.log(JSON.stringify(payload))
        const libname = payload.libname;
        console.log(`libname:${libname}`)
        if(payload.spawn) {
            console.error(`todo: not implemented`)
        } else {
            // const modules = Process.enumerateModules();
            const targetModule = Process.getModuleByName(libname);
            let targetAddress = null;
            if("symbol" in payload) {
                targetAddress = targetModule.findExportByName(payload.symbol);
            } else if("offset" in payload) {
                targetAddress = targetModule.base.add(ptr(payload.offset));
                console.log(`------targetAddress---------:` + targetAddress)
            }
            target_addr.writePointer(targetAddress)
            traceAddr(targetAddress)
        }
    })
})()