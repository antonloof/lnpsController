import threading, html

from psController import *
from ledController import *
from testStatusController import *
from restapi import *

class LnpsControllerBranch(ApiBranch):
	def __init__(self, psControllers):
		self.psControllers = psControllers
		
	def get(self, respHeader, navData):
		if navData["benchNo"] in self.psControllers and self.psControllers[navData["benchNo"]].hasPs():
			return self._get(respHeader, navData)
		else:
			respHeader.setError(404)
			raise ValueError("Bench no " + navData["benchNo"] + " does not have a powersupply")
			
	def put(self, respHeader, reqData, navData):
		if navData["benchNo"] in self.psControllers and self.psControllers[navData["benchNo"]].hasPs():
			return self._put(respHeader, reqData, navData)
		else:
			respHeader.setError(404)
			raise ValueError("Bench no " + navData["benchNo"] + " does not have a powersupply")
	
class NoPsRequiredBranch(ApiBranch):
	def __init__(self, psControllers):
		self.psControllers = psControllers
		
	def get(self, respHeader, navData):	
		if navData["benchNo"] in self.psControllers:
			return self._get(respHeader, navData)
		else:
			respHeader.setError(404)
			raise ValueError("Bench no " + navData["benchNo"] + " does not exist")
	
	def put(self, respHeader, reqData, navData):	
		if navData["benchNo"] in self.psControllers:
			return self._put(respHeader, reqData, navData)
		else:
			respHeader.setError(404)
			raise ValueError("Bench no " + navData["benchNo"] + " does not exist")
	
class SerialNoBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getSerialNo"))
		
class ManBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getManufacturer"))
		
class PartNoBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getPartNo"))
		
class SWVersionBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getSWVersion"))
		
class TypeBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getType"))
		
class NomVolatageBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getNomVoltage"))
		
class NomCurrentBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getNomCurrent"))
		
class NomPowerBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getNomPower"))
		
class ClassBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getClass"))
		
class VoltageBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getVoltage"))
		
	def _put(self, respHeader, reqData, navData):
		sVoltage, pw = validateSet(reqData, respHeader, "voltage", "pw")
		if not self.psControllers[navData["benchNo"]].validatePw(pw):
			respHeader.setError(401)
			raise ValueError("Wrong password")
		nomVoltage = self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getNomVoltage"))
		nomPower = self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getNomPower"))
		nomCurrent = self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getNomCurrent"))
		voltage = validateFloat(sVoltage, respHeader, "voltage", 0, nomVoltage)
		# limit current before setting voltage
		if nomPower / voltage > nomCurrent:
			setCurrent = nomCurrent
		else:
			setCurrent = nomPower / voltage
		self.psControllers[navData["benchNo"]].waitQuery(PsRequest("setCurrentLimit", setCurrent))
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("setVoltage", voltage))
		
class CurrentLimitBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getCurrentLimit"))
		
	def _put(self, respHeader, reqData, navData):
		sCurrent, pw = validateSet(reqData, respHeader, "currentLimit", "pw")
		if not self.psControllers[navData["benchNo"]].validatePw(pw):
			respHeader.setError(401)
			raise ValueError("Wrong password")
		nomCurrent = self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getNomCurrent"))
		current = validateFloat(sCurrent, respHeader, "current", 0, nomCurrent)
		nomPower = self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getNomPower"))
		voltage = self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getVoltage"))
		if current * voltage > nomPower:
			respHeader.setError(400)
			raise ValueError("Current can not exceed " + str(nomPower / voltage) + "A at the currently configured voltage (" + str(voltage) + "V)")
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("setCurrentLimit", current))
		
class ConfBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getConf"))

class RemoteBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getRemote"))
		
	def _put(self, respHeader, reqData, navData):
		sRemote, pw = validateSet(reqData, respHeader, "remote", "pw")
		if not self.psControllers[navData["benchNo"]].validatePw(pw):
			respHeader.setError(401)
			raise ValueError("Wrong password")
		remote = validateBool(sRemote, respHeader, "remote")
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("setRemote", remote))
		
class SwitchBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getSwitch"))
	
	def _put(self, respHeader, reqData, navData):
		sSwitch, pw = validateSet(reqData, respHeader, "switch", "pw")
		if not self.psControllers[navData["benchNo"]].validatePw(pw):
			respHeader.setError(401)
			raise ValueError("Wrong password")
		switch = validateBool(sSwitch, respHeader, "switch")
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("setSwitch", switch))
		
class OverVoltageBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getOverVoltage"))
		
	def _put(self, respHeader, reqData, navData):
		sOverVoltage, pw = validateSet(reqData, respHeader, "overVoltage", "pw")
		if not self.psControllers[navData["benchNo"]].validatePw(pw):
			respHeader.setError(401)
			raise ValueError("Wrong password")
		nomVoltage = self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getNomVoltage"))
		overVoltage = validateFloat(sOverVoltage, respHeader, "overVoltage", 0, nomVoltage)
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("setOverVoltage", overVoltage))
		
class OverCurrentBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getOverCurrent"))
		
	def _put(self, respHeader, reqData, navData):
		sOverCurrent = validateSet(reqData, respHeader, "overCurrent", "pw")
		if not self.psControllers[navData["benchNo"]].validatePw(pw):
			respHeader.setError(401)
			raise ValueError("Wrong password")
		nomCurrent = self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getNomCurrent"))
		overCurrent = validateFloat(sOverCurrent, respHeader, "overCurrent", 0, nomCurrent)
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("setOverCurrent", overCurrent))
		
class StatusBranch(LnpsControllerBranch):	
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("getStatus"))
		
