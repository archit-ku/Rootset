from flask import Blueprint, render_template, url_for, request, redirect, flash
from .models import User, TwitterData
from flask_login import login_required, login_user, current_user
from sqlalchemy import func
from . import db, creatingClassifier
import tweepy, configparser, requests, math, pickle, os, random
from nltk.corpus import stopwords
from datetime import datetime

stop_words = stopwords.words('english')

seeData = Blueprint("seeData", __name__)

with open("config.classifier", "rb") as classifier_file:
        classifier = pickle.load(classifier_file)

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
} #maps id of weather condition with possible evaluation score, eg weather code 200 (thunderstorm with light rain) returns score of 3


weatherStateMap = {210:"Light Thunderstorm",
221:"Ragged Thunderstorm",
211:"Thunderstorm",
230:"Thunderstorm with Light Drizzle",
231:"Thunderstorm with Drizzle",
232:"Thunderstorm with Heavy Drizzle",
200:"Thunderstorm with Light Rain",
201:"Thunderstorm with Rain",
212:"Heavy Thunderstorm",
202:"Thunderstorm with Heavy Rain",
300:"Light Intensity Drizzle",
301:"Drizzle",
321:"Shower Drizzle",
302:"Heavy Intensity Drizzle",
310:"Light Intensity Drizzle Rain",
313:"Shower Rain and Drizzle",
311:"Drizzle Rain",
312:"Heavy Intensity Drizzle Rain",
314:"Heavy Shower Rain and Drizzle",
500:"Light Rain",
520:"Light Intensity Shower Rain",
521:"Shower Rain",
531:"Ragged Shower Rain",
501:"Moderate Rain",
522:"Heavy Intensity Shower Rain",
502:"Heavy Intensity Rain",
503:"Very Heavy Rain",
504:"Extreme Rain",
511:"Freezing Rain",
601:"Snow",
602:"Heavy Snow",
621:"Shower Snow",
620:"Light Shower Snow",
600:"Light Snow",
622:"Heavy Shower Snow",
615:"Light Rain and Snow",
616:"Rain and Snow",
612:"Light Shower Sleet",
613:"Shower Sleet",
611:"Sleet",
701:"Mist",
741:"Fog",
721:"Haze",
751:"Sand",
761:"Dust",
771:"Squalls",
731:"Sand/Dust Whirls",
711:"Smoke",
781:"Tornado",
762:"Volcanic Ash",
800:"Clear Sky",
801:"Few Clouds",
802:"Scattered Clouds",
803:"Broken Clouds",
804:"Overcast Clouds"
}


class WeatherRecord:
    def __init__(self, temp, windSpeed, weatherID, score=0):
        self.temp = temp
        self.windSpeed = windSpeed
        self.weatherID = weatherID
        self.score = score

    def recursiveAdd(self, nums):
        if len(nums)!=0:
            return nums[0] + self.recursiveAdd(nums[1:])
        return 0

    def tempCurve(self):
        #evaluates output of curve y = 30e^(-((x/22)-1)^2), which is a curve i found that nicely distributes temperature scores
        rank = self.temp
        rank = (rank/22)-1
        rank = -(rank**2)
        rank = math.e ** rank
        rank *= 30
        rank = round(rank)
        return rank
    
    def windCurve(self):
        rank = self.windSpeed
        if rank > 7: 
            rank += 12
            rank = round(300/rank) #same thing as above with curve y = 300/(x+12)
        else:
            #y = (x/2) + 12.29 if speed lower than 7
            rank = round((rank/2) + 12.29) # y = (x/2) + 12.29 if speed lower than 7
        return rank

    def weatherRank(self):
        #find rank for weather's specific description from global dictionary "weatherMap"
        rank = weatherMap[self.weatherID]
        return rank
    
    def getScore(self):
        #collate scores from the 3 methods above
        self.score += self.recursiveAdd([self.tempCurve(), self.windCurve(), self.weatherRank()])
        return self.score

#object class that returns facts
class Feedback:
    def __init__(self, location):
        self.location = location
    
    #acccess location in files, randomly select a fact
    def factGen(self):
        with open(self.location) as f:
            lines = f.readlines()
            fact = random.choice(lines)
            f.close()
        return fact
    
class SadFact(Feedback):
    #inherits from Feedback class, so has the factGen function
    #location is overwritten to where the sad facts are stored
    def __init__(self, location="website/static/sadFacts.txt"):
        super().__init__(location)

class FunFact(Feedback):
    #also inherits from Feedback class
    #location is overwritten to where the fun facts are stored
    def __init__(self, location="website/static/funFacts.txt"):
        super().__init__(location)
        
#returns a random joke from jokeapi
def jokeGen():
    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,racist,sexist,explicit&type=twopart"
    jokeData = requests.get(url).json()
    setup = jokeData["setup"]
    delivery = jokeData["delivery"]
    return [setup, delivery]

