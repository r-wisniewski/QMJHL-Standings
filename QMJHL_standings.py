"""
Usage: python Q_sql_scrape.py 
"""
from urllib import request
import requests
import json
import psycopg2
import sys
import numpy as np
from requests.sessions import Session
from concurrent.futures import ThreadPoolExecutor
from threading import local,Lock
from tqdm import tqdm
import datetime
import csv

#pxpverbose includes all the shot/goal data including x,y coordinates etc...
url = 'https://cluster.leaguestat.com/feed/index.php?feed=gc&key=f322673b6bcae299&client_code=lhjmq&game_id='
end = '&lang_code=en&fmt=json&tab=pxpverbose'
#2021-22 schedule response
schedule_url = 'https://lscluster.hockeytech.com/feed/?feed=modulekit&view=schedule&key=f322673b6bcae299&fmt=json&client_code=lhjmq&lang=en&season_id=199&team_id=&league_code=&fmt=json'
thread_local = local()
mutex = Lock()

# CONNECT TO POSTGRES DB #
try:
    connection = psycopg2.connect(user = <insert username>,
                                  password = <insert password>,
                                  host = <insert sql server addr>,
                                  port = <insert sql server port number>,
                                  database = <insert database name>)
    #Create cursor object. This will allow us to interact with the database and execute commands
    cursor = connection.cursor()
    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)

#drop previous table if it exists
try:
    cursor.execute("DROP TABLE q_raw_results;")
    connection.commit()
    print("Table q_raw_results has been dropped")
except (Exception, psycopg2.DatabaseError) as error :
    print ("Error while deleting PostgreSQL table", error)

try:
    create_table = '''CREATE TABLE q_raw_results ( 
        Team varchar NOT NULL,
        Win INT,
        Loss INT,
        OTW INT,
        OTL INT,
        PP INT,
        PK INT,
        PIM INT,
        PPG INT,
        SHGA INT,
        GF INT,
        GA INT)'''
    cursor.execute(create_table)
    connection.commit()
except (Exception, psycopg2.DatabaseError) as error :
    print ("Error while creating PostgreSQL table", error)

def make_url_list(game_list:list) -> list:
    url_list = []
    for n in game_list:
        fullurl = url + str(n) + end
        url_list.append(fullurl)
    return url_list

def request_all(url_list:list) -> None:
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(request_url,url_list)

def get_session() -> Session:
    if not hasattr(thread_local,'session'):
        thread_local.session = requests.Session()
    return thread_local.session

def request_url(url:str) -> None:
    session = get_session()
    with session.get(url) as resp:
        json_data = json.loads(resp.text)
        bar.update(1)

        #Use a dict to store per game info per team
        Team1 = {}
        Team2 = {}
        #ie, Team = {"team_id" : "team_code", ...}
        #grab the team names first
        team_id = []
        team_code = []
        for i in json_data['GC']['Pxpverbose']:
            event = i['event'] 
            #Log PIM
            if event == "goalie_change":
                t = i['team_id']
                t= int(t)
                tc = i['team_code']
                team_id.append(t)
                team_code.append(tc)
        Team1[team_id[0]] = team_code[0]
        Team2[team_id[1]] = team_code[1]
        team_1 = team_id[0]
        team_2 = team_id[1]
        #zero out the dict
        Team1['Win'] = 0
        Team1['Loss'] = 0
        Team1['OTW'] = 0
        Team1['OTL'] = 0
        Team1['PP'] = 0
        Team1['PK'] = 0
        Team1['PIM'] = 0
        Team1['PPG'] = 0
        Team1['SHGA'] = 0
        Team1['GF'] = 0
        Team1['GA'] = 0
        Team2['Win'] = 0
        Team2['Loss'] = 0
        Team2['OTW'] = 0
        Team2['OTL'] = 0
        Team2['PP'] = 0
        Team2['PK'] = 0
        Team2['PIM'] = 0
        Team2['PPG'] = 0
        Team2['SHGA'] = 0
        Team2['GF'] = 0
        Team2['GA'] = 0
        for i in json_data['GC']['Pxpverbose']:
            event = i['event'] 
            #Log PIM
            if event == "penalty":
                pp = i['pp']
                pp = int(pp)
                mins = i['minutes']
                mins = int(mins.split(".")[0])
                against_team = i['team_id']
                against_team = int(against_team)
                #Assign PIMs to the appropriate team
                if against_team == team_1:
                    Team1['PIM'] += mins
                    if pp == 1:
                        Team1['PP'] += pp
                        Team2['PK'] += pp
                elif against_team == team_2:
                    Team2['PIM'] += mins
                    if pp == 1:
                        Team2['PP'] += pp
                        Team1['PK'] += pp
            elif event == "goal":
                ppg = i['power_play']
                ppg = int(ppg)
                goal_team = i['team_id']
                goal_team = int(goal_team)
                game_winning = i['game_winning']
                game_winning = int(game_winning)
                period = i['period_id']
                period = int(period)
                if goal_team == team_1:
                    Team1['GF'] += 1
                    Team2['GA'] -= 1
                    if ppg == 1:
                        Team1['PPG'] += 1
                        Team2['SHGA'] += 1
                    if game_winning == 1 and period == 4:
                        Team1['OTW'] = 1
                        Team2['OTL'] = 1
                    elif game_winning == 1 and not period == 4:
                        Team1['Win'] = 1
                        Team2['Loss'] = 1
                elif goal_team == team_2:
                    Team2['GF'] += 1
                    Team1['GA'] -= 1
                    if ppg == 1:
                        Team2['PPG'] += 1
                        Team1['SHGA'] += 1
                    if game_winning == 1 and period == 4:
                        Team2['OTW'] = 1
                        Team1['OTL'] = 1
                    elif game_winning == 1 and not period == 4:
                        Team2['Win'] = 1
                        Team1['Loss'] = 1
            elif event == "shootout":
                game_winning = i['winning_goal']
                game_winning = int(game_winning)
                if game_winning == 1:
                    win_team = i['team_id']
                    win_team = int(win_team)
                    if win_team == team_1:
                        Team1['OTW'] = 1
                        Team2['OTL'] = 1
                    elif win_team == team_2:
                        Team2['OTW'] = 1
                        Team1['OTL'] = 1

        #Write Team1 to the DB
        values = """INSERT INTO q_raw_results (Team, Win, Loss, OTW, OTL, PP, PK, PIM, PPG, SHGA, GF, GA) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        mutex.acquire()
        cursor.execute(values, (Team1[team_1],Team1['Win'],Team1['Loss'],Team1['OTW'],Team1['OTL'],Team1['PP'],Team1['PK'],Team1['PIM'],Team1['PPG'],Team1['SHGA'],Team1['GF'],Team1['GA']))
        connection.commit()
        mutex.release()
        #Write Team2 to the DB
        values = """INSERT INTO q_raw_results (Team, Win, Loss, OTW, OTL, PP, PK, PIM, PPG, SHGA, GF, GA) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        mutex.acquire()
        cursor.execute(values, (Team2[team_2],Team2['Win'],Team2['Loss'],Team2['OTW'],Team2['OTL'],Team2['PP'],Team2['PK'],Team2['PIM'],Team2['PPG'],Team1['SHGA'],Team2['GF'],Team2['GA']))
        connection.commit()
        mutex.release()

