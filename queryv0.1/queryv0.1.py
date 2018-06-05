#Author: John Maner
#Contact: jmaner33@tamu.edu 

import numpy as np
from operator import add
import lvdb.database
import psycopg2 as psy 

input=np.genfromtxt('input.csv', dtype=str, delimiter=',')

#search for glossary table based on input table request
#This is easily expandable!  
tables=np.array(['distance_glossary_test','ERROR'])

if input[1] == 'distance': 
    table=tables[0]
    
elif input[1] != 'distance': 
    print('ERROR: The table',input[1],'you requested does not exist.')

#connect to database 
db= lvdb.database.Database()
db.connect()

#constructs the id query as a string
idquery=reduce(add, ('SELECT id FROM ' , table , ' WHERE key=\'' , input[0] ,'\';'))

#generate array of desired id's 
q_id =np.array(db.select(idquery))

id= str(q_id[0]).replace('[','').replace(']','')

q_out=reduce(add, ('SELECT * FROM ', input[1] , ' WHERE id=\'' , id , '\';'))

out=db.select(q_out)

print(out)
