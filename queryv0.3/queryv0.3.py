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
in_param=np.genfromtxt('in_param.csv', dtype=str, delimiter=',')
#specific parameters to be searched-- This is designed to work with both the individual
#parameters, but also the table. 

#check for errors in files- this is used to determine if the data present
#in a file is the correct type (not datatype), i.e keys in in_keys.csv, etc. 

if set(in_keys).issubset(keys) == True:
    pass
else:
    key_error = []
    key_error.append(list(set(in_keys) - set(keys)))
    raise IOError('in_keys.csv contains entries that are not in the glossary: ' + str(key_error))

if set(in_param).issubset(master_header) == True:
    pass
else:
    param_error = []
    param_error.append(list(set(in_param) - set(master_header))) #I am leaving tables here for the planned expansion of the params file structure
    raise IOError('in_param.csv contains a parameter(s) that does not exist: ' + str(param_error))
    
        
#verify that the keys a user is requesting exist in mast_gloss_test
for x in in_keys:
    if x in keys:
        pass
    else:
        raise IOError('A key you requested is not currently in the glossary: ' + str(x))

        
####input interpreter

#search for requested tables 

#verify whether a user is requesting data from a certain table--tables currently in mast_gloss_test have to be added manually currently 

#define dummy variables-- when dist, stru, or kine become active, i.e =1, this indicates
#specific parameters have been queried

#when dist_table, stru_table, or kine_table become active, the entire table has been queried (v0.2 functionality)
dist=0
stru=0
kine=0
dist_table=0
stru_table=0
kine_table=0


#activate dummy variables if necessary to indicate that a table must be searched
#then fill list with parameters to be searched using a somewhat hard to read (but functional) comparison
#if just a table is being queried, the ...._table variable is activated, and the program simply proceeds
#as it did in v0.2
for x in in_param:
    if x == 'distance':
        dist_table=1
    elif x == 'structure':
        stru_table=1
    elif x == 'kinematics':
        kine_table=1
    elif x in dist_header:
        dist=1
        dist_param=[i for e in dist_header for i in in_param if e in i]
    elif x in kine_header:
        kine=1
        kine_param=[i for e in kine_header for i in in_param if e in i]
    elif x in stru_header:
        stru=1
        stru_param=[i for e in stru_header for i in in_param if e in i]


    #I do not include an exception here because in_param inputs have been verified above
        

####id fetcher
#constructs a lists of queries with the appropriate keys for each requested table

#create queries as strings, then add to lists
dist_id_select=[]
stru_id_select=[]
kine_id_select=[]

if dist_table or dist == 1:
    for key in in_keys:
        dist_id_select.extend(['SELECT dist_id FROM mast_gloss_test WHERE key=\'' + str(key) + '\';'])#replace mast_gloss_test with final glossary table
        
if stru_table or stru == 1:
    for key in in_keys:
        stru_id_select.extend(['SELECT stru_id FROM mast_gloss_test WHERE key=\'' + str(key) + '\';'])
        
if kine_table or kine == 1:
    for key in in_keys:
        kine_id_select.extend(['SELECT kine_id FROM mast_gloss_test WHERE key=\'' + str(key) + '\';'])
        

#I am (perhaps lazily) using the select function in the lvdb package. This function recieves a query as a string

dist_id=[]
stru_id=[]
kine_id=[]

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

#create query to retrive results-- 

#for entrire tables-- note the SELECT * FROM ...... query format

dist_table_search=[]
stru_table_search=[]
kine_table_search=[]

if dist_table == 1:
    for id in dist_id:
        dist_table_search.extend(['SELECT * FROM distance WHERE id=\'' + str(id).replace('(','').replace(',)','') + '\';'])
        
if stru_table == 1:
    for id in stru_id:
        stru_table_search.extend(['SELECT * FROM structure WHERE id=\'' + str(id).replace('(','').replace(',)','') + '\';'])
        
if kine_table == 1:
    for id in kine_id:
        kine_table_search.extend(['SELECT * FROM kinematics WHERE id=\'' + str(id).replace('(','').replace(',)','') + '\';'])

