from psconnection import *
import threading
from restapi import *

class LnpsControllerBranch(ApiBranch):
	def __init__(self, psThreadContainers):
		self.psThreadContainers = psThreadContainers
		
	def get(self, respHeader, navData):
		if navData["benchNo"] in self.psThreadContainers:
			return self._get(respHeader, navData)
		else:
			respHeader.setError(404)
			raise ValueError("Bench no " + navData["benchNo"] + " does not exist")
			
	def put(self, respHeader, reqData, navData):
		if navData["benchNo"] in self.psThreadContainers:
			return self._put(respHeader, reqData, navData)
		else:
			respHeader.setError(404)
			raise ValueError("Bench no " + navData["benchNo"] + " does not exist")
	
class SerialNoBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getSerialNo"))
		
class ManBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getManufacturer"))
		
class PartNoBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getPartNo"))
		
class SWVersionBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getSWVersion"))
		
class TypeBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getType"))
		
class NomVolatageBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getNomVoltage"))
		
class NomCurrentBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getNomCurrent"))
		
class NomPowerBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getNomPower"))
		
class ClassBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getClass"))
		
class VoltageBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getVoltage"))
		
	def _put(self, respHeader, reqData, navData):
		sVoltage = validateSet(reqData, respHeader, "voltage")
		nomVoltage = self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getNomVoltage"))
		nomPower = self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getNomPower"))
		nomCurrent = self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getNomCurrent"))
		voltage = validateFloat(sVoltage, respHeader, "voltage", 0, nomVoltage)
		# limit current before setting voltage
		if nomPower / voltage > nomCurrent:
			setCurrent = nomCurrent
		else:
			setCurrent = nomPower / voltage
		self.psThreadContainers[navData["benchNo"]].waitQuery(Request("setCurrent", setCurrent))
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("setVoltage", voltage))
		
class CurrentLimitBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getCurrentLimit"))
		
	def _put(self, respHeader, reqData, navData):
		sCurrent = validateSet(reqData, respHeader, "current")
		nomCurrent = self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getNomCurrent"))
		current = validateFloat(sCurrent, respHeader, "current", 0, nomCurrent)
		nomPower = self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getNomPower"))
		voltage = self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getVoltage"))
		if current * voltage > nomPower:
			respHeader.setError(400)
			raise ValueError("Current can not exceed " + str(nomPower / voltage) + "A at the currently configured voltage (" + str(voltage) + "V)")
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("setCurrentLimit", current))
		
class ConfBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getConf"))

class RemoteBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getRemote"))
		
	def _put(self, respHeader, reqData, navData):
		sRemote = validateSet(reqData, respHeader, "remote")
		remote = validateBool(sRemote, respHeader, "remote")
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("setRemote", remote))
		
class SwitchBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getSwitch"))
	
	def _put(self, respHeader, reqData, navData):
		sSwitch = validateSet(reqData, respHeader, "switch")
		switch = validateBool(sSwitch, respHeader, "switch")
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("setSwitch", switch))
		
class OverVoltageBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getOverVoltage"))
		
	def _put(self, respHeader, reqData, navData):
		sOverVoltage = validateSet(reqData, respHeader, "overVoltage")
		nomVoltage = self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getNomVoltage"))
		overVoltage = validateFloat(sOverVoltage, respHeader, "overVoltage", 0, nomVoltage)
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("setOverVoltage", overVoltage))
		
class OverCurrentBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getOverCurrent"))
		
	def _put(self, respHeader, reqData, navData):
		sOverCurrent = validateSet(reqData, respHeader, "overCurrent")
		nomCurrent = self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getNomCurrent"))
		overCurrent = validateFloat(sOverCurrent, respHeader, "overCurrent", 0, nomCurrent)
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("setOverCurrent", overCurrent))
		
class StatusBranch(LnpsControllerBranch):	
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getStatus"))
		
def createApi(psThreadContainers):
	rootApi = RestAPI()
	ps = rootApi.add("/api/v1/dev/<benchNo>/ps")
	general = ps.add("general")
	general.add("serialNo", SerialNoBranch(psThreadContainers))
	general.add("manufacturer", ManBranch(psThreadContainers))
	general.add("partNo", PartNoBranch(psThreadContainers))
	general.add("swVersion", PartNoBranch(psThreadContainers))
	general.add("type", TypeBranch(psThreadContainers))
	general.add("nomVoltage", NomVolatageBranch(psThreadContainers))
	general.add("nomCurrent", NomCurrentBranch(psThreadContainers))
	general.add("nomPower", NomPowerBranch(psThreadContainers))
	general.add("class", ClassBranch(psThreadContainers))
	status = ps.add("status")
	status.add("voltage", VoltageBranch(psThreadContainers))
	status.add("currentLimit", CurrentLimitBranch(psThreadContainers))
	status.add("conf", ConfBranch(psThreadContainers))
	status.add("remote", RemoteBranch(psThreadContainers))
	status.add("switch", SwitchBranch(psThreadContainers))
	status.add("overVoltage", OverVoltageBranch(psThreadContainers))
	status.add("overCurrent", OverCurrentBranch(psThreadContainers))
	status.add("status", StatusBranch(psThreadContainers))
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
		
def validateBool(_value, respHeader, name):
	try:
		value = int(_value)
	except ValueError:
		respHeader.setError(400)
		raise ValueError(name + " is not a boolean (" + str(_value) + ")")
	return value
		