import MySQLdb

import sys, os, glob, shutil
if len(sys.argv) < 2:
    print "Usage: check_assets_puzzle.py <path to assets dir>"
    sys.exit(1)
print "Starting, this can take some time, be patience :-)"
p = sys.argv[1]
tb = 'game_puzzle'

print """\
------------------------------------------------------------------
Starting to check table %s
""" % tb

report = \
"""Number of ID in query: %(cids)s
Number of files found in %(path)s: %(files)s
Number of files with correct ID: %(foundfiles)s
Number of files without ID: %(wrongfiles)s
Couldn't find files for these IDS: %(missing)s
Files that that corresponds with found ID are moved to %(dest)s"""
report_hash = {'path':p}

db=MySQLdb.connect(user="root",  db="btp_content")
c = db.cursor()
c.execute('''SELECT * FROM %s WHERE NOT ISNULL(fileOriginalName) AND \
                                    content_checked > 0;''' % (tb, ))
cids = [row[0] for row in c.fetchall()]

report_hash['cids'] = len(cids)

files = glob.glob(os.path.join(p, "*"))
report_hash['files'] = len(files)
report_hash['missing'] = []

cid_hash = {}
missingcids = []
for cid in cids:
    files = glob.glob(os.path.join(p, "game_puzzle_%s_width_324.jpg" % (cid)))
    if not files:
        report_hash['missing'].append(cid)
        print "not found", cid
        continue
    cid_hash[cid] = files
        
report_hash['foundfiles'] = len(cid_hash.keys())

dest = os.path.join(p, 'checked', 'puzzle')
if not os.path.exists(dest):
    os.makedirs(dest)
report_hash['dest'] = dest
print "moving files into %s" % dest

for files in cid_hash.values():
    for file in files:
        try:
            shutil.move(file, dest)
        except Exception, info:
            print "failed to move %s, %s" % (file, info)
        
leftfiles = glob.glob(os.path.join(p, "*_*.ogg"))
report_hash['wrongfiles'] = min(0, len(leftfiles) -1) 

print report % report_hash



