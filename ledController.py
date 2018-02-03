import serial, threading
from controller import *
BAUD_RATE = 115200

LED_ERRORS = {0: "OK", 1: "ROW OUT OF RANGE", 2: "COL OUT OF RANGE", 3: "MODE OUT OF RANGE"}

class LedRequest(Request):
	def __init__(self, isGet, r, c, m=0):
		super().__init__()
		self.isGet = isGet
		self.row = r
		self.col = c
		self.mode = m

class LedController(Controller):
	def __init__(self, port):
		super().__init__()
		self.port = port
		self.tryConnectSerial()
		
		
	def tryConnectSerial(self):
		self.isConnected = False
		try:
			self.serial = serial.Serial(self.port, BAUD_RATE, timeout=1)
		except serial.serialutil.SerialException:
			print("WARNING: Could not connect to led controller at port", self.port)
			return False
		self.isConnected = True
		return True
		
	def process(self, req):
		self.serial.reset_input_buffer() # the led controller sends bs serial data sometimes
		
		if req.isGet:
			firstChar = "G"
		else:
			firstChar = "S"
		mess = firstChar + ":" + str(req.row) + ":" + str(req.col)
		if not req.isGet:
			mess += ":" + str(req.mode)
		mess += "\n"
		
		try:
			self.serial.write(mess.encode("ascii"))
		except serial.serialutil.SerialException:
			print("WARNING: Serial connection with led controller on port", self.port, "lost (write)")
			if not self.tryConnectSerial():
				req.error = "No serial connection with led controller"
				return
			else:
				return self.process(req)

		resp = b""
		prevChar = b''
		try:
			nextChar = self.serial.read()
			while nextChar != b'\n' and prevChar != b'\r':
				resp += nextChar
				prevChar = nextChar
				nextChar = self.serial.read()
		except serial.serialutil.SerialException:
			print("WARNING: Serial connection with led controller on port", self.port, "lost (read)")
			if not self.tryConnectSerial():
				req.error = "No serial connection with led controller"
				return
			else:
				return self.process(req)
		
		resp = resp.decode("ascii")
		
		#parse response
		if req.isGet:
			if resp[0] != 'G':
				return "Incorrect response 1"
			if resp.count(":") != 3:
				return "Incorrect response 2"
			try:
				r, c, v = [int(x) for x in resp[2:].split(":")]
			except ValueError:
				return "Incorrect response 3"
			if r != req.row or c != req.col:
				return "Incorrect response 4"
			return v
		else:
			if resp[0] != "E":
				return "Incorrect response 1"
			try:
				return LED_ERRORS[int(resp[2:])]
			except (ValueError, KeyError):
				return "Incorrect response 2"