# app.py
from flask import Flask, render_template, request, redirect, make_response
import time
from pymongo import MongoClient
from collections.abc import MutableMapping
from random import randint
app = Flask(__name__, template_folder='templates')

# Function to check if a word is valid (you can replace this with your own validation logic)
def is_valid_word(word):
    with open("words_alpha.txt", "r") as word_file:
        word_contents = word_file.read()
        if word in word_contents:
            return True
        else:
            return False

# Connect to your MongoDB database
CONNECTION_STRING = "mongodb+srv://avneh:bhatia@cluster0.3hldccc.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)
db = client.Cluster0

# MongoDB collections for word data and attempted words
word_data_collection = db.get_collection("word_data")
attempted_words_collection = db.get_collection("attempted_words")
# Add this line to your code to get the 'streaks' collection
streaks_collection = db.get_collection("streaks")
users = db.get_collection("users")

@app.route('/', methods=['GET', 'POST'])
def index():
    user_id = request.cookies.get("user")
    if user_id == None:
        user_id = "Anonymous"
    streak = request.cookies.get("streak")
    if streak is None:
        streak = 0

    if request.method == 'POST':
        day = request.cookies.get("day")
        if day is None:
            day = float(time.time()) - 86400

        if float(time.time()) - float(day) >= 86400:
            word = request.form['word'].lower()

            if is_valid_word(word):
                if word_data_collection.find_one({"word": word}):
                    resp = make_response(render_template('come_back.html', streakp=''))
                else:
                    word_data_collection.insert_one({"word": word})
                    attempted_words_collection.insert_one({"word": word})
                        # Update the user's streak in the 'streaks' collection
                    if user_id == 'Anonymous':
                        user_id = f'{word}#{randint(1,9999)}'
                        while users.find_one({"user_id":user_id}):
                            user_id = f'{word}#{randint(1,9999)}'
                    users.insert_one({'user_id':user_id})
                    resp = make_response(render_template('new_word.html', streakp=''))
                    resp.set_cookie('user', str(user_id))
                    streaks_collection.update_one(
                        {"user_id": user_id},  # You can use a user identifier here
                        {"$inc": {"streak": 1}},  # Increment the streak by 1
                        upsert=True  # Create a new document if the user doesn't exist
                    )

                    resp.set_cookie('streak', str(int(streak) + 1))
                resp.set_cookie('day', str(time.time()))
                return resp
            else:
                return "Invalid word. Please enter a valid word."
        else:
            return render_template('already_tried.html', streakp='')
    top_streaks = list(streaks_collection.find().sort("streak", -1).limit(10))
    return render_template('index.html', streakp=f'Current streak {streak}', leaderboard=top_streaks, username="Username:"+user_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
