#Authors: John Maner, Liam Plybon
#Contact: jmaner33@tamu.edu, katana@tamu.edu

import numpy as np
from operator import add
#import lvdb.database #leave commented out while testing offline
#import psycopg2 as psy #leave commented out while testing offline


in_keys=np.genfromtxt('in_keys.csv', dtype=str, delimiter=',')#keys input
in_tabl=np.genfromtxt('in_tabl.csv', dtype=str, delimiter=',')#desired tables to be searched


#input interpreter
#search for requested tables 

tables=np.array([str('distance'), str('structure'), str('kinematics')])

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
        
#construct id search query
distid=[]

if dist == 1:
    for key in in_keys:
        dist_id_select=distid.extend([add('SELECT dist_id FROM mast_gloss_test WHERE key=\'' + key , '\';')])
