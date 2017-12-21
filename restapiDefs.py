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
			respHeader.error(404)
			raise ValueError("Bench no " + navData["benchNo"] + " does not exist")
			
	def put(self, respHeader, reqData, navData):
		if navData["benchNo"] in self.psThreadContainers:
			return self._put(respHeader, reqData, navData)
		else:
			respHeader.error(404)
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
		
class VoltageBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getVoltage"))
		
class CurrentBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getCurrent"))
		
class ConfBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getConf"))

class RemoteBranch(LnpsControllerBranch):
	def _get(self, respHeader, navData):
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("getRemote"))
		
	def _put(self, respHeader, reqData, navData):
		if not "remote" in reqData:
			respHeader.error(400)
			raise ValueError("Remote not set")
		
		try:
			remote = int(reqData["remote"])
		except ValueError:
			respHeader.error(400)
			raise ValueError("Remote is not int")
		return self.psThreadContainers[navData["benchNo"]].waitQuery(Request("setRemote", remote))
		
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
	status = ps.add("status")
	status.add("voltage", VoltageBranch(psThreadContainers))
	status.add("current", CurrentBranch(psThreadContainers))
	status.add("conf", ConfBranch(psThreadContainers))
	status.add("remote", RemoteBranch(psThreadContainers))
	return rootApi