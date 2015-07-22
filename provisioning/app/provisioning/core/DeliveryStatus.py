import sqlite3
from .utils import ARTIFACTS_PATH

class DeliveryStatus:
    """
    Delivery status, the build numbers and image
    """
    def __init__(self, productName, productVersion, branch, serverType, dbType):
        self.productName = productName
        self.productVersion = productVersion
        self.branch = branch
        self.serverType = serverType
        self.dbType = dbType

        dbPath = "%s/projects/%s/v%s/%s/var/status/delivery_status.db" % (ARTIFACTS_PATH, self.productName, self.productVersion, self.branch)
        self.db = dbPath

        self._checkTableExists()


    def _connect(self):
        return sqlite3.connect(self.db)


    def _checkTableExists(self):
        sql = """create table if not exists delivery_status (
            id integer primary key autoincrement,
            task text not null default '',
            build_number text not null default '',
            status text not null default '',
            status_detail text not null default '',
            happen text not null default current_timestamp,
            location text not null default '',
            owner text not null default ''
            )"""
        conn = None
        cursor = None
        try:
            conn = self._connect()
            with conn:
                cursor = conn.cursor()
                cursor.execute(sql)
        finally:
            if cursor:  cursor.close()
            if conn:    conn.close()


    def getImageTask(self):
        task = "%s.%s.%s" % ('image', self.serverType, self.dbType)
        return task


    def getBuildTask(self):
        task = 'build'
        return task


    def getAllBuildNumbers(self, task):
        sql = "select distinct build_number from delivery_status where status = 'successful' and task = :task order by build_number asc"

        conn = None
        cursor = None
        try:
            conn = self._connect()
            with conn:
                cursor = conn.cursor()
                cursor.execute(sql, {'task': task})
                builds = cursor.fetchall()
        finally:
            if cursor:  cursor.close()
            if conn:    conn.close()

        return [t[0] for t in builds]


    def getLaterBuildNumbers(self, task, lastBuildNumber = '0'):
        sql = "select distinct build_number from delivery_status where status = 'successful' and task = :task and cast(build_number as integer) > :lastBuildNumber order by build_number asc"

        conn = None
        cursor = None
        try:
            conn = self._connect()
            with conn:
                cursor = conn.cursor()
                cursor.execute(sql, {'task': task, 'lastBuildNumber': int(lastBuildNumber)})
                builds = cursor.fetchall()
        finally:
            if cursor:  cursor.close()
            if conn:    conn.close()

        return [t[0] for t in builds]


    def getLatestBuildNumber(self, task):
        sql = "select max(cast(build_number as integer)) from delivery_status where status = 'successful' and task = :task"

        conn = None
        cursor = None
        try:
            conn = self._connect()
            with conn:
                cursor = conn.cursor()
                cursor.execute(sql, {'task': task})
                build = cursor.fetchone()
        finally:
            if cursor:  cursor.close()
            if conn:    conn.close()

        return build[0] if build and build[0] else "0"


    def addBuildNumber(self, task, buildNumber, status = 'successful', statusDetail = 'successful', happen = None, location = '', owner = ''):
        if not happen:
            import datetime
            happen = datetime.datetime.utcnow()

        sql = """insert into delivery_status(task, build_number, status, status_detail, happen, location, owner) 
                    values(:task, :buildNumber, :status, :statusDetail, :happen, :location, :owner)"""

        conn = None
        cursor = None
        try:
            conn = self._connect()
            with conn:
                cursor = conn.cursor()
                cursor.execute(sql,
                    {'task': task, 'buildNumber': buildNumber, 'status': status, 'statusDetail': statusDetail, 'happen': happen, 'location': location, 'owner': owner})
        finally:
            if cursor:  cursor.close()
            if conn:    conn.close()

