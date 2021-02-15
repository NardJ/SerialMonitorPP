# SerialMonitor++

SerialMonitor++ is meant as a better Serial Monitor than the Arduino IDE provides. It comes with the following extra features:
- display message log in ascii, hex, dec or auto (text when possible and else binary)
- include messages you sent in log besides the received messages 
- click on message to show ascii, hex and dec representations of message
- auto search and connect to serial device on start and auto reconnect if connection interrupted
- buttons to store often send messages
- script engine to automate sending messages depending on received messages

### Main window
![Main Window](/images/overview.png)
### How to run
- Install python 3: https://www.python.org/downloads/
- Install module pyserial: ```>pip3 install pyserial```
- Run with command: ```>python3 SerialMonitor++.py```
---

### Hex/Dec/Ascii
You can display the entire message log in ascii, decimal, hex, but you can also display a single message in all representations by clicking on it.
![Hex](/images/representations.png)

### Other line endings
![Hex](/images/lineending.png)

### Script Engine
![Hex](/images/scriptengine.png)

