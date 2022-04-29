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

