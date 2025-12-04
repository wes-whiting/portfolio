import requests
import csv
import time

BASE_URL = "https://raider.io/"
STATIC_DATA_URL = "api/v1/mythic-plus/static-data"
RUNS_URL = "api/v1/mythic-plus/runs"
REGION = "us"
SEASON = "season-tww-2"
EXPANSION_ID_TWW = 10      #Expansion number in order. 10 = TWW, 9 = DF, etc.
AFFIXES_TWW_S2 = ['xalataths-bargain-ascendant',
                  'xalataths-bargain-voidbound',
                  'xalataths-bargain-devour',
                  'xalataths-bargain-pulsar']


def describe(data, indent=0):
    pad = "  " * indent
    if isinstance(data, dict):
        print(f"{pad}Dict with keys:")
        for k, v in data.items():
            print(f"{pad}- {k}: ({type(v).__name__})")
            describe(v, indent + 1)
    elif isinstance(data, list):
        print(f"{pad}List[{len(data)}] of "
              f"{type(data[0]).__name__ if data else 'EMPTY'}")
        if data:
            describe(data[0], indent + 1)   # describe one example item
    else:
        print(f"{pad}{type(data).__name__}")

def api_call(suffix, params):
    r = requests.get(BASE_URL + suffix,params)
    r.raise_for_status()
    return r.json()

def fetch_dungeons(expansion,season):
    """Gets the pool of the dungeons for the season."""
    params = {
        "expansion_id": expansion
    }
    r = api_call(STATIC_DATA_URL, params)["seasons"]
    season_static_data =(
        next((item for item in r if item["slug"] == season), None))
    dungeons = season_static_data["dungeons"]
    names = [item["name"] for item in dungeons]
    return names

def make_affix_combos(season_affixes):
    """
    Keystones have a variety of affixes, varying by week and level.
    Generates the list of all possible combinations.
    """
    #No affix at +2 to +3
    affix_list = ['']
    for affix in season_affixes:
        #Just the bargain affix at +4
        affix_list.append(affix)
        #Bargain and fort or tyran at +7
        affix_list.append(affix+'-tyrannical')
        affix_list.append(affix+'-fortified')
        #Bargain and fort and tyran at +10
        affix_list.append(affix+'-tyrannical-fortified')
        #Drop bargain, add guile at +12
    affix_list.append('tyrannical-fortified-xalataths-guile')
    return affix_list

def fetch_run_page(page,dungeon,affixes):
    """
    Fetch one page of runs from the raider.io API.
    Each API call returns a dict['rankings','leaderboard_url','params'].
    'rankings' is a list of runs, each a dict['rank','score','run'].
    'run' is a dict with many keys, the relevant one is 'roster'.
    'roster' is a list[5] of dict['character','role'].
    'character' has many keys, the important ones are 'name', 'realm','spec'.
    """
    params = {
        "region": REGION,
        "season": SEASON,
        "dungeon": dungeon,
        "affixes:": affixes,
        "page": page,
    }
    return api_call(RUNS_URL, params)['rankings']

def make_rows_by_character(page,row):
    """From a page of rankings from fetch_run(), gets one run
    and makes 5 rows describing the run, one for each character.
    """
    roster_dict = page[row]['run']['roster']
    rows = []
    for character_dict in roster_dict:
        rows.append([
            page[row]['run']['dungeon']['name'],
            page[row]['run']['mythic_level'],
            page[row]['score'],
            character_dict['character']['name'],
            character_dict['character']['realm']['name'],
            character_dict['character']['class']['name'],
            character_dict['character']['spec']['name'],
            character_dict['role'],
        ])
    return rows

def make_file(filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = ['Dungeon',
                  'Level',
                  'Score',
                  'Name',
                  'Realm',
                  'Class',
                  'Spec',
                  'Role',
                  ]
        writer.writerow(header)

dungeons = fetch_dungeons(EXPANSION_ID_TWW,SEASON)
affixes = make_affix_combos(AFFIXES_TWW_S2)
make_file('runs.csv')
for dungeon in dungeons:
    for affix in affixes:
        for pagenum in range(1000):
            page = fetch_run_page(pagenum,dungeon,affixes)
            rows = make_rows_by_character(page,run)
        """Rewrite make_rows to take page[row] directly instead
        of an index?"""


# page=fetch_run_page(0)
# rows = make_rows_by_character(page,0)
# with open('runs.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerows(rows)