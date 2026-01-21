# Project Background and Overview
World of Warcraft, released in 2004, is still one of the biggest video games in the world, boasting millions of active players. A popular game mode is its mythic keystone dungeons, commonly referred to as "Mythic Plus", "Mythic+", or "M+". Players can climb the leaderboard by completing increasingly difficult versions of each dungeon, increasing their rating to earn both in-game rewards and community prestige.

Raider.IO is a third-party website that aggregates this leaderboard data, and gives access to this data through its API. This project collects, processes, and analyzes data from the most recent full season (Season 2 of "The War Within" expansion) to uncover critical insights into the behaviors of successful players.

This project aims to provide insight on the following key areas and questions:

* **Climb Early:** M+ is a team sport, and so you are more successful when you have good teammates. A common piece of advice in the M+ community is that it is easier to climb early in the season, when the best players are still in lower brackets with you. To what degree is this true?
* **Playing the Meta:** Players can choose from a wide variety of classes, races, and specs to play as, but the playerbase tends to favor some over others. How much effect on your rating does playing meta have compared to playing off-meta?
* **Role Comparison:** Tanks and healers are often in high demand. Does playing an in-demand role provide an easier path to success?

This repository includes:

* A Power BI dashboard, available as a [.pbix file](https://github.com/wes-whiting/portfolio/blob/main/raider.io_funnel_analysis/Mythic%2B%20Rating%20Funnel%20Dashboard.pbix). Screenshots of the dashboard will be included throughout this document to support the analysis.

* Python code to [download](https://github.com/wes-whiting/portfolio/blob/main/raider.io_funnel_analysis/get_rio_data.py) the raw Raider.IO data and [insert](https://github.com/wes-whiting/portfolio/blob/main/raider.io_funnel_analysis/process_to_postgres.py) it into a PostgreSQL database . Note that the raw Raider.IO data for a season is several GB, which is much too large to include in Github, and due to API rate limits, downloading this data takes hours regardless of machine or network speed.

* SQL queries to [clean](https://github.com/wes-whiting/portfolio/blob/main/raider.io_funnel_analysis/queries/1_clean_runs_raw.sql) the data, [transform](https://github.com/wes-whiting/portfolio/blob/main/raider.io_funnel_analysis/queries/2_make_tables.sql) it into relevant tables, and finally [compute](https://github.com/wes-whiting/portfolio/blob/main/raider.io_funnel_analysis/queries/3_make_thresholds.sql) the relevant KPIs used in the dashboard.

# Data Structure and Pipeline

![Data pipeline image](pipeline.svg)

The raw data from the Raider.IO API comes in JSON format with a complex nested structure and many keys, much of it irrelevant for our purpose. I queried the data in Python and stored the raw responses as a large .jsonl file. This gives a clean separation between data procurement and data processing, and allows me to include additional metrics in the future without needing to re-query the API. Then, I flattened the JSON data to one row per character and dungeon run, keeping only the relevant attributes: character demographic data (name, realm, class, spec, role, faction, race) and run data (dungeon, level, completion time, score).

These rows were inserted into a PostgreSQL database in a table `runs_raw`. At this step, I cleaned the data with SQL queries to drop null entries and anonymized characters, and convert timestamp data from strings to the proper data type `timestamptz`. Since data will be tabulated character-wise, I made an index on `(name, realm, class, spec)` since these keys together uniquely identify a character.

For each character, we want to construct their score history. This means that on each run, we annotate their running max score for each dungeon, and their running total score, creating a new annotated table `runs_enriched`. For this project I used TWW season 2, but to make the query reusable for another season with a different dungeon pool, I first generated a small dimension table `dungeons` and used it to dynamically generate the running max columns.

With the score history reconstructed, we can finally make a table `characters`, aggregating data from individual runs to determine if and when each character crossed each progression milestone. The `characters` table contains the data used in the final dashboard.

# Executive Summary

# Insights Deep Dive

# Recommendations

# Limitations & Assumptions
First, this is strictly observational data. Although we can see which practices more successful players have, it is risky to conclude that they are successful because of those practices. For example, out of the 21 paladins who made title, 12 were dwarves and only 2 were human. Is that because dwarves really are that much better, or is it because the kind of player who is dedicated enough to push for title is also dedicated enough to buy a race change for even a marginal benefit? So we should be careful about drawing strong conclusions that a certain practice is very beneficial, when instead the causation might run the other way.

Second, although the dataset is extensive, it is not complete. Our data was obtained from the raider.io API, and due to limitations of that API, we do not  have access to the entire recorded leaderboard, only the first 1000 pages of runs per dungeon-affix combination (at 20 runs per page), and many of these categories have over 1000 pages. In total, our dataset includes 1.4 million runs and 955 thousand players, while the full US leaderboard includes 8.7 millions runs and 1.05 million players.

The good news is that, since we have the first 1000 pages of runs sorted by score, the missing runs are strictly at lower brackets. For example, the first 1000 pages of the Darkflame Cleft leaderboard includes every single +15 or higher key (for reference, completing all dungeons at +15 corresponds to a rating of 3280). Conclusions about the highest brackets (3200 and above) should be robust.

Lastly, we cannot reliably track characters who have been transferred or renamed. Any character who was transferred or renamed mid-season will show up in our data as two different characters, or more if they were transferred multiple times, with ratings calculated separately. This pollutes the data with multiple incomplete characters that should be just one. However, since transfers and renames are relatively infrequent, this effect should be minor. Characters who were anonymized (eg, due to inappropriate names that violate the naming policy) have been excluded from the data entirely; again, this is rare and the effect is minor.