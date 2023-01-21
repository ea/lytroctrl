import socket
from lytroctrl.commands import Message

class Connection(object):
	"""docstring for Connection"""
	BASE_MSG_LEN = None
	def __init__(self):
		super(Connection, self).__init__()
		
class UsbConnection(Connection):
	BASE_MSG_LEN = 12
	def __init__(self):
		#find camera
		dev = usb.core.find(idVendor=0x24cf, idProduct=0x00a1)
		#it would make more sense to augment lyli than try lowlevel usb/scsi in python
		# pyusb doesn't have direct implementation

		super(Connection,self).__init__()
	def connect(self):
		pass

class TcpConnection(Connection):
	"""docstring for TcpConnection"""
	BASE_MSG_LEN = 28
	def __init__(self, host,port):
		super(TcpConnection, self).__init__()
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	def connect(self):
		self.socket.connect((self.host,self.port))
	def send(self,msg):
		data = msg.build(base_msg_len=self.BASE_MSG_LEN)
		#print(">>>",msg)
		self.socket.send(data[:28])
		if len(data) > 28:
			self.socket.send(data[28:])		
	def recv(self):
		data = self.socket.recv(self.BASE_MSG_LEN)
		while len(data) != self.BASE_MSG_LEN:
			data += self.socket.recv(1)
		msg = Message.parse(data)
		if msg.flags == 0x03 or True:
			payload = b""
			while len(payload) != msg.length:
				payload+=self.socket.recv(1024)
			msg.payload = payload
		#print("<<<",msg)
		return msg
	def close(self):
		self.socket.close()