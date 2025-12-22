import json
import sqlite3
import pandas as pd
import progressbar

INFILE = 'rio_data_raw_tww_s2.jsonl'
OUTFILE = 'tww_s2.db'

def describe(data, indent=0):
    pad = '  ' * indent
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
    """From the dict for one run, makes one row for each character.
    """
    roster_list = run['run']['roster']
    rows = []
    for character_dict in roster_list:
        rows.append({
            'Dungeon':          run['run']['dungeon']['name'],
            'dungeon_short':    run['run']['dungeon']['short_name'],
            'dungeon_slug':     run['run']['dungeon']['slug'],
            'Level':            run['run']['mythic_level'],
            'Time':             run['run']['completed_at'],
            'Status':           run['run']['status'],
            'num_chests':       run['run']['num_chests'],
            'Score':            run['score'],
            'Name':             character_dict['character']['name'],
            'id':               character_dict['character']['id'],
            'Realm':            character_dict['character']['realm']['name'],
            'realm_slug':       character_dict['character']['realm']['slug'],
            'Class':            character_dict['character']['class']['name'],
            'Race':             character_dict['character']['race']['name'],
            'Faction':          character_dict['character']['faction'],
            'isTransfer':       character_dict['isTransfer'],
            'Spec':             character_dict['character']['spec']['name'],
            'Role':             character_dict['role'],
        })
    return rows

def count_lines(filename):
    line_count = 0
    with open(filename, 'r') as f:
        for line in f:
            line_count += 1
    return line_count

line_count = count_lines(INFILE)

list = []
bar = progressbar.ProgressBar(line_count)
with open(INFILE, mode='r') as file:
    for line in file:
        json_line = json.loads(line)
        list.extend(make_rows_by_character(json_line))
        bar.increment()

df = pd.DataFrame(list)
conn = sqlite3.connect(OUTFILE)
df.to_sql('runs_raw', conn, if_exists='replace')
conn.close()