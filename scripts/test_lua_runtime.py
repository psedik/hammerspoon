#!/usr/bin/env python3
"""Compile the vendored Lua with its Objective-C exception bridge and smoke-test it."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = root / "LuaSkin/lua-5.5.1/src"
with tempfile.TemporaryDirectory(prefix="hs-lua-test-") as directory:
    directory = Path(directory)
    test = directory / "test.m"
    test.write_text(r'''#include "lua.h"
#include "lauxlib.h"
#include "lualib.h"
#import <Foundation/Foundation.h>
#include <assert.h>
static int raiseNative(lua_State *L) {
    @throw [NSException exceptionWithName:@"Expected" reason:@"test" userInfo:nil];
}
int main(int argc, char **argv) {
    @autoreleasepool {
        lua_State *L = luaL_newstate();
        assert(L);
        luaL_openlibs(L);
        lua_pushcfunction(L, raiseNative);
        lua_setglobal(L, "raiseNative");
        int status = luaL_dostring(L,
            "assert(_VERSION == 'Lua 5.5'); "
            "local ok,err=pcall(raiseNative); assert(not ok and err:find('Expected')); "
            "assert(not pcall(error, 'expected')); "
            "local co=coroutine.create(function() coroutine.yield(42); return 99 end); "
            "local ok,v=coroutine.resume(co); assert(ok and v==42); "
            "ok,v=coroutine.resume(co); assert(ok and v==99); "
            "collectgarbage('collect'); assert(2+2==4)");
        if (status) fprintf(stderr, "%s\n", lua_tostring(L, -1));
        assert(status == LUA_OK);
        for (int i = 1; i < argc; i++) {
            status = luaL_loadfile(L, argv[i]);
            if (status) fprintf(stderr, "%s: %s\n", argv[i], lua_tostring(L, -1));
            assert(status == LUA_OK);
            lua_pop(L, 1);
        }
        lua_close(L);
    }
    return 0;
}
''')
    executable = directory / "test"
    command = ["clang", "-O2", "-DLUA_USE_MACOSX", "-I" + str(source),
               "-framework", "Foundation", "-o", str(executable)]
    command += [str(p) for p in sorted(source.glob("*.c")) if p.name not in ("lua.c", "luac.c")]
    command += [str(source / "lobjectivec_exceptions.m"), str(test)]
    subprocess.run(command, check=True)
    scripts = []
    for folder in ("extensions", "Hammerspoon", "LuaSkin/LuaSkin", "LuaSkin/LuaSkinTests"):
        scripts.extend(str(p) for p in sorted((root / folder).rglob("*.lua")))
    subprocess.run([str(executable), *scripts], check=True)
    print(f"Syntax checked {len(scripts)} bundled Lua files")
print("Lua runtime, Objective-C exceptions and coroutine smoke passed")
