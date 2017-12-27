import serial, threading
BAUD_RATE = 115200

class LedRequest:
	def __init__(self, mess):
		self.mess = mess
		self.res = None
		self.sem = threading.Semaphore(0)
		
	def callback(self, res):
		self.res = res
		self.sem.release()

class LedController(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		# self.serial = serial.Serial(port, BAUD_RATE, timeout=1)
		self.queue = []
		self.lock = threading.RLock()
		self.sem = threading.Semaphore(0)
		
	def run(self):
		while True:
			self.sem.acquire()
			with self.lock:
				req = self.queue.pop()
			req.callback(self.proccess(req))
				
	def waitQuery(self, req):
		with self.lock:
			self.queue.append(req)
		self.sem.release() 
		req.sem.acquire()
		return req.res
		
	def proccess(self, req):
		return req.mess
		