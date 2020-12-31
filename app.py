from flask import Flask, request, render_template, redirect, url_for, flash
from flask_pymongo import PyMongo
from pymongo import MongoClient
from forms import RegistrationForm, LoginForm


import json
import requests
import jsonify
import random


app = Flask(__name__)
app.config['SECRET_KEY'] = '5f12bb0e4dc6ed2d01ba6ac064416f42'
app.config["MONGO_URI"] = 'mongodb+srv://wasiq:password123password@cluster0.g3f41.mongodb.net/application?retryWrites=true&w=majority'
app.debug = True
mongo = PyMongo(app)


#Route for home page
@app.route("/")
def index():
    return render_template("index.html", title='Home')

@app.route("/register", methods = ["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account Created For {form.username.data}!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', title = 'Register', form=form)

@app.route("/login",  methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data=='password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html', title = 'Login', form=form)

@app.route("/about", methods = ["GET", "POST"])
def about():
    return render_template('about.html', title = 'About')

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
@app.route("/movies_recommendations", methods=["POST","GET"])
def movies_recommendations():

    #GOD CODE 2.0!!
    tmdb_session = requests.Session()

    cursor_object = mongo.db.movies.find({})

    id_list = []

    for item in cursor_object:
        id_list.append(item['_id'])
    
    all_recommended_movies_ids = []


    for item in id_list:
        endpointMovie = "https://api.themoviedb.org/3/movie/{}/recommendations?api_key=586f9b611ec26170fbc7b228645fa5ca".format(item)
        responseMovie = tmdb_session.get(endpointMovie)
        json_data_movie = json.loads(responseMovie.text)  
        counter = 0 
            
        for data in json_data_movie['results']:
            if counter < 5: 
                all_recommended_movies_ids.append(data['id'])
                counter += 1
            else:
                break


    shuffled_recommended_list = random.sample(all_recommended_movies_ids,len(all_recommended_movies_ids))

    recommended_movie_information = []
    
    for movie_name in shuffled_recommended_list:
        endpointMovie = "https://api.themoviedb.org/3/movie/{}?api_key=586f9b611ec26170fbc7b228645fa5ca".format(movie_name)
        responseMovie = tmdb_session.get(endpointMovie)
        json_data_movie = json.loads(responseMovie.text) 

        temp_dict = {"id":json_data_movie["id"], "title":json_data_movie['original_title']}
        recommended_movie_information.append(temp_dict.copy())


    #loop this shit into the html
   # print(recommended_movie_information)

    return render_template("movie_recommendations.html", recommended_movie_information=recommended_movie_information)




@app.route("/tv_recommendations", methods=["POST","GET"])
def tv_recommendations():

    #GOD CODE 2.0!!
    tmdb_session = requests.Session()

    cursor_object = mongo.db.shows.find({})

    id_list = []

    for item in cursor_object:
        id_list.append(item['_id'])
    
    all_recommended_shows_ids = []


    for item in id_list:
        endpointShow = "https://api.themoviedb.org/3/tv/{}/recommendations?api_key=586f9b611ec26170fbc7b228645fa5ca".format(item)
        responseShow = tmdb_session.get(endpointShow)
        json_data_show = json.loads(responseShow.text)  
        counter = 0 
            
        for data in json_data_show['results']:
            if counter < 5: 
                all_recommended_shows_ids.append(data['id'])
                counter += 1
            else:
                break


    shuffled_recommended_list = random.sample(all_recommended_shows_ids,len(all_recommended_shows_ids))

    recommended_shows_information = []
    
    for show_name in shuffled_recommended_list:
        endpointShow = "https://api.themoviedb.org/3/tv/{}?api_key=586f9b611ec26170fbc7b228645fa5ca".format(show_name)
        responseShow = tmdb_session.get(endpointShow)
        json_data_show = json.loads(responseShow.text) 

        temp_dict = {"id":json_data_show["id"], "title":json_data_show['name']}
        recommended_shows_information.append(temp_dict.copy())


    return render_template("tv_recommendations.html", recommended_shows_information=recommended_shows_information)


#Recommendation list of a specific movie that user picks.

@app.route("/recommendations_one/<string:recommendation_id>", methods=["POST","GET"])
def recommendations_one(recommendation_id):

    type_of_content = request.args.get('type')


    if type_of_content == 'movie':
        endpoint_recommendation= "https://api.themoviedb.org/3/movie/{}/recommendations?api_key=586f9b611ec26170fbc7b228645fa5ca".format(recommendation_id)
    

    else: 
        endpoint_recommendation= "https://api.themoviedb.org/3/tv/{}/recommendations?api_key=586f9b611ec26170fbc7b228645fa5ca".format(recommendation_id)


    response_recommendation = requests.get(endpoint_recommendation)
    json_data_movie = json.loads(response_recommendation.text)
   
    return json_data_movie

if __name__ == "__main__":
    
    app.run(debug=True)


