from asyncio.windows_events import NULL
from cmath import nan
from pickletools import long1
from unicodedata import decimal
import mysql.connector as MySQL
from mysql.connector import errorcode
import os
from numpy import float64, int64, number
import numpy as np
import pandas as pd
import random
import time

host_name = "localhost"
username = 'root'
password = 'root' #dba password
db = "webtrust"
auth_plugin = 'mysql_native_password'
conn = None

def connect_to_db(host_name, username, password, auth_plugin):
    try:
        conn = MySQL.connect(host=host_name, user = username, password = password, database = db, auth_plugin=auth_plugin)
    except MySQL.errorcode as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print('Connected!')
        return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except MySQL.errorcode as err:
        print(err)

def create_and_setup_db():
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
    
    conn = connect_to_db(host_name, username, password, auth_plugin)
    if conn is not None: 
        create_table(conn,create_table_command2)
        # Commit all DB changes until here
        conn.commit()
        return " Table created successfully"
    else:
        return "Failure"

def import_file(filepath):
    conn = connect_to_db(host_name, username, password, auth_plugin)
    df_raw = pd.read_csv(filepath,index_col=0)
    
    cur = conn.cursor()
    sql_query = "SELECT ifnull(MAX(Serial_number),0) AS MAX_ID FROM WEB_RAW_DATA"
    cur.execute(sql_query)
    rows = cur.fetchall()
    li_max=rows[0][0]
    if li_max ==0:
        li_serial_num = 1
    else:
        li_serial_num = li_max+ 1

    for row in range(len(df_raw)):
        li_doc_id = int(df_raw.loc[row,"document_id"])
        ls_url = str(df_raw.loc[row,"URL"])
        ld_credibility_rating = float64(df_raw.loc[row,"Credibility_rating"])
        if np.isnan(df_raw.loc[row,"ad_count"]):
            ld_ad_count = None
        else:
            ld_ad_count = float64(df_raw.loc[row,"ad_count"])
        
        if np.isnan(df_raw.loc[row,"ad_max_size"]):
            ld_ad_max_size = None
        else:
            ld_ad_max_size = float64(df_raw.loc[row,"ad_max_size"])
        
        if np.isnan(df_raw.loc[row,"css_definitions"]):
            ld_css_definitions = None
        else:
            ld_css_definitions = float64(df_raw.loc[row,"css_definitions"])
        
        if np.isnan(df_raw.loc[row,"page_rank"]):
            ld_page_rank = None
        else:
            ld_page_rank = float64(df_raw.loc[row,"page_rank"])
        
        
        
        sql_query = """INSERT INTO WEB_RAW_DATA (Serial_number,document_id,URL,Credibility_rating, ad_count,ad_max_size,css_definitions,page_rank) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(sql_query,(li_serial_num, li_doc_id, ls_url, ld_credibility_rating,ld_ad_count,ld_ad_max_size,ld_css_definitions,ld_page_rank))
        
        li_serial_num = li_serial_num +1
    conn.commit()
    cur.close()
    conn.close()
    return {"status":200,"Info":"Web data added to DB sucessfully"}


if __name__ =="__main__":
    print(create_and_setup_db())
    # load the web trust csv file database
    print(import_file("./config/web_trust.csv"))
    