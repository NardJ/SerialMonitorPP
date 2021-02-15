# This is a comment

print ("Hello World!")

var firstName = "John"
var lastName = "Smith"
print (f"\nMy name is {firstName} {lastName}")

print ("\nWatch me count even numbers between 0 and 10:")
for x = 0 ... 10 : 2 {
  gosub showNumber
}

sub showNumber
  print (f"  {x}")
return