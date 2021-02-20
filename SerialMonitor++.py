import tkinter as tk
from tkinter import font as tkf
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tooltip import CreateToolTip
import scriptWindow
import messagePopup
import bytes2String

import serial
import re 

import time
from datetime import datetime
import os

#GLOBALS
scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)

running=True
win=None

evalPortsMax=24
portList=[]
serialPort=None

nrSaveButtons=10
buttonTimes=nrSaveButtons*[None]
longPressSecs=1.5

histReceived=[] 
histSent=[]
histIdx=0

def listPorts():
    global portList
    sName="auto"
    portList=[]
    portList.append(sName)
    win.ddPorts.children["menu"].delete(0,"end")
    win.ddPorts.children["menu"].add_command(label=sName,command=lambda port=sName: win.varPorts.set(port))

    for sNr in range(evalPortsMax):
        sName=f'/dev/ttyUSB{sNr}'
        try:
            sPort = serial.Serial(sName,9600) 
            sPort.close()
            print (f"Available {sName}")
            portList.append(sName)
            win.ddPorts.children["menu"].add_command(label=sName,command=lambda port=sName: win.varPorts.set(port))
        except: pass
    win.varPorts.set("auto")
    print (f"portList:{portList}")

def findSerial():
    sName=win.varPorts.get()
    sBaudrate=win.varBaudrate.get()
    sPort=None    
    if sName=="auto":        # Try to open each port        
        for sNr in range(evalPortsMax):
            sName=f'/dev/ttyUSB{sNr}'
            #print (f".......Poll {sName}")
            sPort=None                                
            try:
                #sPort = serial.Serial(port=sName,baudrate=sBaudrate,
                #                      parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, 
                #                      bytesize = serial.EIGHTBITS,xonxoff=True,
                #                      timeout=0.5
                #                      ) 
                sPort=serial.Serial()
                sPort.baudrate = sBaudrate
                sPort.port = sName
                sPort.timeout=0.1
                sPort.open()
                if sPort.is_open:
                    print (f"Found Serial @ {sName}")
                    return sPort
            except: pass
    else:                   # Try to open selected port
        try:
            sPort = serial.Serial(sName,sBaudrate) 
            print (f"Connected Serial @ {sName}")
            return sPort
        except: pass

                            # No port found
    print (f"Serial not found")    
    return None

def closeWindow():
    global running
    saveSettings()
    print ("CLOSED")
    win.destroy()
    running=False

def send2Prev(val=None):
    global histIdx
    if len(histSent)==0: return
    if histIdx>0: histIdx-=1
    win.varSent.set(histSent[histIdx])

def send2Next(val=None):
    global histIdx
    if len(histSent)==0: return
    if histIdx<len(histSent): histIdx+=1
    if histIdx==len(histSent):
        win.varSent.set("")    
    else:    
        win.varSent.set(histSent[histIdx])

def send(val=None):
    print ("[SEND]")
    if not isConnected(): return
    global histSent,histIdx
    # check if val has value to send
    if not (val==None): 
        if isinstance(val,str):
            print ("[send] updated entry value")
            win.varSent.set(val)   
    # otherwise we retreive this from entry box
    string=win.varSent.get()
    print (f"win.varSent.get():{win.varSent.get()}")
    print (f"type(val):{type(val)}")

    # store in history
    histSent.append(string)
    histSent=histSent[-100:]
    histIdx=len(histSent)

    # add string terminator
    endMessage=win.varEndMessage.get()
    if (endMessage=="Newline"):  string+= '\n' 
    if (endMessage=="Carriage"): string+= '\r'
    if (endMessage=="CR & NL"):  string+= '\r\n'
    if (endMessage=="Endstring"):string+= '\0'
    # send message over serialPort
    tStart=time.time()
    serialPort.write(string.encode('utf-8'))
    serialPort.flush()
    tDelta=time.time()-tStart    

    # display in log if needed
    histReceived.append((time.time(),string.encode(),tk.RIGHT))
    appendReceived(len(histReceived)-1)  

    # clear sent entry widget
    print(f"Sent:'{string.encode('utf-8')}' in {round(tDelta*1_000_000,0)} usecs")
    win.varSent.set("")

def guiEnable():    
    win.textReceived.configure(bg="white")
    win.textentry.configure(bg="white")
    win.textentry.configure(state='normal')
    win.entryframe.configure(bg="white")

