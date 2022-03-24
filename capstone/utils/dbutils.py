import pandas as pd
import mysql.connector as MySQL
from numpy import float64, int64, number
import numpy as np

class database:
    def __init__(self, host_name, username, password, auth_plugin, db, table):
        self.host_name = host_name
        self.username = username
        self.password = password
        self.auth_plugin = auth_plugin
        self.db = db
        self.table = table

    def connect_to_db(self):
        try:
            conn = MySQL.connect(host=self.host_name, user=self.username, password=self.password,
                                 auth_plugin=self.auth_plugin)
        except Exception as err:
            print(err)
        else:
            print('Connected!')
            return conn

    def execute_query(self,conn, sql_query):
        c = conn.cursor()
        c.execute(sql_query)
        return conn, c

    def last_sr_no(self):
        conn=self.connect_to_db()
        conn, cursor = self.execute_query(conn,"select max(serial_number) from {}.{}".format(self.db, self.table))
        srno = cursor.fetchone()
        conn.close()
        return srno[0]

    def insert_row(self, df):
        new_srno = self.last_sr_no() + 1
        cols = "`,`".join([str(i) for i in df.columns.tolist()])
        row = tuple(df.loc[0])
        sql = "INSERT INTO {0}.{1} (`serial_number`,`{2}`) VALUES ({3},{4})".format(self.db, self.table, cols, new_srno,
                                                                                    str(row)[1:-1])
        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return new_srno

    def updateseqcolumn(self, seq_id, column_name, value):
        sql = "UPDATE {0}.{1} SET {2}=\"{3}\" WHERE SERIAL_NUMBER={4}".format(self.db, self.table, column_name, value,
                                                                              seq_id)
        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return seq_id

    def delete_url(self, url):
        sql = "DELETE FROM {0}.{1} WHERE URL=\"{2}\"".format(self.db, self.table, url)
        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def query_cols(self, seq_id, col_list):
        sql = "select {0} from {1}.{2}".format(", ".join(col_list), self.db, self.table)
        if not seq_id is None:
            sql = "select {0} from {1}.{2} where serial_number={3}".format(", ".join(col_list), self.db, self.table, seq_id)
        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return pd.DataFrame(result, columns=col_list)

    def create_and_setup_db(self):
        create_table_command2 = ("""CREATE TABLE IF NOT EXISTS WEB_RAW_DATA (
                                Serial_number bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                                document_id bigint,
                                URL varchar(255),
                                Credibility_rating decimal(30,15),
                                ad_count decimal(30,15),
                                ad_max_size decimal(30,15),
                                css_definitions decimal(30,15),
                                page_rank decimal(30,15),
                                bitly_clicks decimal(30,15),
                                bitly_referrers decimal(30,15),
                                tweets decimal(30,15),
                                delicious_bookmarks decimal(30,15),
                                fb_clicks decimal(30,15),
                                fb_comments decimal(30,15),
                                fb_likes decimal(30,15),
                                fb_shares decimal(30,15),
                                fb_total decimal(30,15),
                                alexa_linksin decimal(30,15),
                                alexa_rank decimal(30,15),
                                commas decimal(30,15),
                                dots decimal(30,15),
                                exclamations decimal(30,15),
                                questions decimal(30,15),
                                spelling_errors decimal(30,15),
                                text_complexity decimal(30,15),
                                smog decimal(30,15),
                                category varchar(255),
                                JJ decimal(30,15),
                                NN decimal(30,15),
                                DT decimal(30,15),
                                VB decimal(30,15),
                                RB decimal(30,15),
                                num_ne decimal(30,15),
                                sum_ne decimal(30,15),
                                document_url_y varchar(255),
                                X1 decimal(30,15),
                                X2 decimal(30,15),
                                X3 decimal(30,15),
                                X4 decimal(30,15),
                                X5 decimal(30,15),
                                X9 decimal(30,15),
                                Total decimal(30,15),
                                Leik decimal(30,15),
                                Eijk decimal(30,15),
                                Tastle decimal(30,15),
                                Leik_3_4_6 decimal(30,15),
                                correction decimal(30,15),
                                resp_HNC varchar(10),
                                Controversial varchar(255),
                                troia_label decimal(30,15)
                                )""")

        create_db = ("CREATE DATABASE IF NOT EXISTS CAPSTONE")
        use_db = ("USE CAPSTONE")
        conn = self.connect_to_db()
        if conn is not None:
            self.execute_query(conn, create_db)
            self.execute_query(conn, use_db)
            self.execute_query(conn, create_table_command2)
            # Commit all DB changes until here
            conn.commit()
            conn.close()
            return " Table created successfully"
        else:
            return "Failure"

    def import_file(self, filepath):
        conn = self.connect_to_db()
        df_raw = pd.read_csv(filepath, index_col=0)

        cur = conn.cursor()
        sql_query = "SELECT ifnull(MAX(Serial_number),0) AS MAX_ID FROM CAPSTONE.WEB_RAW_DATA"
        cur.execute(sql_query)
        rows = cur.fetchall()
        li_max = rows[0][0]
        if li_max == 0:
            li_serial_num = 1
        else:
            li_serial_num = li_max + 1

        for row in range(len(df_raw)):
            li_doc_id = int(df_raw.loc[row, "document_id"])
            ls_url = str(df_raw.loc[row, "URL"])
            ld_credibility_rating = float64(df_raw.loc[row, "Credibility_rating"])
            if np.isnan(df_raw.loc[row, "ad_count"]):
                ld_ad_count = None
            else:
                ld_ad_count = float64(df_raw.loc[row, "ad_count"])

            if np.isnan(df_raw.loc[row, "ad_max_size"]):
                ld_ad_max_size = None
            else:
                ld_ad_max_size = float64(df_raw.loc[row, "ad_max_size"])

            if np.isnan(df_raw.loc[row, "css_definitions"]):
                ld_css_definitions = None
            else:
                ld_css_definitions = float64(df_raw.loc[row, "css_definitions"])

            if np.isnan(df_raw.loc[row, "page_rank"]):
                ld_page_rank = None
            else:
                ld_page_rank = float64(df_raw.loc[row, "page_rank"])

            if np.isnan(df_raw.loc[row, "bitly_clicks"]):
                ld_bitly_clicks = None
            else:
                ld_bitly_clicks = float64(df_raw.loc[row, "bitly_clicks"])

            if np.isnan(df_raw.loc[row, "bitly_referrers"]):
                ld_bitly_referrers = None
            else:
                ld_bitly_referrers = float64(df_raw.loc[row, "bitly_referrers"])

            if np.isnan(df_raw.loc[row, "tweets"]):
                ld_tweets = None
            else:
                ld_tweets = float64(df_raw.loc[row, "tweets"])

            if np.isnan(df_raw.loc[row, "delicious_bookmarks"]):
                ld_delicious_bookmarks = None
            else:
                ld_delicious_bookmarks = float64(df_raw.loc[row, "delicious_bookmarks"])

            if np.isnan(df_raw.loc[row, "fb_clicks"]):
                ld_fb_clicks = None
            else:
                ld_fb_clicks = float64(df_raw.loc[row, "fb_clicks"])

            if np.isnan(df_raw.loc[row, "fb_comments"]):
                ld_fb_comments = None
            else:
                ld_fb_comments = float64(df_raw.loc[row, "fb_comments"])

            if np.isnan(df_raw.loc[row, "fb_likes"]):
                ld_fb_likes = None
            else:
                ld_fb_likes = float64(df_raw.loc[row, "fb_likes"])

            if np.isnan(df_raw.loc[row, "fb_shares"]):
                ld_fb_shares = None
            else:
                ld_fb_shares = float64(df_raw.loc[row, "fb_shares"])

            if np.isnan(df_raw.loc[row, "fb_total"]):
                ld_fb_total = None
            else:
                ld_fb_total = float64(df_raw.loc[row, "fb_total"])

            if np.isnan(df_raw.loc[row, "alexa_linksin"]):
                ld_alexa_linksin = None
            else:
                ld_alexa_linksin = float64(df_raw.loc[row, "alexa_linksin"])

            if np.isnan(df_raw.loc[row, "alexa_rank"]):
                ld_alexa_rank = None
            else:
                ld_alexa_rank = float64(df_raw.loc[row, "alexa_rank"])

            if np.isnan(df_raw.loc[row, "commas"]):
                ld_commas = None
            else:
                ld_commas = float64(df_raw.loc[row, "commas"])

            if np.isnan(df_raw.loc[row, "dots"]):
                ld_dots = None
            else:
                ld_dots = float64(df_raw.loc[row, "dots"])

            if np.isnan(df_raw.loc[row, "exclamations"]):
                ld_exclamations = None
            else:
                ld_exclamations = float64(df_raw.loc[row, "exclamations"])

            if np.isnan(df_raw.loc[row, "questions"]):
                ld_questions = None
            else:
                ld_questions = float64(df_raw.loc[row, "questions"])

            if np.isnan(df_raw.loc[row, "spelling_errors"]):
                ld_spelling_errors = None
            else:
                ld_spelling_errors = float64(df_raw.loc[row, "spelling_errors"])

            if np.isnan(df_raw.loc[row, "text_complexity"]):
                ld_text_complexity = None
            else:
                ld_text_complexity = float64(df_raw.loc[row, "text_complexity"])

            if np.isnan(df_raw.loc[row, "smog"]):
                ld_smog = None
            else:
                ld_smog = float64(df_raw.loc[row, "smog"])

            if pd.isnull(df_raw.loc[row, "category"]):
                ls_category = None
            else:
                ls_category = str(df_raw.loc[row, "category"])

            if np.isnan(df_raw.loc[row, "JJ"]):
                ld_JJ = None
            else:
                ld_JJ = float64(df_raw.loc[row, "JJ"])

            if np.isnan(df_raw.loc[row, "NN"]):
                ld_NN = None
            else:
                ld_NN = float64(df_raw.loc[row, "NN"])

            if np.isnan(df_raw.loc[row, "DT"]):
                ld_DT = None
            else:
                ld_DT = float64(df_raw.loc[row, "DT"])

            if np.isnan(df_raw.loc[row, "VB"]):
                ld_VB = None
            else:
                ld_VB = float64(df_raw.loc[row, "VB"])

            if np.isnan(df_raw.loc[row, "RB"]):
                ld_RB = None
            else:
                ld_RB = float64(df_raw.loc[row, "RB"])

            if np.isnan(df_raw.loc[row, "num_ne"]):
                ld_num_ne = None
            else:
                ld_num_ne = float64(df_raw.loc[row, "num_ne"])

            if np.isnan(df_raw.loc[row, "sum_ne"]):
                ld_sum_ne = None
            else:
                ld_sum_ne = float64(df_raw.loc[row, "sum_ne"])

            if pd.isnull(df_raw.loc[row, "document_url_y"]):
                ls_document_url_y = None
            else:
                ls_document_url_y = str(df_raw.loc[row, "document_url_y"])

            if np.isnan(df_raw.loc[row, "X1"]):
                ld_X1 = None
            else:
                ld_X1 = float64(df_raw.loc[row, "X1"])

            if np.isnan(df_raw.loc[row, "X2"]):
                ld_X2 = None
            else:
                ld_X2 = float64(df_raw.loc[row, "X2"])

            if np.isnan(df_raw.loc[row, "X3"]):
                ld_X3 = None
            else:
                ld_X3 = float64(df_raw.loc[row, "X3"])

            if np.isnan(df_raw.loc[row, "X4"]):
                ld_X4 = None
            else:
                ld_X4 = float64(df_raw.loc[row, "X4"])

            if np.isnan(df_raw.loc[row, "X5"]):
                ld_X5 = None
            else:
                ld_X5 = float64(df_raw.loc[row, "X5"])

            if np.isnan(df_raw.loc[row, "X9"]):
                ld_X9 = None
            else:
                ld_X9 = float64(df_raw.loc[row, "X9"])

            if np.isnan(df_raw.loc[row, "Total"]):
                ld_Total = None
            else:
                ld_Total = float64(df_raw.loc[row, "Total"])

            if np.isnan(df_raw.loc[row, "Leik"]):
                ld_Leik = None
            else:
                ld_Leik = float64(df_raw.loc[row, "Leik"])

            if np.isnan(df_raw.loc[row, "Eijk"]):
                ld_Eijk = None
            else:
                ld_Eijk = float64(df_raw.loc[row, "Eijk"])

            if np.isnan(df_raw.loc[row, "Tastle"]):
                ld_Tastle = None
            else:
                ld_Tastle = float64(df_raw.loc[row, "Tastle"])

            if np.isnan(df_raw.loc[row, "Leik 3 4 6"]):
                ld_Leik_3_4_6 = None
            else:
                ld_Leik_3_4_6 = float64(df_raw.loc[row, "Leik 3 4 6"])

            if np.isnan(df_raw.loc[row, "correction"]):
                ld_correction = None
            else:
                ld_correction = float64(df_raw.loc[row, "correction"])

            if pd.isnull(df_raw.loc[row, "resp_HNC"]):
                ls_resp_HNC = None
            else:
                ls_resp_HNC = str(df_raw.loc[row, "resp_HNC"])

            if pd.isnull(df_raw.loc[row, "Controversial"]):
                ls_Controversial = None
            else:
                ls_Controversial = str(df_raw.loc[row, "Controversial"])

            if np.isnan(df_raw.loc[row, "troia_label"]):
                ld_troia_label = None
            else:
                ld_troia_label = float64(df_raw.loc[row, "troia_label"])

            sql_query = """INSERT INTO CAPSTONE.WEB_RAW_DATA (Serial_number,document_id,URL,Credibility_rating, ad_count,ad_max_size,css_definitions,page_rank,bitly_clicks,bitly_referrers,tweets,delicious_bookmarks,fb_clicks,fb_comments,fb_likes,fb_shares,fb_total,alexa_linksin,alexa_rank,commas,dots,exclamations,questions,spelling_errors,text_complexity,smog,category,JJ,NN,DT,VB,RB,num_ne,sum_ne,document_url_y,X1,X2,X3,X4,X5,X9,Total,Leik,Eijk,Tastle,Leik_3_4_6,correction,resp_HNC,Controversial,troia_label) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(sql_query, (
            li_serial_num, li_doc_id, ls_url, ld_credibility_rating, ld_ad_count, ld_ad_max_size, ld_css_definitions,
            ld_page_rank, ld_bitly_clicks, ld_bitly_referrers, ld_tweets, ld_delicious_bookmarks, ld_fb_clicks,
            ld_fb_comments, ld_fb_likes, ld_fb_shares, ld_fb_total, ld_alexa_linksin, ld_alexa_rank, ld_commas, ld_dots,
            ld_exclamations, ld_questions, ld_spelling_errors, ld_text_complexity, ld_smog, ls_category, ld_JJ, ld_NN,
            ld_DT, ld_VB, ld_RB, ld_num_ne, ld_sum_ne, ls_document_url_y, ld_X1, ld_X2, ld_X3, ld_X4, ld_X5, ld_X9,
            ld_Total, ld_Leik, ld_Eijk, ld_Tastle, ld_Leik_3_4_6, ld_correction, ls_resp_HNC, ls_Controversial,
            ld_troia_label))

            li_serial_num = li_serial_num + 1
        conn.commit()
        cur.close()
        conn.close()
        return {"status": 200, "Info": "Web data added to DB sucessfully"}

    def reset_db(self):
        sql="DROP TABLE IF EXISTS {0}.{1}".format(self.db,self.table)
        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.close()
        self.create_and_setup_db()
        self.import_file("data/web_trust.csv")