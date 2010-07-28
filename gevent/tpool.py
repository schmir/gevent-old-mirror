
import os
import fcntl
import gevent
import Queue
import gevent.event
from gevent import tlmonkey

threading = tlmonkey.import_unpatched("threading")


# Simple wrapper to os.pipe() - but sets to non-block
def _pipe():
    r, w = os.pipe()
    fcntl.fcntl(r, fcntl.F_SETFL, os.O_NONBLOCK)
    fcntl.fcntl(w, fcntl.F_SETFL, os.O_NONBLOCK)
    return r, w

_core_pipe_read, _core_pipe_write = _pipe()

_hubq = tlmonkey.run_with_unpatched(Queue.Queue)


def _core_pipe_read_callback(event, evtype):
    try:
        os.read(event.fd, 1)
    except EnvironmentError:
        pass

    while 1:
        try:
            f, args, kwargs = _hubq.get(block=False)
        except Queue.Empty:
            return
        try:
            f(*args, **kwargs)
        except:
            pass  # XXX: log error

gevent.core.event(gevent.core.EV_READ | gevent.core.EV_PERSIST,
                  _core_pipe_read, _core_pipe_read_callback).add()


def call_in_hub(func, *args, **kwargs):
    _hubq.put((func, args, kwargs))
    os.write(_core_pipe_write, " ")


class ThreadPool(object):
    def __init__(self, poolsize=20):
        self.poolsize = poolsize
        self.thread_list = []
        self.q = tlmonkey.run_with_unpatched(Queue.Queue)

        for x in range(poolsize):
            t = threading.Thread(target=self._work,)
            t.setDaemon(True)
            t.start()
            self.thread_list.append(t)

    def spawn(self, func, *args, **kwargs):
        res = gevent.event.AsyncResult()

        def doit():
            try:
                t = func(*args, **kwargs)
            except Exception, err:
                call_in_hub(res.set_exception, err)
            else:
                call_in_hub(res.set, t)

        self.q.put(doit)

        return res

    def _work(self):
        while 1:
            func = self.q.get()
            if func is None:
                return

            try:
                func()
            except:
                pass

default_pool = None


def get_default_pool():
    global default_pool
    if default_pool is None:
        default_pool = ThreadPool(20)
    return default_pool


def spawn(func, *args, **kwargs):
    return get_default_pool().spawn(func, *args, **kwargs)
