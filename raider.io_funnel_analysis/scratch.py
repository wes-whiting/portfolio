from process_to_postgres import describe
from get_rio_data import fetch_run_page

page = (fetch_run_page(0))
print(page[0]['run']['keystone_run_id'])