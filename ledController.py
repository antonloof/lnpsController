import serial, threading
from controller import *
BAUD_RATE = 115200

class LedRequest(Request):
	def __init__(self, mess):
		super().__init__()
		self.mess = mess

class LedController(Controller):
	def __init__(self, port):
		super().__init__()
		# self.serial = serial.Serial(port, BAUD_RATE, timeout=1)
		
	def process(self, req):
		return req.mess
		