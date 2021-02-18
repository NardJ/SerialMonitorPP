'''
PyInterpreter: A simple script interpreter written in python. 

All tokens must be seperated by spaces, except for tokens within expressions (calculations). 
String values should be enclosed between double quotes (") and can be formatted with python3 
f-formatting syntax, e.g. f"The number is {nr}." 
All python3 math functions are available for expressions e.g. a = 3+math.sin(math.pi/2). 

The interpreter only recognizes 9 core commands: var defition, var assignment, if goto, label, 
goto, sub gosub, return, exit

The following 'macro' multiline statements are rewritten to core commands beforehand:
if else, while and for.

Some chars are removed beforehand and can be used to increase readability of script:
'=', '...', ':'. Expressions and string can be enclosed in parentheses '(',')'

Usage

  1 Copy PyInterpreter.py to your project

  2 Add to your main projectfile
    Import PyInterpreter

  3 If you want to add function use addSystemFunction e.g.
    PyInterpreter.addSystemFunction('sleep',time.sleep,[(int,float),])
    First argument is call name, second is python function, this is list of allowed types for each argument the function takes.

  4 If you want to add variables use addSystemVar e.g.
    PyInterpreter.addSystemVar('pi', math,pi)

  5 Run script with loadScript and runScript() e.g.
    PyInterpreter.loadScript("myscript.pyi")
    PyInterpreter.runScript()
    or
    PyInterpreter.runScript("myscript.pyi")

  6 After loading script, the script can be rerun with runScript().
    System variables can be changed with modSystemVar. e.g.
    PyInterpreter.modSystemVar('pi', 3.2)
    PyInterpreter.runScript()       
'''

import os
import time
import re
import math

# GLOBALS
scriptpath= os.path.realpath(__file__) 
scriptdir = os.path.dirname(scriptpath)

# FOLLOWING VARS, SYSTEM FUNCTIONS can be called from scipt
systemVars={'version':'09.02.21'}
systemDefs={'print'  :(print,[[bool,int,float,str],]),}
callStack=[]
errorStack=[]

def clearGlobals():
    global systemVars,systemVars,callStack,errorStack
    systemVars={'version':'09.02.21'}
    systemDefs={'print'  :(print,[[bool,int,float,str],]),}
    callStack=[]
    errorStack=[]


def millis():
    return time.time()*1000

#####################################################
# ERROR TRACING
#####################################################
errorHandler=None
def logError(lineNr,scriptline,token,errMsg):
    errLine=f"{lineNr+1:04} > '{scriptline.strip()}'\n"
    if token: errLine+=f"Token: '{token}'\n"
    errLine+=f"{errMsg}"
    errorStack.append (errLine)  

def printErrorStack():
    if not errorHandler:
        if errorStack:
            print ("Errors found:")
            for error in errorStack:
                print (error)
                print ('\n')
    else:
        errorHandler(errorStack)            
quitOnError=True # needed for debugging error messages


#####################################################
# CODE REWRITING
#####################################################
def replaceOutsideQuotes(strLine,replaceDict):
    parts=strLine.split('"')
    for pNr in range(0,len(parts),2): # ony part #0,2,4... are outside of quotes
        for oldSeq in replaceDict:
            newSeq=replaceDict[oldSeq]
            parts[pNr]=parts[pNr].replace(oldSeq,newSeq)
    #print (parts)
    strLine='"'.join(parts)
    return strLine

def findIfElse(scriptlines,fromLineNr):
    #fromLineNr should be linenr of if-statement
    level=1
    #print ("----")
    for lineNr in range(fromLineNr+1,len(scriptlines)):
        scriptline = scriptlines[lineNr]
        statements = scriptline2statements(scriptline)
        if statements:
            for statement in statements:
                tokens=statement2tokens(statement)
                if tokens[0]=="}": level-=1
                if tokens[-1]=="{": level+=1
                if tokens[0]=="}else{" and level==1: return lineNr
        #print (f"{lineNr} : {level} > '{scriptline.strip()}'")
        if level==0: return -1
    #if nothing found we return -1 so rewrite macros can append error to stack
    return -1

def findGroupEnd(scriptlines,fromLineNr):
    #fromLineNr should be linenr of if-statement
    level=1
    for lineNr in range(fromLineNr+1,len(scriptlines)):
        scriptline = scriptlines[lineNr]
        statements = scriptline2statements(scriptline)
        if statements:
            for statement in statements:
                tokens=statement2tokens(statement)
                for token in tokens[1:-1]:
                    if token=="{" or token=="}": return -1
                if tokens[0]=="}": level-=1
                if tokens[-1]=="{": level+=1
                if level==0: return lineNr

    #if nothing found we return -1 so rewrite macros can append error to stack
    return -1

