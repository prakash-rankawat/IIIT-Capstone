# Load the required libraries
from flask import Flask, jsonify, request, json
from flask_cors import CORS
from RunModel import *
# import pandas as pd
# from joblib import load
# import sklearn
from training import credibiltiy_training, category_training

import warnings

warnings.filterwarnings('ignore')
# model = load("prediction_model.joblib")

# Initialize flask app
app = Flask(__name__)
CORS(app)


# Home Page
@app.route('/')
def test():
    return 'this is test api'


@app.route('/retrain_credibility_model')
def retrain_cred():
    return jsonify(credibiltiy_training.regression_retrain())


@app.route('/retrain_category_model')
def retrain_category():
    return jsonify(category_training.classification_retrain())


def get_features(url):
    genre, credibility_score = predict(url)
    reg_performance, class_performance = GetRegModelPerformance()
    print(reg_performance, class_performance)
    features = json.dumps({"URL": url, "Score": credibility_score, "Genre": genre,
                           "regAccuracy": reg_performance["accuracy_score"],
                           "regR2Score": reg_performance["test_r2_score"],
                           "classAccuracy": class_performance['Accuracy'], "classF1Score": class_performance["F1-Score"]
                           })
    return features


@app.route('/prediction', methods=["POST"])
def get_prediction():
    url = request.args.get('url')
    if len(url) == 0:
        return "URL is not supplied"
    else:
        return get_features(request.args.get('url', None))
