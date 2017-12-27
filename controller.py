import threading

class Request:
	def __init__(self):
		self.res = None
		self.sem = threading.Semaphore(0)
		
	def callback(self, res):
		self.res = res
		self.sem.release()
		
class Controller(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.queue = []
		self.lock = threading.RLock()
		self.sem = threading.Semaphore(0)
		
	def run(self):
		while True:
			self.sem.acquire()
			with self.lock:
				req = self.queue.pop()
			req.callback(self.process(req))
				
	def waitQuery(self, req):
		with self.lock:
			self.queue.append(req)
		self.sem.release() 
		req.sem.acquire()
		return req.res
		
	def process(self, req):
		raise NotImplementedError("IT'S MISSING, ARRG!!1")