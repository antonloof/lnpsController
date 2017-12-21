import threading, serial, time, struct, sys

REQUEST_GET = 0
REQUEST_SET = 0

## ps communication constants
MSG_TYPE_SEND = 0xC0
MSG_TYPE_QUERY = 0x40
MSG_TYPE_ANSWER = 0x80

CAST_TYPE_ANSWER_FROM_DEV = 0x00
CAST_TYPE_BROADCAST = 0x20

DIRECTION_FROM_PC = 0x10
DIRECTION_FROM_DEV = 0x00

TRANSMISSION_LATENCY = 0.100 #100 ms
BAUD_RATE = 115200

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

class PsConf:
	def __init__(self):
		self.remoteOn                    = 0
		self.switchOn                    = 0
		self.voltageLimitOn              = 0
		self.currentLimitOn              = 0
		self.trackingOn                  = 0
		self.overVoltageProtectionActive = 0
		self.overCurrentProtectionActive = 0
		self.overPowerProtectionActive   = 0
		self.overTempProtectionActive    = 0
	
class DeviceControll:
	SWITCH_POWER_ON    = 0x0101
	SWITCH_POWER_OFF   = 0x0100
	ACK_ALARM          = 0x0A0A
	REMOTE_CONTROL_ON  = 0x1010
	REMOTE_CONTROL_OFF = 0x1000
	TARCKING_ON        = 0xF0F0
	TARCKING_OFF       = 0xF0E0
	
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
	
def createHeader(sd, dn, obj):
	return bytes([sd, dn, obj])
	
class PsResponse():
	def __init__(self):
		self.data = b""
		self.errors = []
		
	def add(self, e):
		self.errors.append(e)
		
	def parse(self, startDelim, deviceNode, data, checksum, obj, expectedObj):
		self.data = data
		self.errors = []
		if startDelim & 0xC0 != MSG_TYPE_ANSWER:
			self.add("Unexpected transmission type: " + str(startDelim & 0xC0))
		if startDelim & CAST_TYPE_BROADCAST != CAST_TYPE_ANSWER_FROM_DEV:
			self.add("Unexpected cast type: " + str(startDelim & CAST_TYPE_BROADCAST))
		if startDelim & DIRECTION_FROM_PC != DIRECTION_FROM_DEV:
			self.add("Unexpected direction: " + str(startDelim & DIRECTION_FROM_PC)) 
		
		if checksum != calculateChecksum(createHeader(startDelim, deviceNode, obj), data):
			self.add("Invalid checksum")
		if obj != expectedObj and obj != ComObject.ERROR_CODE:
			self.add("Object returned was not the expected one, got:" + str(obj) + " expected: " + str(expectedObj))
		if obj == ComObject.ERROR_CODE:
			self.add(PS_ERRORS[ord(data)]) 
		
	def forceLength(self, length):
		if len(self.data) != length:
			self.add("The data does not meet the required length, is " + len(self.data) + " should be " + length + " bytes") 
	
	def clean(self):
		return len(self.errors) == 0
	
	def toString(self):
		return str(self.data[:-1], "ascii")
	
	def toFloat(self):
		self.forceLength(4)
		data = self.data
		if sys.byteorder == 'little':
			data = bytes(reversed(data))
		return struct.unpack('f', data)[0]
		
	def toPsConf(self):
		conf = PsConf()
		conf.remoteOn = (self.data[0] & (1 << 0)) == (1 << 0)
		conf.switchOn = (self.data[1] & (1 << 0)) == (1 << 0)
		conf.voltageLimitOn = ((self.data[1] & (3 << 1)) == (0 << 0))
		conf.currentLimitOn = ((self.data[1] & (3 << 1)) == (2 << 1))
		conf.trackingOn = ((self.data[1] & (1 << 3)) == (1 << 3))              
		conf.overVoltageProtectionActive = ((self.data[1] & (1 << 7)) == (1 << 4))
		conf.overCurrentProtectionActive = ((self.data[1] & (1 << 7)) == (1 << 5))
		conf.overPowerProtectionActive = ((self.data[1] & (1 << 7)) == (1 << 6))
		conf.overTempProtectionActive = ((self.data[1] & (1 << 7)) == (1 << 7))
		return conf
	
	def toInt16(self):
		self.forceLength(2)
		return int.from_bytes(self.data, byteorder='big')
		
	def getError(self):
		if len(self.errors) > 0:
			return self.errors[0]
		return ""
		
