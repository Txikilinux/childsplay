sqlalchemy mysql setup:

For mysql:
sudo apt-get install mysql-server python-mysqldb
mysqladmin -u root create btp_content #on my system root has no password
# Add content mysql dbase
mysql -u root -p sp_content < sp_content.sql 

--------------------------------------------------------
contentdb data related stuff:

Any "binary blobs" that are in fileOriginalName col in a table should be constructed
to the correct image file name with the info from the game_filenames table.
The path should not be included, the caller will construct the path.
All the  "blobs" are located in lib/DbaseAssets/Images ../Sounds or ../Movies.


