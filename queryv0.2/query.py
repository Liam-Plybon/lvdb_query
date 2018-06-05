#Authors: John Maner, Liam Plybon
#Contact: jmaner33@tamu.edu, katana@tamu.edu

import numpy as np
from operator import add
import lvdb.database #leave commented out while testing offline
import psycopg2 as psy #leave commented out while testing offline

####inputs
in_keys=np.genfromtxt('in_keys.csv', dtype=str, delimiter=',')#keys input
in_tabl=np.genfromtxt('in_tabl.csv', dtype=str, delimiter=',')#desired tables to be searched


####input interpreter

#search for requested tables 

tables=['distance', 'structure', 'kinematics']

#define dummy variables-- when these becomes "active", i.e =1, the corresponding table will be searched. 
dist=0
stru=0
kine=0
error=0

for x in in_tabl:
    if x == 'distance':
        dist=1
    elif x == 'structure':
        stru=1
    elif x == 'kinematics':
        kine=1
    elif x != 'distance' or 'structure' or 'kinematics':
        error=1
        
####id fetcher
#constructs a lists of queries with the appropriate keys for each requested table

#blank lists to be written to
dist_id_select=[]
stru_id_select=[]
kine_id_select=[]

if error == 1:#this is my lazy implementation-- try: https://docs.python.org/3.4/tutorial/errors.html
    print("ERROR: A table you requested does not exist")

if dist == 1:
    for key in in_keys:
        dist_id_select.extend([add('SELECT dist_id FROM mast_gloss_test WHERE key=\'' + key , '\';')])
        
if stru == 1:
    for key in in_keys:
        stru_id_select.extend([add('SELECT stru_id FROM mast_gloss_test WHERE key=\'' + key , '\';')])
        
if kine == 1:
    for key in in_keys:
        kine_id_select.extend([add('SELECT kine_id FROM mast_gloss_test WHERE key=\'' + key , '\';')])
        
#connect to local-volume
db=lvdb.database.Database() 
db.connect()

dist_id=[]
stru_id=[]
kine_id=[]

for x in dist_id_select:
    dist_id.extend(db.select(x))
    
for x in stru_id_select:
    stru_id.extend(db.select(x))
    
for x in kine_id_select:
    kine_id.extend(db.select(x))
    
print(dist_id)
print(stru_id)
print(kine_id)
