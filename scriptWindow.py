import tkinter as tk
from tkinter import font as tkf
from tkinter import ttk
import PyInterpreter as pyi
import os
import time
import messagePopup
import scriptHelp
import bytes2String

win=None
send=None
receive=None

def close():
    #guiEnable()
    win.popupWait.destroy()

def received():
    rec = receive()
    print (f"Rec: {rec} of type {type(rec)}")
    if rec==None: rec==['']
    return rec

def show(rootWin,scriptpath,rmtSend,rmtReceive):
    global win,send,receive
    win=rootWin
    send=rmtSend
    receive=rmtReceive
    scriptHelp.init(win)

    scriptname=os.path.basename(scriptpath).split(".")[0]

    # construct dialog
    popupWait = tk.Toplevel(win)
    popupWait.transient(win)    
    popupWait.scriptname=scriptname
    popupWait.wm_title(f"Script - {scriptname}")
    #popupWait.resizable(False,False)
    popupWait.scriptpath=scriptpath
    win.popupWait=popupWait    
    backcolor=win["bg"]#"#DDDDDD"
    #popupWait.protocol("WM_DELETE_WINDOW", pass_WaitForScript) # custom function which sets winDestroyed so we can check state of win

    # header/message
    headerframe=tk.Frame(popupWait,background=backcolor)
    headerframe.pack(side=tk.TOP,fill='x',padx=(0,0),pady=(8,4))
    lb = tk.Label(headerframe,  anchor='w',text='Status:')
    lb.pack(side=tk.LEFT,padx=8)
    popupWait.varInfo=tk.StringVar()
    popupWait.varInfo.set(f"Loaded '{scriptname}'")
    lbInfo = tk.Label(headerframe, anchor=tk.W,textvariable=popupWait.varInfo)
    lbInfo.pack(side=tk.LEFT,padx=8,fill=tk.X,expand=True)

    #   resize grip
    resizeGrip=ttk.Sizegrip(popupWait,style='TSizegrip')
    resizeGrip.place(rely=1.0, relx=1.0, x=0, y=0, anchor=tk.SE)

    # draw sep
    separator = ttk.Separator(popupWait,orient='horizontal').pack(side=tk.TOP,fill='x',pady=8)

    # footer
    footerframe=tk.Frame(popupWait,background=backcolor)
    footerframe.pack(side=tk.BOTTOM,fill='x',padx=(8,8),pady=(4,4))

    lb = tk.Label(footerframe, text='Delay')
    lb.pack(side=tk.LEFT)

    popupWait.varDelay=tk.StringVar()
    popupWait.delayList=("No delay","0.01 sec","0.1 sec","0.5 sec","1 sec","2 sec","5 sec")
    popupWait.delayTimes=(0,0.01,0.1,0.5,1.0,2.0,5.0)
    popupWait.varDelay.set('0.5 sec')
    ddDelay=tk.OptionMenu(footerframe,popupWait.varDelay,*popupWait.delayList)
    ddDelay.pack(side=tk.LEFT,padx=(3,0))
    ddDelay.configure(width=6)
    ddDelay.configure(relief=tk.FLAT)
    ddDelay.configure(bg='white')
    footerbgcolor,footersgcolor,footerfgcolor=backcolor,backcolor,'#000'
    ddDelay.configure(background=footerbgcolor,activebackground=footersgcolor,foreground=footerfgcolor,activeforeground=footerfgcolor,highlightbackground='red')
    ddDelay.configure(bd=3)
    ddDelay["menu"].configure(background=footerbgcolor,activebackground=footersgcolor,foreground=footerfgcolor,activeforeground=footerfgcolor)
    ddDelay["menu"].configure(relief=tk.FLAT)
    ddDelay.pack(side=tk.LEFT,padx=(3,0))
    ddDelay.configure(bd='0p')
    ddDelay.configure(highlightthickness=0)

    popupWait.varSkipVars=tk.BooleanVar(value=True)
    cbSkipVars=tk.Checkbutton(footerframe,text="Skip Vars:",variable=popupWait.varSkipVars)
    cbSkipVars.configure(background=footerbgcolor,activebackground=footersgcolor,fg=footerfgcolor,activeforeground=footerfgcolor,highlightbackground=footerbgcolor,selectcolor=footerbgcolor)
    cbSkipVars.pack(side=tk.LEFT)
    cbSkipVars.configure(relief=tk.FLAT)

    popupWait.cmdRun = tk.Button(footerframe, text="Run",command= process)
    popupWait.cmdRun.pack(side=tk.RIGHT)
    popupWait.cmdRun.configure(relief=tk.FLAT)

    popupWait.cmdSave = tk.Button(footerframe, text="Save",command= save)
    popupWait.cmdSave.pack(side=tk.RIGHT)
    popupWait.cmdSave.configure(relief=tk.FLAT)

    popupWait.cmdReload = tk.Button(footerframe, text="Reload",command= load)
    popupWait.cmdReload.pack(side=tk.RIGHT)
    popupWait.cmdReload.configure(relief=tk.FLAT)

    popupWait.cmdHelp = tk.Button(footerframe, text="Help",command= scriptHelp.show)
    popupWait.cmdHelp.pack(side=tk.RIGHT)
    popupWait.cmdHelp.configure(relief=tk.FLAT)

    # draw sep
    separator = ttk.Separator(popupWait,orient='horizontal').pack(side=tk.BOTTOM,fill='x',pady=(8,0))

    # tabs
    popupWait.tabs=ttk.Notebook(popupWait)
    popupWait.scriptTab=ttk.Frame(popupWait.tabs)
    popupWait.tabs.add(popupWait.scriptTab,text=" Script ")#,command=showScript)
    popupWait.errorsTab=ttk.Frame(popupWait.tabs)
    popupWait.tabs.add(popupWait.errorsTab,text=" Errors ")#,command=showErrors)
    popupWait.tabs.pack(side=tk.TOP, fill=tk.BOTH,expand=True,padx=(8,8),pady=(2,0))

    # script area
    #popupWait.varScript=tk.StringVar() #use textInput.get()
    popupWait.scrollText = tk.Scrollbar(popupWait.scriptTab)#popupWait)
    popupWait.scriptText=tk.Text(popupWait.scriptTab,bg='white')#popupWait,bg="white")
    popupWait.scrollText.pack(side=tk.RIGHT, fill=tk.Y,padx=(0,0),pady=(2,2))
    popupWait.scriptText.pack(expand=True,padx=(2,0),pady=(2,0),fill=tk.BOTH)
    popupWait.scrollText.config(command=popupWait.scriptText.yview)
    popupWait.scriptText.config(yscrollcommand=popupWait.scrollText.set)
    popupWait.scriptText.configure(wrap=tk.NONE) # needed for autoscroll (using .see) to function reliably
    popupWait.scriptText.configure(relief=tk.SOLID)
    popupWait.scrollText.configure(relief=tk.FLAT)
    popupWait.scrollText.configure(borderwidth=0)
    popupWait.scrollText.configure(elementborderwidth=1)
    popupWait.scrollText.configure(width=14)
    #popupWait.scrollText.configure(trough=backcolor)
    popupWait.scriptText.configure(wrap=tk.NONE)
    popupWait.scriptText.configure(font= tkf.Font(family='Terminal', weight = 'normal', size = 9)) #TkFixedFont
    popupWait.scriptText.oldlinenr=0

    # error area
    #popupWait.varScript=tk.StringVar() #use textInput.get()
    popupWait.scrollErrors = tk.Scrollbar(popupWait.errorsTab)#popupWait)
    popupWait.scriptErrors=tk.Text(popupWait.errorsTab,bg='white')#popupWait,bg="white")
    popupWait.scrollErrors.pack(side=tk.RIGHT, fill=tk.Y,padx=(0,0),pady=(2,2))
    popupWait.scriptErrors.pack(expand=True,padx=(2,0),pady=(2,0),fill=tk.BOTH)
    popupWait.scrollErrors.config(command=popupWait.scriptErrors.yview)
    popupWait.scriptErrors.config(yscrollcommand=popupWait.scrollErrors.set)
    popupWait.scriptErrors.configure(wrap=tk.NONE) # needed for autoscroll (using .see) to function reliably
    popupWait.scriptErrors.configure(relief=tk.SOLID)
    popupWait.scrollErrors.configure(relief=tk.FLAT)
    popupWait.scrollErrors.configure(borderwidth=0)
    popupWait.scrollErrors.configure(elementborderwidth=1)
    popupWait.scrollErrors.configure(width=14)
    #popupWait.scrollText.configure(trough=backcolor)
    popupWait.scriptErrors.configure(wrap=tk.NONE)
    popupWait.scriptErrors.configure(font= tkf.Font(family='Terminal', weight = 'normal', size = 9)) #TkFixedFont

    # show script
    load()

    # bindings and show
    popupWait.protocol("WM_DELETE_WINDOW", close) # custom function which sets winDestroyed so we can check state of win
    #guiDisable()
    popupWait.update()
    popupWait.grab_set() # to redirect all user input to this popup

