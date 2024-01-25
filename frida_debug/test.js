setTimeout(function() {

var il2cpp = Module.getBaseAddress('libil2cpp.so');
var libunity = Module.getBaseAddress('libunity.so');
console.log(`il2cpp: ${il2cpp}`)

function dump_bytearr(arr, len = null) {
    if (len === null) {
        len = arr.add(24).readInt()
    }
    return hexdump(arr.add(32), {length: len})
}

function read_ilstr(str) {
    return str.add(20).readUtf16String()
}


/*Interceptor.attach(libunity.add(0x430bc8), {
    onEnter(args) {
        this.readLen = args[1].toUInt32();
        this.readBuf = args[2];
        console.log(`FileAccessor::Read in: ${args[1]} ${args[2]}`)}, onLeave(retval) {console.log(`FileAccessor::Read ret: ${this.readBuf}, ${this.readLen}, ${hexdump(this.readBuf, this.readLen)}`)
    }
})

Interceptor.attach(libunity.add(0x430868), {
    onEnter(args) {
        console.log(`FileAccessor::Init: ${args[1].readPointer().readUtf8String()} ${args[2]} ${args[3].readPointer().readUtf8String()}`)
    }
})

Interceptor.attach(il2cpp.add(0x3939E90), {
    onEnter(args) {
        var s = args[0].add(20).readUtf16String(); console.log(`CrcHashString: ${s}`)
    }, 
    onLeave(retval) { 
        console.log(retval.add(16).readPointer().add(20).readUtf16String()) 
    },
})*/


Interceptor.attach(il2cpp.add(0x4202CC4), {
    onEnter(args) {
        console.log(`CommonUtility__StringToHash: ${args[0].add(20).readUtf16String()}`)
    },
    onLeave(retval) {
        console.log(`CommonUtility__StringToHash => ${retval.toInt32()}`)
    }
})

/*Interceptor.attach(il2cpp.add(0x4206180), {
    onEnter(args) {
        console.log(`XFilePackage__ReadBytes: pos: ${args[0]}`)
    },
    onLeave(retval) {
        console.log(`XFilePackage__ReadBytes: ${hexdump(retval.add(32), retval.add(24).readInt())}`)
    }
})*/

/*Interceptor.attach(il2cpp.add(0x4207D88), {
    onEnter(args) {
        var decoderCls = args[0].add(0x88).readPointer()
        var decoder = null
        if (decoderCls) {
            decoder = decoderCls.add(24).readPointer().sub(il2cpp)
        }
        console.log(`XFileStream__Read: off ${args[2]} size ${args[3]}, decodeFunc: ${decoder}`)
        this.arr = args[1]
        this.size = args[3].toInt32()
    },
    onLeave(retval) {
        console.log(`XFileStream__Read => ${dump_bytearr(this.arr, this.size)}`)
    }
})*/

Interceptor.attach(il2cpp.add(0x42065B0), {
    onEnter(args) {
        console.log(`XFilePackage__GenFileStream: ${read_ilstr(args[1])} ${dump_bytearr(args[0].add(0x10).readPointer())}`)
        console.log(Thread.backtrace(this.context, Backtracer.FUZZY).map(DebugSymbol.fromAddress).join('\n') + '\n')
    },
    onLeave(retval) {
    }
})

Interceptor.attach(il2cpp.add(0x4202EDC), {
    onEnter(args) {
        console.log(`XFileMgr__GetPackageId: ${args[0].toString(10)}`)
    },
    onLeave(retval) {
        console.log(`XFileMgr__GetPackageId => ${retval.toString(10)}`)
    }
})

Interceptor.attach(il2cpp.add(0x4200C94), {
    onEnter(args) {
        console.log(`XFileConf__Get: ${args[1].toString(10)}`)
    },
    onLeave(retval) {
        console.log(`XFileConf__Get => ${retval.toString(10)}`)
    }
})

Interceptor.attach(il2cpp.add(0x4205B0C), {
    onEnter(args) {
        console.log(`XFilePackageConf__Get: ${args[1].toString(10)}`)
    },
    onLeave(retval) {
        console.log(`XFilePackageConf__Get => ${retval.toString(10)}`)
    }
})

Interceptor.attach(il2cpp.add(0x3845BA4), {
    onEnter(args) {
        console.log(`LuaFileLoader__LoadFromPackage: ${read_ilstr(args[0])}`)
    },
    onLeave(retval) {
    }
})



Interceptor.attach(il2cpp.add(0x42012E4), {
    onEnter(args) {
        console.log(`XFileHashConf__Parse!`)
    },
    onLeave(retval) {
        console.log(`XFileHashConf__Parse finish!`)
        //console.log(`XFileHashConf__Parse: ${hexdump(retval.add(32), retval.add(24).readInt())}`)
    }
})

}, 2000)