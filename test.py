from flask import Flask
from flask.helpers import url_for
from werkzeug.utils import redirect

app  = Flask(__name__)

@app.route("/")
def hello():
    return redirect('/public/')