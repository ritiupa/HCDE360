# Week 6 -- Chart Justifications and Competency Claim

## Note on Question Changes

The original MP1a questions were refined after professor feedback and after thinking through what is actually feasible with pandas and Plotly. Q2 originally proposed full sentiment scoring on surrounding words, which needs specialized NLP tools beyond what this course covers. It was reframed as **emotion-keyword neighbor** analysis: only words from a curated affect/attitude lexicon are counted near technology terms, so the charts track how emotional language around tech shifts over time—not random high-frequency words like *know*, *use*, or *call*. **`fetch_cornell.py` only tags lines with technology terms and exports CSVs; the emotion lexicon and Q2 charts live in `week6_cornell_analysis.ipynb`.** Q3 originally asked about grammatical subject vs object, which requires dependency parsing. It was reframed as a sentence position proxy, and expanded to compare communication technology terms against computational technology terms rather than treating all tech as one group. This made it possible to answer without any manual tagging or advanced NLP.

---

## Chart 1 -- Technology Term Frequency by Decade

**File:** chart1_tech_frequency_by_decade.png

**Question it answers:** Q1 -- Which technology terms appear first and how does frequency change across decades?

**Why this chart type:** The question is about change over time across many periods. The class chart guide maps this to a line chart. Each line is one term so you can compare trajectories directly. A bar chart would make it hard to follow individual terms across eight decades.

**What someone could misread:** Higher frequency does not mean the term is more culturally important. Phone will appear more often than algorithm simply because phone refers to a more everyday thing. The y-axis shows mentions per 1000 lines, not raw counts, to account for the fact that some decades have more films in the corpus than others.

---

## Chart 2a and 2b -- Emotion Keywords Near Tech Terms (Pre vs Post 1990)

**Files:** chart2a_emotion_near_tech_pre1990.png, chart2b_emotion_near_tech_post1990.png

**Question it answers:** Q2 -- Which emotion-related words appear near technology terms, and how does that vocabulary shift across eras?

**Why this chart type:** Two separate horizontal bar charts, one per time period. Horizontal bars work better than vertical here because word labels are long and easier to read on the y-axis. Two separate charts instead of a grouped chart keeps each era's vocabulary readable without crowding. You read each list on its own and compare by looking across the two charts.

**What someone could misread:** The y-axis lists only **lexicon hits** (curated affect/attitude words), not every word near a tech term. The x-axis is **mentions per 1,000 lines that contain a technology term**, so the two eras are comparable despite different corpus sizes. A keyword list cannot handle negation or sarcasm (for example, “not afraid” still counts the token *afraid*), so the charts show **lexical co-presence** with tech in a short window, not full sentiment or intent.

---

## Chart 3 -- Agency Shift by Technology Category

**File:** chart3_agency_by_category.png

**Question it answers:** Q3 -- Does technology shift toward sentence-initial position across decades, and does it happen at different rates for communication vs computational tech?

**Why this chart type:** A line chart with two lines, one per category. The question is about change over time for two groups, which is exactly what a multi-line chart shows. No manual tagging is needed because the categories were defined in the fetch script when each term was classified as communication or computational. The position threshold of 0.33 was chosen to identify the first third of a sentence as a proxy for subject position.

**What someone could misread:** Sentence position is a proxy, not a direct measure of grammatical agency. A term appearing in the first third of a sentence is more likely to be the subject but that is not guaranteed. The chart supports a directional argument rather than a precise linguistic finding.

---

## C6 -- Data Visualization Competency Claim

I built three charts from the Cornell Movie Dialogs Corpus using Plotly. Each chart answers a different analytical question and uses the chart type the class framework maps to that kind of question. Q1 uses a line chart because the question is about change over time across many periods. Q2 uses two horizontal bar charts to compare pre- and post-1990 **emotion-keyword** rates near tech terms (normalized per 1,000 tech-containing lines). Q3 uses a multi-line chart to compare two trend lines across decades. Each chart has a title that states the finding rather than just describing the data, labeled axes with units, and a markdown cell below it explaining what the chart argues and what a reader could misread. I also normalized Q1 frequency by total lines per decade to avoid decades with more films dominating the result. That is a deliberate choice about what the chart is actually claiming.
