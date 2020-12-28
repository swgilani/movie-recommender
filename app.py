from flask import Flask, request, render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import json
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:42024@localhost/postgres'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE']=True
app.config['SECURITY_PASSWORD_SALT'] = 'secret-string'
app.debug = True
db = SQLAlchemy(app)





@app.route('/')
def index():
    response = requests.get("https://api.themoviedb.org/3/movie/157336/recommendations?api_key=586f9b611ec26170fbc7b228645fa5ca")
    json_data = json.loads(response.text)
    return json_data

if __name__ == "__main__":
    app.run()
#comment
#zawar's comment