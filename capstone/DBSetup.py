from utils.dbutils import database

host_name = "localhost"
username = 'root'
password = 'root' #dba password
db = "capstone"
auth_plugin = 'mysql_native_password'
table="web_raw_data"


dbutil=database(host_name, username, password, auth_plugin, db, table)

dbutil.reset_db()
