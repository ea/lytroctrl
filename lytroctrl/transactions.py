from lytroctrl.commands import *
from lytroctrl.payloads import *
from lytroctrl.utils import get_sha1

class Transaction(object):
	CmdSequence = []
	def __init__(self,connection):
		super(Transaction, self).__init__()
		self.seq_idx = 0
		self.connection = connection
	def transact(self,payload=b""):
		while self.seq_idx < len(self.CmdSequence):
			msg = self.CmdSequence[self.seq_idx](payload=payload)
			self.connection.send(msg)
			msg = self.connection.recv()
			payload = msg.payload
			self.seq_idx += 1
		return payload


class GetTimeTransact(Transaction):
	"""docstring for GetTimeTransact"""
	CmdSequence = [GetTime]
	def transact(self):
		b = self.transact_one({"length": 0xff})
		print(b)
		#self.connection.send(msg)
		#msg = self.connection.recv()
		#return msg.payload
		
class GetCameraInfoTransact(Transaction):
	"""docstring for GetCameraInfoTransact"""
	CmdSequence = [GetCameraInfo,ContentLength]
	def transact(self):
		msg = GetCameraInfo()
		self.connection.send(msg)
		_ = self.connection.recv()
		read_tr = ReadTransact(self.connection)
		info_payload = read_tr.transact()
		mfc = info_payload[:info_payload.index(b"\x00")]
		serial_num = info_payload[256:256+info_payload[256:].index(b"\x00")]
		fw_ver = info_payload[384:384+info_payload[384:].index(b"\x00")]
		sf_ver = info_payload[512:512+info_payload[512:].index(b"\x00")]
		return CameraInfo(mfc.decode("utf-8"),serial_num.decode("utf-8"),fw_ver.decode("utf-8"),sf_ver.decode("utf-8"))

class ReadFileTransact(Transaction):
	"""docstring for ReadFile"""
	def __init__(self, connection,filename):
		super(ReadFileTransact, self).__init__(connection)
		self.connection = connection
		self.filename = filename
	def transact(self):
		msg = LoadFile(payload=bytes(self.filename,'utf-8')+b"\x00")
		self.connection.send(msg)
		msg = self.connection.recv()
		print("load",msg.payload)
		read_tr = ReadTransact(self.connection)
		print(read_tr.transact().decode("unicode_escape"))		

class ReadTransact(Transaction):
	"""docstring for ReadTransact"""
	def __init__(self, connection):
		self.connection = connection
		super(ReadTransact, self).__init__(connection)
	def transact(self):
		self.connection.send(ContentLength())
		msg = self.connection.recv()
		total_length = struct.unpack("I",msg.payload)[0]
		total_read = 0
		data = b""
		print(total_length)
		while total_read != total_length:
			self.connection.send(Read())
			msg = self.connection.recv()
			total_read += msg.length
			data += msg.payload
		return data

class UnlockTransact(object):
	"""docstring for UnlockTransact"""
	def __init__(self,connection, serial_num):
		super(UnlockTransact, self).__init__()
		self.connection = connection
		self.serial_num = serial_num
	def unlock(self):
		print(self.serial_num)
		secret_hash = get_sha1(self.serial_num + " please")
		self.connection.send(CmdExec(secret_hash))
		_ = self.connection.recv()

class SyncUartTransact(object):
	"""docstring for SyncUartTransact"""
	def __init__(self, connection):
		super(SyncUartTransact, self).__init__()
		self.connection = connection
	def transact(self):
		output = ""
		while True:
			self.connection.send(ReadUart())
			msg = self.connection.recv()
			out =  msg.payload.decode("unicode_escape")
			if len(out) < 450:
				break
			output += out
		return output

		
class ExecTransact(object):
	"""docstring for ExecTransact"""
	def __init__(self, connection,cmd):
		super(ExecTransact, self).__init__()
		self.connection = connection
		self.cmd = cmd
	def transact(self):
		self.connection.send(CmdExec(self.cmd))
		_ = self.connection.recv()
		#SyncUartTransact(self.connection).transact()
	
class UDPLiveView(Transaction):
	CmdSequence = [CmdUDPLiveView]
	def transact(self,enable=True,cratio=1,fps=2):
		self.connection.send(CmdUDPLiveView(enable,cratio,fps))
		self.connection.recv()

class SetZoom(Transaction):
	CmdSequence = [CmdSetZoom]


class CmdManual(Transaction):
	CmdSequence = [CmdManualCtrl]
