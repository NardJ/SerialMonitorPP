print "\nTEST SCRIPT"
print "============"
print "\nBasic print"
print "-------------"
print "Print succesfull"
print f"Print formatting {'succesfull'}"

print "\nCore commands"
print "--------------"
var a 1
print f"{'OK  ' if 1==a else 'FAIL'} var assignment"

if 2*3==6 skip
print "FAIL oneline branch (IF-command)"
label skip
print "OK   oneline branch (IF-command)"

goto skip2
print "FAIL goto"
label skip2
print "OK   goto"

gosub subproc1
print "OK   return from sub"


print "NOT  TESTED   exit"

print "\nAssignements (var-command)"
print "-------------"
var a 1
var b 1+2
var c a+1
var d 2+a
var e a+b
var f "abc"
var g "def"+f
var h f+g
var t True
var s False
var u t&s
var v t|s
print f"{'OK  ' if 1==a           else 'FAIL'} var a 1       = {a} expected 1"
print f"{'OK  ' if 3==b           else 'FAIL'} var b 1+2     = {b} expected 3"
print f"{'OK  ' if 2==c           else 'FAIL'} var c a+1     = {c} expected 2"
print f"{'OK  ' if 3==d           else 'FAIL'} var d 2+a     = {d} expected 3"
print f"{'OK  ' if 4==e           else 'FAIL'} var e a+b     = {e} expected 4"
print f"{'OK  ' if f=='abc'       else 'FAIL'} var f \"abc\"   = {f} expected 'abc':"
print f"{'OK  ' if g=='defabc'    else 'FAIL'} var g \"def\"+f = {g} expected 'defabc':"
print f"{'OK  ' if h=='abcdefabc' else 'FAIL'} var h f+g     = {h} expected 'abcdefabc':"
print f"{'OK  ' if t==True        else 'FAIL'} var t True    = {t} expected True"
print f"{'OK  ' if s==False       else 'FAIL'} var s False   = {s} expected False"
print f"{'OK  ' if u==False       else 'FAIL'} var u t&S     = {u} expected False"
print f"{'OK  ' if v==True        else 'FAIL'} var v t|s     = {v} expected True"

print "\nArithmetics"
print "------------"
print f"{'OK  ' if 8==4*(1+2)/3+2**2 else 'FAIL'} 4*(1+2)/3+2**2      = {4*(1+2)/3+2**2}   expected 8"
print f"{'OK  ' if 8==e*(a+c)/b+c**c else 'FAIL'} e*(a+c)/b+c**c      = {e*(a+c)/b+c**c}   expected 8"
print f"{'OK  ' if True==(2<3) else 'FAIL'} (2<3)               = {(2<3)}  expected True"
print f"{'OK  ' if False==(2>3) else 'FAIL'} (2>3)               = {(2>3)} expected False"
print f"{'OK  ' if math.sin(3.1415)<0.001 else 'FAIL'} math.sin(3.1415)    = {math.sin(3.1415)} expected <0.001"

print "\nSystem commands"
print "-----------"


print "\nMacros (if-command)"
print "-----------"
if False {
    goto skip3
}
print ("OK   if-multiline")
goto skip4
label skip3
print ("FAIL if-multiline)")
label skip4

a 0

if True {
  a 1
}else{
  a a+2
}
print f"{'OK  ' if a==1 else 'FAIL'} if/else-multiline part if"

a 0
if False {
  a 1
}else{
  a a+2
}
print f"{'OK  ' if a==2 else 'FAIL'} if/else-multiline part else"

var i 0
while (i<4) {    
  i i+1
}
print f"{'OK  ' if (i==4) else 'FAIL'} while loop"

i 0
for x 0 9 3 {
  i i+1
}
print f"{'OK  ' if (i==3) else 'FAIL'} for loop"

i 0
for x 0 3 {
  for y 0 3 {
    i i+1
  }
}
print f"{'OK  ' if (i==9) else 'FAIL'} for nested loop"


print "\nSyntax"
print "------------"

var a (2+3)
print f"{'OK  ' if a==5 else 'FAIL'} calc enclosed in ()"

var b (f"{'OK  ' if a==5 else 'FAIL'} string enclosed in ()")
print b

if True  skip5
print "FAIL multiple spaces between tokens"
goto skip6
label skip5
print "OK   multiple spaces between tokens"
label skip6

print "\nOptional formatting"
print "------------"
var b = 1
print f"{'OK  ' if b==1 else 'FAIL'} 'var b = 1'"
b = 2
print f"{'OK  ' if b==2 else 'FAIL'} 'b = 2'"

var b = 1
for a = 1...3 : 2 {
  b = b+1
}
print f"{'OK  ' if b==2 else 'FAIL'} 'for a = 1...3 : 2 {'{'}'"

print "\nSystem Vars"
print "------------"

var p pi
print f"{'OK  ' if (p-3.1415)<0.001 else 'FAIL'} calling system var with 'var p pi'"

sleep (1)
print "OK   system (python) function sleep (and print) with statement 'sleep (1)'"

var m millis()
print "OK   custom coded function with statement 'var m millis()'"

gosub subproc1

print "\n-----------------"
print f"Version: {version}"
print "\nEND SCRIPT"
print "============"



#print "\nError handling"
#print "------------"
#print "Unclosed loop
#if True {
#print "Unclosed string...

exit

#======================================

label subproc1
  print ("OK   gosub label")
  gosub subproc2
return

sub subproc2
  print ("OK   gosub sub")
return