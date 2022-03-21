from sklearn.preprocessing import StandardScaler
import pickle
import pandas as pd

def preprocess(X):
    #array = ['com', 'org', 'gov', 'edu','net','uk','au','ca','in']
    #df2 = df_main.loc[df_main['document_url_y'].isin(array)]

    X=X.fillna(0)
    ## dummy encode the categorical variable.
    le= pickle.load(open("models/le.pkl","rb"))
    X.document_url_y = le.transform(X.document_url_y)
    sc = pickle.load(open("models/standardscaler.pkl","rb"))
    X= sc.transform(X)
    return X

def preprocess_class(X):
    X=X.fillna(0)
    ## dummy encode the categorical variable.
    le_x_docURL= pickle.load(open("models/le_x_docURL.pkl","rb"))
    X.document_url_y = le_x_docURL.transform(X.document_url_y)
    sc = pickle.load(open("models/sscaler_class.pkl","rb"))
    X= sc.transform(X)
    return X