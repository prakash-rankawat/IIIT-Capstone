# Load the required libraries
from flask import Flask, render_template, request
# import pandas as pd
# from joblib import load
# import sklearn
import warnings

warnings.filterwarnings('ignore')
# model = load("prediction_model.joblib")

# Initialize flask app
app = Flask(__name__)


# Home Page
@app.route('/')
def main():
    return render_template('url.html')


# def get_data(url):
#   pass

def get_genre():
    genre = "Example"
    return genre


def get_cred_score():
    score = 4.5
    return score


# After clicking on get prediction
@app.route("/result", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # get url
        url = request.form.get("urlCheck")
        print(url)
        # scrape the data from URL
        # df = get_data()
        # predict genre
        genre = get_genre()

        # predict credibility score
        cred_score = get_cred_score()

        return render_template('url.html', genre=genre, score=cred_score)


# main method
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
