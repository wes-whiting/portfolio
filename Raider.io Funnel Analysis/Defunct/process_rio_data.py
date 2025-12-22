import json
import pandas as pd
import progressbar

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
    count = 0
    with open(filename, 'r') as f:
        for line in f:
            print('\r',line_count, end='')
            count += 1
    return line_count

print('Counting lines...')
line_count = count_lines(INFILE)
print('Line count: ', line_count)

rows_list = []
bar = progressbar.ProgressBar(max_value=line_count)
with open(INFILE, mode='r') as file:
    for line in file:
        json_line = json.loads(line)
        rows_list.extend(make_rows_by_character(json_line))
        bar.increment()

print('\nMaking dataframe...')
df = pd.DataFrame(rows_list)
print('Making csv...')
df.to_csv("data/runs_raw.csv", index=False)
print('Done!')