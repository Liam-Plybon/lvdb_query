#Authors: John Maner, Liam Plybon
#Contact: jmaner33@tamu.edu, katana@tamu.edu
#Origin: github.com/jmaner/lvdb_query
#Version: 0.3
###############################################################################

import time
import csv
import random
import string
import os
import numpy as np
#import lvdb.database #uncomment to import without try except statement below

#start timer to output query run time (diagnostic tool, however, this may be kept.)
t = time.time()


#connect to local-volume

#I (perhaps lazily) use the lvdb package rather than psycopg2 due to capability to use the .pgpass file of a user (i.e no manual entry to USER and PASS)
#I can try to migrate to psycopg2 and remove this dependance to decrease runtime.-- A small query may take 30ms, however, loading packages takes ~1s. 

#this adds about 0.6s to the elapsed time, however, makes the usage more user friendly and easier to troublshoot. Most of the time 
#seen in the elapsed time after a successfuly query comes from importing this package (in the case of small queries used to test the software)

try:
    import lvdb.database 
except ImportError:
    print('Unable to import lvdb.database. Are you sure your .bashrc file are correctly configured?')

try:
    db=lvdb.database.Database() 
    db.connect()
except ConnectionError:
    print('Unable to connect to local-volume. Are you sure your .pgpass file is correctly configured?')

#it may be nice if the tables in the glossary could be fetched automatically as the glossary is expanded/updated. 
tables=['distance', 'structure', 'kinematics']#update when a table is added to mast_gloss_test


#these headers are used for the final output csv, and will also be used to allow users to query individual parameters. 
#it may be nice if the headers could be fetched automatically in case they are changed. this would take a little work because I don't know how to query headers 
#this works for now
dist_header=['id','key','dist_mod','dist_mod_em','dist_mod_ep','method','ref','comments']

stru_header=['id','key','ra','ra_ep','ra_em','dec','dec_em','dec_ep','ellipticity','ellipticity_em',
             'ellipticity_ep','position_angle','position_angle_em','position_angle_ep','rscale',
             'rscale_em','rscale_ep','rparam_2','rparam_2_em','rparam_2_ep','rhalf','rhalf_em',
             'rhalf_ep','m_v','m_v_em','m_v_ep','apparent_magnitude','apparent_magnitude_em',
             'apparent_magnitude_ep','ref','comments','model']

kine_header=['id','key','helio_velocity','helio_velocity_em','helio_velocity_ep','velocity_dispersion',
             'velocity_dispersion_ep','velocity_dispersion_em','ref','comments','n']


master_header=['id','key','dist_mod','dist_mod_em','dist_mod_ep','method','ref','comments',
               'ra','ra_em','ra_ep','dec','dec_em','dec_ep','ellipticity','ellipticity_em','ellipticity_ep',
               'position_angle','position_angle_em','position_angle_ep','rscale','rscale_em','rscale_ep',
               'rparam_2','rparam_2_em','rparam_2_ep','rhalf','rhalf_em','rhalf_ep','m_v','m_v_em','m_v_ep',
               'apparent_magnitude','apparent_magnitude_em','apparent_magnitude_ep','model',
               'helio_velocity','helio_velocity_em','helio_velocity_ep','velocity_dispersion',
               'velocity_dispersion_ep','velocity_dispersion_em','n','distance', 'structure', 'kinematics']#contains table names as well


#verify which keys are present in mast_gloss_test. This will be used to verify whether the user is querying objects that have entries in mast_gloss_test
keys=[]

key_search=(db.select('SELECT key FROM mast_gloss_test;'))

for item in key_search:
    keys.extend(item)

#if we wanted to write this to a csv 
#with open('valid_keys.csv', 'wb') as f:
#    writer = csv.writer(f)
#    writer.writerow(valid_keys)

####inputs

in_keys=np.genfromtxt('in_keys.csv', dtype=str, delimiter=',')#keys to search
in_tabl=np.genfromtxt('in_tabl.csv', dtype=str, delimiter=',')#tables to be searched(please read note below)
in_param=np.genfromtxt('in_param.csv', dtype=str, delimiter=',')
#specific parameters to be searched-- This is designed to work with both the individual
#parameters, but also expand to the table as a whole. 
#the goal is to allow a user to simply input a table name
#and return all parameters. This will make the software more versatile, and is 
#more convenient to use. For the moment, I will keep in_tabl.csv, however, it is planeed
#to be removed a simply replaced with in_param.csv. 


