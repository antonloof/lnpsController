import threading, json, socket

class PsMock():
	def __init__(self, data):
		self.data = data
		
	def getVoltage(self):
		return self.data["voltage"]

	def getCurrent(self):
		return self.data["current"]
		
	def getSerialNo(self):
		return self.data["serialNo"]
		
class PsThread(threading.Thread):
	def __init__(self, ps, queue, sem, lock):
		threading.Thread.__init__(self)
		self.ps = ps
		self.queue = queue
		self.sem = sem
		self.lock = lock
		
	def run(self):
		while True:
			self.sem.acquire()
			with self.lock:
				request = self.queue.pop()
			try:
				print(self.ps.data[request[1]])
			except KeyError:
				print("Key", request[1], "does not exist")
		
class PsThreadContainer():
	def __init__(self, ps):
		self.sem = threading.Semaphore(0)
		self.queue = []
		self.lock = threading.RLock()
		self.psThread = PsThread(ps, self.queue, self.sem, self.lock)
		self.psThread.start()
		
	def add(self, request):
		with self.lock:
			self.queue.append(request)
		self.sem.release()
	
class ClientThread(threading.Thread):
	def __init__(self, cs):
		threading.Thread.__init__(self)
		self.cs = cs
		self.headers = {}
		self.target = b""
		self.method = b""
		self.url = []
		
	def run(self):
		data = b""
		expectedLength = 0
		while True:
			packet = cs.recv(1024)
			
			# socket closed
			if not packet:
				break
			data += packet
			# http header finished
			if b"\r\n\r\n" in data and not self.headers:
				split = data.split(b"\r\n\r\n")
				sHeader = split[0]
				if len(split) > 1:
					data = split[1]
				else:
					data = b""
				if not self.parseHeader(sHeader):
					self.cs.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
					return
				if b"Content-Length" in self.headers:
					expectedLength = int(str(self.headers[b"Content-Length"], "UTF-8"))
			
			# wait for remaing data
			if self.headers:
				if len(data) == expectedLength:
					break
				elif len(data) > expectedLength:
					self.cs.send(b"HTTP/1.1 411 Length Required\r\n\r\n")
		if not self.parseTarget():
			self.cs.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
			return
			
		print(self.url)
		content = b'{"a":2,"b":5}'
		cs.send(b"HTTP/1.1 200 OK\r\nContent-Length:"+bytes(str(len(content)), "utf-8")+b"\r\nContent-Type:text/json;charset=UTF-8\r\n\r\n"+content)
				
	def parseTarget(self):
		split = self.target.split(b" ")
		if len(split) < 2:
			return False
		if not split[0] in [b"GET",b"POST",b"PUT",b"DELETE"]:
			return False
		self.method = split[0]
		#split on / and remove empty
		self.url = list(filter(None, split[1].split(b"/")))
		#convert to string
		for i in range(len(self.url)):
			self.url[i] = str(self.url[i], "UTF-8")
			
		return True
				
	def parseHeader(self, sHeader):
		aHeader = sHeader.split(b"\r\n")
		if len(aHeader) == 0:
			return False
		
		self.target = aHeader.pop(0)
		for kvp in aHeader:
			kvpsplit = kvp.split(b":")
			if len(kvpsplit) < 2:
				return False
			self.headers[kvpsplit[0]] = b":".join(kvpsplit[1:])
		return True
			
CONFIG_FILE = "ps_config.json"
with open(CONFIG_FILE, "r") as f:
	config = json.load(f)

if len(config["ports"]) != len(config["powersupplies"]):
	print("Could not start server, config file does not describe an equal amount of powersupplies and ports")
	exit(0)
	
pss = [
	PsMock({"voltage":10, "current":2, "serialNo":123}),
	PsMock({"voltage":13, "current":0.5, "serialNo":12345}),
	PsMock({"voltage":1, "current":5, "serialNo":1234})
]

psThreadContainers = {}
for i in range(len(config["ports"])):
	for ps in pss:
		if ps.getSerialNo() == config["powersupplies"][i]["serialNo"]:
			psThreadContainers[config["powersupplies"][i]["dev"]] = PsThreadContainer(ps)
			break

#start the rest api server
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("localhost", 5049))
serversocket.listen(5)
# lite dirty testkod
while True:
	cs, addr = serversocket.accept()
	ct = ClientThread(cs)
	ct.start()