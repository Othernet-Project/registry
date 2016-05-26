"""
system.py: utility functions related to systems

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import sys
import gevent
import signal


def on_interrupt(handler):
    """ Registers a signal handler function
    The handler function should not expect any arguments, and should return an
    integer that is passed to ``sys.exit()``. Exceptions raised in the handler
    will be propagaed without being trapped.
    """

    def wrapper(*args, **kwargs):
        ret = handler()
        sys.exit(ret)

    gevent.signal(signal.SIGINT, wrapper)
    gevent.signal(signal.SIGTERM, wrapper)
    gevent.signal(signal.SIGSEGV, wrapper)