class DevBranch(ApiBranch):
	def __init__(self, psControllers):
		self.psControllers = psControllers
	
	def _get(self, respHeader, navData):
		return list(self.psControllers.keys())
		
class LedBranch(NoPsRequiredBranch):
	def __init__(self, ledController, psControllers):
		super().__init__(psControllers)
		self.ledController = ledController
		
	def _get(self, respHeader, navData):
		psController = self.psControllers[navData["benchNo"]]
		return self.ledController.waitQuery(LedRequest(True, psController.row, psController.col))
			
	def _put(self, respHeader, reqData, navData):
		psController = self.psControllers[navData["benchNo"]]
		mode = validateSet(reqData, respHeader, "mode")
		return self.ledController.waitQuery(LedRequest(False, psController.row, psController.col, mode))
		
class QueryBranch(LnpsControllerBranch):
	def _post(self, respHeader, reqData, navData):
		validateSet(reqData, respHeader, "hex", "pw")
		if not self.psControllers[navData["benchNo"]].validatePw(pw):
			respHeader.setError(401)
			raise ValueError("Wrong password")
		try:
			bytes = bytearray.fromhex(reqData["hex"])
		except ValueError:
			respHeader.setError(400)
			raise ValueError("hex is not a hexadecimal string")
		if len(bytes) < 3:
			respHeader.setError(400)
			raise ValueError("hex must be 3 bytes long (6 chars)")
		return self.psControllers[navData["benchNo"]].waitQuery(PsRequest("query", bytes))
		
class TestStatusBranch(NoPsRequiredBranch):
	def __init__(self, psControllers, testStatusController):
		super().__init__(psControllers)
		self.testStatusController = testStatusController

	def _get(self, respHeader, navData):
		id = self.psControllers[navData["benchNo"]].getId()
		return self.testStatusController.waitQuery(TestStatusRequest(TYPE_GET, id))
		
	def _put(self, respHeader, reqData, navData):
		status = html.escape(validateSet(reqData, respHeader, "teststatus"))
		id = self.psControllers[navData["benchNo"]].getId()
		return self.testStatusController.waitQuery(TestStatusRequest(TYPE_SET, id, status))
		
class NameBranch(NoPsRequiredBranch):
	def _get(self, respHeader, navData):
		return self.psControllers[navData["benchNo"]].getName()
	
class PwBranch(NoPsRequiredBranch):
	def _get(self, reqData, navData):
		return self.psControllers[navData["benchNo"]].getpw()
		
def createApi(psControllers, ledController, testStatusController):
	rootApi = RestAPI()
	dev = rootApi.add("/api/v1/dev", DevBranch(psControllers))
	bench = dev.add("<benchNo>")
	ps = bench.add("ps")
	general = ps.add("general")
	general.add("serialNo", SerialNoBranch(psControllers))
	general.add("manufacturer", ManBranch(psControllers))
	general.add("partNo", PartNoBranch(psControllers))
	general.add("swVersion", PartNoBranch(psControllers))
	general.add("type", TypeBranch(psControllers))
	general.add("nomVoltage", NomVolatageBranch(psControllers))
	general.add("nomCurrent", NomCurrentBranch(psControllers))
	general.add("nomPower", NomPowerBranch(psControllers))
	general.add("class", ClassBranch(psControllers))
	status = ps.add("status")
	status.add("voltage", VoltageBranch(psControllers))
	status.add("currentLimit", CurrentLimitBranch(psControllers))
	status.add("conf", ConfBranch(psControllers))
	status.add("remote", RemoteBranch(psControllers))
	status.add("switch", SwitchBranch(psControllers))
	status.add("overVoltage", OverVoltageBranch(psControllers))
	status.add("overCurrent", OverCurrentBranch(psControllers))
	status.add("status", StatusBranch(psControllers))
	bench.add("led", LedBranch(ledController, psControllers))
	ps.add("query", QueryBranch(psControllers))
	bench.add("pw", PwBranch(psControllers))
	bench.add("name", NameBranch(psControllers))
	bench.add("teststatus", TestStatusBranch(psControllers, testStatusController))
	return rootApi
	
def validateSet(arr, respHeader, *keys):
	res = []
	for k in keys:
		if not k in arr:
			respHeader.setError(400)
			raise ValueError("Key: " + str(k) + " is not set")
		else:
			res.append(arr[k])
	if len(res) == 1:
		return res[0]
	return res
	
def validateFloat(_value, respHeader, name, min, max):
	try:
		value = float(_value)
	except ValueError:
		respHeader.setError(400)
		raise ValueError(name + " is not a float (" + str(_value) + ")")
	
	if not (min <= value <= max):
		respHeader.setError(400)
		raise ValueError(name + " is not between " + str(min) + " and " + str(max) + "(" + str(value) + ")")	
	return value
		
def validateInt(_value, respHeader, name, min, max):
	try:
		value = int(_value)
	except ValueError:
		respHeader.setError(400)
		raise ValueError(name + " is not a float (" + str(_value) + ")")
	
	if not (min <= value <= max):
		respHeader.setError(400)
		raise ValueError(name + " is not between " + str(min) + " and " + str(max) + "(" + str(value) + ")")	
	return value	
	
def validateBool(_value, respHeader, name):
	try:
		value = int(_value)
	except ValueError:
		if _value.lower() == "true" or _value.lower() == "on":
			return 1
		elif _value.lower() == "false" or _value.lower() == "off":
			return 0
		else:
			respHeader.setError(400)
			raise ValueError(name + " is not a boolean (" + str(_value) + ")")
	return value
		