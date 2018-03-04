from flask import jsonify

def benchNotFound(dev):
	return jsonify("Bench " + dev + " does not exist"), 404
	
def benchNoPs(dev):
	return jsonify("Bench " + dev + " does not have a power supply"), 500

def missingKeys(*args):
	res = "Keys "
	for k in args:
		res += "'" + k + "' "
	res += "expected"
	return jsonify(res), 400
	
def wrongPw():
	return jsonify("Wrong password"), 401
	
def preformPsQuery(benches, dev, request):
	if dev in benches:
		if benches[dev].hasPs():
			res = benches[dev].waitQuery(request)
			if res.success:
				return jsonify(res.res)
			else:
				return jsonify(res.error), 400
		else:
			return benchNoPs(dev)
	else:
		return benchNotFound(dev)