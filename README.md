# lytroctrl

Utilities and supporting library for controlling original Lytro lightfield cameras

See the accompanying writeup at https://github.com/ea/lytro_unlock

Code is split into payloads, commands, transactions and connections. Commands are either requests or responses and relevant flags are set mostly automatically. For more complicated commands, they override the default behaviour from `Message` class. Some commands have payloads that can be parsed. Transactions wrap a command or multiple commands and handle sending requests and receiving responses via connections. Only currently implemented connection is over WiFi. 



I've implemented a number of commands and set a scafolding for all of them. I've made a couple of utilities that show how you can interact with the camera over WiFi. 
	
#### Shell
	
```
	usage: shell.py [-h] [-v] [-a ADDRESS] [-p PORT] [-l] [-s]

Lytro control shell

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         output includes debug logs
  -a ADDRESS, --address ADDRESS
                        ip address
  -p PORT, --port PORT  destination port
  -l, --no-unlock       don't perform unlocking
  -s, --no-keepalive    don't start keepalive connection (camera will sleep due to inactivity)
```

A simple shell will connect to the camera over WiFi, unlock it, present you with stdout and expect commands to be sent. Whenever a command is sent, output is synced back. Note that by default, error/logging is also emited which can be annoying so it's disabled by default, use `-v` to enable that. 
	
	
#### Demo

There's a short script that demonstrates different functionalities by wiggling the lens, controling zoom and taking a photo:
	
```python
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
```
	
#### LiveView
 
And finaly, an example that shows how to enable live view streaming. Streaming is performed over UDP multicast, and consists simply of transmited jpegs. You can either capture those directly, or instruct ffmpeg to save them. 
	
```python
transactions.UDPLiveView(con).transact(enable=True,cratio=2,fps=1)
utils.keep_alive(con)
```
	
Keep alive function above will periodically issue a query command just to stave off the watchdog which turns of wifi to conserve battery. 
