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

def describe(data, indent=0, tabsize=4):
    """Maps the structure of nested dicts and lists, and prints it as an indented list.

    This is a helper function used during development, but is not used in the final pipeline.
    The Raider.IO API returns large JSON objects with lots of nesting, and their structure is not
    in the documentation, so mapping out keys and their location is helpful to locate the desired
    data, which may be scattered at various levels of nesting.
    See make_rows_by_character() below for examples.

    Keyword arguments:
        data -- a dict or list to be mapped
        indent -- the starting level of indentation, increments with each recursive call
        tabsize -- the number of spaces to indent each level
    """
    pad = ' ' * tabsize * indent
    if isinstance(data, dict):
        print(f'{pad}Dict with keys:')
        for k, v in data.items():
            print(f'{pad}- {k}: ({type(v).__name__})')
            describe(v, indent + 1)
    elif isinstance(data, list):
        print(f'{pad}List[{len(data)}] of '
              f'{type(data[0]).__name__ if data else "EMPTY"}')
        if data:
            describe(data[0], indent + 1)   # describe one example item

def make_rows_by_character(run):
    """From the dict for one run, makes one row for each character and returns a list of rows.

    The relevant keys were located with the help of describe() above.

    Keyword arguments:
        run -- a dict representing one run from the Raider.IO leaderboard.
    """
    roster_list = run['run']['roster']
    rows = []
    for character_dict in roster_list:
        rows.append({
            'dungeon':          run['run']['dungeon']['name'],
            'dungeon_short':    run['run']['dungeon']['short_name'],
            'completed_at':     run['run']['completed_at'],
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
    """Returns the number of lines in a .jsonl file.

    Keyword arguments:
        filename -- the name of the jsonl file to be counted.
    """
    line_count = 0
    with open(filename, 'r') as f:
        for line in f:
            print('\r',line_count, end='')
            line_count += 1
    return line_count

def read_file(filename):
    """Reads a .jsonl file and returns a dataframe that will become the table runs_raw.

    From a .jsonl file containing the raw JSON responses from the Raider.IO API, reads out the
    relevant data and forms it into one row per character per run. These rows are returned in a
    dataframe, which can later be made into an SQL database table.

    Displays a progress bar, since this can take several minutes for the data from a full season.

    Keyword arguments:
        filename -- the name of the .jsonl file where the Raider.IO API run data is saved.
    """
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
    """Checks if a PostgreSQL database already exists.

    Keyword arguments:
        cursor -- the database connection cursor object
        name -- the string name of the database to check for
    """
    cursor.execute(
        f'SELECT 1 FROM pg_database WHERE datname = \'{name}\';'
    )
    exists = cursor.fetchone()
    return exists

def make_database(name):
    """Creates an empty PostgreSQL database.

    Keyword arguments:
        name -- the string name of the database to be created
    """
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
    """Writes a dataframe to a PostgreSQL database as a table.

    Since the dataframe for a full season is large, this operation can be very slow with
    the native .to_sql function from pandas. Instead, we use the COPY command in SQL,
    which is much faster, on the order of 1 minute instead of 40.

    Keywords arguments:
        df -- the dataframe to write
        db_name -- the string name of the database
        table_name -- the string name for the new table
    """
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

def main():
    db_name = 'raider_io_funnel_analysis'
    make_database(db_name)

    df_runs_raw = read_file(INFILE)

    print('Making table...')
    write_to_database(df_runs_raw, db_name, 'runs_raw')

    print('Done!')

if __name__ == '__main__':
    main()