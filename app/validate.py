def validateFloat(dispName, _value, min = None, max = None):
	try:
		value = float(_value)
	except ValueError:
		return dispName + " is not a float", False
	
	if min != None and value < min:
		return dispName + " is lower than " + str(min), False
	if max != None and value > max:
		return dispName + " is larger than " + str(max), False
	return value, True
	
def validateBool(dispName, _value):
	try:
		value = int(_value)
	except ValueError:
		if _value.lower() == "true" or _value.lower() == "on":
			return 1, True
		elif _value.lower() == "false" or _value.lower() == "off":
			return 0, True
		else:
			return dispName + " is not a boolean", False
	if value == 0:
		return 0, True
	else:
		return 1, True
		