def findSubEnd(scriptlines,fromLineNr):
    level=1
    for lineNr in range(fromLineNr+1,len(scriptlines)):
        scriptline = scriptlines[lineNr]
        statements = scriptline2statements(scriptline)
        if statements:
            for statement in statements:
                tokens=statement2tokens(statement)
                if tokens[0]=="return": level-=1
                if tokens[0]=="sub": level+=1
                if level==0: return lineNr

    #if nothing found we return -1 so rewrite macros can append error to stack
    return -1

def removeRemarks(scriptlines):
    for lnr,scriptline in enumerate(scriptlines):
        # remove remarks
        if len(scriptline.strip())==0:       #do nothing if empty    
            #print (f"{lnr} empty")
            scriptlines[lnr]="\n"
        elif scriptline.strip()[0]=='#': 
            scriptlines[lnr]="\n"
            #print (f"{lnr} comment")
        else:    
            #count nr quotes
            if scriptline.count('"')%2==1:     # if odd number of quotes, the line is malformed
                logError(lnr,scriptline,None,"SyntaxError: String not closed on line.")
                return False
            #remove remark 
            PATTERN_REMARKS = re.compile(r'''((?:[^#"']|"[^"]*"|'[^']*')+)''')    
            scriptline= PATTERN_REMARKS.split(scriptline)[1::2][0]  
            scriptlines[lnr]=scriptline

    return scriptlines

def rewriteSyntax(scriptlines):    
    for lineNr,scriptline in enumerate(scriptlines):
        #replacements are now not specific for commands, but can be made by checking against first token
        #  cmd=statement2tokens(scriptline)[0]
        replaceDict={'  ' :' ',
                    ' = ':' ', 
                    ' : ': ' ',
                    '...':' '}
        scriptlines[lineNr]=replaceOutsideQuotes(scriptline,replaceDict)
    return scriptlines

def rewriteMacros(scriptlines):
    # ; not accounted for
    for lineNr,scriptline in enumerate(scriptlines):
        tokens=statement2tokens(scriptline)
        scriptline=scriptline.strip() # for printing errorStack without \n
        
        if tokens:
            #print (f"{lineNr}> '{scriptline:20}'   Tokens:{len(tokens)} {tokens}")        
            cmd=tokens[0]

            if cmd=="if" and tokens[-1]=="{":
                if len(tokens)!=3:  
                    logError(lineNr,scriptline,None,f"SyntaxError: If statement has {('more','less')[len(tokens)<3]} tokens than expected.")
                    return False          
                else:
                    jumpNr=findGroupEnd(scriptlines,lineNr)                                         # find closing bracket
                    elseNr=findIfElse(scriptlines,lineNr)
                    fndClosingBracket = (jumpNr>=0)
                    fndElse           = (elseNr>=0)
                    #print (f"lineNr:{lineNr:2}  elseNr:{elseNr:2}  endNr:{jumpNr:2}")
                    if fndClosingBracket:                                                           # if } found
                        cond=tokens[1]
                        if fndElse:
                            scriptlines[lineNr]=f"if not({cond}) {elseNr+1}\n"#                               # {scriptlines[lineNr]}"
                            scriptlines[elseNr]=f"goto {jumpNr}\n"##                                                     # {scriptlines[jumpNr]}"            
                        else:
                            scriptlines[lineNr]=f"if not({cond}) {jumpNr}\n"#                               # {scriptlines[lineNr]}"
                        scriptlines[jumpNr]=f"\n"##                                                     # {scriptlines[jumpNr]}"            
                    else:   
                        logError(lineNr,scriptline,None,f"SyntaxError: If statement is missing closing bracket {'}'}.")
                        return False            
            if cmd=="while":
                if tokens[-1]!="{" or len(tokens)!=3:  
                    logError(lineNr,scriptline,None,f"SyntaxError: While statement has {('more','less')[len(tokens)<3]} tokens than expected.")
                    return False          
                else:
                    jumpNr=findGroupEnd(scriptlines,lineNr)                                         # find closing bracket
                    fndClosingBracket = (jumpNr>=0)
                    if fndClosingBracket:                                                           # if } found
                        cond=tokens[1]
                        scriptlines[lineNr]=f"if not({cond}) {jumpNr}\n"#                               # {scriptlines[lineNr]}"
                        scriptlines[jumpNr]=f"if {cond} {lineNr}\n"#                                    # {scriptlines[jumpNr]}"
                    else:                                                                           # if } not found
                        logError(lineNr,scriptline,None,f"SyntaxError: While statement is missing closing bracket {'}'}.")
                        return False            
            if cmd=="for":
                if tokens[-1]!="{" or (len(tokens)!=5 and len(tokens)!=6):  
                    logError(lineNr,scriptline,None,f"SyntaxError: For statement has {('more','less')[len(tokens)<5]} tokens than expected.")
                    return False          
                else:
                    tkVar  = tokens[1]
                    tkFrom = tokens[2]
                    tkTo   = tokens[3]
                    tkStep = tokens[4] if len(tokens)==6 else 1
                    jumpNr=findGroupEnd(scriptlines,lineNr)                                         # find closing bracket
                    fndClosingBracket = (jumpNr>=0)
                    if fndClosingBracket:                                                           # if } found
                        scriptlines[lineNr]=f"var {tkVar} {tkFrom}\n"#                                  # {scriptlines[lineNr]}"
                        if int(tkStep)>0:
                            scriptlines[jumpNr]=f"{tkVar} {tkVar}+{tkStep} ; if {tkVar}<{tkTo} {lineNr+1}\n"#  # {scriptlines[jumpNr]}"
                        else:    
                            scriptlines[jumpNr]=f"{tkVar} {tkVar}+{tkStep} ; if {tkVar}>{tkTo} {lineNr+1}\n"#  # {scriptlines[jumpNr]}"
                    else:                                                                           # if } not found
                        logError(lineNr,scriptline,None,f"SyntaxError: For statement is missing closing bracket {'}'}.")
                        return False  
    

    #with open(os.path.join(scriptdir,"debug.raw"), "w") as reader: # open file
    #    reader.writelines(scriptlines)      # read all lines

    return scriptlines


