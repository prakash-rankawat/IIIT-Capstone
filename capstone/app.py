# Load the required libraries
from flask import Flask, render_template, request
# import pandas as pd
# from joblib import load
# import sklearn
import warnings
from utils import scraper
import pickle
from utils.utility import preprocess,preprocess_class
from utils.dbutils import database

warnings.filterwarnings('ignore')
# model = load("prediction_model.joblib")
# Initialize flask app
app = Flask(__name__)
host_name = "localhost"
username = 'root'
password = 'root'  # dba password
db = "capstone"
table = 'web_raw_data'
auth_plugin = 'mysql_native_password'
table="web_raw_data"

# Home Page
@app.route('/')
def main():
    return render_template('url.html')


# def get_data(url):
#   pass
def get_features(url):
    seq_id=scraper.feature_extract(url,True)
    return seq_id

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
        li_seq_id=get_features(url)
        db_util = database(host_name, username, password, auth_plugin, db, table)

        if li_seq_id is not None and li_seq_id>0:
            features_class=preprocess_class(li_seq_id)
            print("length of preproccessed features Classification is ",len(features_class))
            if len(features_class)>0:
                ls_category = get_genre(features_class)
                le_y=pickle.load(open("models/le_y.pkl","rb"))
                ls_category = le_y.inverse_transform(ls_category)[0]
                db_util.updateseqcolumn(li_seq_id, "category", ls_category)

        # predict credibility score
        if li_seq_id is not None and li_seq_id>0:
            features_reg=preprocess(li_seq_id)
            print("length of preproccessed features Regression is ",len(features_reg))
            if len(features_reg)>0:
                ld_cred_score = get_cred_score(features_reg)
                db_util.updateseqcolumn(li_seq_id,"credibility_rating", ld_cred_score)

        return render_template('url.html', genre=ls_category, score=ld_cred_score)


# main method
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
