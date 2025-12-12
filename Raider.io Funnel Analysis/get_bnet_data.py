import requests
import sqlite3
import pandas as pd
import progressbar
import time
import datetime

CLIENT_ID = 'db7c135ef2f14e4381d0669283fd273b'
CLIENT_SECRET = '8yZ3aEgaDoP7rErZ1YChG1k5idbPD17U'
NAMESPACE = 'profile-us'
LOCALE = 'en-US'
SEASON = 'season-tww-2'
ACHIEVEMENT_IDS =   {'season-tww-2':
                       {
                           'KSE': 40949,
                           'KSC': 40950,
                           'KSM': 41533,
                           'KSH': 40952,
                           'KSL': 40951,
                           'Title': 40954,
                       },
                    }

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

def get_bnet_access_token(id,secret):
    url = 'https://oauth.battle.net/token'

    response = requests.post(
        url,
        data={'grant_type': 'client_credentials'},
        auth=(id, secret)
    )

    response.raise_for_status()  # raises exception on 4xx/5xx
    token = response.json()['access_token']
    return token

def bnet_api_call(suffix, params, token, region='us'):
    base_url = f'https://{region}.api.blizzard.com'
    header = {'Authorization': f'Bearer {token}'}
    params['namespace'] = NAMESPACE
    params['locale'] = LOCALE
    attempts=1
    while True:
        try:
            response = requests.get(base_url + suffix,params=params, headers=header)
            response.raise_for_status()
            break
        except:
            print(f'Attempt {attempts} failed. Retrying...')
            attempts += 1
            time.sleep(1)
    return response.json()

def get_character_achievements(characterName, realmSlug, token):
    """Makes an API call for character achievement info.

    API call gives a dict, the key ['Achivement'] is a list of dicts
    with keys 'id' (number), 'achievement' (name), and 'completed_timestamp'.

    Keyword arguments:
        characterName -- the name of the character.
        realmSlug -- the slug of the realm, eg wyrmrest-accord
        token - oauth token, probably from get_bnet_access_token()
    """
    suffix = f'/profile/wow/character/{realmSlug}/{characterName.lower()}/achievements'
        #API requires name to be lowercase
    return bnet_api_call(suffix, params={}, token=token)['achievements']

def get_achievement_time(achievements, target_id):
    """Returns completion time of an achievement, or None if incomplete.

    Keyword arguments:
          achievements -- the list of achievements, probably from get_character_achievements()
          target_id -- the id of the achievement you want, look up in ACHIEVEMENT_IDS
    """
    for entry in achievements:
        if entry['id'] == target_id:
            x = entry['completed_timestamp'] #Unix timestamp in milliseconds
            return x
            #return datetime.datetime.fromtimestamp(x/1000)
    return None

def make_achievement_columns(name, realm, token, season=SEASON):
    ids = ACHIEVEMENT_IDS[season]
    achievements = get_character_achievements(name, realm, token)
    achievementStatus = {
        'KSE': get_achievement_time(achievements, ids['KSE']),
        'KSC': get_achievement_time(achievements, ids['KSC']),
        'KSM': get_achievement_time(achievements, ids['KSM']),
        'KSH': get_achievement_time(achievements, ids['KSH']),
        'KSL': get_achievement_time(achievements, ids['KSL']),
        'Title': get_achievement_time(achievements, ids['Title']),
    }
    return achievementStatus

conn = sqlite3.connect('TWW_S2.db')
df = pd.read_sql_query(
    """
    SELECT *
    FROM characters
    ORDER BY name
    LIMIT 5
    """,
    conn
    )
print(df)

# token = get_bnet_access_token(CLIENT_ID, CLIENT_SECRET)
#
# df['KSE','KSC','KSM','KSH','KSL','Title'] = df.apply(
#     lambda row: make_achievement_columns(row['Name'], row['Realm'], token),
#     axis=1)

#
# #x = get_character_achievements('Ravicana', 'wyrmrest-accord', token)
# #describe(x)
# print(make_achievement_columns('Ravicana', 'wyrmrest-accord', token))