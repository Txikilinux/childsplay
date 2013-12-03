# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPContentTables
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

# This module parses the content xml files and turns them into sqlite tables.
# The xml files must be named like this: content_<name of the quiz>.xml
# For example the content file for the picture quiz, content_picture.xml

import os
import logging

import glob
import zlib
from SPConstants import *

if NoGtk:
    try:
        from pysqlite2 import dbapi2 as sqlite3
    except ImportError:
        import sqlite3
else:
    import sqlite3

try:
    from xml.etree.ElementTree import ElementTree
except ImportError:
    # try the python2.4 way
    from elementtree.ElementTree import ElementTree

class ParserError(Exception):
    pass


def check_tables(dbase):
    """Called by the core when it starts.
    It checks if all the quiz content tables are in sync with the content xml files.
    It checks for differences in the xml files by checking their adler32 checksums
    against the sum in the adler32 sql table.
    When the sums differ the xml is parsed and a new sql table is created.
    When there's a xml file with no table it will be parsed and stored into a sql table.
    """
    # first check the quizcontent dbase and add any missing table.
    logger = logging.getLogger("childsplay.SPContentTables.check_tables")
    logger.debug("Sync quiz content dbase: %s" % dbase)
    
    contentdir = os.path.join(ACTIVITYDATADIR,'CPData','Quizcontent', '*', 'content_*.xml')
    
    con = sqlite3.connect(dbase)
    cursor = con.cursor()
    cursor.execute(''' SELECT name FROM sqlite_master
                            WHERE type='table' 
                            ORDER BY name;
                            ''')
    tl = [tn[0] for tn in cursor.fetchall()]
    contentfiles = glob.glob(contentdir)
    
    path_types = {}
    for f in contentfiles:
        lang = f.rsplit('/',2)[-2]
        tp = os.path.basename(f).split('_')[1][:-4]
        path_types[f] = tp + '_%s' % lang
    
    for t in path_types.values():
        if t not in tl:
            logger.debug("Creating table '%s'" % t)
            # group is named _group as group is a reserved word in sqlite3
            cursor.execute(''' CREATE TABLE %s
                    ( id INTEGER PRIMARY KEY, content_id TEXT, content_type TEXT,
                    difficulty TEXT, question_text TEXT,
                    question_audio TEXT, answer TEXT, answer_audio TEXT,
                    wrong_answer1 TEXT, wrong_answer1_audio TEXT,
                    wrong_answer2 TEXT, wrong_answer2_audio TEXT,
                    wrong_answer3 TEXT, wrong_answer3_audio TEXT,
                    data TEXT, year TEXT, _group TEXT) 
                    ''' % t)
            con.commit()
            for p, pt in path_types.items():
                if pt == t:
                    break
            if parse_xml(p, cursor, t):
                con.commit()
            
    if 'adler32' not in tl:
        logger.debug("Creating table '%s'" % 'adler32')
        cursor.execute(''' CREATE TABLE %s
                    ( id INTEGER PRIMARY KEY, path TEXT, sum INTEGER, type TEXT) 
                    ''' % 'adler32')
    con.commit()
    
    # Now we know we have all the tables we gonna check the checksums
    cursor.execute(''' SELECT * FROM adler32 ''')
    rowlist = cursor.fetchall()
    # check if we have rows
    if not rowlist:
        logger.debug("no rows found in adler32")
        for p in contentfiles:
            logger.debug("creating row for %s" % p)
            data = open(p, 'r').read()
            cs = zlib.adler32(data)
            cursor.execute(''' INSERT INTO adler32 VALUES (NULL,?,?,?)''', (p, cs, path_types[p]))
            logger.debug("created row for %s with adler %s" % (p, cs))
            # As we don't had adler rows we assume we don't have correct content tables as well.
            # remove content table
            logger.debug("replacing table %s" % path_types[p])
            cursor.execute('''DELETE FROM %s''' % path_types[p])
            con.commit()
            # parse content xml and stote it into the new content table
            if parse_xml(p, cursor, path_types[p]):
                con.commit()
        # just to make sure
        close_dbase(con)
        return
    else: 
        # if we have rows check that we have rows for each content file.
        # The actual files present on disk are leading for this.
        tp = [t[1] for t in rowlist]
        for p in contentfiles:
            if p not in tp:
                data = open(p, 'r').read()
                cs = zlib.adler32(data)
                cursor.execute(''' INSERT INTO adler32 VALUES (NULL,?,?,?)''', (p, cs, path_types[p]))
                logger.debug("created row for %s with adler %s" % (p, cs))
    # renew rowlist
    cursor.execute(''' SELECT * FROM adler32 ''')
    rowlist = cursor.fetchall()
    for row in rowlist:
        p = row[1]
        try:
            data = open(p, 'r').read()
        except IOError:
            logger.warning("Quizcontent file not found: %s" % p)
            logger.warning("replacing table %s" % p)
            cursor.execute(''' DELETE FROM adler32 WHERE id=? ''', (row[0], ))
            lang = p.rsplit('/',2)[-2]
            tp = os.path.basename(p).split('_')[1][:-4]
            ptype = tp + '_%s' % lang
            cursor.execute('''DELETE FROM %s''' % ptype)
            con.commit()
            continue
        cs = zlib.adler32(data)
        logger.debug("checking data from %s with adler %s" % (p, cs))
        #print type(cs), cs, type(row[2]), row[2]
        if cs != row[2]:
            logger.debug("checksum differ for %s" % p)
            # first remove the row from adler32 table
            cursor.execute(''' DELETE FROM adler32 WHERE id=? ''', (row[0], ))
            # add a new one with correct sum
            logger.debug("Added new row for %s" % row[1])
            cursor.execute(''' INSERT INTO adler32 VALUES (NULL,?,?,?)''', (p, cs, path_types[p]))
            con.commit()
            # remove content table
            logger.debug("replacing table %s" % path_types[p])
            cursor.execute('''DELETE FROM %s''' % path_types[p])
            con.commit()
            # and parse content xml and stote it into the new content table
            if parse_xml(p, cursor, path_types[p]):
                con.commit()
    # just to make sure
    close_dbase(con)
    
