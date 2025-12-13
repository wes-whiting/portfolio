import json
#from itertools import islice

FILENAME = 'rio_data_raw_tww_s2.jsonl'

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

# def load_jsonl_line(filename, n):
#     "Loads one line from a .jsonl file"
#     with open(filename, 'r') as file:
#         line = next(islice(file,n,n+1), None)
#         if line is None:
#             return None
#         return json.loads(line)

# data = load_jsonl_line(FILENAME,317)
# print(data['rank'])

with open(FILENAME, mode='r') as file:
    for line in file:
        json_line = json.loads(line)


# def make_rows_by_character(pagerow):
#     """From a page of rankings from fetch_run(), gets one run
#     and makes 5 rows describing the run, one for each character.
#     """
#     roster_list = pagerow['run']['roster']
#     rows = []
#     for character_dict in roster_list:
#         rows.append({
#             'Dungeon':          pagerow['run']['dungeon']['name'],
#             'dungeon_short':    pagerow['run']['dungeon']['short_name'],
#             'dungeon_slug':     pagerow['run']['dungeon']['slug'],
#             'Level':            pagerow['run']['mythic_level'],
#             'Time':             pagerow['run']['completed_at'],
#             'Status':           pagerow['run']['status'],
#             'num_chests':       pagerow['run']['num_chests'],
#             'Score':            pagerow['score'],
#             'Name':             character_dict['character']['name'],
#             'id':               character_dict['character']['id'],
#             'Realm':            character_dict['character']['realm']['name'],
#             'realm_slug':       character_dict['character']['realm']['slug'],
#             'Class':            character_dict['character']['class']['name'],
#             'Race':             character_dict['character']['race'],
#             'Faction':          character_dict['character']['faction'],
#             'isTransfer':       character_dict['isTransfer'],
#             'Spec':             character_dict['character']['spec']['name'],
#             'Role':             character_dict['role'],
#         })
#     return rows