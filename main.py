# app.py
from flask import Flask, render_template, request, redirect, make_response
import time
import enchant

dict = enchant.Dict("en_US")

app = Flask(__name__, template_folder='templates')


# Function to check if a word is valid (you can replace this with your own validation logic)
def is_valid_word(word):
    return dict.check(word)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        day = request.cookies.get("day")
        if day == None:
            day = float(time.time()) - 86400
        if float(time.time()) - float(day) >= 86400:
            with open('word_data.txt', 'r') as file:
                word_data = file.read().replace('\n', '')
                word = request.form['word'].lower()
                if is_valid_word(word) is True:
                    if word in word_data:
                        resp = make_response(render_template('come_back.html'))
                        resp.set_cookie('day', str(time.time()))
                        with open('attempted_words.txt', 'w+') as file:
                            file.write(f"{word}\n")
                        return resp
                    with open('word_data.txt', 'w+') as file:
                        file.write(f"{word}\n")
                    with open('attempted_words.txt', 'w+') as file:
                        file.write(f"{word}\n")
                    resp = make_response(render_template('come_back.html'))
                    resp.set_cookie('day', str(time.time()))
                    return resp
                else:
                    return "Invalid word. Please enter a valid word."
        else:
            return render_template('already_tried.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