#check for errors in files- this is used to determine if the data present
#in a file is the correct type (not datatype), i.e keys in in_keys.csv, etc. 

if set(in_keys).issubset(keys) == True:
    pass
else:
    key_error = []
    key_error.append(set(in_keys) - set(keys))
    raise IOError('in_keys.csv contains entries that are not in the glossary: ' + str(key_error))

if set(in_tabl).issubset(tables) == True:
        pass
else:
    tabl_error = []
    tabl_error.append(set(in_tabl) - set(tables))
    raise IOError('in_tabl.csv contains table entries in the glossary:' + str(tabl_error))

if set(in_param).issubset(master_header) == True:
    pass
else:
    param_error = []
    param_error.append(set(in_param) - set(master_header)) #I am leaving tables here for the planned expansion of the params file structure
    raise IOError('in_param.csv contains a parameter that does not exist: ' + str(param_error))
        
####input interpreter

#search for requested tables 

#verify whether a user is requesting data from a certain table--tables currently in mast_gloss_test have to be added manually currently 

#define dummy variables-- when these becomes "active", i.e = 1, the corresponding table will be searched. 
dist=0
stru=0
kine=0

for x in in_tabl:
    if x == 'distance':
        dist=1
    elif x == 'structure':
        stru=1
    elif x == 'kinematics':
        kine=1
    else:
        msg = 'A table you requested does not exist in the glossary: '
        raise TypeError(msg + str(x))
        

#verify that the keys a user is requesting exist in mast_gloss_test
for x in in_keys:
    if x in keys:
        pass
    else:
        msg = 'A key you requested is not currently in the glossary: '
        raise TypeError(msg + str(x))


####id fetcher
#constructs a lists of queries with the appropriate keys for each requested table

#blank lists for id search queries to be added to
dist_id_select=[]
stru_id_select=[]
kine_id_select=[]

#create queries as strings, then add to lists
if dist == 1:
    for key in in_keys:
        dist_id_select.extend(['SELECT dist_id FROM mast_gloss_test WHERE key=\'' + str(key) + '\';'])#replace mast_gloss_test with final glossary table
        
if stru == 1:
    for key in in_keys:
        stru_id_select.extend(['SELECT stru_id FROM mast_gloss_test WHERE key=\'' + str(key) + '\';'])
        
if kine == 1:
    for key in in_keys:
        kine_id_select.extend(['SELECT kine_id FROM mast_gloss_test WHERE key=\'' + str(key) + '\';'])
        

#blank lists to be populated with desired id's from mast_gloss_test
dist_id=[]
stru_id=[]
kine_id=[]

#I am (perhaps lazily) using the select function in the lvdb package. This function recieves a query as a string
for x in dist_id_select:
    dist_id.extend(db.select(x))
    
for x in stru_id_select:
    stru_id.extend(db.select(x))
    
for x in kine_id_select:
    kine_id.extend(db.select(x))
###############################################################################
#all code above is more or less universal, i.e, only retieves id's for a given table
#the code below is currently only capable of selecting all parameters
#individual parameter search feature is being built that will also handle searching entire tables
###############################################################################


####search query
#create query to retrive results-- currently recieves all entries from each requested table. Looking into adding capability to pick and choose which parameters. 
#Could probably implement using the headers and input the headers in place of * in the query below. 

#blank lists to be populated with search queries
dist_search=[]
stru_search=[]
kine_search=[]

if dist == 1:
    for id in dist_id:
        dist_search.extend(['SELECT * FROM distance WHERE id=\'' + str(id).replace('(','').replace(',)','') + '\';'])
        
if stru == 1:
    for id in stru_id:
        stru_search.extend(['SELECT * FROM structure WHERE id=\'' + str(id).replace('(','').replace(',)','') + '\';'])
        
if kine == 1:
    for id in kine_id:
        kine_search.extend(['SELECT * FROM kinematics WHERE id=\'' + str(id).replace('(','').replace(',)','') + '\';'])

#fetch results
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

#I added a random character generator to the end of each file name to avoid files being overwritten. These will start to pile up in testing
#you may want to add a file on your personal machine that removes these files that begin with distance_out, structure_out, etc in the lvdb_query/query_v0.2 directory
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

#print location files are saved to-- currently assuming the current working directory. should be easy enough to change if necessary. 
if dist or stru or kine == 1:
    print("FILE(S) SAVED TO: " + os.getcwd())

#print elapsed time (does not include time to load packages intentionally)
print('ELAPSED TIME TO FETCH AND WRITE DATA: ' + str(time.time() - t) + 's.')
quit()
