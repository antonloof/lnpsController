from flask import send_from_directory, jsonify, request

from app import app, benches, testStatusController, ledController
from app.controller.psController import PsRequest
from app.controller.ledController import LedRequest
from app.controller.testStatusController import TestStatusRequest, TYPE_GET, TYPE_SET
from app.validate import *
from app.util import *

@app.route("/favicon.ico")
def favicon():
	return ""

@app.route("/web/")
def webIndex():
	return send_from_directory("web", "index.html")

@app.route("/web/<path:path>")
def staticWebFile(path):
	return send_from_directory("web", path)

@app.route("/api/v1/dev", methods = ["GET"])
def listBenches():
	return jsonify(list(benches.keys()))
	
@app.route("/api/v1/dev/<dev>/ps/general/serialNo", methods = ["GET"])
def getSerialNo(dev):
	return preformPsQuery(benches, dev, PsRequest("getSerialNo"))
	
@app.route("/api/v1/dev/<dev>/ps/general/manufacturer", methods = ["GET"])
def getManufacturer(dev):
	return preformPsQuery(benches, dev, PsRequest("getManufacturer"))
	
@app.route("/api/v1/dev/<dev>/ps/general/partNo", methods = ["GET"])
def getPartNo(dev):
	return preformPsQuery(benches, dev, PsRequest("getPartNo"))
	
@app.route("/api/v1/dev/<dev>/ps/general/swVersion", methods = ["GET"])
def getSwVersion(dev):
	return preformPsQuery(benches, dev, PsRequest("getSwVersion"))
	
@app.route("/api/v1/dev/<dev>/ps/general/type", methods = ["GET"])
def getType(dev):
	return preformPsQuery(benches, dev, PsRequest("getType"))

@app.route("/api/v1/dev/<dev>/ps/general/nomVoltage", methods = ["GET"])
def getNomVoltage(dev):
	return preformPsQuery(benches, dev, PsRequest("getNomVoltage"))

@app.route("/api/v1/dev/<dev>/ps/general/nomCurrent", methods = ["GET"])
def getNomCurrent(dev):
	return preformPsQuery(benches, dev, PsRequest("getNomCurrent"))
	
@app.route("/api/v1/dev/<dev>/ps/general/nomPower", methods = ["GET"])
def getNomPower(dev):
	return preformPsQuery(benches, dev, PsRequest("getNomPower"))
	
@app.route("/api/v1/dev/<dev>/ps/general/class", methods = ["GET"])
def getClass(dev):
	return preformPsQuery(benches, dev, PsRequest("getClass"))
	
@app.route("/api/v1/dev/<dev>/ps/status/voltage", methods = ["GET", "PUT"])
def voltage(dev):
	if request.method == "GET":
		return preformPsQuery(benches, dev, PsRequest("getVoltage"))
	else:
		if not dev in benches:
			return benchNotfound(dev)
			
		if not benches[dev].hasPs():
			return benchNoPs(dev)

		data = request.get_json(force = True)
		if not ("voltage" in data and "pw" in data):
			return missingKeys("voltage", "pw")
		
		if not benches[dev].validatePw(data["pw"]):
			return wrongPw()
		
		nomCurrent = benches[dev].waitQuery(PsRequest("getNomCurrent"))
		nomVoltage = benches[dev].waitQuery(PsRequest("getNomVoltage"))
		nomPower = benches[dev].waitQuery(PsRequest("getNomPower"))

		v,e = validateFloat("Voltage", data['voltage'], 0, nomVoltage)
		if not e:
			return jsonify(v), 400
		
		if nomPower >= nomCurrent * voltage:
			setCurrent = nomCurrent
		else:
			setCurrent = nomPower / v
			
		benches[dev].waitQuery(PsRequest("setCurrentLimit", setCurrent))
		return preformPsQuery(benches, dev, PsRequest("setVoltage", v))
			
@app.route("/api/v1/dev/<dev>/ps/status/currentLimit", methods = ["GET", "PUT"])
def currentLimit(dev):
	if request.method == "GET":
		return preformPsQuery(benches, dev, PsRequest("getCurrentLimit"))
	else:
		if not dev in benches:
			return benchNotfound(dev)

		if not benches[dev].hasPs(): 
			return benchNoPs(dev)
			
		data = request.get_json(force = True)
		if not ("currentLimit" in data and "pw" in data):
			return missingKeys("currentLimit", "pw")

		if not benches[dev].validatePw(data["pw"]):
			return wrongPw()
		
		nomCurrent = benches[dev].waitQuery(PsRequest("getNomCurrent"))
		voltage = benches[dev].waitQuery(PsRequest("getVoltage"))
		nomPower = benches[dev].waitQuery(PsRequest("getNomPower"))
		
		currentLimit,e = validateFloat("Current limit", data['currentLimit'], 0, nomCurrent)
		if not e:
			return jsonify(currentLimit), 400
			
		if currentLimit * voltage > nomPower:
			return jsonify("Current can not exceed " + str(nomPower / voltage) + "A at the currently configured voltage (" + str(voltage) + "V)"), 400
			
		return preformPsQuery(benches, dev, PsRequest("setCurrentLimit", currentLimit))

@app.route("/api/v1/dev/<dev>/ps/status/conf", methods = ["GET"])
def getConf(dev):
	return preformPsQuery(benches, dev, PsRequest("getConf"))
	
@app.route("/api/v1/dev/<dev>/ps/status/status", methods = ["GET"])
def getStatus(dev):
	return preformPsQuery(benches, dev, PsRequest("getStatus"))
	
