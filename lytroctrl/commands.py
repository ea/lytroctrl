from enum import Enum,Flag, auto
import struct

SYNC_HEADER = 0xFAAA55AF 

class CommandClass(Enum):
	CMD_CTRL = 0xC0
	CMD_FW = 0xC1
	CMD_LOAD = 0xC2
	CMD_CLR = 0xC3
	CMD_READ = 0xC4
	CMD_FW_UP = 0xC5
	CMD_QUERY = 0xC6


class CtrlCmd(Enum):
	CMD_CLASS = CommandClass.CMD_CTRL
	TAKE_PHOTO = 0x00
	DELETE = 0x01
	UPDATE_FW = 0x02
	REBOOT = 0x03
	SET_TIME = 0x04
	UNK1 = 0x05 # something with files
	UNK2 = 0x06 # delete all ? 
	SET_SHARE_MODE_SSID = 0x07
	SET_SYNC_MODE_SSID = 0x08
	SET_SHARE_MODE_PASS = 0x09
	SET_SYNC_MODE_PASS = 0x0A
	SET_SHARE_MODE_AUTH = 0x0B
	MANUAL_CTRL = 0x0C
	WIFI_OFF = 0x0D
	INJECT_UART = 0xFE
	EXEC_CMD = 0xFF

class FwCmd(Enum):
	CMD_CLASS = CommandClass.CMD_FW
	SET_FW_SIZE = 0x00

class LoadCmd(Enum):
	CMD_CLASS = CommandClass.CMD_LOAD
	CAMERA_INFO = 0x00
	FILE = 0x01
	PHOTO_LIST = 0x02
	UNK1 = 0x03
	UNUSED = 0x04
	PHOTO = 0x05
	CALLIBRATION = 0x06
	RAW  = 0x0a
	CRASHES = 0x0b

class ClearCmd(Enum):
	CMD_CLASS = CommandClass.CMD_CLR
	CLEAR_BUFFERS = 0x00

class ReadCmd(Enum):
	CMD_CLASS = CommandClass.CMD_READ
	READ = 0x00

class FirmwareUploadCmd(Enum):
	CMD_CLASS = CommandClass.CMD_FW_UP
	UPLOAD_CHUNK = 0x00

class QueryCmd(Enum):
	CMD_CLASS = CommandClass.CMD_QUERY
	CONTENT_LENGTH = 0x00
	UNK1 = 0x01
	READ_UART = 0x02
	CAMERA_TIME = 0x03
	RECOVER_CALLIBRATION  = 0x04
	READ_GLOB_80020a60 = 0x05
	BATTERY = 0x06
	SETTINGS = 0x0A



class Flags(Flag):
	HAS_PAYLOAD = auto()
	HAS_BUFFER = auto()

class Message(object):
	CMD = None
	def __init__(self,is_response = False,length = 0,extra_params=None ,payload = b""):
		self.payload = payload
		self.length = length
		self.flags = (is_response << 1) | (len(payload) == 0)
		self.extra_params = extra_params
		if self.flags & 0x01: #length is response length
			self.length = length
		elif self.payload:
			self.length = len(payload)
		super(Message, self).__init__()
	def __repr__(self):
		return repr("{} {} {} ".format(self.CMD,self.length,self.build()))

	def build(self,base_msg_len=0):
		bmesg = struct.pack("IIIHB",SYNC_HEADER,self.length,self.flags,self.CMD.CMD_CLASS.value.value,self.CMD.value)
		if self.extra_params:
			bmesg += self.extra_params
		if base_msg_len:
			bmesg += b"\x00"*(base_msg_len-len(bmesg))
		if not self.flags & 0x01:
			bmesg += self.payload
		return bmesg

	@classmethod
	def parse(cls,data):
		_,length,flags,cmd_class,cmd = struct.unpack("IIIHB",data[0:15])
		extra_params = None
		if len(data) > 16:
			extra_params = data[16:]
		is_response = False
		payload = b""
		if flags & 0x02:
			is_response = True
		if flags & 0x01:
			payload = b"\xea" #just a placeholder , will be populated later
		#is_response,length,extra_params,payload
		msg = msg_cls_mapping[cmd_class][cmd]()
		msg.flags = flags
		msg.extra_params = extra_params
		msg.payload = payload
		msg.length = length
		return msg





class GetTime(Message):
	CMD = QueryCmd.CAMERA_TIME
	"""docstring for GetTime"""
	def __init__(self,length=0xff):
		super(GetTime, self).__init__(length=length)
		
class ContentLength(Message):
	CMD = QueryCmd.CONTENT_LENGTH
	def __init__(self):
		super(ContentLength, self).__init__(length=0x4)
	
class ReadUart(Message):
	CMD = QueryCmd.READ_UART
	def __init__(self):
		super(ReadUart, self).__init__(length=0xfffff)

class GetCameraInfo(Message):
	CMD = LoadCmd.CAMERA_INFO
	def __init__(self):
		super(GetCameraInfo, self).__init__()

class LoadFile(Message):
	CMD = LoadCmd.FILE
	def __init__(self,payload):
		super(LoadFile, self).__init__(length=len(payload),payload=payload)
		
class Read(Message):
	CMD = ReadCmd.READ
	def __init__(self):
		super(Read, self).__init__(length=0xffff)
		

class CmdExec(Message):
	CMD = CtrlCmd.EXEC_CMD
	def __init__(self,cmd_text=""):
		super(CmdExec,self).__init__(payload=bytes(cmd_text,"utf-8")+b"\x00")

class CmdUDPLiveView(Message):
	CMD = CtrlCmd.MANUAL_CTRL
	def __init__(self,enable=True,cratio=1,fps=2):
		payload = b""
		if enable: 
			payload	+= b"1"
		else:
			payload += b"0"
		payload += bytes(str(cratio)+str(fps),"utf-8")
		super(CmdUDPLiveView,self).__init__(payload=payload,extra_params=b"\x07")

class CmdSetZoom(Message):
	CMD= CtrlCmd.MANUAL_CTRL
	def __init__(self,payload="0.0"):
		super(CmdSetZoom,self).__init__(payload=payload,extra_params=b"\x03")

class CmdManualCtrl(Message):
	CMD= CtrlCmd.MANUAL_CTRL
	def __init__(self,payload=None):
		payload = b"1.1"
		super(CmdManualCtrl,self).__init__(payload=payload,extra_params=b"\x06")

msg_cls_mapping = {}
for cmd_class in CommandClass:
	msg_cls_mapping[cmd_class.value] = {}
for msg_cls in Message.__subclasses__():
	msg_cls_mapping[msg_cls.CMD.CMD_CLASS.value.value][msg_cls.CMD.value] = msg_cls 
