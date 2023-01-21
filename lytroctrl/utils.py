import hashlib
import time
from lytroctrl import transactions
		
def get_sha1(msg):
	h = hashlib.sha1(bytes(msg,"utf-8"))
	return h.hexdigest()


def keep_alive(con):
	while True:
		transactions.GetCameraInfoTransact(con)
		time.sleep(30)