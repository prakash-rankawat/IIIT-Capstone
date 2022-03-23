# Load the required libraries
from flask import Flask, jsonify, request, json
from flask_cors import CORS
from RunModel import *
# import pandas as pd
# from joblib import load
# import sklearn
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

def get_features(url):
    genre, credibility_score=predict(url)
    reg_performance,class_performance=GetRegModelPerformance()
    print(reg_performance,class_performance)
    features = json.dumps({"URL": url, "Score": credibility_score, "Genre": genre,
                           "regTrainAccuScore": reg_performance["regTrainAccuScore"], "regTrainR2Score": reg_performance["regTrainR2Score"],
                           "regTestAccuScore": reg_performance["regTestAccuScore"], "regTestR2Score": reg_performance["regTestR2Score"],
                           "classTrainAccuScore": class_performance["classTrainAccuScore"], "classTrainF1Score": class_performance["classTrainF1Score"],
                           "classTestAccuScore": class_performance["classTestAccuScore"], "classTestF1Score": class_performance["classTestF1Score"]})
    return features


@app.route('/prediction', methods=["POST"])
def get_prediction():
    url = request.args.get('url')
    if len(url) == 0:
        return "URL is not supplied"
    else:
        return get_features(request.args.get('url', None))
0