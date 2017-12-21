from asyncRESTServer import *
import json
	
class ApiBranch():
	def get(self, respHeader, navData):
		self._get(respHeader, navData)
	
	def _get(self, respHeader, navData):
		respHeader.setError(404)
		
	def put(self, respHeader, reqData, navData):
		self._put(respHeader, reqData, navData)
		
	def _put(self, respHeader, reqData, navData):
		respHeader.setError(405)
	
	def post(self, respHeader, reqData, navData):
		self._post(respHeader, reqData, navData)
	
	def _post(self, respHeader, reqData, navData):
		respHeader.setError(405)
		
	def delete(self, respHeader, navData):
		self._delete(respHeader, navData)
		
	def _delete(self, respHeader, navData):
		respHeader.setError(405)
	
class RestAPI():
	def __init__(self, parent=None,name=""):
		self.parent = parent
		self.children = {}
		self.apiBranch = None
		self.isArray = False
		self.arrayKeyName = ""
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
			nextStart = 1
			self.isArray = step[0] == "<" and step[-1] == ">"
			if self.isArray:
				self.arrayKeyName = step[1:-1]
				step = steps[1]
				nextStart = 2
			if not step in self.children:
				self.children[step] = RestAPI(self, step)
			return self.children[step].addList(steps[nextStart:], apiBranch)
			
	def response(self, steps, method, respHeader, reqData, navData):
		if len(steps) == 0:
			return self.fetchData(method, respHeader, reqData, navData)
		else:
			step = steps[0]
			nextStart = 1
			if self.isArray:
				navData[self.arrayKeyName] = step
				if len(steps) >= 2:
					step = steps[1]
					nextStart = 2
				else:
					
					return self.fetchData(method, respHeader, reqData, navData)
			if step in self.children:
				return self.children[step].response(steps[nextStart:], method, respHeader, reqData, navData)
			else:
				respHeader.setError(404)
				return {}
				
	def fetchData(self, method, respHeader, reqData, navData):
		if self.apiBranch is None:
			if self.isArray and not self.arrayKeyName in navData:
				#ändra så att den ger alla
				respHeader.setError(400)
				raise ValueError("Getting entire lists not supported")
			res = {}
			for k,v in self.children.items():
				if k in reqData:
					res[k] = v.fetchData(method, respHeader, reqData[k], navData)
				else:
					res[k] = v.fetchData(method, respHeader, reqData, navData)
			return res
		if method == "GET":
			return self.apiBranch.get(respHeader, navData)
		elif method == "POST":
			return self.apiBranch.post(respHeader, reqData, navData)
		elif method == "PUT":
			return self.apiBranch.put(respHeader, reqData, navData)
		elif method == "DELETE":
			return self.apiBranch.delete(respHeader, navData)
		
	def executeQuery(self, reqHeaders, respHeader, reqData):
		return self.response(reqHeaders.url, reqHeaders.method, respHeader, reqData, {})


