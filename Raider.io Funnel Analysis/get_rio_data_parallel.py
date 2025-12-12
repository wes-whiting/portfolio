import requests
import progressbar
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
import threading

API_KEY = 'RIOHdZVtbhmmSsTQqiKMTyMqK'
PREFIX = 'https://raider.io/'
STATIC_DATA_URL = 'api/v1/mythic-plus/static-data'
RUNS_URL = 'api/v1/mythic-plus/runs'
REGION = 'us'
SEASON_SLUG = 'season-tww-2'
EXPANSION_ID = 10      #Expansion number in order. 10 = TWW, 9 = DF, etc.
AFFIXES_TWW_S2 = ['xalataths-bargain-ascendant',
                  'xalataths-bargain-voidbound',
                  'xalataths-bargain-devour',
                  'xalataths-bargain-pulsar']
PAGE_LIMIT = 1001

class RateLimiter:
    def __init__(self,limit,period):
        self.limit = limit
        self.period = period
        self.tokens = -1 #We start 1 in the hole from getting dungeons
        self.updated = time.time()
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            while True:
                now = time.time()
                elapsed = now - self.updated
                self.updated = now

                #Increment tokens based on time passed
                self.tokens += elapsed * (self.limit / self.period)
                if self.tokens > self.limit:
                    self.tokens = self.limit

                #If not enough tokens, wait
                if self.tokens <1:
                    time_to_wait = (1 - self.tokens) / (self.limit / self.period)
                    time.sleep(time_to_wait)
                    #self.tokens = 0
                if self.tokens >= 1:
                    self.tokens -= 1
                    break

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

def rio_api_call(suffix, params, prefix = PREFIX, key = API_KEY):
    params['access_key'] = key
    attempts = 1
    while True:
        try:
            r = requests.get(prefix + suffix,params=params)
            r.raise_for_status()
            break
        except Exception as e:
            print(f'Attempt {attempts} failed: {type(e).__name__}: {e}')
            attempts += 1
            time.sleep(10)
            pass
    return r.json()

def fetch_dungeons(expansion_id=EXPANSION_ID,season_slug=SEASON_SLUG):
    """Gets the pool of the dungeons for the season."""
    params = {
        'expansion_id': expansion_id
    }
    r = rio_api_call(STATIC_DATA_URL, params)['seasons']
    season_static_data =(
        next((item for item in r if item['slug'] == season_slug), None))
    dungeons = season_static_data['dungeons']
    names = [item['slug'] for item in dungeons]
    return names

def make_affix_combos(season_affixes):
    """Combines seasonal affixes with level-based affixes to form all possible combos.

    Note that some combos are excluded because they are illegal in the raider.IO API.
    Specifically it only allows combos of 3 or 4 affixes, or 'Tyrannical' or 'Fortified'.
    The Xal bargain affixes are allowed alone, probably because the 3-word slug looks like 3 affixes.

    Currently only works for TWW s2-style affixes. If extending this project to earlier seasons,
    will need to handle cases by season.

    Keyword arguments:
        season_affixes -- A list of rotating weekly affixes.
    """
    affix_list = []
    for affix in season_affixes:
        #Just the bargain affix at +4
        affix_list.append(affix)
        """
        The affix combos below are illegal in raider.io API for some reason.
        #Bargain and fort or tyran at +7
        affix_list.append(affix+'-tyrannical')
        affix_list.append(affix+'-fortified')
        """
        #Bargain and fort and tyran at +10
        affix_list.append(affix+'-tyrannical-fortified')
        #Drop bargain, add guile at +12
    affix_list.append('tyrannical-fortified-xalataths-guile')
    return affix_list

def fetch_run_page(page,dungeon='all',affixes='all', season_slug=SEASON_SLUG, region=REGION):
    """Fetch one page of runs from the raider.io API.

    Each API call returns a dict['rankings','leaderboard_url','params'].
    'rankings' is a list of runs, each a dict['rank','score','run'].
    'run' is a dict with many keys, the relevant one is 'roster'.
    'roster' is a list[5] of dict['character','role'].
    'character' has many keys, the important ones are 'name', 'realm','spec'.

    Keyword arguments:
        page -- the page number on the leaderboard, API allows up to 1000
        dungeon -- the dungeon slug to filter by, can be 'all'
        affixes -- the affix combo slug to filter by, can be 'all'
    """
    params = {
        'season': season_slug,
        'region': region,
        'dungeon': dungeon,
        'affixes': affixes,
        'page': page,
    }
    response = rio_api_call(RUNS_URL, params)['rankings']
    #print(f'\rgot response for {page},{dungeon},{affixes}', end='')
    return response

