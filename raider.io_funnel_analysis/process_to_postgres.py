import json
import pandas as pd
import progressbar
import psycopg2
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from io import StringIO

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
            'race':             character_dict['character']['race']['name'],
            'faction':          character_dict['character']['faction'],
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

def check_exists_database(cursor, name):
    cursor.execute(
        f'SELECT 1 FROM pg_database WHERE datname = \'{name}\';'
    )
    exists = cursor.fetchone()
    return exists

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

    exists = check_exists_database(cursor, name)
    if not exists:
        cursor.execute(f'CREATE DATABASE {name}')
    connection.close()

def write_to_database(df, db_name, table_name):
    db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{db_name}'
    engine = create_engine(db_url)

    #Create an empty table
    df.head(0).to_sql(
        table_name,
        engine,
        index=False,
        if_exists='replace',
    )

    #Write to the table with COPY, much faster than .to_sql
    connection = psycopg2.connect(
        dbname=db_name,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        )
    cursor = connection.cursor()

    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    cursor.copy_expert(
        f"""
        COPY {table_name} ({', '.join(df.columns)})
        FROM STDIN WITH (FORMAT CSV)
        """,
        buffer
        )

    connection.commit()
    cursor.close()
    connection.close()

db_name = 'raider_io_funnel_analysis'
make_database(db_name)

df_runs_raw = read_file(INFILE)

print('Making table...')
write_to_database(df_runs_raw, db_name, 'runs_raw')
# db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{db_name}'
# engine = create_engine(db_url)
# print('Making table...')
# runs_raw.to_sql(
#     name='runs_raw',
#     con=engine,
#     if_exists='replace',
#     index=False,
#     method='multi',
#     chunksize=10000
#     )

print('Done!')