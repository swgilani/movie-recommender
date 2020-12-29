from flask import Flask, request, render_template, redirect, url_for
from flask_pymongo import PyMongo
from pymongo import MongoClient
import json
import requests
import jsonify

app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb+srv://wasiq:password123password@cluster0.g3f41.mongodb.net/recommender?retryWrites=true&w=majority'
app.debug = True
mongo = PyMongo(app)

#Route for home page
@app.route("/")
def index():
    return render_template("index.html")

#Route to a form where you can search for a movie
@app.route("/search", methods=["POST","GET"])
def search():
    if request.method == "POST":
        item = request.form["movie_search"]
        return redirect(url_for("searchmovie", movie=item))
    
    else: 
        return render_template("search.html")

#Routes to a json object with the searched movie.
@app.route("/searchmovie/<movie>")
def searchmovie(movie):
    endpoint = "https://api.themoviedb.org/3/search/movie?api_key=586f9b611ec26170fbc7b228645fa5ca&query={}".format(movie)
    response = requests.get(endpoint)
    json_data = json.loads(response.text)
    return json_data

if __name__ == "__main__":
    app.run(debug=True)