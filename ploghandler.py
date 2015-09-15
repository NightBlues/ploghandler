"""Posix concurrent rotate file logging handler."""

import fcntl
import logging.handlers
import multiprocessing
import os


class Flock(object):
    """Use flock for locking file."""

    def __init__(self, lock_filename):
        self.lock_filename = lock_filename
        self._lock = None

    def acquire(self, block=False):
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

    def acquire(self, block=False):
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


class PLogHandler(logging.handlers.RotatingFileHandler):
    """Uses unix file locks for concurrent rollovering files."""

    def __init__(self, filename, mode="a", maxBytes=0, backupCount=0, encoding=None,
        delay=0, rotlock=None):
        """ConcurrentRotatingFileHandler has one additinal keyword argument
        comparing to RotatingFileHandler - rotlock.

        :param rotlock: object used for locking, Lockf can be used
        :type rotlock: should provide acquire(block=True) and release methods
        """
        logging.handlers.RotatingFileHandler.__init__(self, filename,
            mode=mode, maxBytes=maxBytes, backupCount=backupCount,
            encoding=encoding, delay=delay)
        self._rotlock = rotlock
        if self._rotlock is None:
            self._rotlock = multiprocessing.Lock()

    def doRollover(self):
        self._rotlock.acquire(True)
        try:
            real_file = self._open()
            # dont rotate already rotated by other process file
            if os.fstat(self.stream.fileno()) == os.fstat(real_file.fileno()):
                # make other processes know that file has max size
                # even their record's size is lower than ours
                # self.stream.write(" " * (self.maxBytes - self.stream.tell() - 1))
                self.stream.seek(self.maxBytes - 1)
                self.stream.flush()
                logging.handlers.RotatingFileHandler.doRollover(self)
        finally:
            self._rotlock.release()
            self.stream = self._open()

    def _open(self):
        """Open the current base file with buffering disabled."""
        # disable buffering to make fwrite do 1 write per call (to avoid "concurrency")
        stream = open(self.baseFilename, self.mode, 0)
        return stream


ConcurrentRotatingFileHandler = PLogHandler
