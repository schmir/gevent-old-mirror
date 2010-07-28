# Last-changed: 2010-10-05 13:10:02 by ralf

"""
this module installs a custom __import__ function, which switches
sys.modules on a per-thread basis. patch_all must be called from the
gevent thread. the threads will only import unpatched modules.
"""

import imp
import sys
import threading

_orig_import = __import__


class LocalModules(threading.local):
    modules = None  # swap this with sys.modules

local_modules = LocalModules()


def copydict(src, dst):
    if src is dst:
        return
    dst.clear()
    dst.update(src)

_active = [None]


def _my_import(*args, **kwargs):
    do_swap = False
    imp.acquire_lock()
    try:
        do_swap = local_modules.modules is not _active[-1]
        if do_swap:
            save = sys.modules.copy()
            copydict(local_modules.modules, sys.modules)
            _active.append(local_modules.modules)
        return _orig_import(*args, **kwargs)
    finally:
        if do_swap:
            copydict(sys.modules, _active.pop())
            if len(_active) > 1:
                copydict(save, sys.modules)

        imp.release_lock()


def patch_all():
    names = "os time thread threading _threading_local socket ssl select".split()
    LocalModules.modules = sys.modules.copy()
    local_modules.modules = patched = sys.modules.copy()

    for name in names:
        patched.pop(name, None)
    import __builtin__
    __builtin__.__import__ = _my_import

    from gevent import monkey
    monkey.patch_all()


def run_with_unpatched(func, *args, **kwargs):
    save = local_modules.modules
    try:
        local_modules.modules = LocalModules.modules
        return func(*args, **kwargs)
    finally:
        local_modules.modules = save


def import_unpatched(name):
    return run_with_unpatched(__import__, name)


def test():
    patch_all()

    threading = import_unpatched("threading")

    import time as patched_time

    def doit():
        import time  # this loads an unpatched time module...
        print "IN-THREAD time:", bool(time is patched_time), "sleeping"
        time.sleep(1)

    t = threading.Thread(target=doit)
    t.start()
    t.join()

if __name__ == "__main__":
    test()
