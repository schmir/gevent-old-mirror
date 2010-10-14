# Copyright (c) 2009-2010 Denis Bilenko. See LICENSE for details.
"""
gevent is a coroutine-based Python networking library that uses greenlet
to provide a high-level synchronous API on top of libevent event loop.

See http://www.gevent.org/ for the documentation.
"""

version_info = (0, 14, 0)
__version__ = '0.14.0dev'

import sys
if sys.platform == 'win32':
    __import__('socket')  # trigger WSAStartup call
del sys


from gevent.apipkg import initpkg
initpkg(
    __name__,
    dict(
        reinit = "gevent.core:reinit",

        Greenlet = "gevent.greenlet:Greenlet",
        joinall = "gevent.greenlet:joinall",
        killall = "gevent.greenlet:killall",

        spawn = "gevent.greenlet:Greenlet.spawn",
        spawn_later = "gevent.greenlet:Greenlet.spawn_later",
        spawn_link = "gevent.greenlet:Greenlet.spawn_link",
        spawn_link_value = "gevent.greenlet:Greenlet.spawn_link_value",
        spawn_link_exception = "gevent.greenlet:Greenlet.spawn_link_exception",

        Timeout = "gevent.timeout:Timeout",
        with_timeout = "gevent.timeout:with_timeout",

        getcurrent = "gevent.hub:getcurrent",
        GreenletExit = "gevent.hub:GreenletExit",
        spawn_raw = "gevent.hub:spawn_raw",
        sleep = "gevent.hub:sleep",
        kill = "gevent.hub:kill",
        signal = "gevent.hub:signal",
        shutdown = "gevent.hub:shutdown",

        fork = "gevent.hub:fork",

        hub = "gevent.hub",
        core = "gevent.core"),

    dict(version_info=version_info))
