# Project Background and Overview
World of Warcraft, released in 2004, is still one of the biggest video games in the world. A popular game mode is its mythic keystone dungeons, commonly referred to as "Mythic Plus", "Mythic+", or "M+". Players can climb the leaderboard by completing increasingly difficult versions of each dungeon, increasing their rating to earn both in-game rewards and community prestige.

Raider.IO is a third-party website that aggregates this leaderboard data, and gives access to this data through its API. This project collects, processes, and analyzes data from the most recent full season (Season 2 of "The War Within" expansion) to uncover critical insights into the behaviors of successful players.

This project aims to provide insight on the following key areas and questions:

* **Climb Early** M+ is a team sport, and so you are more successful when you have good teammates. A common piece of advice in the M+ community is that it is easier to climb early in the season, when the best players are still in lower brackets with you. To what degree is this true?
* **Playing the Meta:** Players can choose from a wide variety of classes, races, and specs to play as, but the playerbase tends to favor some over others. How much effect on your rating does playing meta have compared to playing off-meta?
* **Role Comparison:** Tanks and healers are often in high demand. Does playing an in-demand role provide an easier path to success?

An interactive Power BI dashboard can be found here ________

The Python code to download and process the Raider.io API data into a Postgres database can be found here ___________

The SQL queries used to clean and transform the data can be found here ________ 

# Data Structure Overview

# Executive Summary

# Insights Deep Dive

# Recommendations

# Limitations & Assumptions
First, this is strictly observational data. Although we can see which practices more successful players have, it is risky to conclude that they are successful because of those practices. For example, out of the 21 paladins who made title, 12 were dwarves and only 2 were human. Is that because dwarves really are that much better, or is it because the kind of player who is dedicated enough to push for title is also dedicated enough to buy a race change for even a marginal benefit? So we should be careful about drawing strong conclusions that a certain practice is very beneficial, when instead the causation might run the other way.

Second, although the dataset is extensive, it is not complete. Our data was obtained from the raider.io API. Due to limitations of that API, we do not  have access to the entire recorded leaderboard, only the first 1000 pages of runs per category. In total, our dataset includes 1.4 million runs and 955 thousand players, while the full US leaderboard includes 8.7 millions runs and 1.05 million players.

The good news is that, since we have the first 1000 pages of runs sorted by score, the missing runs are strictly at lower brackets. For example, the first 1000 pages of the Darkflame Cleft leaderboard includes every single +15 or higher key (for reference, completing all dungeons at +15 corresponds to a rating of 3280). Conclusions about the highest brackets (3200 and above) should be robust.

Lastly, we cannot reliably track characters who have been transferred or renamed. Any character who was transferred or renamed mid-season will show up in our data as two different characters, or more if they were transferred multiple times, with ratings calculated separately. This pollutes the data with multiple incomplete characters that should be just one. However, since transfers and renames are relatively infrequent, this effect should be minor. Characters who were anonymized (eg, due to violating the naming policy) have been excluded from the data entirely; again, this is rare and the effect is minor.