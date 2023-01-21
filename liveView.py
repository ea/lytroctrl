import sys
from lytroctrl import transactions
from lytroctrl import connections
from lytroctrl import utils
import re
import signal
from threading import Thread
import time
import os
import argparse


def main():

	parser = argparse.ArgumentParser(description='Start Live View')
	parser.add_argument('-a','--address',
						action="store",help="ip address",default="10.100.1.1")
	parser.add_argument('-p','--port', 
						action="store",help="destination port",default="5678")
	parser.add_argument('-l','--no-unlock',help="don't perform unlocking",action="store_true")
	args = parser.parse_args()


	con = connections.TcpConnection(args.address,int(args.port))
	con.connect()
	def signal_handler(sig, frame):
		print("Stopping Live View...")
		transactions.UDPLiveView(con).transact(enable=False,cratio=0,fps=0)
		print("Stopped")
		sys.exit(0)

	signal.signal(signal.SIGINT, signal_handler)

	if not args.no_unlock:
		print("Unlocking...")
		tr = transactions.GetCameraInfoTransact(con)
		ci = tr.transact()
		camera_serial = ci.serial_num
		transactions.UnlockTransact(con,camera_serial).unlock()
		print("Unlocked!")

	print("Starting Live View stream...")
	transactions.UDPLiveView(con).transact(enable=True,cratio=2,fps=1)
	print("Capture example: ffmpeg -i 'udp://224.0.0.100:10101?&localaddr=10.100.1.100' -vcodec copy output.mp4")
	utils.keep_alive(con)


if __name__ == '__main__':

	main()