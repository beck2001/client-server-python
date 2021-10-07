import time
import socket


class ClientError(Exception):
	pass


class Client:
	
	def __init__(self, host, port, timeout=None):
		self._host = host
		self._port = port
		self._timeout= timeout
	
		try:
			self._sock = socket.create_connection((self._host, self._port), self._timeout)
		except socket.error as err:
			raise ClientError(err)

	def put(self, key, value, timestamp=None):
		timestamp = str(timestamp or int(time.time()))
		send_data = f"put {key} {value} {timestamp}\n".encode("utf8")

		try:
			self._sock.sendall(send_data)
			resp = self._sock.recv(1024)
			if b"ok\n" not in resp:
				raise ClientError()
		except Exception as err:
			raise ClientError(err)

	def get(self, key):
		result = {}
		send_data = f"get {key}".encode("utf8")

		try:
			self._sock.sendall(send_data)
			resp = self._sock.recv(1024)
			if b"ok\n" not in resp:
				raise ClientError()
	
			resp = str(resp).strip("\n").split("\n")
			for m in resp:
				metrics = m.split(" ")
				if len(metrics) == 3:
					key = metrics[0]
					value = metrics[1]
					timestamp = metrics[2]
					metrics_list = result.get(key, [])
					metrics_list.append((timestamp, value))
					result.update({key: sorted(metrics_list)})
				elif metrics not in [["b'ok"], [""], ["'"]]:
					raise ClientError()
			return result
		except Exception as err:
			raise ClientError(err)


if __name__ == "__main__":
	client = Client("127.0.0.1", 8888, timeout=15)
	print(client.get("*"))		





