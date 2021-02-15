# SerialMonitor++

SerialMonitor++ is meant as a better Serial Monitor than the Arduino IDE provides. It comes with the following extra features:
- display message log in ascii, hex, dec or auto (text when possible and else binary)
- include messages you sent in log besides the received messages 
- click on message to show ascii, hex and dec representations of message
- auto search and connect to serial device on start and auto reconnect if connection interrupted
- buttons to store often send messages
- script engine to automate sending messages depending on received messages

### Main window
![Main Window](/images/format.png)
### Required python modules
To run SerialMonitor++ you have to install Python3 and the following modules:
- serial
- re

### Decimal
![Decimal](/images/dec.png)

### Hex
![Hex](/images/hex.png)

### Click on message
![Hex](/images/allrepresentations.png)

### Other line endings
![Hex](/images/lineending.png)

### Script Engine
![Hex](/images/scriptengine.png)