def get_game_IDs() -> list:
    game_list = []
    session = get_session()
    with session.get(schedule_url) as resp:
        json_data = json.loads(resp.text)
        #parse json resp
        for i in json_data['SiteKit']['Schedule']:
            game_id = i['game_id']
            game_id = int(game_id)
            date = i['date_played']
            date = date.split('-')
            year = int(date[0])
            month = int(date[1])
            day = int(date[2])
            #d1 is the date of the game. Feb 10 2022 is the first game we want to consider games
            d1 = datetime.datetime(year,month,day)
            #d2 = datetime.datetime(2021, 9, 30)
            d2 = datetime.datetime(2022, 2, 9)
            if d1 > d2:
                game_list.append(game_id)
    return game_list

game_list = get_game_IDs()

#setup the progress bar
global bar 
bar = tqdm(desc="Progress",total=len(game_list))

url_list = make_url_list(game_list)
request_all(url_list)

bar.close()

f = open('results.csv', 'w')
header = ['Team', 'GP', 'Wins', 'Losses', 'OTW', 'OTL', '# of PP', '# of PK', 'PP%', 'PK%', 'PIM', 'PPG', 'SHGA', 'GF', 'GA']
writer = csv.DictWriter(f, fieldnames=header)
writer.writeheader()

#Grab the cumulative rows in q_raw_results for each team and write the summary to q_results
query = '''SELECT DISTINCT Team FROM q_raw_results;'''
cursor.execute(query)
matching_records = cursor.fetchall()
#Select a single distinct team from the SELECT DISTINCT sql query
for t in matching_records:
    query = '''SELECT * FROM q_raw_results WHERE TEAM = '%s';'''
    cursor.execute(query % ((t[0])))
    team_records = cursor.fetchall()
    x = ('GP', 'Team', 'Wins', 'Losses', 'OTW', 'OTL', '# of PP', '# of PK', 'PP%', 'PK%', 'PIM', 'PPG', 'SHGA', 'GF', 'GA')
    y = 0
    team_record = dict.fromkeys(x,y)
    team_record['Team'] = t[0]
    total_pk = 0
    total_pp = 0
    total_ppg = 0
    total_shga = 0
    for j in team_records:
        team_record['Wins'] += j[1]
        team_record['Losses'] += j[2]
        team_record['OTW'] += j[3]
        team_record['OTL'] += j[4]
        team_record['PIM'] += j[7]
        team_record['PPG'] += j[8]
        team_record['SHGA'] += j[9]
        team_record['GF'] += j[10]
        team_record['GA'] += j[11]
        team_record['# of PK'] += j[6]
        team_record['# of PP'] += j[5]

    team_record['PP%'] = round((team_record['PPG']/team_record['# of PP'])*100,2)
    team_record['PK%'] = round(((team_record['# of PK']-team_record['SHGA'])/team_record['# of PK'])*100,2)
    gp =  team_record['Wins'] +  team_record['Losses'] + team_record['OTW'] + team_record['OTL']
    team_record['GP'] = gp
    writer.writerow(team_record)

f.close()
#closing database connection.
if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")