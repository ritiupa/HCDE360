# Week 4 Competency Claims

## C4- APIs and Data Acquisition:

I used the Wikimedia Pageviews REST API to pull 90 days of daily Wikipedia article traffic for five UX/UI design trends: Glassmorphism, Neumorphism, Flat Design, Dark Mode, and Skeuomorphism. The endpoint returns daily view counts per article, which I used as a proxy for public interest in each trend. When a design style is getting attention, people look it up. The API is fully public, requires no key, and returns clean JSON. I chose this over pytrends (the common Google Trends library) because pytrends is an unofficial scraper that breaks frequently and would be unreliable for an assignment with a deadline.

The script extracts total views over 90 days, average daily views, peak day, and a momentum classification computed by comparing the most recent 30 days of traffic against the 30 days before that. It also generates lcd_line1 and lcd_line2 fields for each trend, formatted to 16 characters, which feed directly into the Arduino LCD display built for my physical computing course.


## Description:

I chose this topic because as a designer, I find it hard to keep up what is trending. Bento grids are in, skeuomorphism is back, flat design is dead; but I would like to also see data with the claims. I wanted to see if public interest in design trends could actually be measured. I selected the Wikimedia Pageviews API because it is free, official, requires no key, and article traffic is a genuinely clean signal: when people are curious about a trend, they look it up. I also chose it over pytrends because that library is an unofficial Google scraper that breaks frequently and I needed something reliable for a deadline. The script pulls 90 days of daily traffic for five design styles, computes momentum by comparing the most recent 30 days against the prior 30, and classifies each trend as Rising, Peaked/Stable, or Fading. It was also interesting to integrate this with my physical computing course by formatting the output as 16-character strings for an Arduino LCD display.


## Reflection:

Design trends are not neutral. They shape what gets built, what gets valued in portfolios, and what designers feel pressure to learn. The industry's conversation about trends is largely qualitative and it lives in blog posts, Twitter threads, and conference talks. Making the trend lifecycle measurable rather than opinionated is directly useful for practitioners: instead of absorbing a general feeling from the discourse, a designer can look at whether interest in a style is actually climbing, plateauing, or declining over time. This kind of data will not replace design judgment, but it can help designers make more informed decisions about what to learn. It can also surface something new, a term with rising traffic that has not yet broken into the mainstream conversation is worth paying attention to before everyone else is talking about it.