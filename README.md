# QMJHL-Standings
This script grabs the QMJHL standings after a date and outputs them in a csv file.

# Getting started

Packages required and SQL DB setup.

## Prerequisites 

1. Python3 with packages requests, psycopg2, numpy, tqdm
```
pip install -r requirements.txt
```
2. A postgres [SQL Database](https://www.postgresql.org/download/linux/) is required.

## SQL DB Setup

Before you begin, step a SQL database. Note the lines 
```
    connection = psycopg2.connect(user = <insert username>,
                                  password = <insert password>,
                                  host = <insert sql server addr>,
                                  port = <insert sql server port number>,
                                  database = <insert database name>)
```
are commented out in the python scripts. Replace the angle brackets in the above statement with your SQL DB’s information.

# Usage

1. Edit line 230 to set the date from which the script will begin gathering team data.
```
d2 = datetime.datetime(year, month, day)
```
2. Create a blank csv file named results.csv in the parent directory.
3. Run the script using:
```
python3 QMJHL_standings.py
```
# Results

The results will be output into the results.csv file. The output should look like:
![image](https://user-images.githubusercontent.com/70489989/166073405-38457772-968f-42ac-b5f9-ed6b484fe028.png)



A few notes regarding the data:

    1. Wins and OT wins are separated and not combined.
    2. Losses and OT losses are also separated and not combined.
    3. # of PP and # of PK represent the total # of PP opportunities and # of times shorthanded.
    4. PPG is the # of PP goals scored by a team.
    5. SHGA is the # of goals scored against a team while shorthanded.
    6. GF and GA includes PPG and SHGA respectively.
