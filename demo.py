import sys
from lytroctrl import transactions
from lytroctrl import connections
import re
import signal
from threading import Thread
import time
import os
import argparse

def main():

	parser = argparse.ArgumentParser(description='Lytro control demo')
	parser.add_argument('-a','--address',
						action="store",help="ip address",default="10.100.1.1")
	parser.add_argument('-p','--port', 
						action="store",help="destination port",default="5678")
	parser.add_argument('-l','--no-unlock',help="don't perform unlocking",action="store_true")
	args = parser.parse_args()

	con = connections.TcpConnection(args.address,int(args.port))
	con.connect()
	if not args.no_unlock:
		print("Unlocking...")
		tr = transactions.GetCameraInfoTransact(con)
		ci = tr.transact()
		camera_serial = ci.serial_num
		transactions.UnlockTransact(con,camera_serial).unlock()
		print("Unlocked!")

	print("Do the lens dance")
	transactions.ExecTransact(con,"rfitamron wiggle").transact()
	time.sleep(3)
	print("Zooming to x3.14...")
	transactions.SetZoom(con).transact(payload=b"3.14")
	time.sleep(1)
	print("Taking photo")
	transactions.ExecTransact(con,"rficapture").transact()



if __name__ == '__main__':
	main()