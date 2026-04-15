# Week 2 Competency Claims

## C1: Vibecoding and Rapid Prototyping

I used Cursor's agent to build a standalone HTML dashboard (`dashboard.html`) that visualizes survey response data from `demo_responses.csv`, showing total responses, unique roles, average word count, and the longest response. After the first version was generated, I noticed it had no way to compare verbosity across roles, so I prompted Cursor to add an Average Word Count by Role panel. That was a deliberate decision about what insight was missing, not just a cosmetic change.

## C2: Code Literacy and Documentation

I added inline comments to `demo_word_count.py` across every major section, writing them from a beginner's perspective to explain not just what the code does but why it works that way. The section I spent the most time understanding was the `for row in responses` loop, specifically that each row is a dictionary and can be accessed by column name like `row["role"]` rather than by position. I also commented on formatting syntax like `:<6` and `:.1f` that looked like noise at first glance but control how the output is aligned and rounded.
