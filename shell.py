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



def signal_handler(sig, frame):
    os._exit(0)




def filter_output(o):
	blue_marker = "\x1b[34m"
	white_marker = "\x1b[m"
	output = re.sub("\x1b\[34m.*?\x1b\[m",'',o,flags=re.DOTALL) # filter blue 
	output = re.sub('\[\d{8}\.\d{6}\] ','',output) #filter time
	return output 


def shell(con,verbose=False):
	r = re.compile('\[m\[\d{8}\.\d{6}\]')
	while True:
		output = transactions.SyncUartTransact(con).transact()
		if not verbose:
			output = filter_output(output)
		print(output)
		cmd_line = input(">")
		transactions.ExecTransact(con,cmd_line).transact()

def main():

	parser = argparse.ArgumentParser(description='Lytro control shell')
	parser.add_argument('-v', '--verbose',
	                    action='store_true',help="output includes debug logs") 
	parser.add_argument('-a','--address',
						action="store",help="ip address",default="10.100.1.1")
	parser.add_argument('-p','--port', 
						action="store",help="destination port",default="5678")
	parser.add_argument('-l','--no-unlock',help="don't perform unlocking",action="store_true")
	parser.add_argument('-s','--no-keepalive',help="don't start keepalive connection (camera will sleep due to inactivity)",action="store_true")
	args = parser.parse_args()


	con = connections.TcpConnection(args.address,int(args.port))
	con.connect()

	if not args.no_unlock:
		tr = transactions.GetCameraInfoTransact(con)
		ci = tr.transact()
		camera_serial = ci.serial_num
		transactions.UnlockTransact(con,camera_serial).unlock()

	if not args.no_keepalive:
		t = Thread(target=utils.keep_alive, args=[con])
		t.start()
	#transactions.CmdManual(con).transact()

	shell(con,args.verbose)


	#SyncUartTransact(con).transact()
	#transactions.ExecTransact(con,"rfiidle 0").transact()

	#transactions.UDPLiveView(con).transact(enable=True,cratio=5)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)
	main()