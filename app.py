from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from pymongo import MongoClient
from forms import RegistrationForm, LoginForm
import json
import requests
import jsonify
import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = '5f12bb0e4dc6ed2d01ba6ac064416f42'
app.config["MONGO_URI"] = 'mongodb+srv://wasiq:password123password@cluster0.g3f41.mongodb.net/application?retryWrites=true&w=majority'
app.debug = True
mongo = PyMongo(app)
bcrypt = Bcrypt(app)


#Route for home page
@app.route("/", methods =['GET'])
def index():
    popular_movies = requests.get('https://api.themoviedb.org/3/movie/popular?api_key=586f9b611ec26170fbc7b228645fa5ca&language=en-US&page=1')
    popular_shows = requests.get('https://api.themoviedb.org/3/tv/popular?api_key=586f9b611ec26170fbc7b228645fa5ca&language=en-US&page=1')
    
    json_data_popular = json.loads(popular_movies.text)
    json_data_populartv = json.loads(popular_shows.text)
    

    return render_template("index.html", title='Home', json_data_popular = json_data_popular, json_data_populartv = json_data_populartv)

@app.route("/register", methods = ["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit() and request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'_id': form.email.data})

        if existing_user is None:
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            users.insert({'_id': form.email.data, 'name': form.username.data, 'password': hashed_password})
            session['email'] = form.email.data
            flash(f'Account Created For {form.username.data}!', 'success')
            return redirect(url_for('index'))

    return render_template('register.html', title = 'Register', form=form)

@app.route("/login",  methods = ["POST", "GET"])
def login():
    form = LoginForm()
    users = mongo.db.users
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        login_user = users.find_one({'_id': email})
      

        if login_user:
            if bcrypt.check_password_hash(login_user['password'],password):
                session['email'] = form.email.data
                flash('You have sucessfully logged in')
                return redirect(url_for('index'))
    else:
        flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html', title = 'Login', form=form)


@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for('index'))
    
@app.route("/about", methods = ["GET", "POST"])
def about():
    return render_template('about.html', title = 'About')

################################################################################################################
# Adding  and deleting movies and shows to the database 
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

#page with info about the content, and the option to add to liked or disliked
@app.route("/content_info", methods=["POST","GET"])
def content_info():

    poster = request.args.get('poster')
    title = request.args.get('title')
    movie_id = request.args.get('id')
    rating = request.args.get('rating')
    overview = request.args.get('overview')
    content_type = request.args.get('content_type')


    return render_template("content_info.html", title = title, poster = poster, movie_id = movie_id, overview = overview, rating = rating,content_type = content_type )


@app.route("/post_movie_to_db", methods=["POST","GET"])
def post_movie_to_database():

    #GOD CODE
    if request.method == "POST":
        item = request.form["movie_search"]
        return redirect(url_for("searchmovie", movie=item))

    #getting title and id 
    title = request.args.get('title')
    movie_id = request.args.get('id')
    liked = request.args.get('liked')
    print(title)
    
    #posting to db (shows)
    if "email" in session:
        #post2 = {"movie_id": movie_id, "email": session['email'], "Title": title}
        post2 = {"movie_id": movie_id, "email": session['email'], "Title": title, 'liked': liked}

    #check if the id exists in the db collection already
        exists = mongo.db.movies.find_one({"movie_id": movie_id, "email": session['email']})
        if exists: 
            print("this show is already in the user's database")
            return render_template("search.html")

        else:
            mongo.db.movies.insert_one(post2)
            print("successfully added to user's db")
            return render_template("search.html")

    return render_template("search.html")


@app.route("/post_tv_to_database", methods=["POST","GET"])
def post_tv_to_database():

    if request.method == "POST":
        item = request.form["movie_search"]
        return redirect(url_for("searchmovie", movie=item))

    #getting title and id 
    title = request.args.get('title')
    show_id = request.args.get('id')
    liked = request.args.get('liked')
    print(title)
    
    #posting to db (shows)
    if "email" in session:

        #like=1, not liked = 0
        post1 = {"show_id": show_id, "email": session['email'], "Title": title, "liked": liked}
    #check if the id exists in the db collection already
        exists = mongo.db.shows.find_one({"show_id": show_id, "email": session['email']})
        if exists: 
            print("this show is already in the user's database")
            return render_template("search.html")

        else:
            mongo.db.shows.insert_one(post1)
            print("successfully added to user's db")
            return render_template("search.html")


    return render_template("search.html")


@app.route("/delete_movie_from_db", methods=["POST","GET"])
def delete_movie_from_db():
    
    if request.method == "POST" and "email" in session:
        list_to_delete = request.form.getlist('delete_checkbox')
        all_movies = mongo.db.movies.find({'email': session['email']})

        for movie_in_db in all_movies:
            for movie_to_del in list_to_delete:
                if movie_in_db["movie_id"] == movie_to_del:
                    mongo.db.movies.delete_one({"movie_id": movie_to_del, "email": session['email']})
                

    
    return redirect(url_for('show_user_content')) 


    
@app.route("/delete_show_from_db", methods=["POST","GET"])
def delete_show_from_db():
    
    if request.method == "POST" and "email" in session:
        list_to_delete = request.form.getlist('delete_checkbox')
        all_shows = mongo.db.shows.find({'email': session['email']})

        for show_in_db in all_shows:
            for show_to_del in list_to_delete:
                if show_in_db["show_id"] == show_to_del:
                    mongo.db.shows.delete_one({"show_id": show_to_del, "email": session['email']})
                

    
    return redirect(url_for('show_user_content')) 



################################################################################################################

#giving movie and tv-show recommendations 
@app.route("/show_user_content", methods=["POST","GET"])
def show_user_content():
    if "email" in session:
        cursor_movies = mongo.db.movies.find({"email": session["email"]})
        cursor_tv = mongo.db.shows.find({"email": session["email"]})
        return render_template("user_content.html", cursor_movies=cursor_movies, cursor_tv=cursor_tv)

    

#Recommendation list of all the movies in the user database
@app.route("/movies_recommendations", methods=["POST","GET"])
def movies_recommendations():


    if "email" in session:
        #GOD CODE 2.0!!
        tmdb_session = requests.Session()

        cursor_object = mongo.db.movies.find({"email": session["email"], "liked": "1"})

        id_list = []

        #adds the ids of the liked movies from the db to a list
        for item in cursor_object:
            id_list.append(item['movie_id'])
        
        all_recommended_movies_ids = []

        
        for item in id_list:
            endpointMovie = "https://api.themoviedb.org/3/movie/{}/recommendations?api_key=586f9b611ec26170fbc7b228645fa5ca".format(item)
            responseMovie = tmdb_session.get(endpointMovie)
            json_data_movie = json.loads(responseMovie.text)  
            
            
            counter = 0 
            
            #adds the ids of the first 5 recommended movies for each id from id_list to another list 
            for data in json_data_movie['results']:
                
                #if the movie is not part of the db and not part of the rec list, add the movie to the list 
                if counter < 5 and (str(data['id']) not in id_list) and (data['id'] not in all_recommended_movies_ids):                   
                    all_recommended_movies_ids.append(data['id'])
                    counter += 1
                elif counter >= 5: 
                    break
  

        shuffled_recommended_list = random.sample(all_recommended_movies_ids,len(all_recommended_movies_ids))

        recommended_movie_information = []
        
        for movie_name in shuffled_recommended_list:
            endpointMovie = "https://api.themoviedb.org/3/movie/{}?api_key=586f9b611ec26170fbc7b228645fa5ca".format(movie_name)
            responseMovie = tmdb_session.get(endpointMovie)
            json_data_movie = json.loads(responseMovie.text) 

            temp_dict = {"id":json_data_movie["id"], "title":json_data_movie['original_title']}
            recommended_movie_information.append(temp_dict.copy())


        #getting the genres of all movies using the tmdb api
        get_genre_endpoint = "https://api.themoviedb.org/3/genre/movie/list?api_key=586f9b611ec26170fbc7b228645fa5ca"
        response_get_genre = tmdb_session.get(get_genre_endpoint)
        json_data_movie_genre = json.loads(response_get_genre.text)

        get_runtime_endpoint = "https://api.themoviedb.org/3/movie/ { } /?api_key=586f9b611ec26170fbc7b228645fa5ca"
        #assign filtered_genres to None because there are no filters when user first comes to the recommendations page
        filtered_genres = None
        filtered_runtime = None
        #get all the genre id's that the user filtered in the movies_recommendations.html page 
        if request.method == "POST":
            filtered_genres = request.form.getlist('genre_checkbox')
            filtered_runtime = str(request.form.getlist('runtime')[0])


           
        #if filtered_generes exists, then update the list of recommended movies with only the filtered genres
        if filtered_genres or filtered_runtime:
            filtered_list = []
            
            for movie in recommended_movie_information:
                temp_movie_id = movie["id"]
                #for each movie in users recommendations, we grab the id and run the movies_details endpoint to get information on the genres of that specific movie
                #then compare if the movie falls under the list of genres the user picked. if yes then add to recommendations, if not then dont show in recommendations
                get_movie_information_endpoint = "https://api.themoviedb.org/3/movie/{}?api_key=586f9b611ec26170fbc7b228645fa5ca".format(temp_movie_id)
                get_movie_information = tmdb_session.get(get_movie_information_endpoint)
                json_data_movie_information = json.loads(get_movie_information.text)

                movie_run_time = int(json_data_movie_information["runtime"])

                if filtered_runtime == "less_than_hour":
                    if movie_run_time > 60:
                        continue

                elif filtered_runtime == "hour_to_hour_half":
                    if movie_run_time < 60 or movie_run_time > 90:
                        continue

                elif filtered_runtime == "hour_half_to_two_hours":
                    if movie_run_time < 90 or movie_run_time > 120:
                        continue

                elif filtered_runtime == "more_than_two_hours":
                    if movie_run_time < 120:
                        continue

                #puts all the genres of that specific movie into genre_id_list and then checks if the filtered_list is a subset of the genre_id_list.
                #if it is a subset, then add the movie to filtered_list
                genre_id_list = []
                for genre_id in json_data_movie_information["genres"]:
                    genre_id_list.append(str(genre_id["id"]))
   
                if set(filtered_genres).issubset(genre_id_list):
                    filtered_list.append(temp_movie_id)
                    

            #finds the movie title of the filtered movie ids and returns them to the html page
            filtered_movie_information = []
            for movie_name in filtered_list:
                endpointMovie = "https://api.themoviedb.org/3/movie/{}?api_key=586f9b611ec26170fbc7b228645fa5ca".format(movie_name)
                responseMovie = tmdb_session.get(endpointMovie)
                json_data_movie = json.loads(responseMovie.text) 

                temp_dict = {"id":json_data_movie["id"], "title":json_data_movie['original_title']}
                filtered_movie_information.append(temp_dict.copy())

            return render_template("movie_recommendations.html", recommended_movie_information=filtered_movie_information, json_data_movie_genre=json_data_movie_genre)

                            
            
        return render_template("movie_recommendations.html", recommended_movie_information=recommended_movie_information, json_data_movie_genre=json_data_movie_genre, filtered_genres=filtered_genres, filtered_runtime=filtered_runtime )



@app.route("/tv_recommendations", methods=["POST","GET"])
def tv_recommendations():

    if "email" in session:
        #GOD CODE 2.0!!
        tmdb_session = requests.Session()

        cursor_object = mongo.db.shows.find({"email": session["email"]})
        
        id_list = []
        
        for item in cursor_object:
            id_list.append(item["show_id"])
        
        
        
        all_recommended_shows_ids = []


        for item in id_list:
            endpointShow = "https://api.themoviedb.org/3/tv/{}/recommendations?api_key=586f9b611ec26170fbc7b228645fa5ca".format(item)
            responseShow = tmdb_session.get(endpointShow)
            json_data_show = json.loads(responseShow.text)  
            counter = 0 
                

            for data in json_data_show['results']:

                #if the show is not part of the db and not part of the rec list, add the show to the list 
                if counter < 5 and (str(data['id']) not in id_list) and (data['id'] not in all_recommended_shows_ids):                   

                    all_recommended_shows_ids.append(data['id'])
                    counter += 1
                elif counter >= 5: 
                    break
   


        shuffled_recommended_list = random.sample(all_recommended_shows_ids,len(all_recommended_shows_ids))

        recommended_shows_information = []
        
        for show_name in shuffled_recommended_list:
            endpointShow = "https://api.themoviedb.org/3/tv/{}?api_key=586f9b611ec26170fbc7b228645fa5ca".format(show_name)
            responseShow = tmdb_session.get(endpointShow)
            json_data_show = json.loads(responseShow.text) 

            temp_dict = {"id":json_data_show["id"], "title":json_data_show['name']}
            recommended_shows_information.append(temp_dict.copy())


    #getting the genres of all movies using the tmdb api
        get_genre_endpoint = "https://api.themoviedb.org/3/genre/tv/list?api_key=586f9b611ec26170fbc7b228645fa5ca"
        response_get_genre = tmdb_session.get(get_genre_endpoint)
        json_data_show_genre = json.loads(response_get_genre.text)
        #assign filtered_genres to None because there are no filters when user first comes to the recommendations page
        filtered_genres = None
        #get all the genre id's that the user filtered in the movies_recommendations.html page 
        if request.method == "POST":
            filtered_genres = request.form.getlist('genre_checkbox')
           
        #if filtered_generes exists, then update the list of recommended movies with only the filtered genres
        if filtered_genres:
            
            filtered_list = []
            
            for show in recommended_shows_information:
                temp_show_id = show["id"]
                #for each movie in users recommendations, we grab the id and run the movies_details endpoint to get information on the genres of that specific movie
                #then compare if the movie falls under the list of genres the user picked. if yes then add to recommendations, if not then dont show in recommendations
                get_show_information_endpoint = "https://api.themoviedb.org/3/tv/{}?api_key=586f9b611ec26170fbc7b228645fa5ca".format(temp_show_id)
                get_show_information = tmdb_session.get(get_show_information_endpoint)
                json_data_show_information = json.loads(get_show_information.text)

                #checks if the genre id of the movie is in the user's genre filters. if yes then it adds the movie_id to the filtered_list
                for genre_id in json_data_show_information["genres"]:                   
                    if str(genre_id["id"]) in filtered_genres:
                        filtered_list.append(temp_show_id)

            #finds the movie title of the filtered movie ids and returns them to the html page
            filtered_show_information = []
            for show_name in filtered_list:
                endpointShow = "https://api.themoviedb.org/3/tv/{}?api_key=586f9b611ec26170fbc7b228645fa5ca".format(show_name)
                responseShow = tmdb_session.get(endpointShow)
                json_data_show = json.loads(responseShow.text) 

                temp_dict = {"id":json_data_show["id"], "title":json_data_show['name']}
                filtered_show_information.append(temp_dict.copy())

            return render_template("tv_recommendations.html", recommended_shows_information=filtered_show_information, json_data_show_genre=json_data_show_genre)

        return render_template("tv_recommendations.html", recommended_shows_information=recommended_shows_information, json_data_show_genre=json_data_show_genre)
    else:
        return "<h1 style='background-color:red;'>stop fkin wth our code</h1>"

    #Recommendation list of a specific movie that user picks.

@app.route("/recommendations_one/<recommendation_id>", methods=["POST","GET"])
def recommendations_one(recommendation_id):

    type_of_content = request.args.get('type')


    if type_of_content == 'movie':
        
        endpoint_recommendation= "https://api.themoviedb.org/3/movie/{}/recommendations?api_key=586f9b611ec26170fbc7b228645fa5ca".format(recommendation_id)
    

    elif type_of_content == 'show': 
        
        endpoint_recommendation= "https://api.themoviedb.org/3/tv/{}/recommendations?api_key=586f9b611ec26170fbc7b228645fa5ca".format(recommendation_id)


    response_recommendation = requests.get(endpoint_recommendation)
    json_data_movie = json.loads(response_recommendation.text)
   
    return json_data_movie

if __name__ == "__main__":
    
    app.run(debug=True)