@seeData.route("/twitter")
@login_required
def twitter():
    #check if lastFetch is at least 30 mins ago, or null. If either true, fetch API data. If not, use stored values from last fetch
    twitterData = TwitterData.query.filter_by(user_id=current_user.id).first()
    now = datetime.now()
    delta = 0
    if twitterData.last_fetch != None:
        delta = (now-twitterData.last_fetch).seconds #time since last fetch in seconds
    SECONDS = 1800  #30 minutes in seconds
    if (twitterData.last_fetch == None) or (delta > SECONDS): #only hits next section if not hit in SECONDS seconds
        #only hits this section if not already hit within last {SECONDS} seconds
        totalPos = 0
        totalNegative = 0
        
        config = configparser.ConfigParser()
        config.read("config.ini")
        
        consumer_key = config["twitter"]["api_key"]
        consumer_secret = config["twitter"]["api_key_secret"]
        access_token = twitterData.user_access_token
        access_token_secret = twitterData.user_access_token_secret
        

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        
        api = tweepy.API(auth)
        timeline_tweets = api.home_timeline(count=15) #higher number = more data, but more representative of timeline
        tweets = []
        for tweet in timeline_tweets:
            tweets.append(tweet.text) #list of tweets
        
        for tweet in tweets:
            tokens = tweet.split()
            #clean tokens (remove links, special characters - anything that doesn't contribute towards mood of a sentence)
            tokens = creatingClassifier.remove_noise(tokens, stop_words)
            #call classifier object
            sentiment = classifier.classify(dict([token, True] for token in tokens))
            if sentiment == "Positive":
                totalPos +=1
                
            elif sentiment == "Negative":
                totalNegative += 1
                
            
        #store total positive tweets, total negative tweets in last fetch in twitter data table
        twitterData.last_fetch_pos = totalPos
        twitterData.last_fetch_negative = totalNegative
        twitterData.last_fetch = func.now() #reset last fetch timer
        db.session.commit()
        
    totalPos = twitterData.last_fetch_pos
    totalNegative = twitterData.last_fetch_negative

    values = [totalPos, totalNegative]
    
    if (totalNegative/totalPos) > 1.3: #more negative tweets than positive
        joke = jokeGen()
        setup = joke[0]
        delivery = joke[1]
        return render_template("twitter.html", user=current_user, values=values, labels=["Positive Tweets", "Negative Tweets"], lastFetch=twitterData.last_fetch, setup=setup, delivery=delivery, op=0)
    elif (totalNegative/totalPos) < 0.75: #more positive tweets than negative
        f = SadFact()
        fact = f.factGen()
        return render_template("twitter.html", user=current_user, values=values, labels=["Positive Tweets", "Negative Tweets"], lastFetch=twitterData.last_fetch, fact=fact, op=1)
    
    #roughly neutral timeline
    f = FunFact()
    fact = f.factGen()
    return render_template("twitter.html", user=current_user, values=values, labels=["Positive Tweets", "Negative Tweets"], lastFetch=twitterData.last_fetch, fact=fact, op=2)

    

@seeData.route("/weather", methods = ["GET","POST"])
@login_required
def weather():
    #when user wants to change location
    if request.method == "POST":
        if request.form.get("setLoc") == "true":
            return redirect(url_for("seeData.setLocation"))

    #if user has never set a location
    if current_user.location == None:
        return redirect(url_for("seeData.setLocation"))
    
    #accessing weather api key
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_key = config["weather"]["api_key"]

    #location is stored in db as "{latitude},{longitude}"
    location = str(current_user.location)
    coords = location.split(",")
    lat = coords[0]
    lon = coords[1]

    #api call, store json data in weather variable
    weatherData = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric")
    weather = (weatherData.json())
    temps = []
    tempScores = []
    weatherIDs = []
    weatherScores = []
    windSpeeds = []
    windScores = []
    times = []
    scores = []

    #city will be passed to weather.html to display
    city = weather["city"]["name"]
    country = weather["city"]["country"]
    #print(weather)
    startDate = weather["list"][0]["dt_txt"][0:10]
    for i in range(0,8):
        temp = weather["list"][i]["main"]["feels_like"]
        weatherID = weather["list"][i]["weather"][0]["id"]
        windSpeed = weather["list"][i]["wind"]["speed"]
        time = weather["list"][i]["dt_txt"][11:16]
        
        #append all instances of weather conditions to temps, weatherIDs and windSpeeds
        #this enables showing how weather progresses over time
        temps.append(temp)
        weatherIDs.append(weatherID)
        windSpeeds.append(windSpeed)
        times.append(time)

        #create object of weather record class in order to process data
        record = WeatherRecord(int(temps[i]), int(windSpeeds[i]), weatherIDs[i])

        #add score as a percentage of max possible score (85.79)
        scores.append(round((record.getScore()/85.79)*100))
        tempScores.append(round((record.tempCurve()/30)*100))

        #add weather description score as a percentage of max score in category, and description itself as string
        weatherScores.append(f"{round((record.weatherRank()/40)*100)}% - ({weatherStateMap[weatherID]})")
        windScores.append(round((windSpeed/60)*100))

    #pass all values to weather.html to display
    return render_template("weather.html", user=current_user, values = scores, city=city, country=country, labels=times, tempScores=tempScores, weatherScores=weatherScores, windScores=windScores,startDate = startDate, windSpeeds=windSpeeds, temps=temps)
    

    #remember to include change location option for a user in here

