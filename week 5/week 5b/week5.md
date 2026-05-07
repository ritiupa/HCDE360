# Week 5 Competency Claims

## C5 -- Data Analysis with Pandas

I used pandas to run five analytical operations on `design_trends.csv`, the output of my A4 Wikipedia Pageviews script. The dataset has 50 rows, one per HCI or UX-related Wikipedia article, with 17 columns covering traffic totals, averages, peak dates, and momentum classifications across a 90-day window.

The most interesting finding came from question 4: grouping by momentum category and averaging total views. I expected Rising articles to be the highest-traffic ones, but the data showed the opposite. Fading articles had higher average total views than Rising ones. That means the topics currently growing in public curiosity are not the dominant ones yet. They are emerging from low traffic but accelerating, which suggests the next wave of public interest in HCI topics is still forming rather than already established.

Question 3 confirmed this: filtering to Rising articles and sorting by percentage change showed that Bad Day (viral video) had 100% growth, while most other Rising articles were growing at 10 to 20%. That is a meaningful difference in signal strength. A 100% jump in a single 30-day window is more likely to reflect a real external event than organic trend growth, so I noted it as an outlier worth investigating rather than a representative finding.

Question 5 flagged a data quality issue: several articles had fewer than 90 days of recorded views, meaning Wikipedia had zero traffic on some days. The momentum labels for those articles are less reliable because the 30-day comparison windows may be uneven. I documented this as a limitation that would need to be addressed before drawing strong conclusions from those specific rows.
