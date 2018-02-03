from asyncRESTServer import *
import json
	
class ApiBranch():
	def get(self, respHeader, navData):
		return self._get(respHeader, navData)
	
	def _get(self, respHeader, navData):
		respHeader.setError(404)
		raise ValueError("Not Found")
		
	def put(self, respHeader, reqData, navData):
		return self._put(respHeader, reqData, navData)
		
	def _put(self, respHeader, reqData, navData):
		respHeader.setError(405)
		raise ValueError("Not allowed")
	
	def post(self, respHeader, reqData, navData):
		return self._post(respHeader, reqData, navData)
	
	def _post(self, respHeader, reqData, navData):
		respHeader.setError(405)
		raise ValueError("Not allowed")
		
	def delete(self, respHeader, navData):
		return self._delete(respHeader, navData)
		
	def _delete(self, respHeader, navData):
		respHeader.setError(405)
		raise ValueError("Not allowed")
		
class RestAPI():
	def __init__(self, parent=None, name="", isKey=False):
		self.parent = parent
		self.children = {}
		self.apiBranch = None
		self.isArray = False
		self.key = None
		self.isKey = isKey
		self.name = name
		
	def add(self, path, apiBranch=None):
		steps = list(filter(None, path.split("/")))
		return self.addList(steps, apiBranch)
		
	def addList(self, steps, apiBranch):
		if len(steps) == 0:
			self.apiBranch = apiBranch
			return self
		else:
			step = steps[0]
			if step[0] == "<" and step[-1] == ">":
				step = step[1:-1]
				self.isArray = True
				if self.key is None:
					self.key = RestAPI(self, step, True)
				elif self.key.name != step:
					raise ValueError("An array can't have two different key names")
				return self.key.addList(steps[1:], apiBranch)
			if not step in self.children:
				self.children[step] = RestAPI(self, step, False)
			return self.children[step].addList(steps[1:], apiBranch)
			
	def response(self, steps, method, respHeader, reqData, navData):
		if len(steps) == 0:
			return self.fetchData(method, respHeader, reqData, navData)
		else:
			step = steps[0]
			if self.isArray:
				navData[self.key.name] = step
				return self.key.response(steps[1:], method, respHeader, reqData, navData)
			if step in self.children:
				return self.children[step].response(steps[1:], method, respHeader, reqData, navData)
			else:
				respHeader.setError(404)
				return None
				
	def fetchData(self, method, respHeader, reqData, navData):
		if self.apiBranch is None:
			if self.isArray:
				respHeader.setError(400)
				raise ValueError("Getting entire lists not supported")
			res = {}
			for k,v in self.children.items():
				try:
					if k in reqData:
						res[k] = v.fetchData(method, respHeader, reqData[k], navData)
					else:
						res[k] = v.fetchData(method, respHeader, reqData, navData)
				except ValueError as e:
					res[k] = str(e)
			return res
		
		try:
			if method == "GET":
				return self.apiBranch.get(respHeader, navData)
			elif method == "POST":
				return self.apiBranch.post(respHeader, reqData, navData)
			elif method == "PUT":
				return self.apiBranch.put(respHeader, reqData, navData)
			elif method == "DELETE":
				return self.apiBranch.delete(respHeader, navData)
		except ValueError as e:
			respHeader.setError(400)
			return str(e)
			
	def executeQuery(self, reqHeaders, respHeader, reqData):
		return self.response(reqHeaders.url, reqHeaders.method, respHeader, reqData, {})