def close_dbase(con):
    logger = logging.getLogger("childsplay.SPContentTables.close_dbase")
    logger.debug("Commiting transactions and closing dbase.")
    con.commit()    
    con.close()    
    
def parse_xml(xml, cursor, tname):
    """Parses the whole xml tree into a hash with lists. Each list contains hashes
    with the elelements from a 'question' element.
    When year is set only the entries that have a year element and whos value
    is between 'year' and 'year'+9 is put into the hash.
    This is used by the history activity."""  
    logger = logging.getLogger("childsplay.SPContentTables.parse_xml")
    logger.debug("Starting to parse: %s" % xml)
    
    #     xml file:
    #    <?xml version="1.0" encoding="utf-8"?>
    #    <questions>
    #         <question id="2" type="text">
    #                <difficulty>1</difficulty>
    #                <question_text audio="">Wat is een Vlaamse reus?</question_text>
    #                <answer audio="">Een konijnensoort</answer>
    #                <data/><misc></misc>
    #                <wrong_answer1 audio="">Een trekpaard</wrong_answer1>
    #                <wrong_answer2 audio="">De bijnaam voor een opstandeling</wrong_
    #                                           answer2>
    #                <wrong_answer3 audio="">Een grote Belg</wrong_answer3>
    #        </question>
    #       ..... 
    tree = ElementTree()
    tree.parse(xml)
    xml = {}
    # here we start the parsing, the check if we have all the content is done
    # in get_exercise.
    # we don't do it here because of speed considerations.
    index = 0
    questions = tree.findall('question')
    logger.debug("found %s questions in total" % len(questions))

    for q in questions:
        hash = {}
        try:
            hash['content_id'] = q.get('id')
            hash['content_type'] = q.get('type')
            
            e = q.find('difficulty')
            hash['difficulty'] = e.text
            
            e = q.find('data')
            hash['data'] = e.text
            
            e = q.find('group')
            hash['_group'] = e.text
            
            e = q.find('question_text')
            hash['question_text'] = e.text
            hash['question_audio'] = e.get('audio')
            
            e = q.find('answer')
            hash['answer'] = e.text
            hash['answer_audio'] = e.get('audio')
            
            e = q.find('wrong_answer1')
            hash['wrong_answer1'] = e.text
            hash['wrong_answer1_audio']  = e.get('audio')
            e = q.find('wrong_answer2')
            hash['wrong_answer2'] = e.text
            hash['wrong_answer2_audio'] = e.get('audio')
            e = q.find('wrong_answer3')
            hash['wrong_answer3'] = e.text
            hash['wrong_answer3_audio'] = e.get('audio')
            try:
                # year is optional
                e = q.find('year')
                hash['year'] = e.text
            except:
                hash['year'] = ''           
        except AttributeError, info:
            logger.error("The content.xml is badly formed, missing element(s):%s,%s" % (info, e))
            logger.error("question '%s' will be removed from the collection" % q.get('id'))
        else:
            index += 1
            cursor.execute(''' INSERT INTO %s VALUES (\
                            NULL, :content_id, :content_type, :difficulty,\
                            :question_text, :question_audio, :answer,\
                            :answer_audio, :wrong_answer1,\
                            :wrong_answer1_audio, :wrong_answer2,\
                            :wrong_answer2_audio, :wrong_answer3,\
                            :wrong_answer3_audio, :data, :year, :_group\
                            ) ''' % tname , hash)
    logger.debug("Done parsing %s questions" % index)
    return True
    
if __name__ == '__main__':
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
    
    lang = 'nl'
    dbase = os.path.join(HOMEDIR, 'quizcontent.db')
    contentdir = os.path.join(ACTIVITYDATADIR,'CPData','Quizcontent', lang, 'content_*.xml')
    check_tables(dbase, contentdir, lang)
      
