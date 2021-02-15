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

### Sending messages
You can send a message by entering it in the text box at the top of SerialMonitor++ and clicking on the Send button. You can select how your message if you want to automatically close your message with a new-line character (NL), a carriage return (CR), both (CR & NL) of with a string end character.
![sendfield](/images/sendfield.png)
If you want to send a previous message, click the up-key in the text box to browse through your history.

![sendbutton](/images/sendbutton.png)
If you want quick access to a send message, long click on one of the buttons to save it. After this a short click on the button resends it.

![Hex](/images/lineending.png)

### Script Engine
For multiline messages, or maybe want to send different messages depending on a received message, you can load/run a script using the 
![Hex](/images/scriptengine.png)

