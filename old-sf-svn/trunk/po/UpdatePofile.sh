#!/bin/sh

VERS=0.7
TEMPDIR=/tmp/SP_temp_po
echo "Saving your po tree to po.org"
cp -r ../po ../po.org

mkdir -p $TEMPDIR
python generate_pot.py ../ schoolsplay $VERS > $TEMPDIR/messages.po
echo "Placed a new pot file in ./po"
cp $TEMPDIR/messages.po schoolsplay_$VERS.pot
find . -name "*.po" | while read pofile
    do
	echo $pofile
        msgmerge --update --backup=off -F $pofile $TEMPDIR/messages.po
    done
