import threading, json, serial
import restapiDefs
from psController import *
from ledController import *
from testStatusController import *
from asyncRESTServer import *

CONFIG_FILE = "config.json"
with open(CONFIG_FILE, "r") as f:
	config = json.load(f)

#validate the config file
if not "ports" in config:
	print("Config file does not contain 'ports' key")
	exit(0)
if not "ledPort" in config:
	print("Config file does not contain 'ledPort' key")
	exit(0)
if not "powersupplies" in config:
	print("Config file does not contain 'powersupplies' key")
	exit(0)
	
if len(config["ports"]) != len(config["powersupplies"]):
	print("Could not start server, config file does not describe an equal amount of powersupplies and ports")
	exit(0)

pss = []
for port in config["ports"]:
	try:
		pss.append(PowerSupply(port))
	except serial.serialutil.SerialException:
		print("Could not start server, com port", port, "could not be opened")
		exit(0)

psControllers = {}
for i in range(len(config["ports"])):
	for ps in pss:
		if ps.getSerialNo() == config["powersupplies"][i]["serialNo"]:
			controller = PsController(ps)
			controller.start()
			ps.name = config["powersupplies"][i]["name"]
			psControllers[str(config["powersupplies"][i]["dev"])] = controller
			break
			
ledController = LedController(config["ledPort"])
ledController.start()
testStatusController = TestStatusController()
testStatusController.start()
rootApi = restapiDefs.createApi(psControllers, ledController, testStatusController)	

server = AsyncRESTServer("localhost", 5049, rootApi)
server.start()
