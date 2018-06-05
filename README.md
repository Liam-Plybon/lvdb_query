# lvdb_query

This is a program being developed to complete psql queries for the local volume database project currently in development. 

### Installation ###



## Development updates: ##


### v0.2 ###

We are now migrating to a new input structure consisting of a individual .csv for the keys and the required tables. Please see the v0.2 folder for more details. 

We will also be using a slightly different tag table structure in the format: 
<pre>
   key    | dist_id | kine_id | stru_id 
----------+---------+---------+---------
 bootes_1 |     145 |     266 |     617
 and_1    |      12 |     355 |     413
</pre>

in which each integer is the id of the most desirable entry in the distance, kinematics, and structure tables. 

### v0.1 ### 

This is our initial proof of concept for a simple tag table stucture in the format: 

<pre>
   key   |    id 
---------+----------
bootes_1 |    145   
and_1    |     12   
</pre>

Program outputs data from database as a tuple in the terminal. This clearly isn't very useful, however, it is functional. 