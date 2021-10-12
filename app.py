import random
import string
import os
from sqlalchemy import *
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

    
class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(10))

    def __init__(self, long, short):
        self.long = long
        self.short = short

@app.before_first_request
def create_tables():
    db.create_all()

    

# suppose, we already have 10 billion urls

id = 10000000000

def encode(id):
    # base 62 characters
    characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(characters)
    ret = []
    # convert base10 id into base62 id for having alphanumeric shorten url
    while id > 0:
        val = id % base
        ret.append(characters[val])
        id = id // base
    # since ret has reversed order of base62 id, reverse ret before return it
    KK = "".join(ret[::-1])
    short_url = Urls.query.filter_by(short=KK).first()
    print(":KK " , short_url, " ",KK)
    return KK
    
def shorten_url():
    global id
    while True:
        random_letters = encode(id) 
        short_url = Urls.query.filter_by(short=random_letters).first()
        print(":::" , random_letters )
        print(">>", short_url)
      
        if not short_url:
            print(">>>")
            return random_letters
        
        id=id+1


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        url_received = request.form["nm"]
        print(url_received)
        found_url = Urls.query.filter_by(long=url_received).first()

        if found_url:
            return redirect(url_for("display_short_url", url=found_url.short))
        else:
            short_url = shorten_url()
            new_url = Urls(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template('url_page.html')

    
@app.route('/display/<url>')
def display_short_url(url):
    return render_template('shorturl.html', short_url_display=url)


@app.route('/all_urls')
def display_all():
    return render_template('all_urls.html', vals=Urls.query.all())


@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f'<h1>URL does not exist</h1>'


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
    