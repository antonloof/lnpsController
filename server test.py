import socket, json, serial, time

## ps communication constants
MSG_TYPE_SEND = 0xC0
MSG_TYPE_QUERY = 0x40
MSG_TYPE_ANSWER = 0x80

CAST_TYPE_ANSWER_FROM_DEV = 0x00
CAST_TYPE_BROADCAST = 0x20

DIRECTION_FROM_PC = 0x10
DIRECTION_FROM_DEV = 0x00

TRANSMISSION_LATENCY = 0.050 #50 ms

class ComObject:
	DEV_TYPE            = 0
	DEV_SER_NO          = 1
	NOM_VOLTAGE         = 2
	NOM_CURRENT         = 3
	NOM_POWER           = 4
	DEV_PART_NO         = 6
	DEV_MANUFACTURER    = 8
	DEV_SW_VERSION      = 9
	DEV_CLASS           = 19
	OVP_THRESHOLD       = 38
	OCP_THRESHOLD       = 39
	VOLTAGE             = 50
	CURRENT             = 51
	DEV_CONTROL         = 54
	DEV_STATUS          = 71
	DEV_CONF            = 72
	DEV_CONTROL_BUG_FIX = 77
	ERROR_CODE          = 0xFF

PS_ERRORS = {0:"OK", 
	3:"INCORRECT_CHECKSUM", 
	4:"INCORRECT_START_DELIMITER",
	5:"WRONG_OUTPUT_ADDRESS",
	7:"UNDEFINED_OBJECT",
	8:"INCORRECT_OBJECT_LENGTH",
	9:"VIOLATED_READ_WRITE_PERMISSION",
	15:"DEVICE_IN_LOCK_STATE",
	48:"EXCEEDED_OBJECT_UPPER_LIMIT",
	49:"EXCEEDED_OBJECT_LOWER_LIMIT"}

## ps communication helpers
def calculateChecksum(h, d):
	checksum = h[0] + h[1] + h[2]
	for i in d:
		checksum += i
	return checksum.to_bytes(2, 'big')
	
def createHeader(sd, dn, obj)
	return bytes([sd, dn, obj])
	
class PowerSupply():
	def __init__(self, serial):
		self.serial = serial
		self.lastSend = 0
		
	def recv(self, expectedObj):
		startDelim = int.from_bytes(self.serial.read(), 'big')
		if startDelim & 0xC0 != MSG_TYPE_ANSWER:
			return 
		if startDelim & CAST_TYPE_BROADCAST != CAST_TYPE_ANSWER_FROM_DEV:
			return
		if srartDelim % DIRECTION_FROM_PC != DIRECTION_FROM_DEV:
			return 
		deviceNode = int.from_bytes(self.serial.read(), 'big')
		obj = int.from_bytes(self.serial.read(), 'big')
		data = self.serial.read(startDelim & 0xF + 1)
		checksum = self.serial.read(2)
		if checksum != calculateChecksum(createHeader(startDelim, deviceNode, obj), data):
			return
		if obj != expectedObj && obj != ComObject.ERROR_CODE:
			return
		
		
	def send(self, startdelim, deviceNode, obj, data=b''):
		# wait for some time to pass in order not to bombard the ps with requests
		timeSinceLastSent = time.time() - self.lastSend
		if timeSinceLastSent < TRANSMISSION_LATENCY: 
			time.sleep(TRANSMISSION_LATENCY - timeSinceLastSent)
			
		header = createHeader(startdelim, deviceNode, obj)
		self.serial.write(header + data + calculateChecksum(header, data))
		
	def get(self, obj):
		startdelim = MSG_TYPE_QUERY + CAST_TYPE_BROADCAST + DIRECTION_FROM_PC
		deviceNode = 0
		self.send(startDelim, deviceNode, obj)
		return self.recv(obj)
	
## load json
CONF_PATH = "ps_config.json"
with open(CONF_PATH, "r") as f:
	config = json.load(f)
print(config)	

## establish which port talks to which ps 
BAUD_RATE = 115200
for port in config.ports:
	ps = PowerSupply(serial.Serial(port, BAUD_RATE, timeout=1, parity=serial.PARITY_ODD))

	## start threads for com ports
## start web server
## delegate

"""
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 5039))
serversocket.listen(5)

while True:
	cs, addr = serversocket.accept()
	request = cs.recv(2048)
	headerbody = request.decode("utf-8").split("\r\n\r\n")
	if len(headerbody) == 1:
		headers = headerbody[0].split("\r\n")
		body = ""
	elif len(headerbody) == 2:
		headers, body = headerbody
		headers = headers.split("\r\n")
	else:
		resp = b"HTTP/1.1 400 Bad Request"
		cs.send(resp)
		continue
		
	print(headers, body)
	resp = b"HTTP/1.1 200 OK\r\nContent-Type: text/json; charset=UTF-8\r\n\r\n{success: 4}"
	cs.send(resp)
"""