from flask import Flask, render_template, redirect, request
app = Flask(__name__)

import os.path
from os import path
import json

data = "/home/fred/mapillary_takeout_web/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mapillary_takeout')
def mapillary_takeout():
    return render_template('mapillary_takeout.html')

@app.route('/mapillary_takeout', methods=['POST'])
def mapillary_takeout_submit():
    email = request.form['email']
    password = request.form['password']
    username = request.form['username']

    f = open(data + "mapillary_user/" + username, "w")
    f.write(json.dumps({'email': email, 'password': password, 'username': username}))
    f.close()

    log = data + 'logs/' + username
    if os.path.exists(log):
        os.remove(log)

    return redirect("mapillary_takeout/" + username, code=302)

@app.route('/mapillary_takeout/<username>')
def mapillary_takeout_username(username):
    log = data + 'logs/' + username
    if not path.exists(log):
        return render_template('mapillary_takeout_init.html')

    content = open(log, 'r').read()
    return render_template('mapillary_takeout_progress.html', username=username, content=content)
