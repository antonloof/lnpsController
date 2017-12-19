import serial

#constants
MSG_TYPE_SEND = 0xC0
MSG_TYPE_QUERY = 0x40
MSG_TYPE_ANSWER = 0x80

CAST_TYPE_ANSWER_FROM_DEV = 0x00
CAST_TYPE_BROADCAST = 0x20

DIRECTION_FROM_PC = 0x10
DIRECTION_FROM_DEV = 0x00

def calculateChecksum(h, d):
	checksum = h[0] + h[1] + h[2]
	for i in d:
		checksum += i
	return checksum.to_bytes(2, 'big')

ps = serial.Serial('COM3', 115200, timeout=1, parity=serial.PARITY_ODD)
# Start Delimiter:    1 byte
# Device Node:        1 byte
# Object:             1 byte
# Data:               0 - 16 bytes
# Checksum:           2 bytes

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
	3: "INCORRECT_CHECKSUM", 
	4:"INCORRECT_START_DELIMITER",
	5:"WRONG_OUTPUT_ADDRESS",
	7:"UNDEFINED_OBJECT",
	8:"INCORRECT_OBJECT_LENGTH",
	9:"VIOLATED_READ_WRITE_PERMISSION",
	15:"DEVICE_IN_LOCK_STATE",
	48:"EXCEEDED_OBJECT_UPPER_LIMIT",
	49:"EXCEEDED_OBJECT_LOWER_LIMIT"}
	
wantedVoltage = 8
startDelim = MSG_TYPE_SEND + CAST_TYPE_BROADCAST + DIRECTION_FROM_PC + 1
header = bytes([startDelim, 0, ComObject.VOLTAGE])
data = (wantedVoltage * 25600 // 42).to_bytes(2, 'big')
checksum = calculateChecksum(header, data)
	
ps.write(header + data + checksum)
startdelim = int.from_bytes(ps.read(), 'big')
deviceNode = int.from_bytes(ps.read(), 'big')
object = int.from_bytes(ps.read(), 'big')
data = ps.read((startdelim & 0xF) + 1)
if startdelim & 0xF0 != MSG_TYPE_ANSWER:
	print("konstig msg type", startdelim & 0xF0)
else:
	if object == ComObject.ERROR_CODE:
		print("svar:", PS_ERRORS[data[0]])
ps.close()