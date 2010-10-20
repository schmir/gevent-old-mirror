#! /usr/bin/env python

import os
import sys
from gevent import sleep, spawn

__all__ = ["run"]


class modwatcher(object):
    def __init__(self):
        self.modtime = {}

    def check(self):
        retval = False

        for mod in sys.modules.values():
            try:
                p = mod.__file__
            except AttributeError:
                continue
            if p.endswith(".pyc") or p.endswith(".pyo"):
                p = p[:-1]
            try:
                mtime = os.stat(p).st_mtime
            except:
                continue
            if p in self.modtime:
                if self.modtime[p] != mtime:
                    retval = True
            self.modtime[p] = mtime

        return retval


def run(interval=1.0):
    mw = modwatcher()
    while 1:
        if mw.check():
            print "restarting"
            os.execv(sys.executable, [sys.executable] + sys.argv)
        sleep(interval)


def main():
    print "now touch %s" % sys.argv[0]
    spawn(run)
    while 1:
        sleep(10)
        print "pid=%s" % os.getpid()

if __name__ == "__main__":
    main()
