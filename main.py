import threading, json, serial
from asyncRESTServer import *
from psconnection import * 
import restapiDefs

CONFIG_FILE = "ps_config.json"
with open(CONFIG_FILE, "r") as f:
	config = json.load(f)

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

psThreadContainers = {}
for i in range(len(config["ports"])):
	for ps in pss:
		if ps.getSerialNo() == config["powersupplies"][i]["serialNo"]:
			psThreadContainers[str(config["powersupplies"][i]["dev"])] = PsThreadContainer(ps)
			break
			
rootApi = restapiDefs.createApi(psThreadContainers)	

server = AsyncRESTServer("localhost", 5049, rootApi)
server.start()
