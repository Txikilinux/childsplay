#!/usr/bin/env python

import os,glob

PONAME = 'schoolsplay.po'
MONAME = 'schoolsplay.mo'
PODIR = os.getcwd()
#MODIR = os.path.join(os.getcwd(),'locale')
MODIR = '/home/stas/SVN-WORK/schoolsplay/locale'
# For testing purposes
##PODIR = os.path.join('/tmp/gvr','po')
##MODIR = os.path.join('/tmp/gvr','locale')

print "podir =",PODIR
print "modir =",MODIR

log = []
f = open('Po2Mo.log','w')

for pofile in glob.glob("%s/*.po" % PODIR):
    #pofile = os.path.join(popath,PONAME)
    print "==================================================================="
    print "Processing",pofile
    if os.path.exists(pofile):
        langname = os.path.basename(pofile).split('_')[1]
        modir = os.path.join(MODIR,langname,'LC_MESSAGES',MONAME)
        if not os.path.exists(os.path.join(MODIR,langname,'LC_MESSAGES')):
            os.makedirs(os.path.join(MODIR,langname,'LC_MESSAGES'))
        line = "Result of compiling %s/%s into %s:\n" % (langname,PONAME,MONAME)
        f.write(line)
        cmd = 'msgfmt -c -v -o %s %s' % (modir, pofile)
        print "Compiling po to mo",cmd
        stdin,stderr,stdout = os.popen3(cmd)
        out = stdout.read()
        line ="output: %s\n" % out
        f.write(line)
f.close()



   
    
