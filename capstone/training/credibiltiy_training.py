from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score,mean_absolute_error
import os
import pickle
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
df_raw = pd.DataFrame(data=records,columns=columns)

def regression_retrain():
    # removing the obvious column not going to used in the model
    cols_not_required = ['Serial_number', 'document_id', 'URL', 'category', 'ad_count', 'ad_max_size',
                         'css_definitions', 'page_rank',
                         'bitly_clicks', 'bitly_referrers', 'tweets', 'delicious_bookmarks',
                         'fb_clicks', 'fb_comments', 'fb_likes', 'fb_shares', 'fb_total',
                         'alexa_linksin', 'num_ne', 'sum_ne', 'X1', 'X2', 'X3', 'X4', 'X5', 'X9', 'Total',
                         'Leik', 'Eijk', 'Tastle', 'Leik_3_4_6', 'correction', 'resp_HNC', 'Controversial',
                         'troia_label']
    # cols_not_required = ['document_id','URL']
    # make a copy of the raw data
    df_main = df_raw.copy()
    df_main.drop(cols_not_required, axis=1, inplace=True)

    # getting on the popular domain as in the list below
    array = ['com', 'org', 'gov', 'edu', 'net', 'uk', 'au', 'ca', 'in']
    df2 = df_main.loc[df_main['document_url_y'].isin(array)]

    # Dropping the missing values.
    df2 = df2.fillna(0)

    # Using label encoder to convert document_url_y into dummy
    le = preprocessing.LabelEncoder()
    df2.document_url_y = le.fit_transform(df2.document_url_y)
    df1 = df2

    # defining x and y
    y = df1["Credibility_rating"]
    X = df1.drop("Credibility_rating", axis=1)

    # Splitting the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

    # performing preprocessing part
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    # reading previous metrics

    path_of_file = './models/regression_performance.json'
    # checking if size of file is 0
    if os.path.getsize(path_of_file) == 0:
        return "File is empty, train the inital model"
    else:
        # loading the json
        with open(path_of_file, 'r') as f:
            previous_perf = json.load(f)
            if (len(previous_perf) != 0):
                previous_r2_score = previous_perf['test_r2_score']
            else:
                return "train the inital model Or Check the Json"
        f.close()

    # Random Forest model
    rf = RandomForestRegressor()
    rf_model = rf.fit(X_train, y_train)
    # y_train_pred = rf_model.predict(X_train)
    y_test_pred = rf_model.predict(X_test)

    # train r2_score = r2_score(y_train,y_train_pred)
    test_r2_score = r2_score(y_test, y_test_pred)
    ac_score = 1 - mean_absolute_error(y_test, y_test_pred)
    perform_metrics = {'test_r2_score': test_r2_score}

    FI_df = pd.DataFrame({'Features': X.columns, 'Importance': rf_model.feature_importances_})
    FI_df = FI_df.sort_values(by='Importance', ascending=False).head(100)
    # compare old and new accuracy and then pickle the new model to use by the application,
    # if retrained model gives better performance
    if test_r2_score > previous_r2_score:
        plt.figure(figsize=(15, 10), dpi=100)
        sns.barplot(x=FI_df[:10].Importance, y=FI_df[:10].Features, orient='h').set_title('Feature Importance')
        plt.savefig("./static/top10features.png")

        with open("./models/le.pkl", 'wb') as file:
            pickle.dump(le, file)
        file.close()
        with open("./models/standardscaler.pkl", 'wb') as file:
            pickle.dump(sc, file)
        file.close()
        with open("./models/rf_credibility_model.pkl", 'wb') as file:
            pickle.dump(rf_model, file)
        file.close()
        # storing the data in JSON format
        current_perf = {"test_r2_score": test_r2_score, "accuracy_score": ac_score}
        # saving the upgraded accuracy along with other metrics and old values in Json
        with open(path_of_file, "w") as outfile:
            json.dump(current_perf, outfile)
        outfile.close()
        return current_perf

    return previous_perf