# def parallel_fetch_pages(dungeons, affix_combos, page_limit=PAGE_LIMIT, max_workers=4):
#     futures = []
#     pages = []
#     bar_get = progressbar.ProgressBar(max_value=len(dungeons)*len(affix_combos)*page_limit)
#     bar_append = progressbar.ProgressBar(max_value=len(dungeons)*len(affix_combos)*page_limit)
#     limiter = RateLimiter(limit=16, period=1)
#     # i = 0
#     # j = 0
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         for pagenum in range(page_limit):
#             for affix_combo in affix_combos:
#                 for dungeon in dungeons:
#                     limiter.acquire()
#                     futures.append(
#                         executor.submit(fetch_run_page,pagenum,dungeon,affix_combo)
#                     )
#                     bar_get.increment()
#         for future in as_completed(futures):
#             page = future.result()
#             #print(f'\racquired for {i}, completed for {j}', end='')
#             # j += 1
#             pages.append(page)
#             bar_append.increment()
#     return pages

def write_jsonl(data, filename, mode='a'):
    with open(filename, mode) as file:
        for object in data:
            file.write(json.dumps(object) + '\n')

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
#
# def parallel_fetch_rows(dungeons, affixes, page_limit=PAGE_LIMIT, max_workers=20):
#     futures = []
#     rows = []
#
#     bar = progressbar.ProgressBar(max_value=len(dungeons)*len(affixes)*page_limit)
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         for pagenum in range(page_limit):
#             for affix in affixes:
#                 for dungeon in dungeons:
#                     futures.append(
#                         executor.submit(fetch_run_page,pagenum,dungeon,affix)
#                     )
#         for future in as_completed(futures):
#             page = future.result()
#             for pagerow in page:
#                 rows.extend(make_rows_by_character(pagerow))
#             bar.increment()
#
#     return rows

dungeon_list = fetch_dungeons()
affix_list = make_affix_combos(AFFIXES_TWW_S2)

OUTPUT_FILE = 'rio_data_tww_s2.jsonl'
#Make a blank file to append to
with open(OUTPUT_FILE, 'w') as file: pass
futures = []
bar_get = progressbar.ProgressBar(
    max_value=len(dungeon_list) * len(affix_list) * PAGE_LIMIT)
bar_append = progressbar.ProgressBar(
    max_value=len(dungeon_list) * len(affix_list) * PAGE_LIMIT)
limiter = RateLimiter(limit=16, period=1)
with ThreadPoolExecutor(max_workers=4) as executor:
    for pagenum in range(PAGE_LIMIT):
        for affix_combo in affix_list:
            for dungeon in dungeon_list:
                limiter.acquire()
                futures.append(
                    executor.submit(fetch_run_page, pagenum, dungeon, affix_combo)
                )
                bar_get.increment()
    for future in as_completed(futures):
        write_jsonl(future.result(),OUTPUT_FILE)
        bar_append.increment()

# pages = []
# bar = progressbar.ProgressBar(
#   max_value=len(dungeon_list) * len(affix_list) * PAGE_LIMIT)
# for pagenum in range(PAGE_LIMIT):
#     for affix_combo in affix_list:
#         for dungeon in dungeon_list:
#             pages.append(fetch_run_page(pagenum,dungeon,affix_combo))
#             bar.increment()

#pages = parallel_fetch_pages(dungeon_list, affix_list)

#save_jsonl(pages, 'rio_data_tww_s2.jsonl', mode='w')

# bar = progressbar.ProgressBar(max_value=len(dungeon_list)*len(affix_list)*PAGE_LIMIT)
# with open('runs.csv', 'a', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     for pagenum in range(PAGE_LIMIT):
#         for affix in affix_list:
#             for dungeon in dungeon_list:
#                 page = fetch_run_page(pagenum,dungeon,affix)
#                 bar.increment()
#                 for pagerow in page:
#                     rows = make_rows_by_character(pagerow)
#                     writer.writerows(rows)