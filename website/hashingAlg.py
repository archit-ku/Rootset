#creating a stack, so that it can be used to reverse a string
class Stack:
    def __init__(self):
        self.__index = []

    def __len__(self):
        return len(self.__index)

    def push(self,item):
        self.__index.insert(0,item)
    
    def pop(self):
        if len(self) == 0:
            raise Exception("pop() called on empty stack.")
        return self.__index.pop(0)


#function to convert string of ASCII chars to ints
def toInt(string):
    inputInt = ""
    for letter in string:
        inputInt += str(ord(letter))
    return inputInt


#function to reverse string of integers
def reverseString(inputInt):
    stack = Stack()
    for num in inputInt:
        stack.push(num)
    
    reversedString = ""
    while len(stack) != 0:
        reversedString += stack.pop()
    
    return reversedString

def customHash(string):

    #conversion from ASCII chars to integers
    inputInt = toInt(string)

    #reversing the string of integers
    reversedString = reverseString(inputInt)
    
    #splitting into pairs and multiplying
    if len(reversedString) % 2 == 1:
        reversedString += "1"
    
    multipliedPairs = ""
    for x in range(int(len(reversedString)/2)):
        pair = reversedString[(2*x):((x+1)*2)]
        num1, num2 = int(pair[0]), int(pair[1])
        multipliedPair = num1 * num2
        multipliedPairs += str(multipliedPair)
        
    output = ""
    
    #splitting into pairs and normalising into ASCII range
    if len(multipliedPairs) % 2 == 1:
        multipliedPairs += multipliedPairs[-1]
    
    for i in range(int(len(multipliedPairs)/2)):
        pair = int(multipliedPairs[(2*i):((i+1)*2)])
        pair = pair % 94
        pair += 33

        #converting to ASCII and outputting
        output += chr(pair)

    return output