#create queries for individual parameters-- this gets a bit messier because the query must be in the format:
#SELECT param_1,param_2,...,param_n
dist_search=[]
stru_search=[]
kine_search=[]

if dist == 1:
    for id in dist_id:
        dist_search.extend(['SELECT ' + str(dist_param).replace('[','').replace(']','').replace('\'','') + ' FROM distance WHERE id=\'' + str(id).replace('(','').replace(',)','') + '\';'])
        
if stru == 1:
    for id in stru_id:
        stru_search.extend(['SELECT ' + str(stru_param).replace('[','').replace(']','').replace('\'','') + ' FROM structure WHERE id=\'' + str(id).replace('(','').replace(',)','') + '\';'])
        
if kine == 1:
    for id in kine_id:
        kine_search.extend(['SELECT ' + str(kine_param).replace('[','').replace(']','').replace('\'','') + ' FROM kinematics WHERE id=\'' + str(id).replace('(','').replace(',)','') + '\';'])
        
        
dist_table_out=[]
stru_table_out=[]
kine_table_out=[]

#fetch results
if dist_table == 1:
    for x in dist_table_search:
        dist_table_out.extend(db.select(x))

if stru_table == 1:    
    for x in stru_table_search:
        stru_table_out.extend(db.select(x))

if kine_table == 1:     
    for x in kine_table_search:
        kine_table_out.extend(db.select(x))
    
dist_out=[]
stru_out=[]
kine_out=[]

if dist == 1:
    for x in dist_search:
        dist_out.extend(db.select(x))
        
if stru == 1:
    for x in stru_search:
        stru_out.extend(db.select(x))
        
if kine == 1:
    for x in kine_search:
        kine_out.extend(db.select(x))
        
        
####write .csv output
#verify whether csv needs to be written by checking if user requested

#I added a random character generator to the end of each file name to avoid files being overwritten. These will start to pile up in testing
#you may want to add a file on your personal machine that removes these files that begin with distance_out, structure_out, etc in the lvdb_query/query_v0.2 directory

suffix=str(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)))

if dist_table == 1:
    dist_csv = 'distance_out' + str(suffix) + '.csv'
    print('FILE ' + dist_csv + ' WAS SAVED')
    with open(dist_csv,'wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(dist_header)
        for row in dist_table_out:
            csv_out.writerow(row)
elif dist == 1:
    dist_csv = 'distance_out' + str(suffix) + '.csv'
    print('FILE ' + dist_csv + ' WAS SAVED')
    with open(dist_csv,'wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(dist_param)
        for row in dist_out:
            csv_out.writerow(row)

if stru_table == 1:
    stru_csv = 'structure_out' + str(suffix) + '.csv'
    print('FILE ' + stru_csv + ' WAS SAVED')
    with open(stru_csv,'wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(stru_header)
        for row in stru_table_out:
            csv_out.writerow(row)
elif stru == 1:
    stru_csv = 'structure_out' + str(suffix) + '.csv'
    print('FILE ' + stru_csv + ' WAS SAVED')
    with open(stru_csv,'wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(stru_param)
        for row in stru_out:
            csv_out.writerow(row)

if kine_table == 1:
    kine_csv = 'kinematics_out' + str(suffix) + '.csv'
    print('FILE ' + kine_csv + ' WAS SAVED')
    with open(kine_csv,'wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(kine_header)
        for row in kine_table_out:
            csv_out.writerow(row)
elif kine == 1:
    kine_csv = 'kinematics_out' + str(suffix) + '.csv'
    print('FILE ' + kine_csv + ' WAS SAVED')
    with open(kine_csv,'wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(kine_param)
        for row in dist_out:
            csv_out.writerow(row)


#print location files are saved to-- currently assuming the current working directory. should be easy enough to change if necessary. 
if dist or stru or kine or dist_table or stru_table or kine_table == 1:
    print("FILE(S) SAVED TO: " + os.getcwd())

#print elapsed time (does not include time to load packages intentionally)
print('ELAPSED TIME TO FETCH AND WRITE DATA: ' + str(time.time() - t) + 's.')
