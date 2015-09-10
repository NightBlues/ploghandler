import collections
import glob
import logging
import os
import shutil
import tempfile
import unittest

from multiprocessing import Process, Queue


class PLogHandlerTest(unittest.TestCase):

    def test_import(self):
        import ploghandler

    def test_lockf_nonblock(self):
        from ploghandler import Lockf
        lock_file, lock_filename = tempfile.mkstemp(".lock")

        def locker(filename, cmd_queue, result_queue):
            lock = Lockf(lock_filename)
            while True:
                cmd = cmd_queue.get()
                if cmd == "quit":
                    break
                elif cmd == "lock":
                    result_queue.put(lock.acquire(block=False))
                elif cmd == "unlock":
                    lock.release()
                    result_queue.put("done")

        p1_c, p1_r = Queue(), Queue()
        p1 = Process(target=locker, args=(lock_filename, p1_c, p1_r))
        p2_c, p2_r = Queue(), Queue()
        p2 = Process(target=locker, args=(lock_filename, p2_c, p2_r))

        p1.start()
        p2.start()

        p1_c.put("lock")
        self.assertTrue(p1_r.get())
        p2_c.put("lock")
        self.assertFalse(p2_r.get())
        p1_c.put("unlock")
        p1_r.get()
        p2_c.put("lock")
        self.assertTrue(p2_r.get())
        p2_c.put("unlock")


    def test_highload(self):
        workers_count = 2
        max_bytes = 1024 * 1024
        backup_count = 5
        msg_len = 100
        msg_count = (max_bytes * backup_count) / (workers_count * msg_len)

        from ploghandler import PLogHandler
        log = logging.getLogger("test")
        log_dir = tempfile.mkdtemp()
        handler = PLogHandler(os.path.join(log_dir, "test.debug.log"),
            maxBytes=max_bytes, backupCount=backup_count)
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)

        def crazylog(l):
            for i in range(msg_count):
                log.debug("{0}: {1}".format(
                    i, l * (msg_len - len(str(i)) - 3)))

        workers = []
        for i in range(workers_count):
            wid = chr(65 + i)
            workers.append((wid, Process(target=crazylog, args=(wid,))))
            workers[-1][1].start()
        for w in workers:
            w[1].join()

        workers_msg_count = collections.defaultdict(lambda: 0)
        for f in glob.glob(os.path.join(log_dir, "test.debug.log*")):
            with open(f, "r") as fp:
                for line in fp.readlines():
                    workers_msg_count[line.split(" ")[1][0]] += 1
        for w, c in workers_msg_count.iteritems():
            self.assertEquals(c, msg_count,
                "Expected {0} messages from worker {1}, but {2} found.".format(msg_count, w, c))

        shutil.rmtree(log_dir)
