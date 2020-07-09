from flask import Flask, render_template, redirect, request, Response, send_file, abort
app = Flask(__name__)

import os.path
from os import path
import json
import zipstream
from PIL import Image
from io import BytesIO

data = os.path.dirname(__file__) + '/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def map():
    return render_template('map.html')

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
        list_of_files = os.listdir(data + 'mapillary_user')
        full_path = ["mapillary_user/{0}".format(x) for x in list_of_files]
        queue = sorted(full_path, key = os.path.getctime)

        return render_template('mapillary_takeout_init.html', queue = queue)

    content = open(log, 'r').read()
    return render_template('mapillary_takeout_progress.html', username=username, content=content)

@app.route('/photo/<username>/<seq>/<image>')
def image(username, seq, image):
    if '/' in username or '/' in seq or '/' in image: # No path injection
        return

    try:
        s = request.args.get('s')
        s = int(s)
    except:
        pass

    img_path = f'{data}/photo/{username}/{seq}/{image}'
    img_mask = img_path.rsplit('.', 1)[0] + '-mask.png'
    if path.exists(img_path):
        if path.exists(img_mask):
            img = Image.open(img_path)
            mask = Image.open(img_mask)
            img.paste(mask, mask=mask)

            if s:
                img.thumbnail((s, s), Image.ANTIALIAS)

            img_io = BytesIO()
            img.save(img_io, 'JPEG', quality=90)
            img_io.seek(0)
            return send_file(img_io, mimetype='image/jpeg')
        else:
            return send_file(img_path)
    else:
        abort(404)

@app.route('/export/<username>.zip')
def zip(username):
    if '/' in username: # No path injection
        return

    z = zipstream.ZipFile(mode = 'w', compression = zipstream.ZIP_DEFLATED, allowZip64 = True)

    list_of_seq = os.listdir(f"{data}/photo/{username}")
    for seq in list_of_seq:
        s = f"{data}/photo/{username}/{seq}"
        if os.path.isdir(s):
            list_of_images = os.listdir(s)
            for image in list_of_images:
                z.write(s + '/' + image)

    response = Response(z, mimetype = 'application/zip')
    response.headers['Content-Disposition'] = f'attachment; filename={username}.zip'
    return response
