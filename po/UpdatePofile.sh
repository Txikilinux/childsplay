#!/bin/sh

TEMPDIR=/tmp/SP_temp_4_po
echo "Saving your po tree to po.org"
cp -r ../po ../po.org

mkdir -p $TEMPDIR
xgettext  -f ./FilesForTrans -p $TEMPDIR

#python generate_pot.py .. seniorplay 2.0 $TEMPDIR/messages.po

echo "Placed a new pot file in ./po"
cp $TEMPDIR/messages.po childsplay_latest.po
find . -name "*.po" | while read pofile
    do
        msgmerge -s --update --backup=off "$pofile" $TEMPDIR/messages.po
    done
