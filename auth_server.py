import json
import os

from requests import post
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect

from definitions import TOKEN_URL, REDIRECT_URI, AUTH_URL, CLI_ID, SECRET_ID

app = Flask(__name__)

@app.route("/login")
def login():
    o2auth = OAuth2Session(CLI_ID, scope="user-read-playback-state", redirect_uri=REDIRECT_URI)
    auth_url, state = o2auth.authorization_url(AUTH_URL)
    return redirect(auth_url)

@app.route("/callback", methods=['GET'])
def callback():
    code = request.args.get('code')
    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    result = post(url=TOKEN_URL, auth=HTTPBasicAuth(CLI_ID, SECRET_ID),
                  data=form)
    return json.dumps(result.json())