@seeData.route("/setLocation", methods=["GET","POST"])
@login_required
def setLocation():
    #when data is sent from setLocation.html
    if request.method == "POST":
        city = request.form.get("city")

        config = configparser.ConfigParser()
        config.read("config.ini")
        api_key = config["weather"]["api_key"]

        #query weather api for the latitude and longitude of the city that user entered
        locationData = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={api_key}")
        
        #if api can't find a city that matches user's input
        if (locationData.json() == []) or city == "":
            flash("City not found", category="error")
            return render_template("setLocation.html", user=current_user)

        else:
            response = locationData.json()
            location = f'{response[0]["lat"]},{response[0]["lon"]}'
            #commit latitude and longitude to database
            current_user.location = location
            db.session.commit()

            #send user back to weather route, with new values in location field
            return redirect(url_for("seeData.weather"))
    
    #show input field for location
    return render_template("setLocation.html", user=current_user)

@seeData.route("/news")
@login_required
def news():
    totalPos = 0
    totalNegative = 0
    
    #read api keys
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_key = config["news"]["api_key2"]
    headlines = []
    urls = []

    url = ('https://newsapi.org/v2/top-headlines?'
        'country=us&'
        f'apiKey={api_key}')
    
    #send get request to newsapi
    response = requests.get(url)

    #format response as json
    data = response.json()

    #extract the article titles, and links to the articles
    for item in data["articles"]:
        headlines.append(item["title"])
        urls.append(item["url"])

    posHeadlines = []
    negativeHeadlines = []
    for headline in headlines:
        tokens = headline.split()

        #run headlines through classifier
        tokens = creatingClassifier.remove_noise(tokens, stop_words)
        sentiment = classifier.classify(dict([token, True] for token in tokens))
        if sentiment == "Positive":
            totalPos +=1

            #splitting all headlines into positive and negative
            posHeadlines.append(headlines.index(headline))
        elif sentiment == "Negative":
            totalNegative += 1

            #splitting all headlines into positive and negative
            negativeHeadlines.append(headlines.index(headline))

    #formatting data to pass to html
    posURLs = []
    negativeURLs = []
    for index in posHeadlines:
        posURLs.append(urls[index])
    for index2 in negativeHeadlines:
        negativeURLs.append(urls[index2])

    values = [totalPos, totalNegative]
    
    posTitles = []
    negativeTitles = []

    try:
        for loc in posHeadlines:
            posTitles.append(headlines[loc])

        for loc in negativeHeadlines:
            negativeTitles.append(headlines[loc])
    
    except:
        #in case there are no positive headlines or negative headlines
        posURLs, negativeURLs, posHeadlines, negativeHeadlines = "none", "none", "none", "none"

    if (totalNegative/totalPos) > 1.3: #more negative than positive
        joke = jokeGen()
        setup = joke[0]
        delivery = joke[1]
        return render_template("news.html", user=current_user, values=values, labels=["Positive Articles", "Negative Articles"], posURLs=posURLs, negativeURLs=negativeURLs, posHeadlines=posHeadlines, negativeHeadlines=negativeHeadlines, negativeTitles=negativeTitles, posTitles=posTitles, setup=setup, delivery=delivery, op=0)
    elif (totalNegative/totalPos) < 0.75: #more positive than negative
        f = SadFact()
        fact = f.factGen()
        return render_template("news.html", user=current_user, values=values, labels=["Positive Articles", "Negative Articles"], posURLs=posURLs, negativeURLs=negativeURLs, posHeadlines=posHeadlines, negativeHeadlines=negativeHeadlines, negativeTitles=negativeTitles, posTitles=posTitles, fact=fact, op=1)
    
    #roughly neutral
    f = FunFact()
    fact = f.factGen()
    return render_template("news.html", user=current_user, values=values, labels=["Positive Articles", "Negative Articles"], posURLs=posURLs, negativeURLs=negativeURLs, posHeadlines=posHeadlines, negativeHeadlines=negativeHeadlines, negativeTitles=negativeTitles, posTitles=posTitles, fact=fact, op=2)