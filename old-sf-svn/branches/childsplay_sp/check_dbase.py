# quick and very dirty script to handle sql dbase used in schoolsplay
import sys
import pprint,csv
from sqlalchemy import *
from SPConstants import DBASEPATH

if len(sys.argv) > 1:
    DBASEPATH = sys.argv[1]
def view():
    prow = "\n-------------------------------------------------------------------------"
    print "Contents of dbase: %s" % DBASEPATH
    
    metadata = BoundMetaData('sqlite:///%s' % DBASEPATH)
    utable = Table('users', metadata, autoload=True)
    select = utable.select()
    rows = select.execute()
    print "table: users"
    print "%12s,%12s,%12s,%12s,%12s,%12s,%12s,%12s,%12s" % tuple(utable.c.keys())
    for row in rows.fetchall():
        print "%12d,%12s,%12s,%12s,%12s,%12s,%12s,%12s,%12s" % tuple(row.values())
    print prow
    for t in ['memory','memorynumbers','memorylower','memoryupper','fishtank',\
        'CP_find_char_sound','soundmemory','puzzle','options','activity_options']:
        mtable = Table(t, metadata, autoload=True)
        select = mtable.select()
        rows = select.execute()
        print "table: %s" % t
        print mtable.c.keys()
        for row in rows.fetchall():
            print row.values()
        print prow
    # used for testing
##    mtable = Table('xxxtesttablexxx', metadata, autoload=True)
##    select = mtable.select()
##    rows = select.execute()
##    print "Table: xxxtesttablexxx"
##    data = [tuple(row.values()) for row in rows.fetchall()]
##    print data
    
##    print "joining users and fishtank"
##    mtable = Table('fishtank', metadata, autoload=True)
##    r = utable.join(mtable).select().execute()
##    print [row for row in r]
##    

def export():
    metadata = BoundMetaData('sqlite:///%s' % DBASEPATH)
    writer = csv.writer(open('sp_tables', 'wb'), dialect=csv.excel)
    for t in ['memory','memorynumbers','memorylower','memoryupper','fishtank',\
        'CP_find_char_sound','options','activity_options']:
        writer.writerow(('%s' % t,))
        mtable = Table(t, metadata, autoload=True)
        select = mtable.select()
        rows = select.execute()
        for row in rows.fetchall():
            writer.writerow(row.values())
    
if __name__ == '__main__':
    c = raw_input("What do you want to do? View the dbase, Export to csv [v/e] ")
    if c.lower() == 'v':
        view()
    elif c.lower() == 'e':
        export()
        
    
    
    

