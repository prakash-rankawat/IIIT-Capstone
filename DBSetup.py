from utils.dbutils import database
from dbconfig import *

dbutil=database(host_name, username, password, auth_plugin, db, table)

dbutil.reset_db()
