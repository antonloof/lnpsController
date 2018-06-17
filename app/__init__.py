from flask import Flask
import json, serial, threading
from app.controller.psController import *
from app.controller.ledController import *
from app.controller.testStatusController import *

CONFIG_FILE = "config.json"
with open(CONFIG_FILE, "r") as f:
	try:
		config = json.load(f)
	except json.decoder.JSONDecodeError:
		print("FATAL: Could not parse config file:", CONFIG_FILE)
		exit(0)
		
#validate the config file
configKeys = ["ledPort", "benches", "ports"]
for key in configKeys:
	if not key in config:
		print("FATAL: Config file does not contain key", key)
		exit(0)

pss = []
usedPss = []
for port in config["ports"]:
	ps = PowerSupply(port)
	pss.append(ps)
	usedPss.append(False)
	if not ps.isConnected:
		print("FATAL: Could not connect to power supply at port", port, "during start up")
		exit(0)

benches = {}
benchKeys = ["pw", "row", "col", "id", "name"]
for i in range(len(config["benches"])):
	bench = config["benches"][i]
	# check keys in every bench
	for k in benchKeys:
		if not k in bench:
			print("FATAL: Key", k, "not found in bench", i)
			exit(0)
	
	# add ps controller if found
	controller = PsController(bench["pw"], bench["row"], bench["col"], bench["id"], bench["name"])
	if "ps" in bench:
		for j in range(len(pss)):
			if pss[j].getSerialNo() == bench["ps"]:
				controller.setPs(pss[j])
				usedPss[j] = True
	
	if not controller.hasPs():
		print("WARNING: Bench", bench["name"], "does not have a power supply")
	
	benches[config["benches"][i]["id"]] = controller

# warn user if there are any unused power supplies
for i in range(len(pss)):
	if not usedPss[i]:
		print("WARNING: Power supply at port", config["ports"][i], "is not used by any bench")

# try to connect to led controller
ledController = LedController(config["ledPort"])
if not ledController.isConnected:
	print("FATAL: Could not connect to led controller")
	exit(0)
ledController.start()
	
print("INFO: CONFIG PARSING FINISHED")
testStatusController = TestStatusController()
testStatusController.start()

app = Flask(__name__, static_url_path='')

from app import routes
