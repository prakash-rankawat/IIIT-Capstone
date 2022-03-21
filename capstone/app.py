# Load the required libraries
from flask import Flask, render_template, request
# import pandas as pd
# from joblib import load
# import sklearn
import warnings
from scraping import scraper
import pickle
from utility import preprocess,preprocess_class

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
    with open("models/category_model.pkl","rb") as file:
        class_model=pickle.load(file)
    file.close()
    category=class_model.predict(features)
    return category


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
        features_reg=preprocess(features)
        features_class=preprocess_class(features)
        genre = get_genre(features_class)
        le_y=pickle.load(open("models/le_y.pkl","rb"))
        genre = le_y.inverse_transform(genre)[0]
        # predict credibility score
        cred_score = get_cred_score(features_reg)

        return render_template('url.html', genre=genre, score=cred_score)


# main method
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