def guiDisable():
    win.textReceived.configure(bg="lightgrey")
    win.textentry.configure(bg="lightgrey")
    win.textentry.configure(state='disable')
    win.entryframe.configure(bg="lightgrey")

def isConnected():
    if serialPort==None          : return False
    if serialPort.is_open==False : return False
    return True

def reconnect(var=None):
    global serialPort
    if not isConnected():       # connect
        print ("Not connected.. trying to connect")
        # try to reconnect
        serialPort=findSerial()
        # if no serial found
        if (serialPort==None): 
            print ("No serial ports found")
            win.varAutoconnect.set(False)
            win.btnReconnect.configure(text="Reconnect")
            win.title("SerialMonitor++  -  not connected")
            guiDisable()
            time.sleep(1)
        else:    
            print (f"Serial port {serialPort} found")
            win.btnReconnect.configure(text="Disconnect")
            win.title(f"SerialMonitor++  -  {serialPort.name}")
            guiEnable()
    else:                       # disconnect
        print ("Connected.. disconnecting")
        win.varAutoconnect.set(False)
        serialPort=None
        win.title("SerialMonitor++  -  not connected")
        win.btnReconnect.configure(text="Reconnect")
        guiDisable()
        listPorts()

def savedInputMDown(buttonIdx):
    if not isConnected(): return
    buttonTimes[buttonIdx]=time.time()
def savedInputMUp(buttonIdx):
    if not isConnected(): return
    delta=time.time()-buttonTimes[buttonIdx]
    if delta<=longPressSecs:
        win.varSent.set(win.btnSavedInput[buttonIdx]["text"])
        buttonTimes[buttonIdx]=None
        send()
def saveInputLongpressCheck():
    if not isConnected(): return
    for buttonIdx in range(nrSaveButtons):
        if not buttonTimes[buttonIdx]==None: 
            delta=time.time()-buttonTimes[buttonIdx]
            if delta>longPressSecs:
                win.btnSavedInput[buttonIdx].configure(text=win.varSent.get())
                win.btnSavedInput[buttonIdx].tooltip.close()
                win.btnSavedInput[buttonIdx].tooltip = CreateToolTip(win.btnSavedInput[buttonIdx], "Click to copy \nto entry box.")
                buttonTimes[buttonIdx]=None
def saveSettings():
    settingsfilepath=os.path.join(scriptdir,"SerialMonitor++.ini")
    with open(settingsfilepath,'w') as writer:
        writer.write(f"{win.varEndMessage.get()}\n")
        writer.write(f"{int(win.varAutoscroll.get())}\n")
        writer.write(f"{int(win.varShowTimestamp.get())}\n")
        writer.write(f"{int(win.varShowSent.get())}\n")
        writer.write(f"{int(win.varSepOuts.get())}\n")
        writer.write(f"{int(win.varWrap.get())}\n")
        writer.write(f"{win.varOutType.get().strip()}\n")
        writer.write(f"{int(win.varAutoconnect.get())}\n")
        writer.write(f"{win.varBaudrate.get().strip()}\n")
        for buttonIdx in range(nrSaveButtons):
            line=win.btnSavedInput[buttonIdx]["text"]
            writer.write(line+'\n')

def loadSettings():
    settingsfilepath=os.path.join(scriptdir,"SerialMonitor++.ini")
    if not os.path.isfile(settingsfilepath): return
    try:
        with open(settingsfilepath,'r') as reader:
            win.varEndMessage.set(reader.readline().strip())
            win.varAutoscroll.set(bool(int(reader.readline().strip())))
            win.varShowTimestamp.set(bool(int(reader.readline().strip())))
            win.varShowSent.set(bool(int(reader.readline().strip())))
            win.varSepOuts.set(bool(int(reader.readline().strip())))
            win.varWrap.set(bool(int(reader.readline().strip())))
            win.varOutType.set(reader.readline().strip())
            win.varAutoconnect.set(bool(int(reader.readline().strip())))
            win.varBaudrate.set(int(reader.readline().strip()))
            for buttonIdx in range(nrSaveButtons):
                win.btnSavedInput[buttonIdx].configure(text=reader.readline().strip())
    except Exception as e:
        print (f"Error reading settings:{e}")

