#!/bin/sh

TEMPDIR=/tmp/SP_temp_4_po
echo "Saving your po tree to po.org"
cp -r ../po ../po.org

mkdir -p $TEMPDIR
xgettext -f ./FilesForTrans -p $TEMPDIR
echo "Placed a new pot file in ./po"
cp $TEMPDIR/messages.po schoolsplay_latest.pot
find . -name "*.po" | while read pofile
    do
        msgmerge --update --backup=off -i -F "$pofile" $TEMPDIR/messages.po
    done
