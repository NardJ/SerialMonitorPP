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

### Bugs
I am mainly developing this for personal use. If you find bugs, I will fix them if I have time.<br>
Feel free to make a copy and enhance on it in your own repository.

---

### Log messages
With the buttons below the log you can specify if you want to scroll the log if the messages exceed the page height, add timestamps, display/hide your sent messages, put extra separation between received messages which are more than 1 sec apart, turn on/off wrap and clear the log.

![formatlog](/images/formatlog.png)

With the format pulldown list you can display the entire message log in ascii, decimal, hex, but you can also display a single message in all representations by clicking on the message in the log.

![Hex](/images/representations.png)

---

### Sending messages
You can send a message by entering it in the text box at the top of SerialMonitor++ and clicking on the Send button. 

![sendfield](/images/sendfield.png)

If you want to send a previous message, click the up-key in the text box to browse through your history.

You can specify if you want to automatically close your message with a new-line character (NL), a carriage return (CR), both (CR & NL) of with a string end character.

![lineendbutton](/images/lineendbutton.png)

If you want quick access to a send message, long click on one of the buttons to save it. After this a short click on the button resends it.

![sendbutton](/images/sendbutton.png)

---

### Script Engine
For multiline messages, or maybe want to send different messages depending on a received message, you can load/run a script using the script button.

![scriptbutton](/images/scriptbutton.png)

Your script will be run, if errors were encountered you can find them in the second tab. You can edit, save or reload the script. If you want a delay between each  scriptline you can specify one using pulldown button at the bottom.

![scriptbutton](/images/scriptengine.png)

---

### Connection
In the statusbar below the window, you can specify the connection port, the communication speed, connect/disconnect and specify if you want to autoconnect on start and after a connection interruption.

![connect](/images/connect.png)

