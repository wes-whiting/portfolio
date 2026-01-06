# Project Background and Overview

# Data Structure Overview

# Executive Summary

# Insights Deep Dive

# Recommendations

# Limitations & Assumptions
First, this is strictly observational data. Although we can see which practices more successful players have, it is risky to conclude that they are successful because of those practices. For example, out of the 21 paladins who made title, 12 were dwarves and only 2 were human. Is that because dwarves really are that much better, or is it because the kind of player who is dedicated enough to push for title is also dedicated enough to buy a race change for even a marginal benefit? So we should be careful about drawing strong conclusions that a certain practice is very beneficial, when instead the causation might run the other way.

Second, although the dataset is extensive, it is not complete. Our data was obtained from the raider.io API. Due to limitations of that API, we do not  have access to the entire recorded leaderboard, only the first 1000 pages of runs per category. In total, our dataset includes 1.4 million runs and 955 thousand players, while the full US leaderboard includes 8.7 millions runs and 1.05 million players.

The good news is that, since we have the first 1000 pages of runs sorted by score, the incompleteness should mostly be at lower brackets. For example, the first 1000 pages of the Darkflame Cleft leaderboard includes every single +15 or higher key (for reference, completing all dungeons at +15 corresponds to a rating of 3280). Conclusions about the highest brackets (3200 and above) should be robust.

Lastly, we cannot reliably track characters who have been transferred or renamed. Any character who was transferred or renamed mid-season will show up in our data as two different characters, or more if they were transferred multiple times, with ratings calculated separately. This pollutes the data with multiple incomplete characters that should be just one. However, since transfers and renames are relatively infrequent, this effect should be minor. Characters who were anonymized (eg, due to violating the naming policy) have been excluded from the data entirely; again, this is rare and the effect is minor.