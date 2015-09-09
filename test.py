import unittest
import tempfile
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
		p2_c.put("lock")
		self.assertTrue(p2_r.get())
		p2_c.put("unlock")
