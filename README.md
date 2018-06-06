# lvdb_query

This is a program in development to support the retrieval of data from the local volume database project. At this time, the program is only function on the computer in which the local volume database is located. 

### Installation ###
Clone this repo with: 

<pre>
git clone https://github.com/jmaner/lvdb_query.git
</pre>

This program depends on the <a href="https://github.com/kadrlica/local-volume-db">local-volume db python package</a> written by <a href="https://github.com/kadrlica/">Alex Drlica-Wagner</a>.

You must then add the appropriate lines to your @.bashrc@ file in the format:

<pre>
source PYTHONPATH=~/your_directory/local-volume-db:$PYTHONPATH
</pre>

### Development updates ###


#### v0.2 ####

We are now migrating to a new input structure consisting of a individual .csv for the keys and the required tables. Please see the v0.2 folder for more details. 

We use an expanded version of the initial tag table structure that may be seen in the LVDB_Notes wiki page on redmine. 

This version is fully functional and returns a .csv with appropriately formatted headers. 

Features in progress: select individual parameters. 

#### v0.1 ####

This is our initial proof of concept for a simple tag table stucture. 

Details on the structure of the tag table may be seen in the LVDB_Notes wiki page on redmine. 

Program outputs data from database as a tuple in the terminal. This clearly isn't very useful, however, it is functional. 
