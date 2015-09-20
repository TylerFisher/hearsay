#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
from datetime import datetime
import json
import os
import sys
import time

from fabric.api import task
from TwitterAPI import TwitterAPI

import app_config
import copytext

@task(default=True)
def update():
    """
    Stub function for updating app-specific data.
    """

def check_status(r):

    print(r.status_code)
    print(r.text)
    if r.status_code < 200 or r.status_code > 299:
        sys.exit(0)

@task
def upload_video(movie):
    nbytes = os.path.getsize(movie)
    file = open(movie, 'rb')
    data = file.read()
    api = TwitterAPI(
        'RCapaO1LKpGu7W5FsGRI4g', 
        'N6tavbh66HuGCguIiDff1Bi78aeHWTNpJraZK0pXGdo', 
        '50555139-kBOAta6N6rQCI4x5y6mOiytPfX8yZPWV5hpTyFeJ4', 
        'nb5bxqWfOot4lfEMtsvqDEtEaVKGaSgCXCKH9LZqJDXA6'
    )

    r = api.request('media/upload', {'command':'INIT', 'media_type':'video/mp4', 'total_bytes':nbytes})
    check_status(r)
    media_id = r.json()['media_id']
    
    r = api.request('media/upload', {'command':'APPEND', 'media_id':media_id, 'segment_index':0}, {'media':data})
    check_status(r)

    r = api.request('media/upload', {'command':'FINALIZE', 'media_id':media_id})
    
    r = api.request('statuses/update', {'status':'test', 'media_ids':media_id})
    check_status(r)
