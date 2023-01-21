class CameraInfo(object):
	"""docstring for CameraInfo"""
	def __init__(self, manufacturer,serial_num,fw_ver,sf_ver):
		super(CameraInfo, self).__init__()
		self.manufacturer = manufacturer
		self.serial_num = serial_num
		self.fw_ver = fw_ver
		self.sf_ver = sf_ver