@app.route("/api/v1/dev/<dev>/ps/status/remote", methods = ["GET", "PUT"])
def remote(dev):
	if request.method == "GET":
		return preformPsQuery(benches, dev, PsRequest("getRemote"))
	else:
		if not dev in benches:
			return benchNotfound(dev)
		data = request.get_json(force = True)
		if not ("remote" in data and "pw" in data):
			return missingKeys("remote", "pw")
			
		if not benches[dev].validatePw(data["pw"]):
			return wrongPw()
			
		v,e = validateBool("Remote", data["remote"])
		if not e:
			return jsonify(v), 400
			
		return preformPsQuery(dev, benches, PsRequest("setRemote", v))
		
@app.route("/api/v1/dev/<dev>/ps/status/switch", methods = ["GET", "PUT"])
def switch(dev):
	if request.method == "GET":
		return preformPsQuery(benches, dev, PsRequest("getSwitch"))
	else:
		if not dev in benches:
			return benchNotfound(dev)
		data = request.get_json(force = True)
		if not ("switch" in data and "pw" in data):
			return missingKeys("switch", "pw")
			
		if not benches[dev].validatePw(data["pw"]):
			return wrongPw()
			
		v,e = validateBool("Switch", data["switch"])
		if not e:
			return jsonify(v), 400
			
		return preformPsQuery(dev, benches, PsRequest("setSwitch", v))
		
@app.route("/api/v1/dev/<dev>/ps/status/overVoltage", methods = ["GET", "PUT"])
def overVoltage(dev):
	if request.method == "GET":
		return preformPsQuery(benches, dev, PsRequest("getOverVoltage"))
	else:
		data = request.get_json(force = True)

		if not dev in benches:
			return benchNotFound(dev)
		if not benches[dev].hasPs():
			return benchNoPs()
		
		if not ("overVoltage" in data and "pw" in data):
			return missingKeys("overVoltage", "pw")
			
		if not benches[dev].validatePw(data["pw"]):
			return wrongPw()
			
		nomVoltage = benches[dev].waitQuery(PsRequest("getNomVoltage"))
		v,e = validateFloat("Over voltage", data["overVoltage"], 0, nomVoltage)
		if not e:
			return jsonify(v), 400
		return preformPsQuery(benches, dev, PsRequest("setNomVoltage", v))
			
@app.route("/api/v1/dev/<dev>/ps/status/overCurrent", methods = ["GET", "PUT"])
def overCurrent(dev):
	if request.method == "GET":
		return preformPsQuery(benches, dev, PsRequest("getOverCurrent"))
	else:
		data = request.get_json(force = True)

		if not dev in benches:
			return benchNotFound(dev)
		if not benches[dev].hasPs():
			return benchNoPs()
		
		if not ("overCurrent" in data and "pw" in data):
			return missingKeys("overCurrent", "pw")
			
		if not benches[dev].validatePw(data["pw"]):
			return wrongPw()
			
		nomCurrent = benches[dev].waitQuery(PsRequest("getNomCurrent"))
		v,e = validateFloat("Over current", data["overCurrent"], 0, nomCurrent)
		if not e:
			return jsonify(v), 400
		return preformPsQuery(benches, dev, PsRequest("setNomCurrent", v))
			
@app.route("/api/v1/dev/<dev>/ps/query", methods = ["POST"])
def postQuery(dev):
	if not dev in benches:
		return benchNotFound(dev)
	if not benches[dev].hasPs():
		return benchNoPs()
		
	if not ("hex" in data and "pw" in data):
		return missingKeys("hex", "pw")
		
	if not benches[dev].validatePw(data["pw"]):
		return wrongPw()
		
	try:
		bytes = bytearray.fromhex(reqData["hex"])
	except ValueError:
		return jsonify("hex is not a hexadecimal string"), 400
	if len(bytes) < 3:
		return jsonify("hex must be 3 bytes long (6 chars)"), 400
		
	return preformPsQuery(benches, dev, PsRequest("query", bytes))
	
@app.route("/api/v1/dev/<dev>/teststatus", methods = ["GET", "PUT"])
def teststatus(dev):
	if not dev in benches:
		return benchNotfound(dev)
	if request.method == "GET":
		return jsonify(testStatusController.waitQuery(TestStatusRequest(TYPE_GET, benches[dev].getId())).res)
	else:
		data = request.get_json(force = True)
		if not "teststatus" in data:
			return missingKeys("teststatus")
		return jsonify(testStatusController.waitQuery(TestStatusRequest(TYPE_SET, benches[dev].getId(), data["teststatus"])).res)
			
@app.route("/api/v1/dev/<dev>/name", methods = ["GET"])
def getName(dev):
	if not dev in benches:
		return benchNotFound(dev)
	return jsonify(benches[dev].getName())
	
@app.route("/api/v1/dev/<dev>/pw", methods = ["GET"])
def getPw(dev):
	if not dev in benches:
		return benchNotFound(dev)
	return jsonify(benches[dev].getpw())
	
@app.route("/api/v1/dev/<dev>/led", methods = ["GET", "PUT"])
def led(dev):
	if not dev in benches:
		return benchNotFound(dev)
	bench = benches[dev]
	if request.method == "GET":
		res = ledController.waitQuery(LedRequest(True, bench.row, bench.col))
	else:
		data = request.get_json(force = True)
		if not "mode" in data:
			return missingKeys("mode")
		res = ledController.waitQuery(LedRequest(True, bench.row, bench.col, data["mode"]))
	if res.success:
		return jsonify(res.res)
	else:
		return jsonify(res.error), 400
