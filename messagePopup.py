import os
import tkinter as tk

scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)

def show(mainWin,type,title, message):
    win=mainWin
    popupMsg = tk.Toplevel(win)
    popupMsg.transient(win.popupWait) 
    popupMsg.wm_title(title)
    #backcolor=win["bg"]#"#DDDDDD"
    popupMsg.configure(background='white')
    
    contentframe=tk.Frame(popupMsg,bg='white')
    contentframe.pack(side=tk.TOP,fill='x',expand=True,padx=(0,0),pady=(0,0))
    cvImg =tk.Label(contentframe,height=48,width=48,bg='white')
    imgpath=os.path.join(scriptdir,f"{type}48.png")
    cvImg.img=tk.PhotoImage(file=imgpath)
    cvImg.pack(side=tk.LEFT,padx=(32,0),pady=(32,32))
    cvImg.configure(image=cvImg.img)

    lb = tk.Label(contentframe, anchor='w',text=message,bg='white')
    lb.pack(side=tk.LEFT,padx=(16,32),pady=(32,32))

    # footer
    footerframe=tk.Frame(popupMsg,height=12,bg='white')
    footerframe.pack(side=tk.BOTTOM,fill='x',expand=True,padx=(0,0),pady=(0,0))
    popupMsg.cmdOk = tk.Button(footerframe, text="OK",command=popupMsg.destroy,width=10)
    popupMsg.cmdOk.pack(side=tk.RIGHT,padx=(8,8),pady=(8,8))
    popupMsg.cmdOk.configure(relief=tk.FLAT)

    popupMsg.grab_set()

