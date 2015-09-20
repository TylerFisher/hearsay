#!/usr/bin/env python

import app_config
import datetime
import json
import logging
import os
import static

from flask import Flask, flash, make_response, render_template, redirect, request, session, url_for
from render_utils import make_context, smarty_filter, urlencode_filter
import requests
from requests_oauthlib import OAuth1
from TwitterAPI import TwitterAPI
from urlparse import parse_qs
from werkzeug.debug import DebuggedApplication

app = Flask(__name__)
app.debug = app_config.DEBUG

try:
    file_handler = logging.FileHandler('%s/public_app.log' % app_config.SERVER_LOG_PATH)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
except IOError:
    print 'Could not open %s/public_app.log, skipping file-based logging' % app_config.SERVER_LOG_PATH

app.logger.setLevel(logging.INFO)

app.register_blueprint(static.static, url_prefix='/%s' % app_config.PROJECT_SLUG)

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')

# Example application views
@app.route('/%s/test/' % app_config.PROJECT_SLUG, methods=['GET'])
def _test_app():
    """
    Test route for verifying the application is running.
    """
    app.logger.info('Test URL requested.')

    return make_response(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/%s/twitterlogin/' % app_config.PROJECT_SLUG, methods=['GET', 'POST'])
def twitter_login():
    oauth = OAuth1(
        'RCapaO1LKpGu7W5FsGRI4g', 
        'N6tavbh66HuGCguIiDff1Bi78aeHWTNpJraZK0pXGdo'
    )
    r = requests.post(
        url='https://api.twitter.com/oauth/request_token',
        auth=oauth,)
    credentials = parse_qs(r.content)
    request_key = credentials.get('oauth_token')[0]
    request_secret = credentials.get('oauth_token_secret')[0]

    return redirect('https://api.twitter.com/oauth/authorize?oauth_token=%s' % request_key, 302)

@app.route('/%s/return/' % app_config.PROJECT_SLUG, methods=['GET'])
def response():
    context = make_context(asset_depth=2)

    request_key = request.args.get('oauth_token')
    verifier = request.args.get('oauth_verifier')
    print request_key, verifier

    # obtain access token
    oauth = OAuth1(
        'RCapaO1LKpGu7W5FsGRI4g', 
        'N6tavbh66HuGCguIiDff1Bi78aeHWTNpJraZK0pXGdo',
        request_key,
        verifier=verifier
    )
    r = requests.post(url='https://api.twitter.com/oauth/access_token', auth=oauth)
    credentials = parse_qs(r.content)
    access_token_key = credentials.get('oauth_token')[0]
    access_token_secret = credentials.get('oauth_token_secret')[0]

    oauth_tokens = {
        'key': access_token_key,
        'secret': access_token_secret
    }
    jsoned = json.dumps(oauth_tokens)
    return redirect(url_for('index', messages=jsoned))

def check_status(r):
    print(r.status_code)
    print(r.text)
    if r.status_code < 200 or r.status_code > 299:
        sys.exit(0)

@app.route('/%s/post_video/' % app_config.PROJECT_SLUG, methods=['GET', 'POST'])
def post_video():
    context = make_context(asset_depth=2)

    video_id = request.args.get('vid_id')
    movie = 'www/assets/%s.mp4' % video_id
    nbytes = os.path.getsize(movie)
    file = open(movie, 'rb')
    data = file.read()

    access_token = request.args.get('token')
    access_secret = request.args.get('secret')

    tweet = request.args.get('tweet')

    print tweet
    api = TwitterAPI(
        'RCapaO1LKpGu7W5FsGRI4g', 
        'N6tavbh66HuGCguIiDff1Bi78aeHWTNpJraZK0pXGdo', 
        access_token,
        access_secret
    )

    r = api.request(
        'media/upload', 
        {
            'command': 'INIT', 
            'media_type': 'video/mp4', 
            'total_bytes': nbytes
        }
    )
    check_status(r)
    media_id = r.json()['media_id']
    
    r = api.request(
        'media/upload', 
        {
            'command': 'APPEND', 
            'media_id': media_id, 
            'segment_index': 0
        }, 
        { 
            'media': data 
        }
    )
    check_status(r)

    r = api.request('media/upload', {
        'command': 'FINALIZE', 
        'media_id': media_id
    })
    
    r = api.request('statuses/update', {
        'status': tweet, 
        'media_ids': media_id
    })
    check_status(r)

    return ('', 204)

# Example of rendering index.html with public_app 
@app.route ('/%s/' % app_config.PROJECT_SLUG, methods=['GET'])
def index():
    """
    Example view rendering a simple page.
    """
    context = make_context(asset_depth=1)
    with open('data/featured.json') as f:
        context['featured'] = json.load(f)

    if request.args.get('messages'):
        messages = json.loads(request.args.get('messages'))
        context['access_token'] = messages['key']
        context['access_secret'] = messages['secret']

    return make_response(render_template('index.html', **context))

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app

# Catch attempts to run the app directly
if __name__ == '__main__':
    print 'This command has been removed! Please run "fab public_app" instead!'
