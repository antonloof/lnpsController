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
configKeys = ["ledPort", "benches", "ports", "serverPort"]
for key in configKeys:
	if not key in config:
		print("Config file does not contain key", key)
		exit(0)

pss = []
for port in config["ports"]:
	try:
		pss.append(PowerSupply(port))
	except serial.serialutil.SerialException:
		print("Could not start server, com port", port, "could not be opened")
		exit(0)

benches = {}

for i in range(len(config["benches"])):
	bench = config["benches"][i]
	controller = PsController(bench["pw"], bench["row"], bench["col"], bench["id"], bench["name"])
	if "ps" in config["benches"][i]:
		for ps in pss:
			if ps.getSerialNo() == bench["ps"]:
				controller.ps = ps
				controller.start()
			
	benches[config["benches"][i]["id"]] = controller
			
ledController = LedController(config["ledPort"])
ledController.start()
testStatusController = TestStatusController()
testStatusController.start()
rootApi = restapiDefs.createApi(benches, ledController, testStatusController)	

server = AsyncRESTServer("localhost", config["serverPort"], rootApi)
server.start()
