import threading, socket, json, os.path
from urllib import parse

HTTP_ERROR_MESS = {200:"OK", 400:"Bad Request",403:"Forbidden",404:"Not Found",405:"Method Not Allowed",411:"Length Required",415:"Unsupported Media Type"}

class AsyncRESTServer():
	def __init__(self, port, api):
		self.api = api
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.serversocket.bind((socket.gethostname(), port))
		self.serversocket.bind(("", port))		

	def start(self):		
		self.serversocket.listen(5)
		while True:
			cs, addr = self.serversocket.accept()
			ct = ClientThread(cs, self.api)
			ct.start()

class HTTPRequestHeader():
	def __init__(self):
		self.method = ""
		self.url = []
		self.headers = {}
		self.populated = False
		
	def hasHeader(self, h):
		return h in self.headers
		
	def getHeader(self, h):
		return self.headers[h]
		
	def parse(self, sHeader):
		#encode with ascii and carry on
		self.populated = False
		aHeader = str(sHeader, "ascii").split("\r\n")
		if len(aHeader) == 0:
			return False
		
		target = aHeader.pop(0)
		for kvp in aHeader:
			kvpsplit = kvp.split(":")
			if len(kvpsplit) < 2:
				return False
			self.headers[kvpsplit[0]] = (":".join(kvpsplit[1:])).strip()
		targetResult = self.parseTarget(target)
		if not targetResult:
			return False
		self.populated = True
		return True
	
	def parseTarget(self, target):
		split = target.split(" ")
		
		if len(split) < 2:
			return False
		if not split[0] in ["GET","POST","PUT","DELETE"]:
			return False
			
		self.method = split[0]
		#split on / and remove empty
		url = split[1].split("?")
		self.url = list(filter(None, url[0].split("/")))
		return True
	
	def __str__(self):
		return str(self.method) + str(self.url) + "\n" + str(self.headers)
	
class HTTPResponseHeader():
	def __init__(self):
		self.error = 0
		self.headers = {}
		
	def setError(self, e):
		self.error = e
		
	def tohttp(self):
		resp = b"HTTP/1.1 " + bytes(str(self.error), "ascii") + b" " + bytes(HTTP_ERROR_MESS[self.error], "ascii") + b"\r\n"
		for k,v in self.headers.items():
			resp += bytes(k, "ascii") + b":" + bytes(v, "ascii") + b"\r\n"
		resp += b"\r\n"
		return resp
	
	def add(self, k, v):
		self.headers[k] = str(v)
		
	def isOk(self):
		return self.error == 200
		
class ClientThread(threading.Thread):
	def __init__(self, cs, api):
		threading.Thread.__init__(self)
		self.cs = cs
		self.api = api
		self.endings = {"js": "application/javascript", "html": "text/html", "css": "text/css"}
		
	def run(self):
		header = HTTPRequestHeader()
		# fetch and parse the http request
		data = b""
		expectedLength = 0
		while True:
			packet = self.cs.recv(1024)
			
			# socket closed
			if not packet:
				break
			data += packet

			# http header finished
			if b"\r\n\r\n" in data and not header.populated:
				split = data.split(b"\r\n\r\n")
				sHeader = split[0]
				if len(split) > 1:
					data = split[1]
				else:
					data = b""
				if not header.parse(sHeader):
					self.respondeError(400)
					return
				if header.hasHeader("Content-Length"):
					expectedLength = int(header.getHeader("Content-Length"))
					
			# wait for remaining data
			if header.populated:
				if len(data) == expectedLength:
					break
				elif len(data) > expectedLength:
					self.respondeError(411)
		
		#parse message body if required
		reqData = {}
		if header.method in ["PUT", "POST"]:
			if not (header.hasHeader("Content-Type") and header.getHeader("Content-Type") == "application/json"):
				self.respondeError(415)
				return
			try:
				reqData = json.loads(str(data, "UTF-8"))
			except (json.decoder.JSONDecodeError, ValueError):
				self.respondeError(400)
				return
			if reqData == None:
				self.respondeError(415)
				return
		# construct a reply
		if len(header.url) > 0 and header.url[0] == "api":
			respHeader, content = self.apiResponse(header, reqData)
		elif len(header.url) > 0 and header.url[0] == "web":
			respHeader, content = self.webResponse(header, reqData)
		else:
			respHeader = HTTPResponseHeader()
			respHeader.setError(403)
			content = b""
		
		self.cs.send(respHeader.tohttp() + content)
		self.cs.close()
		
	def webResponse(self, reqHeaders, reqData):
		respHeader = HTTPResponseHeader()
		respHeader.setError(200)
		
		file = reqHeaders.url[-1]
		if file.count(".") == 0:
			file = "index.html"
			folder = os.path.join(*reqHeaders.url)
		else:
			folder = os.path.join("", *(reqHeaders.url[:-1]))
			
		if folder.count(".") != 0:
			respHeader.setError(403)
			return respHeader, b""		
		
		if file.count(".") < 1:
			respHeader.setError(403)
			return respHeader, b""
		
		ending = file.split(".")[1]
		if ending in self.endings:
			contentType = self.endings[ending]
		else:
			contentType = "text/plain"
		path = os.path.join(folder, file)
		if not os.path.isfile(path):
			respHeader.setError(404)
			return respHeader, b""
		
		with open(path) as f:
			content = f.read()
		respHeader.add("Content-Type", contentType)
		respHeader.add("Content-Length", len(content))
		return (respHeader, bytes(content, "utf-8"))
			
	def apiResponse(self, reqHeaders, reqData):
		respHeader = HTTPResponseHeader()
		respHeader.setError(200)
		
		content = self.api.executeQuery(reqHeaders, respHeader, reqData)
		sContent = json.dumps(content)
		respHeader.add("Content-Type", "application/json")
		respHeader.add("Content-Length", len(sContent))
		return (respHeader, bytes(sContent, "utf-8"))
		
	def respondeError(self, httpErrorCode):
		self.cs.send(b"HTTP/1.1 " + httpErrorCode + b" " + HTTP_ERROR_MESS[httpErrorCode] + b"\r\nContent-Length:0\r\n\r\n")
