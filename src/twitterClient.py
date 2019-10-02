#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

from flask import Flask, request, redirect, url_for, flash, render_template
from flask_oauthlib.client import OAuth
import requests, json
from requests_oauthlib import OAuth1
import time

app = Flask(__name__)
app.config['DEBUG'] = True
oauth = OAuth()
mySession=None
currentUser=None
glb_oauth=None
usr_login = True

app.secret_key = 'development'


twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='CwZRtZ7ffXaqbPjrn95PUXYAM',
    consumer_secret='OQGbE4Ek0ONQMz1bewzY0fqHguopmjee219nhUFaZIUz6DSZpG'
)


# Obtener token para esta sesion
@twitter.tokengetter
def get_twitter_token(token=None):
    global mySession
    
    if mySession is not None:
        return mySession['oauth_token'], mySession['oauth_token_secret']

    
# Limpiar sesion anterior e incluir la nueva sesion
@app.before_request
def before_request():
    global mySession
    global currentUser
    
    currentUser = None
    if mySession is not None:
        currentUser = mySession
        

# Pagina principal
@app.route('/')
def index():
    global currentUser
    
    tweets = None
    if currentUser is not None:
        resp = twitter.request('statuses/user_timeline.json')
        if resp.status == 200:
            tweets = resp.data
        #else:
         #   flash('Imposible acceder a Twitter.')
    return render_template('index.html', user=currentUser, tweets=tweets)


# Get auth token (request)
@app.route('/login')
def login():
    callback_url=url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


# Eliminar sesion
@app.route('/logout')
def logout():
    global mySession
    
    mySession = None
    return redirect(url_for('index'))


# Callback
@app.route('/oauthorized', methods=['GET'])
def oauthorized():
    global mySession
    global glb_oauth
 
    
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        mySession = resp
        glb_oauth = OAuth1(twitter.consumer_key, client_secret=twitter.consumer_secret,resource_owner_key=mySession['oauth_token'], resource_owner_secret=mySession['oauth_token_secret'])

    return redirect(url_for('index', next=request.args.get('next')))




# Operaciones
@app.route('/deleteTweet', methods=['POST'])
def deleteTweet():
    global mySession
    if (mySession is None):
        flash("𝙀𝙧𝙧𝙤𝙧: No se ha podido eliminar el tweet porque no estanas logeado, prueba otra vez.")
        return login()
      
    global glb_oauth

    tweetID = request.form['deleteTweetId']

    del_url= twitter.base_url + 'statuses/destroy.json'
    del_payload = {'id':tweetID}

    del_resp = requests.post(url=del_url ,data=del_payload,auth=glb_oauth)

    if(del_resp.status_code == 200):  
        flash("𝙄𝙣𝙛𝙤: Has eliminado el tweet: " + tweetID)
    else:
        flash("𝙀𝙧𝙧𝙤𝙧: Ha habido un error al intentar eliminar el tweet:" + tweetID + ", el código de error es: "+del_resp.status_code)

    return redirect(url_for('index'))

@app.route('/retweet', methods=['POST'])
def retweet():
    global mySession
    if (mySession is None):
        flash("𝙀𝙧𝙧𝙤𝙧: No se ha podido retwitear porque no estabas logeado, prueba otra vez.")
        return login()
      
    global glb_oauth

    tweetID = request.form['retweetId']

    rt_url= twitter.base_url + 'statuses/retweet.json'
    rt_payload = {'id':tweetID}

    rt_resp = requests.post(url=rt_url ,data=rt_payload,auth=glb_oauth)

    if(rt_resp.status_code == 200):  
        flash("𝙄𝙣𝙛𝙤: Has retwiteado el tweet: " + tweetID)
    else:
        flash("𝙀𝙧𝙧𝙤𝙧: Ha habido un error al intentar retwitear el tweet:" + tweetID + ", el código de error es: "+rt_resp.status_code)

    return redirect(url_for('index'))

@app.route('/follow', methods=['POST'])
def follow():
    global mySession
    if (mySession is None):
        flash("𝙀𝙧𝙧𝙤𝙧: No se ha podido seguir al usuario porque no estabas logeado, prueba de nuevo")
        return login()

    global glb_oauth
    userID = request.form['userId']
    userName = request.form['userName']
    
    fl_url = twitter.base_url + 'friendships/create.json'
    if userID is '':
        fl_payload = {'screen_name':userName}
    else:
        fl_payload = {'user_id':userID}


    fl_resp = requests.post(url=fl_url,data =fl_payload,auth=glb_oauth)

    if(fl_resp.status_code == 200):  
        flash("𝙄𝙣𝙛𝙤: Has empezado a seguir a: " + userName)
    else:
        flash("𝙀𝙧𝙧𝙤𝙧: Ha habido un error al intentar seguir a:" + userName + ", el código de error es: "+fl_resp.status_code)
    
    return redirect(url_for('index'))
    
    
@app.route('/tweet', methods=['POST'])
def tweet():
    global mySession
    if (mySession is None):
        flash("𝙀𝙧𝙧𝙤𝙧: No se ha podido twitear porque no estabas logeado, prueba otra vez.")
        return login()

    global glb_oauth
    tw_text = request.form['tweetText']
    
    tw_url = twitter.base_url + 'statuses/update.json'
    tw_payload = {'status':tw_text}

    tw_resp = requests.post(url=tw_url,data =tw_payload,auth=glb_oauth)

    if(tw_resp.status_code == 200):  
        flash("𝙄𝙣𝙛𝙤: Has twiteado: " + tw_text)
    else:
        flash("𝙀𝙧𝙧𝙤𝙧: Ha habido un error al intentar twitear, el código de error es: "+ tw_resp.status_code)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005)