#####################################################
# CODE EXTRACTION
#####################################################

def multiSplit(strText,delimiters):
    regular_exp = '|'.join(map(re.escape, delimiters))
    return re.split(regular_exp, strText) 

#https://stackoverflow.com/questions/2785755/how-to-split-but-ignore-separators-in-quoted-strings-in-python
def statement2tokens(scriptline):
    # remove remarks
    scriptline=scriptline.strip()               
    if len(scriptline)>0:
        PATTERN_SPACES = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
        tokens= PATTERN_SPACES.split(scriptline)[1::2]
        return tokens
    else:
        return None

def scriptline2statements(scriptline):
    # remove remarks
    if len(scriptline.strip())==0: return None
    if scriptline.strip()[0]=='#': return None
    if len(scriptline)>0:
        PATTERN_SPACES = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
        tokens= PATTERN_SPACES.split(scriptline)[1::2]
        return tokens
    else:
        return None

def extractLabels(scriptlines,varis):
    # create list of labels
    lineNr=0
    while lineNr<len(scriptlines):                  
        tokens=statement2tokens(scriptlines[lineNr])
        if tokens:
            cmd=tokens[0]
            nrArgs=len(tokens)-1
            if (cmd=="label" or cmd=="sub")  and nrArgs==1: 
                labelName =tokens[1]
                labelValue=lineNr
                varis[labelName]=labelValue
        lineNr+=1 
    return varis

#####################################################
# CODE EVALUATION
#####################################################

'''
def tokenIsString(token):
    if not token.count('"')==2: return False
    return ( (token[0]=='"') and (token[-1]=='"') )
def strIsNumber(strEval):
    return strEval.replace('.','0').isdigit()
'''
def evalArgument(varis,calcToken,linenr):
    try:
        return eval(calcToken,None,varis)
    except Exception as e:
        #print (f"Error evalStrArgument: {calcToken} is not a valid calculation.")   
        #print (f"       {e}")
        return ValueError(f"{e}")

def evalStatement(tokens,varis,linenr):
    args=[]             
    cmd=tokens[0]                                
    for tnr,token in enumerate(tokens[1:]):                            
        if ((cmd!="var" or tnr>0) and               # if cmd='var' do not eval 1st arg (name), but do eval 2nd arg (initial value of var) 
             cmd!="label"):                         # if cmd='label' first argument is name of label and should not be evaluated
            args.append(evalArgument(varis,token,linenr))                  
            #print (f"  {tokens[tnr+1]} -> {args[-1]}")
        else: 
            args.append(token)
            #print (f"  raw {token}")
    return args

