"""
import math
import ast
import random

weatherMap = {200:3,400:50} #maps id of weather condition with possible evaluation score, eg weather code 200 (thunderstorm with light rain) returns score of 3

class WeatherRecord:
    def __init__(self, temp, windSpeed, weatherID, score=0):
        self.temp = temp
        self.windSpeed = windSpeed
        self.weatherID = weatherID
        self.score = score

    def tempCurve(self):
        rank = self.temp
        rank = (rank/20)-1
        rank = -(rank**2)
        rank = math.e ** rank
        rank = round(30*rank) #evaluates output of curve y = 30e^(-((x/20)-1)^2), which is a curve i found that nicely distributes temperature scores
        return rank
    
    def windCurve(self):
        rank = self.windSpeed
        if rank > 7: 
            rank += 12
            rank = round(300/rank) #same thing with curve y = 300/(x+12)
        else:
            rank = round((rank/2) + 12.29)
        return rank
    
    def getScore(self):
        self.score += self.tempCurve()
        self.score += self.windCurve()
        self.score += weatherMap[self.weatherID]

        return self.score

print(WeatherRecord(20,0,400).getScore())
print(WeatherRecord(-10,50,200).getScore())"""

#string = '2023-01-27 04:00:00'
#print(string[11:16])
#print(chr(63))
"""
def sadFactGen():
    with open("website/static/sadFacts.txt") as f:
        lines = f.readlines()
        fact = random.choice(lines)
        f.close()
    return fact

print(sadFactGen())
"""
#print(ord("き"))


"""
class Feedback:
    def __init__(self, location):
        self.location = location
    
    def factGen(self):
        with open(self.location) as f:
            lines = f.readlines()
            fact = random.choice(lines)
            f.close()
        return fact
    
class SadFact(Feedback):
    def __init__(self, location="website/static/sadFacts.txt"):
        super().__init__(location)

class funFactGen(Feedback):
    def __init__(self, location="website/static/funFacts.txt"):
        super().__init__(location)

s = SadFact()
print(s.factGen())

"""


"""
weatherMap = {210:14,
221:13,
211:12,
230:11,
231:10,
232:9,
200:9,
201:7,
212:4,
202:3,
300:15,
301:13,
321:13,
302:12,
310:12,
313:15,
311:13,
312:11,
314:8,
500:17,
520:17,
521:15,
531:13,
501:12,
522:12,
502:10,
503:8,
504:5,
511:0,
601:34,
602:22,
621:22,
620:22,
600:20,
622:15,
615:13,
616:10,
612:8,
613:5,
611:3,
701:14,
741:14,
721:12,
751:10,
761:10,
771:9,
731:9,
711:3,
781:0,
762:0,
800:40,
801:38,
802:30,
803:20,
804:15
}

def recursiveAdd(nums):
    if len(nums)!=0:
        return nums[0] + recursiveAdd(nums[1:])
    return 0


class WeatherRecord:
    def __init__(self, temp, windSpeed, weatherID, score=0):
        self.temp = temp
        self.windSpeed = windSpeed
        self.weatherID = weatherID
        self.score = score

    def tempCurve(self):
        rank = self.temp
        rank = (rank/22)-1
        rank = -(rank**2)
        rank = math.e ** rank
        rank *= 30#; print(f"temp curve {rank}")
        rank = round(rank) #evaluates output of curve y = 30e^(-((x/22)-1)^2), which is a curve i found that nicely distributes temperature scores
        return rank
    
    def windCurve(self):
        rank = self.windSpeed
        if rank > 7: 
            rank += 12
            rank = round(300/rank) #same thing with curve y = 300/(x+12)
        else:
            rank = round((rank/2) + 12.29) # y = (x/2) + 12.29 if speed lower than 7
        return rank

    def weatherRank(self):
        rank = weatherMap[self.weatherID]
        return rank
    
    def getScore(self):
        self.score += recursiveAdd([self.tempCurve(), self.windCurve(), self.weatherRank()])

        return self.score
"""
"""

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


#ascii characters to ints
def toInt(string):
    inputInt = ""
    for letter in string:
        inputInt += str(ord(letter))
    return inputInt


#reverse an input string
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

print(customHash("asdasdasd"))
"""