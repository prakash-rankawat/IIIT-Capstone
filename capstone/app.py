# Load the required libraries
from flask import Flask, render_template, request
# import pandas as pd
# from joblib import load
# import sklearn
import warnings
from scraping import scraper
import pickle
from utility import preprocess

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
def get_features(url):
    return scraper.feature_extract(url,True)

def get_genre(features):
    try:
        with open("models/website_cat_model.pkl","rb") as file:
            reg_model=pickle.load(file)
        file.close()
        score=reg_model.predict(features)
    except:
        genre = "Example"
    return genre


def get_cred_score(features):
    with open("models/rf_credibility_model.pkl","rb") as file:
        reg_model=pickle.load(file)
    file.close()
    score=reg_model.predict(features)

    return score[0]


# After clicking on get prediction
@app.route("/result", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # get url
        url = request.form.get("urlCheck")
        print(url)
        features=get_features(url)
        print(features)
        # scrape the data from URL
        # df = get_data()
        # predict genre
        genre = get_genre(features)

        # predict credibility score
        cred_score = get_cred_score(preprocess(features))

        return render_template('url.html', genre=genre, score=cred_score)


# main method
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
