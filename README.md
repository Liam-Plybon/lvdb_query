# lvdb_query

This is a program in development to support the retrieval of data from the local volume database project. At this time, the program is only function on the computer in which the local volume database is located. 

### Installation ###
Clone this repo with: 

<pre>
git clone https://github.com/jmaner/lvdb_query.git
</pre>

This program depends on the <a href="https://github.com/kadrlica/local-volume-db">local-volume db </a> python package written by <a href="https://github.com/kadrlica/">Alex Drlica-Wagner</a>.

You must then add the line to your .bashrc file in the format:

<pre>
source PYTHONPATH=~/your_installation_directory/local-volume-db:$PYTHONPATH
</pre>

### Development updates ###

<b>Features in progress/planned: </b>

<ul>
<li>✓Detect typos/tables not present in glossary </li>   (v0.2)
  
<li>✓Detect typos/keys not located in database </li>  (v0.2)
  
<li>✓Allow users to select individual parameters</li> (v0.3)

<li>✓Handle requested entries with key but no id listed in glossary (v0.3)

<li>output key,table,reference,notes to a single separate file called ref? </li>
</ul>

#### v0.4 ####
In development. 

#### v0.3 ####
Allows user to query data as a function in python. The function and its arguments are:

query(<b>keys</b>=<i>'in_keys.csv'</i>, <b>params</b>=<i>'in_param.csv'</i>

This is done so to make further versions more versatile, and will eventually see the input structure become more open ended. Another function is available in v0.4(in development) that fetches keys from the database based on an WHERE query in which all keys that fall within a range of values for a parameter. This may then be called in the function, removing the need for an input file. 

#### v0.2 ####

We are now migrating to a new input structure consisting of a individual .csv for the keys and the required tables. Please see the v0.2 folder for more details. 

We use an expanded version of the initial tag table structure that may be seen in the LVDB_Notes wiki page on redmine. 

This version is fully functional and returns a .csv with appropriately formatted headers. 


#### v0.1 ####

This is our initial proof of concept for a simple tag table stucture. 

Details on the structure of the tag table may be seen in the LVDB_Notes wiki page on redmine. 

Program outputs data from database as a tuple in the terminal. This clearly isn't very useful, however, it is functional. 