class PowerSupply():
	def __init__(self, port):
		self.serial = serial.Serial(port, BAUD_RATE, timeout=1, parity=serial.PARITY_ODD)
		self.lastSend = 0
		self.nomCurrent = None
		self.nomVoltage = None
		self.nomPower = None
		
	def recv(self, expectedObj):
		startDelim = int.from_bytes(self.serial.read(), 'big')
		deviceNode = int.from_bytes(self.serial.read(), 'big')
		obj = int.from_bytes(self.serial.read(), 'big')
		data = self.serial.read((startDelim & 0xF) + 1)
		checksum = self.serial.read(2)
		resp = PsResponse()
		resp.parse(startDelim, deviceNode, data, checksum, obj, expectedObj)
		return resp
			
	def send(self, startdelim, deviceNode, obj, data=b''):
		# wait for some time to pass in order not to bombard the ps with requests
		timeSinceLastSent = time.time() - self.lastSend
		if timeSinceLastSent < TRANSMISSION_LATENCY: 
			time.sleep(TRANSMISSION_LATENCY - timeSinceLastSent)
			
		header = createHeader(startdelim, deviceNode, obj)
		self.serial.write(header + data + calculateChecksum(header, data))
		
	def dynamicCall(self, func, data=[]):
		def funcNotFound():
			print("Function", func, "not found in PowerSupply")
			resp = PsResponse()
			resp.add("Func not found")
			return resp
			
		return getattr(self, func, funcNotFound)(*data)
		
	def get(self, obj):
		startDelim = MSG_TYPE_QUERY + CAST_TYPE_BROADCAST + DIRECTION_FROM_PC
		self.send(startDelim, 0, obj)
		return self.recv(obj)
		
	def set(self, obj, data):
		res = PsResponse()
		if len(data) != 2:
			res.add("Send data not 2 bytes long")
			return res
		startDelim = MSG_TYPE_SEND + CAST_TYPE_BROADCAST + DIRECTION_FROM_PC + 1
		self.send(startDelim, 0, obj, data)
		return self.recv(obj)
		
	def getSerialNo(self):
		return self.get(ComObject.DEV_SER_NO).toString()
		
	def getManufacturer(self):
		return self.get(ComObject.DEV_MANUFACTURER).toString()
		
	def getPartNo(self):
		return self.get(ComObject.DEV_PART_NO).toString()
		
	def getType(self):
		return self.get(ComObject.DEV_TYPE).toString()
		
	def getSWVersion(self):
		return self.get(ComObject.DEV_SW_VERSION).toString()
		
	def getNomVoltage(self):
		if self.nomVoltage is None:
			self.nomVoltage = self.get(ComObject.NOM_VOLTAGE).toFloat()
		return self.nomVoltage
		
	def getNomCurrent(self):
		if self.nomCurrent is None:
			self.nomCurrent = self.get(ComObject.NOM_CURRENT).toFloat()
		return self.nomCurrent
		
	def getNomPower(self):
		if self.nomPower is None:
			self.nomPower = self.get(ComObject.NOM_POWER).toFloat()
		return self.nomPower
		
	def getVoltage(self):
		return self.getNomVoltage() * self.get(ComObject.VOLTAGE).toInt16() / 25600
		
	def getCurrent(self):
		return self.getNomCurrent() * self.get(ComObject.CURRENT).toInt16() / 25600
		
	def getConf(self):
		return self.getConfObj().__dict__
		
	def getConfObj(self):
		return self.get(ComObject.DEV_CONF).toPsConf()
	
	def getRemote(self):
		return self.getConfObj().remoteOn
		
	def getSwitch(self):
		return self.getConfObj().switchOn
		
	def setRemote(self, value):
		if value:
			send = DeviceControll.REMOTE_CONTROL_ON
		else:
			send = DeviceControll.REMOTE_CONTROL_OFF
		return self.set(ComObject.DEV_CONTROL, send.to_bytes(2, 'big')).getError()
		
	def setSwitch(self, value):
		if value:
			send = DeviceControll.SWITCH_POWER_ON
		else:
			send = DeviceControll.SWITCH_POWER_OFF
		return self.set(ComObject.DEV_CONTROL, send.to_bytes(2, 'big')).getError()
		
class Request():
	def __init__(self, func, *data):
		self.func = func
		self.data = data
		self.callback = None

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
			request.callback(self.ps.dynamicCall(request.func, request.data))
		
class PsThreadContainer():
	def __init__(self, ps):
		self.sem = threading.Semaphore(0)
		self.queue = []
		self.lock = threading.RLock()
		self.psThread = PsThread(ps, self.queue, self.sem, self.lock)
		self.psThread.start()
		self.waitQuerySem = threading.Semaphore(0)
		
	def add(self, request):
		with self.lock:
			self.queue.append(request)
		self.sem.release()
		
	def waitQuery(self, request):
		request.callback = self.callback
		self.add(request)
		self.waitQuerySem.acquire()
		return self.response
		
	def callback(self, data):
		self.response = data
		self.waitQuerySem.release()