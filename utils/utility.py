from sklearn.preprocessing import StandardScaler
import pickle
import pandas as pd
from utils.dbutils import database
from dbconfig import *

def preprocess(seq_id):
    #array = ['com', 'org', 'gov', 'edu','net','uk','au','ca','in']
    #df2 = df_main.loc[df_main['document_url_y'].isin(array)]
    db_util = database(host_name, username, password, auth_plugin, db, table)
    X= db_util.query_cols(seq_id,['commas', 'exclamations', 'dots', 'questions', 'spelling_errors', 'text_complexity', 'smog',
                                  'NN', 'VB', 'JJ', 'RB', 'DT', 'alexa_rank', 'document_url_y'])
    X= X.fillna(0)
    ## dummy encode the categorical variable.
    le= pickle.load(open("models/le.pkl", "rb"))
    X.document_url_y = le.transform(X.document_url_y)
    sc = pickle.load(open("models/standardscaler.pkl", "rb"))
    X= sc.transform(X)
    return X

def preprocess_class(seq_id):
    db_util = database(host_name, username, password, auth_plugin, db, table)
    X = db_util.query_cols(seq_id,
                           ['commas', 'exclamations', 'dots', 'questions', 'spelling_errors', 'text_complexity', 'smog',
                            'NN', 'VB', 'JJ', 'RB', 'DT', 'alexa_rank', 'document_url_y'])
    X=X.fillna(0)
    ## dummy encode the categorical variable.
    le_x_docURL= pickle.load(open("models/le_x_docURL.pkl", "rb"))
    X.document_url_y = le_x_docURL.transform(X.document_url_y)
    sc = pickle.load(open("models/sscaler_class.pkl", "rb"))
    X= sc.transform(X)
    return X