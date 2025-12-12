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