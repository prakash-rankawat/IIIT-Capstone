from utils import scraper
import pickle
from utils.utility import preprocess,preprocess_class
from utils.dbutils import database
import json

host_name = "localhost"
username = 'root'
password = 'root'  # dba password
db = "capstone"
table = 'web_raw_data'
auth_plugin = 'mysql_native_password'
table="web_raw_data"

def get_features(url):
    seq_id=scraper.feature_extract(url,True)
    return seq_id

def get_genre(features):
    with open("models/category_model.pkl","rb") as file:
        class_model=pickle.load(file)
    file.close()
    category=class_model.predict(features)
    print(category)
    return category

def get_cred_score(features):
    with open("models/rf_credibility_model.pkl","rb") as file:
        reg_model=pickle.load(file)
    file.close()
    score=reg_model.predict(features)
    return score[0]

def predict(url):
    print(url)
    li_seq_id = get_features(url)
    db_util = database(host_name, username, password, auth_plugin, db, table)

    if li_seq_id is not None and li_seq_id > 0:
        features_class = preprocess_class(li_seq_id)
        print("length of preproccessed features Classification is ", len(features_class))
        if len(features_class) > 0:
            ls_category = get_genre(features_class)
            le_y = pickle.load(open("models/le_y.pkl", "rb"))
            ls_category = le_y.inverse_transform(ls_category)[0]
            db_util.updateseqcolumn(li_seq_id, "category", ls_category)

    # predict credibility score
    if li_seq_id is not None and li_seq_id > 0:
        features_reg = preprocess(li_seq_id)
        print("length of preproccessed features Regression is ", len(features_reg))
        if len(features_reg) > 0:
            ld_cred_score = get_cred_score(features_reg)
            db_util.updateseqcolumn(li_seq_id, "credibility_rating", ld_cred_score)

    return ls_category, ld_cred_score

def GetRegModelPerformance():
    reg_performance = json.load(open("models/regression_performance.json", "r"))
    class_performance=json.load(open("models/classification_performance.json","r"))
    return reg_performance,class_performance
