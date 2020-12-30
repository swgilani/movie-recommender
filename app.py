from flask import Flask, request, render_template, redirect, url_for
from flask_pymongo import PyMongo
from pymongo import MongoClient
import json
import requests
import jsonify


app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb+srv://wasiq:password123password@cluster0.g3f41.mongodb.net/application?retryWrites=true&w=majority'
app.debug = True
mongo = PyMongo(app)


#Route for home page
@app.route("/")
def index():
    return render_template("index.html")

################################################################################################################
# Adding movies and shows to the database 
################################################################################################################

#Route to a form where you can search for a movie
@app.route("/search", methods=["POST","GET"])
def search():
    if request.method == "POST":
        item = request.form["movie_search"]
        return redirect(url_for("searchmovie", movie=item))
    
    else: 
        return render_template("search.html")

#Routes to a json object with the searched movie.
@app.route("/searchmovie/<movie>", methods=["POST","GET"])
def searchmovie(movie):

    if request.method == "POST":
        item = request.form["movie_search"]
        return redirect(url_for("searchmovie", movie=item))

    endpointMovie = "https://api.themoviedb.org/3/search/movie?api_key=586f9b611ec26170fbc7b228645fa5ca&query={}".format(movie)
    endpointTv = "https://api.themoviedb.org/3/search/tv?api_key=586f9b611ec26170fbc7b228645fa5ca&query={}".format(movie)

    responseMovie = requests.get(endpointMovie)
    json_data_movie = json.loads(responseMovie.text)

    responseTv = requests.get(endpointTv)
    json_data_tv = json.loads(responseTv.text)       

    return render_template("search.html", json_data_movie=json_data_movie, json_data_tv=json_data_tv )


@app.route("/post_movie_to_db", methods=["POST","GET"])
def post_movie_to_database():

    #GOD CODE
    if request.method == "POST":
        item = request.form["movie_search"]
        return redirect(url_for("searchmovie", movie=item))

    #getting title and id 
    title = request.args.get('title')
    movie_id = request.args.get('id')
    print(title)
    
    #posting to db (movies)
    post1 = {"_id":movie_id,"Title": title}
    
    #check if the id exists in the db collection already 
    mongo.db.movies.insert_one(post1)

    return render_template("search.html")

@app.route("/post_tv_to_database", methods=["POST","GET"])
def post_tv_to_database():

    if request.method == "POST":
        item = request.form["movie_search"]
        return redirect(url_for("searchmovie", movie=item))

    #getting title and id 
    title = request.args.get('title')
    show_id = request.args.get('id')
    print(title)
    
    #posting to db (shows)
    post2 = {"_id":show_id,"Title": title}

    #check if the id exists in the db collection already 
    mongo.db.shows.insert_one(post2)

    return render_template("search.html")

################################################################################################################

#giving movie and tv-show recommendations 

@app.route("/show_user_content", methods=["POST","GET"])
def show_user_content():
    cursor_movies = mongo.db.movies.find({})
    cursor_tv = mongo.db.shows.find({})
    return render_template("user_content.html", cursor_movies=cursor_movies, cursor_tv=cursor_tv)

    

#Recommendation list of all the movies in the user database
@app.route("/recommendations_all", methods=["POST","GET"])
def recommendations_all():

    return

#Recommendation list of a specific movie that user picks.
@app.route("/recommendations_one", methods=["POST","GET"])
def recommendations_one():
   return







if __name__ == "__main__":
    app.run(debug=True)


