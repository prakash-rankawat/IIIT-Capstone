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