def setShowSent():
    if win.varShowSent.get(): win.varWrap.set(True)
    refreshInput()
    wrapReceived()

def btnReconnect_enter(arg=None):
    win.btnReconnect.configure(bg=win.btnReconnect.bgEnter)
def btnReconnect_leave(arg=None):
    win.btnReconnect.configure(bg=win.btnReconnect.bgLeave)
def sendScript(arg=None):
    if not isConnected(): return
    rep = filedialog.askopenfilenames(                  # open dialog so user can select file
        parent=win,
    	initialdir=scriptdir,
        defaultextension="*.scr",
    	filetypes=[
    		("Script files", "*.scr"),
    		])
    print(rep)
    scriptpath=rep[0]                                   # use first file in list
    if (scriptpath==None): return                       # exit if user selected no file
    guiEnable()
    scriptWindow.show(win,scriptpath,send,received)
    guiDisable()
    
def initWindow():
    global win
    global portList

    # CREATE WINDOW
    win = tk.Tk()  

    # Set Window properties
    win.title(f"SerialMonitor++  -  not connected")
    win.geometry("800x480")
    backcolor=win["bg"]#"#DDDDDD"
    win.configure(background=backcolor)
    style=tk.SOLID
    iconpath=os.path.join(scriptdir,"SerialMonitor.png")
    win.tk.call('wm', 'iconphoto', win._w, tk.PhotoImage(file=iconpath))
    # set fonts
    #hfont = tkf.Font(weight = 'bold', underline=True, size = 9)
    #kfont = tkf.Font(family='Terminal', weight = 'bold', size = 8)
    #lfont = tkf.Font(family='Consolas', weight = 'bold', size = 9)

    inputframe=tk.Frame(win,padx=4,pady=0,background=backcolor)
    inputframe.pack(fill='x',padx=(4,0),pady=(4,0))
    # INPUT HEADER
    #  add frame so create a margin to left and right of entered text
    win.entryframe=tk.Frame(inputframe,background=backcolor,border=1,highlightthickness=0,relief=tk.SOLID)
    win.entryframe.pack(side=tk.LEFT,padx=(0,3),ipady=3,expand=True,fill=tk.X)
    win.varSent=tk.StringVar() #use win.varSent.get()
    win.textentry=tk.Entry(win.entryframe,background=backcolor,textvariable=win.varSent,bd=0,border=0,highlightthickness=0)
    win.textentry.pack(side=tk.LEFT,padx=(0,3),ipady=0,expand=True,fill=tk.X)
    win.textentry.bind('<Return>', send)
    win.textentry.bind('<KP_Enter>', send)
    win.textentry.bind('<Up>', send2Prev)
    win.textentry.bind('<Down>', send2Next)
    win.textentry.configure(bg="lightgrey")
    win.textentry.configure(state='disable')

    label = tk.Label(inputframe, text="+", relief=tk.FLAT )
    label.pack(side=tk.LEFT,padx=(3,3))

    win.varEndMessage=tk.StringVar()
    endList=("Nothing","Newline","Carriage","CR & NL","Endstring")
    win.varEndMessage.set('CR & NL')
    ddEndMessage=tk.OptionMenu(inputframe,win.varEndMessage,*endList)
    ddEndMessage.pack(side=tk.LEFT,padx=(3,0))
    ddEndMessage.configure(width=6)
    ddEndMessage.configure(relief=style)
    ddEndMessage.configure(bd='1p')
    ddEndMessage.configure(highlightthickness=0)
    ddEndMessage.configure(bg='white')

    sendbutton=tk.Button(inputframe,text="Send", command=send)
    sendbutton.pack(side=tk.RIGHT,padx=(2,2))
    sendbutton.configure(relief=style)

    # SAVED SCRIPTS and INPUTS
    inputsframe=tk.Frame(win,padx=4,pady=0)#, relief=tk.SUNKEN,borderwidth=2)
    inputsframe.pack(side=tk.TOP,fill='x',pady=(3,0))
    imgpath=os.path.join(scriptdir,"folder24x24.png")
    img=tk.PhotoImage(file=imgpath)
    
    win.openscript =tk.Button(inputsframe, command=sendScript,height=27,width=26)
    win.openscript.img=img
    win.openscript.configure(image=img)
    win.openscript.pack(side=tk.LEFT,padx=(3,0))
    win.openscript.configure(relief=style)

    win.btnSavedInput=nrSaveButtons*[None]
    for i in range (nrSaveButtons):
        win.btnSavedInput[i]=tk.Button(inputsframe,text=f"...",relief=tk.FLAT,width=10,anchor='w')
        win.btnSavedInput[i].bind('<Button-1>',lambda event,arg=i: savedInputMDown(arg))
        win.btnSavedInput[i].bind('<ButtonRelease-1>',lambda event,arg=i: savedInputMUp(arg))
        win.btnSavedInput[i].pack(side=tk.LEFT,padx=(2,2))
        win.btnSavedInput[i].configure(relief=style)
        win.btnSavedInput[i].tooltip = CreateToolTip(win.btnSavedInput[i], "Hold to save current input \ntext to this button.")

    # draw sep
    separator = ttk.Separator(orient='horizontal').pack(side=tk.TOP,fill='x',pady=8)

    # FOOTER 2
    footerbgcolor='#333333'
    footersgcolor='#444444'
    footerfgcolor='#BBBBBB'
    connectframe=tk.Frame(win,padx=0,pady=0,background=footerbgcolor,bd=0)
    connectframe.pack(side=tk.BOTTOM,fill='x',pady=(6,0))

    win.varAutoconnect=tk.BooleanVar(value=True)
    cbAutoconnect=tk.Checkbutton(connectframe,text="Autoconnect to:",variable=win.varAutoconnect)
    cbAutoconnect.configure(background=footerbgcolor,activebackground=footersgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
    cbAutoconnect.pack(side=tk.LEFT)
    cbAutoconnect.configure(relief=tk.FLAT)

    win.varPorts=tk.StringVar()
    #portList=["auto","/dev/usb01","/dev/usb02","/dev/usb03"]
    portList.append("auto")
    portList.append("/tty/usb01")
    win.varPorts.set("auto")
    win.ddPorts=tk.OptionMenu(connectframe, win.varPorts, *portList)
    win.ddPorts.configure(background=footerbgcolor,activebackground=footersgcolor,foreground=footerfgcolor,activeforeground=footerfgcolor,highlightbackground='red')
    win.ddPorts.configure(bd=3)
    win.ddPorts["menu"].configure(background=footerbgcolor,activebackground=footersgcolor,foreground=footerfgcolor,activeforeground=footerfgcolor)
    win.ddPorts["menu"].configure(relief=style)
    win.ddPorts.pack(side=tk.LEFT,padx=(3,0))
    win.ddPorts.configure(bd='0p')
    win.ddPorts.configure(highlightthickness=0)
    listPorts()

    label = tk.Label(connectframe, text="@", relief=tk.FLAT,background=footerbgcolor,fg=footerfgcolor)
    label.pack(side=tk.LEFT,padx=(3,3))

    win.varBaudrate=tk.StringVar()
    baudList=(2400,4800,9600,19200,38400,57600,75880,115200,230400,250000,500000,1000000,2000000)
    win.varBaudrate.set(115200)
    ddBaudrate=tk.OptionMenu(connectframe,win.varBaudrate, *baudList)
    ddBaudrate.configure(background=footerbgcolor,activebackground=footersgcolor,foreground=footerfgcolor,activeforeground=footerfgcolor,highlightbackground='red')
    ddBaudrate["menu"].configure(background=footerbgcolor,activebackground=footersgcolor,foreground=footerfgcolor,activeforeground=footerfgcolor)
    ddBaudrate["menu"].configure(relief=style)
    ddBaudrate.pack(side=tk.LEFT,padx=(3,0))
    ddBaudrate.configure(relief=style)
    ddBaudrate.configure(bd='0p')
    ddBaudrate.configure(highlightthickness=0)

    label = tk.Label(connectframe, text="baud", relief=tk.FLAT,background=footerbgcolor,fg=footerfgcolor)
    label.pack(side=tk.LEFT,padx=(3,3))

    #We want a flat button without any margin
    #   this add a 1 px margin at bottom between button and frame 
    #   win.btnReconnect=tk.Button(connectframe,text="Reconnect", command=reconnect)
    win.btnReconnect = tk.Label(connectframe, text="Reconnect", relief=tk.FLAT,background=footerbgcolor,fg=footerfgcolor,bd=0,padx=8,pady=6)
    win.btnReconnect.configure(background=footerbgcolor,activebackground=footersgcolor,foreground=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor)
    win.btnReconnect.pack(side=tk.RIGHT,padx=(3,6),pady=(1,0))# some space at right for resizeGrip
    win.btnReconnect.configure(relief=style)
    #Needed because label does not have these events 
    win.btnReconnect.bgLeave=footerbgcolor
    win.btnReconnect.bgEnter=footersgcolor
    win.btnReconnect.bind('<Enter>',btnReconnect_enter)
    win.btnReconnect.bind('<Leave>',btnReconnect_leave)
    win.btnReconnect.bind('<ButtonRelease-1>',reconnect)

    #   resize grip
    resizeGrip=ttk.Sizegrip(connectframe,style='win.TSizegrip')
    #resizeGrip.pack(side=tk.RIGHT,anchor=tk.SE)
    resizeGrip.place(rely=1.0, relx=1.0, x=0, y=0, anchor=tk.SE)
    resizeGrip.style = ttk.Style()
    resizeGrip.style.configure('win.TSizegrip', background=footerbgcolor)

    # draw sep
    #separator = ttk.Separator(orient='horizontal').pack(side=tk.BOTTOM,fill='x',pady=(8,0))

    # LEFT 1
    settingsframe=tk.Frame(win,padx=6,pady=0,background=backcolor)
    settingsframe.pack(side=tk.BOTTOM,fill='x',pady=(4,0))
    
    win.varAutoscroll=tk.BooleanVar(value=True)
    cbAutoscroll=tk.Checkbutton(settingsframe,text="Autoscroll",variable=win.varAutoscroll)
    cbAutoscroll.pack(side=tk.LEFT)
    cbAutoscroll.configure(relief=tk.FLAT)
    
    win.varShowTimestamp=tk.BooleanVar()
    cbTimestamp=tk.Checkbutton(settingsframe,text="Timestamp",variable=win.varShowTimestamp, command=refreshInput)
    cbTimestamp.pack(side=tk.LEFT)
    cbTimestamp.configure(relief=tk.FLAT)

    win.varShowSent=tk.BooleanVar(value=False)
    cbShowSent=tk.Checkbutton(settingsframe,text="Sent",variable=win.varShowSent,command=setShowSent,)
    cbShowSent.pack(side=tk.LEFT,padx=(0,4))
    cbShowSent.configure(relief=tk.FLAT)

    win.varSepOuts=tk.BooleanVar(value=True)
    cbSepOuts=tk.Checkbutton(settingsframe,text="Separate",variable=win.varSepOuts, command=refreshInput)
    cbSepOuts.pack(side=tk.LEFT)
    cbSepOuts.configure(relief=tk.FLAT)

    win.varWrap=tk.BooleanVar(value=False)
    cbWrap=tk.Checkbutton(settingsframe,text="Wrap",variable=win.varWrap, command=wrapReceived)
    cbWrap.pack(side=tk.LEFT)
    cbWrap.configure(relief=tk.FLAT)

    label = tk.Label(settingsframe, text="Format:", relief=tk.FLAT )
    label.pack(side=tk.LEFT,padx=(12,3))
    win.varOutType=tk.StringVar()
    outList=("ASCII","HEX","DEC","AUTO")
    win.varOutType.set("ASCII")
    ddOutType=tk.OptionMenu(settingsframe,win.varOutType, *outList, command=refreshInput)
    ddOutType.pack(side=tk.LEFT,padx=(3,0))
    ddOutType.configure(relief=style)
    ddOutType.configure(bd='1p')
    ddOutType.configure(highlightthickness=0)

    btnClearinput=tk.Button(settingsframe,text="Clear input", command=clearReceived)
    btnClearinput.pack(side=tk.RIGHT,padx=(3,0))
    btnClearinput.configure(relief=style)

    # RECEIVED AREA
    win.varReceived=tk.StringVar() #use textInput.get()
    win.scrollReceived = tk.Scrollbar(win)
    win.textReceived=tk.Text(win,bg="white")#,variable=win.varReceived )
    win.scrollReceived.pack(side=tk.RIGHT, fill=tk.Y,padx=(0,8),pady=(2,2))
    win.textReceived.pack(expand=True,padx=(6,0),pady=(0,0),fill=tk.BOTH)
    win.scrollReceived.config(command=win.textReceived.yview)
    win.textReceived.config(yscrollcommand=win.scrollReceived.set)
    win.textReceived.configure(relief=style)
    win.scrollReceived.configure(relief=tk.FLAT)
    win.scrollReceived.configure(borderwidth=0)
    win.scrollReceived.configure(elementborderwidth=1)
    win.scrollReceived.configure(width=14)
    win.scrollReceived.configure(trough=backcolor)
    win.textReceived.config(state=tk.DISABLED)
    win.textReceived.configure(bg="lightgrey")
    win.textReceived.configure(wrap=tk.NONE)
    win.textReceived.oldHighlightIdx=-1
    win.textReceived.stampColor='#AAAAAA'
    win.textReceived.textColorL1='#00AA00'
    win.textReceived.textColorL2='#55AA55'
    win.textReceived.textColorR1='#0000AA'
    win.textReceived.textColorR2='#3333AA'
    win.textReceived.textColor=win.textReceived.textColorL1

    win.textReceived.textFont = tkf.Font(family='Terminal', weight = 'normal', size = 9) #TkFixedFont
    win.textReceived.stampFont= tkf.Font(family='Terminal', weight = 'normal', size =6) #TkFixedFont

    # bind keys
    win.protocol("WM_DELETE_WINDOW", closeWindow) # custom function which sets winDestroyed so we can check state of win
    #win.bind('<escape>', closeWindow) # make Esc exit the program

    # load settings
    loadSettings()

def popup_AllReceiveReps(receiveIdx):
    _,data_bytes,_=histReceived[receiveIdx]

    # get ascii, remove last EOL and respace each char
    data_str_ascii=bytes2String.ascii(data_bytes).strip()
    new_str_ascii=""
    for c in data_str_ascii: new_str_ascii+="   "+c
    new_str_ascii=new_str_ascii.replace(" \   b","\\b")    
    new_str_ascii=new_str_ascii.replace(" \   t","\\t")    
    new_str_ascii=new_str_ascii.replace(" \   n","\\n")    
    new_str_ascii=new_str_ascii.replace(" \   f","\\f")    
    new_str_ascii=new_str_ascii.replace(" \   r","\\r")    
    data_str_ascii=new_str_ascii[1:]

    # get hex remove last EOL and respace each char
    data_str_hex=bytes2String.hex(data_bytes).strip()
    data_str_hex=" "+"  ".join(data_str_hex.split(" "))

    # get dec remove last EOL but keep leading space if first numbers <=99 
    data_str_dec=bytes2String.dec(data_bytes)
    data_str_dec=" "+data_str_dec.strip() if data_str_dec[0]==" " else data_str_dec.strip()

    # construct dialog
    winPopup = tk.Toplevel(win)
    winPopup.wm_title("Alternate representations")
    winPopup.resizable(False,False)

    f = tk.Frame(winPopup)
    f.pack(fill=tk.X,side=tk.TOP)
    l = tk.Label(f, text="ASCII:",width=6,anchor=tk.W,justify=tk.LEFT)
    l.pack(padx=(12,24),pady=(12,0),side=tk.LEFT)
    l = tk.Label(f, text=data_str_ascii,relief=tk.SUNKEN,wraplength=800,anchor=tk.W,justify=tk.LEFT,font='TkFixedFont')#,background='white')
    l.pack(fill=tk.X,expand=True,padx=(12,12),pady=(12,0),side=tk.RIGHT)

    f = tk.Frame(winPopup)
    f.pack(fill=tk.X,side=tk.TOP)
    l = tk.Label(f, text="HEX:",width=6,anchor=tk.W,justify=tk.LEFT)
    l.pack(padx=(12,24),pady=(0,0),side=tk.LEFT)
    l = tk.Label(f, text=data_str_hex,relief=tk.SUNKEN,wraplength=800,anchor=tk.W,justify=tk.LEFT,font='TkFixedFont')#,background='white')
    l.pack(fill=tk.X,expand=True,padx=(12,12),pady=(0,0),side=tk.RIGHT)

    f = tk.Frame(winPopup)
    f.pack(fill=tk.X,side=tk.TOP)
    l = tk.Label(f, text="DEC:",width=6,anchor=tk.W,justify=tk.LEFT)
    l.pack(padx=(12,24),pady=(0,6),side=tk.LEFT)
    l = tk.Label(f, text=data_str_dec,relief=tk.SUNKEN,wraplength=800,anchor=tk.W,justify=tk.LEFT,font='TkFixedFont')#,background='white')
    l.pack(fill=tk.X,expand=True,padx=(12,12),pady=(0,6),side=tk.RIGHT)

    # draw sep
    separator = ttk.Separator(winPopup,orient='horizontal').pack(side=tk.TOP,fill='x',pady=8)

    b = ttk.Button(winPopup, text="Close", command=winPopup.destroy)
    b.pack(padx=(12,12),pady=(6,12),side=tk.BOTTOM)

    winPopup.update()
    winPopup.transient(win) 
    winPopup.grab_set() # redirect all user input to this popup


def tokenIsString(token):
    return ( (token[0]=='"') and (token[-1]=='"') )


def received():
    if len(histReceived)>0:
        msg=histReceived[len(histReceived)-1][1]
        #print (f"msg:{msg}'")
        return msg # histReceived contains tuples (timestamp, message,'right')
    else:
        return "None"    


def clearText():
    win.textReceived.config(state=tk.NORMAL)
    win.textReceived.delete('1.0',tk.END)
    win.textReceived.config(state=tk.DISABLED)
    win.textReceived.yview_moveto('1')
    for tagname in win.textReceived.tag_names():
        win.textReceived.tag_delete(tagname) 

def clearReceived():
    histReceived.clear()
    clearText()        
def wrapReceived(val=None):
    if win.varWrap.get():
        win.textReceived.configure(wrap=tk.CHAR)#tk.WORD | tk.CHAR
    else:
        win.textReceived.configure(wrap=tk.NONE)#tk.WORD | tk.CHAR

# see https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/text-methods.html for all tag options
def clickReceivedLine(event,tagIdx=None):
    # only do if pressed left mouse button
    if not event.num==1: return
    
    # set cursor
    print (f"clickReceivedLine: {event}{tagIdx}")
    win.textReceived.config(state=tk.NORMAL)
    win.textReceived.tag_config(f"{win.textReceived.oldHighlightIdx}",background='white')
    win.textReceived.tag_config(f"{tagIdx}",background='yellow')
    win.textReceived.oldHighlightIdx=tagIdx
    win.textReceived.config(state=tk.DISABLED)
    #tooltip
    popup_AllReceiveReps(tagIdx)

def appendReceived(receiveIdx):
    marginLR=0.5*8

    # retreive time, bytes and alignment of log idx
    receiveTime,data_bytes,align=histReceived[receiveIdx]
    # get previous retrieve which was not sent
    prevReceive=receiveTime
    if receiveIdx>0: 
        prevReceive,_,palign=histReceived[receiveIdx-1]
        if palign==tk.RIGHT and receiveIdx>1: prevReceive,_,_=histReceived[receiveIdx-2]

    # only display right aligned (sent messages) if varLogSent = checked
    if align==tk.RIGHT and not win.varShowSent.get(): return

    # retreive text
    win.textReceived.config(state=tk.NORMAL)
    if (win.varOutType.get()=="ASCII"):data_str=bytes2String.ascii(data_bytes)
    if (win.varOutType.get()=="HEX"): data_str=bytes2String.hex(data_bytes)
    if (win.varOutType.get()=="DEC"): data_str=bytes2String.dec(data_bytes)
    if (win.varOutType.get()=="AUTO"):data_str=bytes2String.raw(data_bytes)

    #check if string is closed with \n
    if data_str[-1:]!='\n': data_str+='\n'
    
    #determine if we need to print seperator (if enough time elapsed)
    elapsed=receiveTime-prevReceive
    if win.varSepOuts.get() and elapsed>0.3: 
        #data_str='---\n'+data_str
        win.textReceived.insert(tk.END,"\n")
    #add timestamp if needed
    if win.varShowTimestamp.get(): 
        curr_time = datetime.fromtimestamp(receiveTime)
        formatted_time = curr_time.strftime('%H:%M:%S.%f')[:13]
        stamp_str=f"\n{formatted_time}\n"        
        #indent new lines in within lines
        tagname=f"{stamp_str}"
        taglist=(tagname,)
        win.textReceived.insert(tk.END, stamp_str,taglist) 
        win.textReceived.tag_configure(tagname,foreground=win.textReceived.stampColor)         
        win.textReceived.tag_configure(tagname,justify=align)    
        win.textReceived.tag_configure(tagname,font=win.textReceived.stampFont)
        if align==tk.LEFT:
            win.textReceived.tag_configure(tagname,lmargin1=marginLR)
            win.textReceived.tag_configure(tagname,lmargin2=marginLR)
        else:
            win.textReceived.tag_configure(tagname,rmargin=marginLR)

        # replace line breaks in middle of string with enough leading spaces so new line indents beyond time-stamp 
        #data_str=re.sub("\n(?=.)","\n                ",data_str) 

    #output received to text widget    
    #  create tagname
    tagname=f"{receiveIdx}"
    taglist=(tagname,)
    #  insert text to widget
    win.textReceived.insert(tk.END, data_str,taglist) 
    #  bind events to new text
    win.textReceived.tag_bind(tagName=tagname,sequence="<Button>", 
                          func=lambda event, arg=receiveIdx: clickReceivedLine(event, arg))
    #  set alternating color for text (some line can be a combination of text received at different times)
    if align==tk.LEFT:
        win.textReceived.textColor=win.textReceived.textColorL2 if win.textReceived.textColor==win.textReceived.textColorL1 else win.textReceived.textColorL1
        win.textReceived.tag_configure(tagname,rmargin=8*12)
        win.textReceived.tag_configure(tagname,lmargin1=marginLR)
        win.textReceived.tag_configure(tagname,lmargin2=marginLR)
    else:
        win.textReceived.textColor=win.textReceived.textColorR2 if win.textReceived.textColor==win.textReceived.textColorR1 else win.textReceived.textColorR1
        win.textReceived.tag_configure(tagname,rmargin=marginLR)
        win.textReceived.tag_configure(tagname,lmargin1=8*12)
        win.textReceived.tag_configure(tagname,lmargin2=8*12)
    win.textReceived.tag_configure(tagname,foreground=win.textReceived.textColor)         
    win.textReceived.tag_configure(tagname,justify=align)    
    win.textReceived.tag_configure(tagname,font=win.textReceived.textFont)
    #  set scroll bar
    if win.varAutoscroll.get():
        win.textReceived.yview_moveto('1')

    #set tot text widget to readonly
    win.textReceived.config(state=tk.DISABLED)

def refreshInput(val=None):
    global histReceived
    if len(histReceived)==0: return
    #set tot text widget to writable
    clearText()
    win.textReceived.config(state=tk.NORMAL)

    #prevReceive=histReceived[0][0]
    #for histTime,data_bytes in histReceived:
    #    appendReceived(prevReceive,histTime,data_bytes)
    #    prevReceive=histTime
    for receiveIdx in range(len(histReceived)):
        appendReceived(receiveIdx)
    win.textReceived.config(state=tk.DISABLED)

def readSerial():
    global serialPort, histReceived

    while running:
        win.update ()  # so window user actions are processed
        saveInputLongpressCheck()# so long press changes save button and user knows to release button
        
        if not isConnected():
            if win.varAutoconnect.get():
                reconnect()
                pass
        else:
            try:
                if (serialPort.in_waiting>0): #if incoming bytes are waiting to be read from the serial input buffer
                    data_bytes=serialPort.read(serialPort.in_waiting)
                    #print (f"databytes:{data_bytes}")

                    #store in history
                    histReceived.append((time.time(),data_bytes,tk.LEFT))
                    appendReceived(len(histReceived)-1)  
                else:
                    #print (f"{time.time()} no data")    
                    pass

            except OSError as e:
                import traceback
                print(f"{e.__class__.__name__}:{serialPort}\n{traceback.format_exc()}")
                # close connection if connected
                if isConnected(): reconnect()
                time.sleep(1)
                # try reconnect if not connected
                if not isConnected(): reconnect()

if __name__ == "__main__":
    initWindow()
    #popup_ScriptInit(os.path.join(scriptdir,"demo.scr"))    # debug, remove !!
    win.update()
    time.sleep(1)
    readSerial()
    if serialPort: serialPort.close()
    quit()


#TODO: Use ScriptEngine to run scripts
#TODO: User SerialMonitor to develop WifiVideoCard