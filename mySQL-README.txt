sqlalchemy mysql setup:

For mysql:
sudo apt-get install mysql-server python-mysqldb
mysqladmin -u root create btp_content #on my system root has no password
# Add content mysql dbase
mysql -u root -p sp_content < sp_content.sql 



