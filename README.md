Posix Concurrent File Handler
=============================

Provides concurrent rotating file handler for posix-compatible OSes.


By default `multiprocessing.Lock` is used. If you fork from one process
that configures logger this case is preferred because of speed.
If you have many undependantly started processes you should use instance
of `ploghandler.Lockf` class. The Lockf class uses `fcntl.lockf` call described
in `man 3 lockf`. Optinally `ploghandler.Flock` (`man 2 flock`) can be used.
