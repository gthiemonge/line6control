#!/usr/bin/env python

DEBUG_MSG = True

if DEBUG_MSG == False:
    def debug_msg(msg = ""):
        pass
else:
    import time
    import inspect

    def debug_msg(msg = ""):
        stack = inspect.stack()
        try:
            filename = stack[1][1].split('/')[-1]
            funcname = stack[1][3]
        finally:
            del stack

        print("%.3f <%s> <%s>  %s" % (time.time(), filename, funcname, msg))
