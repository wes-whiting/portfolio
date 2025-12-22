import json
import pandas as pd
import progressbar
import psycopg2
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
POSTGRES_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

INFILE = 'rio_data_raw_tww_s2.jsonl'

def make_rows_by_character(run):
    """From the dict for one run, makes one row for each character.
    """
    roster_list = run['run']['roster']
    rows = []
    for character_dict in roster_list:
        rows.append({
            'dungeon':          run['run']['dungeon']['name'],
            'dungeon_short':    run['run']['dungeon']['short_name'],
            'level':            run['run']['mythic_level'],
            'timestamp':        run['run']['completed_at'],
            'status':           run['run']['status'],
            'num_chests':       run['run']['num_chests'],
            'score':            run['score'],
            'name':             character_dict['character']['name'],
            'realm':            character_dict['character']['realm']['name'],
            'class':            character_dict['character']['class']['name'],
            'spec':             character_dict['character']['spec']['name'],
            'role':             character_dict['role'],
        })
    return rows

def count_lines(filename):
    line_count = 0
    with open(filename, 'r') as f:
        for line in f:
            print('\r',line_count, end='')
            line_count += 1
    return line_count

def read_file(filename):
    print('Counting lines...')
    line_count = count_lines(filename)
    print('Line count: ', line_count)

    line_list = []
    bar = progressbar.ProgressBar(max_value=line_count)
    with open(INFILE, mode='r') as file:
        for line in file:
            json_line = json.loads(line)
            line_list.extend(make_rows_by_character(json_line))
            bar.increment()
    print('\nMaking dataframe...')
    df = pd.DataFrame(line_list)
    return df

def make_database(name):
    print('Making database...')
    connection = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(f'DROP DATABASE IF EXISTS {name}')
    cursor.execute(f'CREATE DATABASE IF NOT EXISTS {name}')
    connection.close()

make_database('raider_io_funnel_analysis')

runs_raw = read_file(INFILE)

print('Making table...')
engine = create_engine(POSTGRES_URL)
runs_raw.to_sql(
    name='runs_raw',
    con=engine,
    if_exists='replace',
    index=False,
    method='multi',
    chunksize=1000,
)

print('Done!')