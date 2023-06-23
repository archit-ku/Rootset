from flask import Blueprint, render_template, url_for, request, redirect
from .models import User, TwitterData
from flask_login import login_required, login_user, current_user
from . import db
import tweepy, configparser
import json

config = configparser.ConfigParser()
config.read("config.ini")

oauth = Blueprint("oauth", __name__)

CONSUMER_KEY = config["twitter"]["api_key"]
CONSUMER_SECRET = config["twitter"]["api_key_secret"]

DEBUG=True
RECEIVED_FILE="Received-Tokens.json"

#global dictionary to store request tokens in.
request_tokens={}
tweet_data=[]
emails = []

@oauth.route("/verify", methods=["GET", "POST"])
def verify():
	#make a note of user currently going through verification
    emails.append(current_user.email)
    try:
        #create Twitter API object
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

        #generate authorization URL
        url=auth.get_authorization_url()

        #capture request_token (made up of a request specific oauth token, oauth token secret, and confirmation that a callback url is configured.
        requestToken = auth.request_token

        #store request token to global dictionary
        #the 'oauth_token' comes across via the callback, so we can use that as the key to retrieve the other info.
        request_tokens[requestToken['oauth_token']]=requestToken

    except Exception as ex:
        return render_template('base.html', user=current_user)
    return redirect(url)

@oauth.route('/callback', methods=['GET'])
def oauth_data_collect():
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

	#if request is not correctly sent/received and permission to make api call is denied
	if "denied" in request.args:
		if DEBUG:
			print("Denied! - Token = ", request.args.get('denied'))
		return render_template('base.html', message="Authorization Denied!")

	else:
		try:
			#if valid response is received
			oauth_token = request.args.get('oauth_token', '')
			oauth_verifier = request.args.get('oauth_verifier', '')
			access_data ="not set"
			access_token = "not set"
			access_secret = "not set"
			requestToken = request_tokens[oauth_token]
			auth.request_token = requestToken
			access_data = auth.get_access_token(oauth_verifier)

		#valid parameters aren't received in response
		except Exception as ex:
			return render_template('base.html', error=ex)

		#set values according to response
		if access_data != "not set":
			access_token = access_data[0]
			access_secret = access_data[1]

			#make sure these new tokens are stored in a record linked to currently logged in user
			email = emails[len(emails)-1]
			emails.remove(email)
			user = User.query.filter_by(email=email).first()

			#log user back in if they have logged out during verification process (they are taken to external twitter portal)
			login_user(user, remember=True)
			data_row = TwitterData(user_access_token = access_token, user_access_token_secret = access_secret, user_id = current_user.id)
			
			#commit new tokens to twitter data table
			db.session.add(data_row)
			db.session.commit()

		#access token takes unexpected value
		if access_token != "not set":
			try:
				return redirect(url_for("seeData.twitter"))
			except Exception as ex:
				if DEBUG:
					print("Error in get_access_token:",  str(ex))
				return render_template('base.html', error=ex)
