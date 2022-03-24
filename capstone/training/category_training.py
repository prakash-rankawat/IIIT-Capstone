import pickle
import json
import os
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score
import pandas as pd
import pymysql

connection = pymysql.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="capstone"
)
# preparing a cursor object
cursorObject = connection.cursor()

query = "SELECT Serial_number,document_id,URL,Credibility_rating, ad_count,ad_max_size,css_definitions,page_rank,bitly_clicks,bitly_referrers,tweets,delicious_bookmarks,fb_clicks,fb_comments,fb_likes,fb_shares,fb_total,alexa_linksin,alexa_rank,commas,dots,exclamations,questions,spelling_errors,text_complexity,smog,category,JJ,NN,DT,VB,RB,num_ne,sum_ne,document_url_y,X1,X2,X3,X4,X5,X9,Total,Leik,Eijk,Tastle,Leik_3_4_6,correction,resp_HNC,Controversial,troia_label FROM capstone.WEB_RAW_DATA"
cursorObject.execute(query)
columns = [col[0] for col in cursorObject.description]
records = cursorObject.fetchall()

# disconnecting from server
connection.close()
df_raw = pd.DataFrame(data=records, columns=columns)


def classification_retrain():
    # removing the obvious column not going to used in the model
    cols_not_required = ['Serial_number', 'document_id', 'URL', 'Credibility_rating']

    # make a copy of the raw data
    df_main = df_raw.copy()
    df_main.drop(cols_not_required, axis=1, inplace=True)

    # getting on the popular domain as in the list below
    array = ['com', 'org', 'gov', 'edu', 'net', 'uk', 'au', 'ca', 'in']
    df2 = df_main.loc[df_main['document_url_y'].isin(array)]

    # filling all null category as 'unknown'
    df2["category"].fillna("Unknown", inplace=True)

    # Dropping the missing values.
    df2 = df2.fillna(0)

    # Categorical features has to be converted into integer values for the model to process(one hot encoding).
    y_data = df2["category"]
    X_data = df2.drop(['category', 'ad_count', 'ad_max_size', 'css_definitions', 'page_rank',
                       'bitly_clicks', 'bitly_referrers', 'tweets', 'delicious_bookmarks',
                       'fb_clicks', 'fb_comments', 'fb_likes', 'fb_shares', 'fb_total',
                       'alexa_linksin', 'num_ne', 'sum_ne', 'X1', 'X2', 'X3', 'X4', 'X5', 'X9', 'Total',
                       'Leik', 'Eijk', 'Tastle', 'Leik_3_4_6', 'correction', 'resp_HNC', 'Controversial',
                       'troia_label'], axis=1)

    # select categorical features
    cat_x = X_data.select_dtypes(include=['object']).columns

    le_x_docURL = preprocessing.LabelEncoder()
    X_data.document_url_y = le_x_docURL.fit_transform(X_data.document_url_y)

    # label encode the target variable
    le_y = preprocessing.LabelEncoder()
    y = le_y.fit_transform(y_data)

    # Splitting the dataset
    X_train, X_test, y_train, y_test = train_test_split(X_data, y, test_size=0.3, random_state=0)

    # performing preprocessing part
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    # reading previous metrics

    path_of_file = './models/classification_performance.json'
    # checking if size of file is 0
    if os.path.getsize(path_of_file) == 0:
        return "File is empty, train the inital model"
    else:
        # loading the json
        with open(path_of_file, 'r') as f:
            previous_perf = json.load(f)
            if (len(previous_perf) != 0):
                previous_accuracy = previous_perf['Accuracy']
            else:
                return "train the inital model Or Check the Json"
        f.close()

    # Random Forest model
    rf = RandomForestClassifier()
    rf_model = rf.fit(X_train, y_train)
    # y_train_pred = rf_model.predict(X_train)
    y_test_pred = rf_model.predict(X_test)

    #     precision = precision_score(y_test,y_test_pred, average='weighted')
    #     recall = recall_score(y_test,y_test_pred, average='weighted')
    accuracy = accuracy_score(y_test, y_test_pred)
    f1 = f1_score(y_test, y_test_pred, average='weighted')
    perform_metrics = {"Accuracy": accuracy, "F1-score": f1}

    # compare old and new accuracy and then pickle the new model to use by the application,
    # if retrained model gives better performance
    if accuracy > previous_accuracy:
        with open("../models/le_x_docURL.pkl", 'wb') as file:
            pickle.dump(le_x_docURL, file)
        file.close()
        with open("../models/le_y.pkl", 'wb') as file:
            pickle.dump(le_y, file)
        file.close()
        with open("../models/sscaler_class.pkl", 'wb') as file:
            pickle.dump(sc, file)
        file.close()
        with open("../models/category_model.pkl", 'wb') as file:
            pickle.dump(rf_model, file)
        file.close()
        # storing the data in JSON format
        current_perf = {"Accuracy": accuracy, "F1-Score": f1}
        # saving the upgraded accuracy along with other metrics and old values in Json
        with open(path_of_file, "w") as outfile:
            json.dump(current_perf, outfile)
        outfile.close()
        return current_perf

    return previous_perf
