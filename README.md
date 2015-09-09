Posix Concurrent File Handler
=============================

Provides concurrent rotating file handler for posix-compatible OSes.


By default `multiprocessing.Lock` is used. If you fork from one process
that configures logger this case is preferred because of speed.
If you have many undependantly started processes you should use instance
of `ploghandler.Lockf` class. The Lockf class uses `fcntl.lockf` call described
in `man 3 lockf`. Optinally `ploghandler.Flock` (`man 2 flock`) can be used.

Example:
--------

```
import logging

from ploghandler import PLogHandler, Lockf

log = logging.getLogger("test")
handler = PLogHandler(
    "/var/log/test.debug.log",
    maxBytes=1024 * 1024,
    backupCount=5,
    rotlock=Lockf("/var/log/test.debug.lock"))

log.addHandler(handler)
log.setLevel(logging.DEBUG)

log.debug("test message")
```
