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
Team	GP	Wins	Losses	OTW	OTL	# of PP	# of PK	PP%	PK%	PIM	PPG	SHGA	GF	GA
She	35	20	10	3	2	123	116	29.27	73.28	348	36	31	141	-99
Cha	32	18	6	3	5	147	130	19.73	76.92	378	29	30	123	-90
Rim	34	15	12	2	5	83	122	32.53	74.59	236	27	31	114	-102
Bat	37	18	10	6	3	162	150	26.54	77.33	436	43	34	156	-103
BLB	34	13	15	1	5	128	132	17.97	77.27	310	23	30	106	-114
SNB	32	23	5	3	1	129	94	24.81	63.83	351	32	34	151	-82
Vic	34	8	22	2	2	117	112	15.38	81.25	357	18	21	72	-137
Cap	34	4	25	3	2	131	144	22.14	72.92	362	29	39	90	-163
Chi	33	10	20	3	0	110	110	16.36	73.64	278	18	29	94	-127
Dru	34	12	13	2	7	110	117	21.82	75.21	298	24	29	109	-130
BaC	34	10	20	2	2	121	103	19.01	78.64	314	23	22	97	-121
Sha	33	14	14	4	1	116	127	31.9	77.95	337	37	28	99	-82
VdO	34	9	17	5	3	112	128	27.68	71.88	306	31	36	113	-144
Hal	34	14	16	4	0	105	131	33.33	72.52	340	35	36	145	-156
Rou	34	12	15	5	2	126	122	22.22	67.21	318	28	40	96	-108
Gat	36	19	7	1	9	126	119	26.19	71.43	334	33	34	143	-110
Mon	35	8	20	3	4	143	139	20.28	74.1	390	29	36	95	-152
Que	33	25	5	2	1	118	111	27.97	72.97	296	33	30	164	-88
![image](https://user-images.githubusercontent.com/70489989/166073405-38457772-968f-42ac-b5f9-ed6b484fe028.png)



A few notes regarding the data:

    1. Wins and OT wins are separated and not combined.
    2. Losses and OT losses are also separated and not combined.
    3. # of PP and # of PK represent the total # of PP opportunities and # of times shorthanded.
    4. PPG is the # of PP goals scored by a team.
    5. SHGA is the # of goals scored against a team while shorthanded.
    6. GF and GA includes PPG and SHGA respectively.
