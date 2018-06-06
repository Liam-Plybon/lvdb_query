#Authors: John Maner, Liam Plybon
#Contact: jmaner33@tamu.edu, katana@tamu.edu

import numpy as np
from operator import add
import lvdb.database #leave commented out while testing offline
import psycopg2 as psy #leave commented out while testing offline
import csv
import random
import string

####inputs
in_keys=np.genfromtxt('in_keys.csv', dtype=str, delimiter=',')#keys input
in_tabl=np.genfromtxt('in_tabl.csv', dtype=str, delimiter=',')#desired tables to be searched


####input interpreter

#search for requested tables 

tables=['distance', 'structure', 'kinematics']

#these headers are used for the final output csv, and will also be used to allow users to query individual parameters. 
dist_header=['id','key','dist_mod','dist_mod_em','dist_mod_ep','method','ref','comments']
stru_header=['id','key','ra','ra_em','dec','dec_em','dec_ep','ellipticity','ellipticity_em','ellipticity_ep','position_angle','position_angle_em','position_angle_ep','rscale','rscale_em','rscale_ep','rparam_2','rparam_2_em','rparam_2_ep','rhalf','rhalf_em','rhalf_ep','m_v','m_v_em','m_v_ep','apparent_magnitude','apparent_magnitude_em','apparent_magnitude_ep','ref','comments','model']
kine_header=['id','key','helio_velocity','helio_velocity_em','helio_velocity_ep','ref','comments','n']

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
    elif x != 'distance' or 'structure' or 'kinematics':#list all table names here. This will be cleaned up with a proper try except statement at some point. 
        error=1
               
if error == 1:#this is my lazy implementation-- try: https://docs.python.org/3.4/tutorial/errors.html
    print("ERROR: A table you requested does not exist")
    quit()
        
####id fetcher
#constructs a lists of queries with the appropriate keys for each requested table

#blank lists to be written to
dist_id_select=[]
stru_id_select=[]
kine_id_select=[]

if dist == 1:
    for key in in_keys:
        dist_id_select.extend([add('SELECT dist_id FROM mast_gloss_test WHERE key=\'' + key , '\';')])#replace mast_gloss_test with final glossary table
        
if stru == 1:
    for key in in_keys:
        stru_id_select.extend([add('SELECT stru_id FROM mast_gloss_test WHERE key=\'' + key , '\';')])
        
if kine == 1:
    for key in in_keys:
        kine_id_select.extend([add('SELECT kine_id FROM mast_gloss_test WHERE key=\'' + key , '\';')])
        
#connect to local-volume
db=lvdb.database.Database() 
db.connect()

#blank lists to be populated with desired id's from mast_gloss_test
dist_id=[]
stru_id=[]
kine_id=[]

for x in dist_id_select:
    dist_id.extend(db.select(x))
    
for x in stru_id_select:
    stru_id.extend(db.select(x))
    
for x in kine_id_select:
    kine_id.extend(db.select(x))

####search query
#create query to retrive results-- currently recieves all entries from each requested table. Looking into adding capability to pick and choose which parameters. 
#Could probably implement using the headers and input the headers in place of * in the query below. if someone select all

#blank lists to be populated with search queries
dist_search=[]
stru_search=[]
kine_search=[]

if dist == 1:
    for id in dist_id:
        dist_search.extend([add('SELECT * FROM distance WHERE id=\'' + str(id).replace('(','').replace(',)','') , '\';')])
        
if stru == 1:
    for id in stru_id:
        stru_search.extend([add('SELECT * FROM structure WHERE id=\'' + str(id).replace('(','').replace(',)','') , '\';')])
        
if kine == 1:
    for id in kine_id:
        kine_search.extend([add('SELECT * FROM kinematics WHERE id=\'' + str(id).replace('(','').replace(',)','') , '\';')])


#search for final results
dist_out=[]
stru_out=[]
kine_out=[]

for x in dist_search:
    dist_out.extend(db.select(x))
    
for x in stru_search:
    stru_out.extend(db.select(x))
    
for x in kine_search:
    kine_out.extend(db.select(x))
    
####write .csv output
#verify whether csv needs to be written by checking if user requested

#I added a random generator to the end of each file name to avoid files being overwritten. 
if dist == 1:
    dist_csv = 'distance_out' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)) + '.csv'
    print('FILE ' + dist_csv + ' WAS SAVED')
    with open(dist_csv,'wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(dist_header)
        for row in dist_out:
            csv_out.writerow(row)

if stru == 1:
    stru_csv = 'structure_out' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)) + '.csv'
    print('FILE ' + stru_csv + ' WAS SAVED')
    with open(stru_csv,'wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(stru_header)
        for row in stru_out:
            csv_out.writerow(row)

if kine == 1:
    kine_csv = 'kinematics_out' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)) + '.csv'
    print('FILE ' + kine_csv + ' WAS SAVED')
    with open(kine_csv,'wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(kine_header)
        for row in kine_out:
            csv_out.writerow(row)

quit()
