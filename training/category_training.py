import pickle
import json
import os
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils.dbutils import database

host_name = "localhost"
username = 'root'
password = 'root'  # dba password
db = "capstone"
auth_plugin = 'mysql_native_password'
table = "web_raw_data"


def classification_retrain():
    # removing the obvious column not going to used in the model
    db_util = database(host_name, username, password, auth_plugin, db, table)
    cols_required = ['alexa_rank', 'commas', 'dots', 'exclamations', 'questions',
                     'spelling_errors', 'text_complexity', 'smog', 'JJ', 'NN', 'DT', 'VB',
                     'RB', 'document_url_y', 'category']
    # make a copy of the raw data
    df = db_util.query_cols(None, cols_required)

    # getting on the popular domain as in the list below
    array = ['com', 'org', 'gov', 'edu', 'net', 'uk', 'au', 'ca', 'in']
    df2 = df.loc[df['document_url_y'].isin(array)]

    # filling all null category as 'unknown'
    print(df2.category.mode()[0])
    df2["category"].fillna(df2.category.mode()[0], inplace=True)

    # Dropping the missing values.
    df2 = df2.fillna(0)

    # Categorical features has to be converted into integer values for the model to process(one hot encoding).
    y_data = df2["category"]
    X_data = df2.drop(['category'], axis=1)

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

    FI_df = pd.DataFrame({'Features': X_data.columns, 'Importance': rf_model.feature_importances_})
    FI_df = FI_df.sort_values(by='Importance', ascending=False).head(100)

    # compare old and new accuracy and then pickle the new model to use by the application,
    # if retrained model gives better performance
    if accuracy > previous_accuracy:
        # plot feature importance
        plt.figure(figsize=(15, 10), dpi=100)
        sns.barplot(x=FI_df[:10].Importance, y=FI_df[:10].Features, orient='h').set_title('Feature Importance')
        plt.savefig("./static/top10featuresclass.png")

        with open("./models/le_x_docURL.pkl", 'wb') as file:
            pickle.dump(le_x_docURL, file)
        file.close()
        with open("./models/le_y.pkl", 'wb') as file:
            pickle.dump(le_y, file)
        file.close()
        with open("./models/sscaler_class.pkl", 'wb') as file:
            pickle.dump(sc, file)
        file.close()
        with open("./models/category_model.pkl", 'wb') as file:
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
