import MySQLdb

import sys, os, glob, shutil, getopt

img_p = None
img_s = None
try:                                
    opts, args = getopt.getopt(sys.argv[1:], "is:")
except getopt.GetoptError:          
    print "Usage: check_assets_quizpic.py  -i <path to image assets> || -s <path to sound assets>"                         
    sys.exit(1)      

if not opts:
    print "Usage: check_assets_quizpic.py  -i <path to image assets> || -s <path to sound assets>"                         
    sys.exit(1) 
    
for opt, arg in opts:
    if opt == '-i':
        img_p = arg
    if opt == '-s':
        snd_p = arg
    else:
        sys.exit(2)
print "Starting, this can take some time, be patience :-)"
tb = 'game_quizpic'
print """\
------------------------------------------------------------------
Starting to check table %s
""" % tb

report_img = \
"""
-------- Image files ---------------------------------------------
Number of ID in query: %(img_ids)s
Number of images files found in %(img_path)s: %(img_files)s
Number of image files with correct ID: %(img_foundfiles)s
Couldn't find image files for these IDS: %(img_missing)s
Image files that that corresponds with found ID are moved to %(img_dest)s
"""
report_snd=\
"""
--------- Sound files ---------------------------------------------
Number of CID in query: %(snd_cids)s
Number of sound files found in %(snd_path)s: %(snd_files)s
Number of sound files with correct CID: %(snd_foundfiles)s (*5)
Couldn't find sound files for these CIDS: %(snd_missing)s
Sound files that that corresponds with found CID are moved to %(snd_dest)s

"""
report_hash = {'img_path':img_p, 'snd_path':snd_p}

db=MySQLdb.connect(user="root",  db="btp_content")
c = db.cursor()
c.execute('''SELECT * FROM %s WHERE content_checked > 0;''' % (tb, ))
ids = [row[0] for row in c.fetchall()]
c.execute('''SELECT * FROM %s WHERE audiofiles = 5 AND content_checked > 0;''' % ('game_quizpic', ))
cids = [row[1] for row in c.fetchall()]
report_hash['img_ids'] = len(ids)
report_hash['snd_cids'] = len(cids)

# check and move image files
left_img_files = []
if img_p:
    files = glob.glob(os.path.join(img_p, "*.jpg"))
    report_hash['img_files'] = len(files)
    report_hash['img_missing'] = []
    id_hash = {}
    for id in ids:
        files = glob.glob(os.path.join(img_p, "%s_%s_width*.jpg" % (tb, id)))
        if not files:
            report_hash['img_missing'].append(id)
            #print "not found", id
            continue
        id_hash[id] = files
    report_hash['img_foundfiles'] = len(id_hash.keys())

    dest = os.path.join(img_p, 'checked', 'images')
    if not os.path.exists(dest):
        os.mkdir(dest)
    report_hash['img_dest'] = dest
    print "moving files into %s" % dest

    for files in id_hash.values():
        for file in files:
            try:
                shutil.move(file, dest)
            except Exception, info:
                print "failed to move %s, %s" % (file, info)
    left_img_files = glob.glob(os.path.join(img_p, "*_*_width*.ogg" ))
    print report_img % report_hash

# check and move sound files
left_snd_files = []
if snd_p:
    files = glob.glob(os.path.join(snd_p, "*.ogg"))
    report_hash['snd_files'] = len(files)
    report_hash['snd_missing'] = []
    cid_hash = {}
    for cid in cids:
        print os.path.join(snd_p, "%s_*.ogg" % (cid))
        files = glob.glob(os.path.join(snd_p, "%s_*.ogg" % (cid)))
        if not files:
            report_hash['snd_missing'].append(cid)
            #print "not found", cid
            continue
        cid_hash[cid] = files
    report_hash['snd_foundfiles'] = len(cid_hash.keys())

    
    dest = os.path.join(snd_p, 'checked')
    if not os.path.exists(dest):
        os.mkdir(dest)
    report_hash['snd_dest'] = dest
    print "moving image files into %s" % dest
    
    for files in cid_hash.values():
        for file in files:
            try:
                shutil.move(file, dest)
            except Exception, info:
                print "failed to move %s, %s" % (file, info)
    left_snd_files = glob.glob(os.path.join(snd_p, "*_*.ogg"))
    print report_snd % report_hash

wrongfiles = min(0, len(left_img_files) + len(left_snd_files) -1) 
print """
----------------------------------------------------------------------
Number of image files without proper ID or CID: %s
---------------------------------------------------------------------
""" % wrongfiles



