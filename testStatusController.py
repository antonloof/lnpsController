from controller import *
import threading, json

DATA_PATH = "data/data.json"
TYPE_SET = 0
TYPE_GET = 1

class TestStatusRequest(Request):
	def __init__(self, type, serNo, value = ""):
		super().__init__()
		self.type = type
		self.value = value
		self.serNo = serNo
		
class TestStatusController(Controller):
	def __init__(self):
		super().__init__()
		self.lock = threading.RLock()
	
	def process(self, req):
		with self.lock:
			with open(DATA_PATH, "r") as f:
				data = json.load(f)
		if req.type == TYPE_GET:
			if req.serNo in data:
				return data[req.serNo]
			else:
				return None
		elif req.type == TYPE_SET:
			data[req.serNo] = req.value
			with self.lock:
				with open(DATA_PATH, "w") as f:
					json.dump(data, f)
			return "OK"