def save(event=None):
    scriptpath=win.popupWait.scriptpath
    scriptlines=win.popupWait.scriptText.get(0.0,tk.END)
    with open(win.popupWait.scriptpath, "w") as writer: # open file
        writer.write(scriptlines)

def load(event=None):
    win.popupWait.scriptText.delete(0.0,tk.END)
    with open(win.popupWait.scriptpath, "r") as reader: # open file
        scriptlines=reader.readlines()                  # read all lines
        for nr,lineStr in enumerate(scriptlines):
            tagname=f"{nr}"
            taglist=(tagname,)
            win.popupWait.scriptText.insert(tk.END, lineStr,taglist) 
            #print(f"scripText append:{nr} {lineStr}")

def showScriptLine(linenr):
    popupWait=win.popupWait
    popupWait.scriptText.tag_config(f"{popupWait.scriptText.oldlinenr}",background='white')
    popupWait.scriptText.tag_config(f"{linenr}",background='yellow')
    popupWait.scriptText.see(float(linenr+2))
    popupWait.update()
    popupWait.scriptText.oldlinenr=linenr

isProcessingScript=False

def process(event=None):
    global isProcessingScript
    popupWait=win.popupWait

    # set flag
    isProcessingScript = not isProcessingScript

    # check if user interupted script
    if not isProcessingScript: 
        pyi.stopScript()
        return

    #disable yellow cursor from previous runs
    popupWait.scriptText.tag_config(f"{popupWait.scriptText.oldlinenr}",background='white')
    popupWait.scriptText.oldlinenr=0

    #read script (can be edited by user)    
    scriptpath=popupWait.scriptpath
    scriptlines=popupWait.scriptText.get(0.0,tk.END).split('\n')
    pyi.setScript(scriptlines)

    #get delay time between commands
    delayIndex = popupWait.delayList.index(popupWait.varDelay.get())
    delayTime  = popupWait.delayTimes[delayIndex]

    #setup script environment
    # callback handler so we can follow which line the script is running
    pyi.setCallbackHandler(showScriptLine)

    #rename run button so we can use it as stop button
    popupWait.cmdRun.configure(text="Stop")

    #  error handler should output to striptErrors widget instead of console
    def errhndlr(errStack):
        win.popupWait.scriptErrors.delete(0.0,tk.END)
        win.popupWait.scriptErrors.insert(tk.END, '\n\n'.join(errStack)) 
        win.popupWait.tabs.select(win.popupWait.errorsTab)        
        msgbox=messagePopup.show(win,type="error",title="Script failed", message=f"Errors in script '{popupWait.scriptname}'!")
    pyi.setErrorHandler(errhndlr)
    #  reroute print to infobos
    def print2InfoBox(msg):
        print (f"msg type {type(msg)}")
        if isinstance(msg,bytes): 
            popupWait.varInfo.set(bytes2String.raw(msg).strip())
        elif isinstance(msg,str):    
            popupWait.varInfo.set(msg.strip())
        else:    
            popupWait.varInfo.set(msg)
    pyi.addSystemFunction('print',print2InfoBox,[[str,int,bool,float,bytes],])
    def printAscii2InfoBox(msg):
        popupWait.varInfo.set(bytes2String.ascii(msg).strip())
    pyi.addSystemFunction('printa',printAscii2InfoBox,[[bytes],])
    def printHex2InfoBox(msg):        
        popupWait.varInfo.set(bytes2String.hex(msg).strip())
    pyi.addSystemFunction('printh',printHex2InfoBox,[[bytes],])
    def printDec2InfoBox(msg):
        popupWait.varInfo.set(bytes2String.dec(msg).strip())
    pyi.addSystemFunction('printd',printDec2InfoBox,[[bytes],])
    def printRaw2InfoBox(msg):
        popupWait.varInfo.set(f"{msg}")
    pyi.addSystemFunction('printr',printRaw2InfoBox,[[bytes],])
    #  add send (over serial) command
    pyi.addSystemFunction('send',send,[[str,],])
    #  add received var (to be updated each x msecs)
    pyi.importSystemFunction(pyi,__name__,"received")

    #run script
    scriptStart=time.time()
    runSuccess=pyi.runScript(delaytime=delayTime,skipVarDelay=popupWait.varSkipVars.get())
    scriptDuration=time.time()-scriptStart
    if runSuccess and isProcessingScript:
        msgbox=messagePopup.show(win,type="info",title="Script finished", message=f"Script '{popupWait.scriptname}' finished in {scriptDuration:.4f} seconds!")

    if runSuccess and not isProcessingScript:
        msgbox=messagePopup.show(win,type="warning",title="Script stopped", message=f"Script '{popupWait.scriptname}' interupted after {scriptDuration:.4f} seconds!")

    # set flag    
    isProcessingScript=False

    #rename stop button so we can use it as run button
    popupWait.cmdRun.configure(text="Run")