def typeToken(arg):
    #this is run by runScipt/evalStatement after it did evalArgument on all rokens
    if isinstance(arg,str): return str
    if isinstance(arg,bool): return bool
    if isinstance(arg,int): return int
    if isinstance(arg,float): return float
    return None    

def checkArgs(lineNr,statement,tokens,tAllowedTypes):
    #this is run by runScipt/evalStatement after it did evalArgument on all rokens
    #print (f"checkArgs:{tokens} {tAllowedTypes}")
    if len(tokens)!=len(tAllowedTypes): 
        logError(lineNr,statement,None,f"ArgError: {len(tokens)} tokens found, {len(tAllowedTypes)} needed.")
        return False

    for token,allowedTypeList in zip(tokens,tAllowedTypes):
        tokenType=typeToken(token)
        #print (f"{token}:{tokenType} ? {tAllowedTypes}")
        if not (tokenType in allowedTypeList):
            logError(lineNr,statement,token,f"ArgError: {token} of type {tokenType}, allowed {allowedTypeList}.")
            return False
    
    return True

#####################################################
# USER FUNCTIONS
#####################################################

orgscriptlines=None
callbackHandler=None

def setErrorHandler(errorHandlerFunction):
    global errorHandler
    errorHandler=errorHandlerFunction

def setCallbackHandler(callbackHandlerFunction):
    global callbackHandler
    callbackHandler=callbackHandlerFunction

def setScript(scriptlinesList):
    global orgscriptlines
    # check if list
    if not isinstance(scriptlinesList,list):
            raise ValueError(f"scriptlinesList should be of type <class 'list'> containing strings of scriptlines. Got {type(scriptlinesList)}.")
    # check if lines are all strings
    for line in scriptlinesList:
        if not isinstance(line,str):
            raise ValueError(f"scriptlinesList should contain elements of type <class 'str'> containing strings of scriptlines. Got line with {type(line)}.")

    orgscriptlines=scriptlinesList

def loadScript(scriptpath):
    with open(scriptpath, "r") as reader: # open file
        setScript(reader.readlines())
    return orgscriptlines

def addSystemVar(varName,varValue):
    systemVars[varName]=varValue

def addSystemFunction(funcName,function,argTypeList):
    systemDefs[funcName]=(function,argTypeList)

linenr=0
def stopScript():
    global linenr
    linenr=len(orgscriptlines)

