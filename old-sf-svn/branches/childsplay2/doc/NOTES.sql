Notes about sql tables used in CP

table: user
columns: 
'user_id', Integer:
used by dbase

'login_name', String(20):
User name

'first_name', String(20):
Not used yet

'last_name', String(40):
Not used yet

'birthdata', String(11):
Not used yet

'class', String(6):
Not used yet

'profile', String(200):
Not used yet

'passwrd', String(10):
Not used yet

'activities', String(250) :
holds a string with activity names, separated with commas, 
which are EXCLUDED, empty means none excluded

table: menu
columns:

'table_id', Integer:
Used by dbase

'module', String(20):
Python module name

'name', String(20):
activity name

'icon', String(60):
name of the icon file

'tooltip', String(80):
tooltip string 

'group', String(20):
name string, to wich group this act belongs. 
Defaults to 'ALL'


