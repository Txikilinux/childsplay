# -*- coding: utf-8 -*-
# Copyright (c) 2010 Rene Dohmen <rene@formatics.nl>
# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           mysql.py
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation.  A copy of this license should
# be included in the file GPL-3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import MySQLdb
import sys

"""
mySQL Class Documentation
Just a quick way to do some mysql stuff.
"""

class MySQL:
    def __init__(self,username,password,host,databaseName):
        self.username = username
        self.password = password
        self.host = host
        self.databaseName = databaseName
        self.connectToDB()

    def connectToDB(self):
        try:
            self.dbConn = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, db=self.databaseName)
        except MySQLdb.Error, e:
            print "Error: %s" % (e.args[1]);
            sys.exit()
        try:
            self.cursor = self.dbConn.cursor(MySQLdb.cursors.DictCursor)
        except MySQLdb.Error, e:
            print "Error: %s" % (e.args[1]);

    def query(self, query):
        try:
            queryResultSet = self.cursor.execute(query)
            count = self.cursor.rowcount
            # print "Querry Executed" # testmessage for executed queries
            return MySQLResultSet(queryResultSet, self.cursor)
        except MySQLdb.Error, e:
            print "Error: %s" % (e.args[1]);
#            self.dbConn.close()

    def getInsertID(self):
        return self.dbConn.insert_id()

class MySQLResultSet:

    def __init__(self, queryResultSet, cursor):
        self.queryResultSet = queryResultSet
        self.cursor = cursor
        self.rows = self.fetchResults()

    def __call__(self, rowNumber, fieldName=""):
        if fieldName == "":
            try:
                return self.rows[rowNumber]
            except IndexError, e:
                return "Error: %s" % e;
        else:
            try:
                return self.rows[rowNumber][fieldName]
            except IndexError, e:
                return "Error: %s" % e;

    def countResults(self):
        rows = self.cursor.rowcount
        return rows

    def fetchResults(self):
        rows = self.countResults()
        i = 0
        while i < rows:
            return self.cursor.fetchall()
            i=i+1
    
    def printAllValues(self):
        for row in self.rows:
            print row
    
if __name__ == '__main__':
    myMySQL = MySQL("root","","localhost","")