def runScript(scriptpath=None,delaytime=0):
    global orgscriptlines
    global errorStack
    global linenr
    # clear errorStack
    errorStack=[]

    # load script
    if scriptpath!=None:
        scriptlines=loadScript(scriptpath)
        orgscriptlines=scriptlines
    else:
        if orgscriptlines==None:  
            raise ValueError("No script loaded. Please specify path or use loadScript(scriptpath) / setScript(listOfscriptlines) first.")
            return
        scriptlines=orgscriptlines    
    # remove remarks
    ret=removeRemarks(scriptlines)
    if ret: scriptlines=ret
    else:
        printErrorStack()
        if quitOnError: return     
    # rewrite syntax
    ret=rewriteSyntax(scriptlines)
    if ret: scriptlines=ret
    else:
        printErrorStack()
        if quitOnError: return     
    # rewrite macros to core statements, returns false if error with brackets
    ret=rewriteMacros(scriptlines)
    if ret: scriptlines=ret
    else:
        printErrorStack()
        if quitOnError: return     
    # make room for variables and fill with systemvars
    varis=systemVars.copy()
    # convert labels to linenumbers and store as variables
    varis=extractLabels(scriptlines,varis)
    # process script
    level=0
    linenr=0
    while linenr<len(scriptlines):                                  # follow lines and control statements until last line
        statements=scriptline2statements(scriptlines[linenr])
        if callbackHandler: callbackHandler(linenr)
        #tokens=scriptline2tokens(scriptlines[linenr])
        if statements:
            for statement in statements:
                statement=statement.strip()
                tokens=statement2tokens(statement)
                if tokens:
                    #print (f"{linenr+1:02}> {statement.strip()}")

                    # extract command
                    cmd=tokens[0]                                       
                    # convert tokens to evaluated arguments
                    args=evalStatement(tokens,varis,linenr)
                    nrArgs=len(args)
                    # handle evaluation errors
                    errors=0
                    for argNr,arg in enumerate(args):
                        if arg.__class__.__name__=='ValueError':
                            logError(linenr,statement,tokens[argNr-1],f"EvalError: {arg.args[0].capitalize()}")
                            linenr=len(scriptlines)
                            errors+=1
                    # handle command
                    if not errors:
                        if cmd=="var"      and checkArgs(linenr,statement,args,[[str],[str,float,bool,int],]):
                            varis[args[0]]=args[1]                             # add variable to variable list
                            #print (f"cmd==var:{args}")                        
                            #print (f"  varis:{varis}")                        
                        elif cmd in varis  and checkArgs(linenr,statement,args,[[str,float,int],]) : 
                            varis[cmd]=args[0]                                  # change value of variable 
                            #print (f"  set var '{cmd}' {args[0]} -> {varis}")
                        elif cmd=="label"  and checkArgs(linenr,statement,args,[[str],]) : 
                            pass                                                # already handled in extractLabels
                        elif cmd=="sub"    and checkArgs(linenr,statement,args,[[int],]) : 
                            ret=findSubEnd(scriptlines,linenr)                  # already handled in extractLabels
                            if ret>-1: linenr=ret
                            else     : 
                                logError(linenr,statement2tokens,None,f"SyntaxError: Sub statement is missing matching 'return' statement.")
                                linenr=len(scriptlines)
                        elif cmd=="goto"   and checkArgs(linenr,statement,args,[[int],]):                           
                            linenr=args[0]                                      # change linenr to that associated with label
                        elif cmd=="gosub"  and checkArgs(linenr,statement,args,[[int],]):                           
                            callStack.append(linenr)
                            linenr=args[0]                                      # change linenr to that associated with label
                        elif cmd=="return" and checkArgs(linenr,statement,args,[]):                           
                            linenr=callStack.pop()
                        elif cmd=="if"     and checkArgs(linenr,statement,args,[[bool],[int]]):   
                            if args[0]: linenr=args[1]-1                        # set linenr -1 to offset linenr+=1 below
                            #print (f"if {args[0]} {args[1]}")                
                        #elif cmd=="print" and checkArgs(args,[[bool,int,float,str],]):   
                        #    print (args[0])                                     # print message
                        elif cmd=="exit"   and checkArgs(linenr,statement,args,[]):
                            linenr=len(scriptlines)                             # print message
                        elif cmd in systemDefs:                            
                            functionH=systemDefs[cmd][0]
                            allowedTypes=systemDefs[cmd][1]
                            #print (f"system function:{cmd} {args} {allowedTypes} ")
                            if checkArgs(linenr,statement,args,allowedTypes): 
                                functionH(*args)                                # call external function
                        else:
                            logError(linenr,statement,arg,f"CmdError: Command '{cmd}'not valid.")
                            linenr=len(scriptlines)
                # if tokens 
            # for statement in statements
        # if statements           
        linenr+=1
        time.sleep(delaytime)
    # while linenr<len(scriptlines)  
    if errorStack:
        printErrorStack()
        return False
    else:
        return True

def importSystemFunction(self,filename,methodname):
    func = getattr(__import__(filename), methodname)
    #setattr(funcs,methodname,func)
    setattr(self,methodname,func)

if __name__=="__main__":
  
    addSystemVar('scriptpath', scriptpath)
    addSystemVar('pi',         math.pi)
    addSystemFunction('sleep',time.sleep,[(int,float),])
    #importSystemFunction('filename')

    # Example 1 - load and run script in one line
    # =========
    runScript(os.path.join(scriptdir,"helloworld.pyi"))

    # Example 2 - load and run script in separate lines
    # =========
    #loadScript(os.path.join(scriptdir,"helloworld.pyi"))
    #runScript()

    # Example 3 - inject script and run 
    # =========
    #script=["var a 0\n","print \"hello\"\n"]
    #setScript(script)
    #runScript()

    # Example 4 - custom error handler
    # =========
    '''
    def myHndlr(errStack):
        print ("Got error stack!")
        print (errStack)

    setErrorHandler(myHndlr)
    script=["var a 0\n","print b\n"]
    setScript(script)
    runScript()
    '''

    # Example 5 - call function internal of ^this module^
    # =========
    #addSystemFunction('millis',time.sleep,[(int,float),])
    #script=["print millis()\n"]
    #setScript(script)
    #runScript()

    # Example 6 - call function external of this module
    # =========
    # in your main project add:
    #   def test():
    #       return "hello"
    #   import PyInterpreter as pyi
    #   pyi.importSystemFunction(pyi,__name__,"test")

    # For debugging
    # =============
    #addSystemVar('pi',         math.pi)
    #addSystemFunction('sleep',time.sleep,[(int,float),])
    #runScript(os.path.join(scriptdir,"testAll.pyi"))

    