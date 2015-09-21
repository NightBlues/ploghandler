"""Posix concurrent rotate file logging handler."""

import codecs
import fcntl
import multiprocessing
import os
from logging.handlers import RotatingFileHandler


class Flock(object):
    """Use flock for locking file."""

    def __init__(self, lock_filename):
        self.lock_filename = lock_filename
        self._lock = None

    def __del__(self):
        if self._lock is not None:
            self._lock.close()
            self._lock = None

    def acquire(self, block=True):
        if self._lock is None:
            self._lock = open(self.lock_filename, "a")
        if block:
            fcntl.flock(self._lock, fcntl.LOCK_EX)
        else:
            try:
                fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                return False
            return True

    def release(self):
        if self._lock is not None:
            try:
                fcntl.flock(self._lock, fcntl.LOCK_UN)
            except ValueError:
                pass


class Lockf(object):
    """Use lockf for locking file."""

    def __init__(self, lock_filename):
        self.lock_filename = lock_filename
        self._lock = None

    def __del__(self):
        if self._lock is not None:
            self._lock.close()
            self._lock = None

    def acquire(self, block=True):
        if self._lock is None:
            self._lock = open(self.lock_filename, "a")
        if block:
            fcntl.lockf(self._lock, fcntl.LOCK_EX)
        else:
            try:
                fcntl.lockf(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                return False
            return True

    def release(self):
        if self._lock is not None:
            try:
                fcntl.lockf(self._lock, fcntl.LOCK_UN)
            except ValueError:
                pass


class PLogHandler(RotatingFileHandler):
    """Uses unix file locks for concurrent rollovering files."""

    def __init__(self, filename, mode="a", maxBytes=0, backupCount=0,
                 encoding="utf-8", delay=0, rotlock=None):
        """ConcurrentRotatingFileHandler has one additinal keyword argument
        comparing to RotatingFileHandler - rotlock.

        :param rotlock: object used for locking, Lockf can be used
        :type rotlock: should provide acquire(block=True) and release methods
        """
        self.delay = delay # python 2.6 compatibility
        RotatingFileHandler.__init__(self, filename,
            mode=mode, maxBytes=maxBytes, backupCount=backupCount,
            encoding=encoding, delay=delay)
        self._rotlock = rotlock
        if self._rotlock is None:
            self._rotlock = multiprocessing.Lock()

    def __del__(self):
        if hasattr(self.stream, "close"):
            self.stream.close()
            self.stream = None

    def emit(self, record):
        try:
            self._rotlock.acquire(True)
            RotatingFileHandler.emit(self, record)
        finally:
            self._rotlock.release()

    def shouldRollover(self, record):
        # dont rotate already rotated by other process file
        real_file = self._open()
        if os.fstat(self.stream.fileno()) != os.fstat(real_file.fileno()):
            self.stream.flush()
            self.stream.close()
            self.stream = real_file
        else:
            real_file.close()

        return RotatingFileHandler.shouldRollover(self, record)

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        backported from python 2.7 (for python 2.6 compatibility)
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d" % (self.baseFilename, i)
                dfn = "%s.%d" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    #print "%s -> %s" % (sfn, dfn)
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.baseFilename + ".1"
            if os.path.exists(dfn):
                os.remove(dfn)
            # Issue 18940: A file may not have been created if delay is True.
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()

    def _open(self):
        """Open the current base file with buffering disabled."""
        # disable buffering to make fwrite do 1 write per call (to avoid "concurrency")
        mode = self.mode.replace("b", "") + "b" # python 3 compatibility
        stream = codecs.open(self.baseFilename, mode, encoding=self.encoding,
                             buffering=0)
        return stream


ConcurrentRotatingFileHandler = PLogHandler
