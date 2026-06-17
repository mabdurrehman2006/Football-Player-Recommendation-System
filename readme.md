


# WSL Striker Recommender Engine

An intelligent, data-driven football scouting and recruitment tool that identifies similar attacking profiles in the Barclays Women's Super League (WSL). By leveraging raw event-level data from the **StatsBomb API**, the system isolates forward positions, aggregates season-long performance metrics, and uses **Cosine Similarity** to match player profiles based on their tactical style rather than sheer team-volume output. WSL was chosen as the free version of the **StatsBomb** API has the complete 2023/2024 season for all teams.


## Features & Architecture

The system is split into three main modules designed to handle everything from raw data to recommendation:


```

[ StatsBomb API / Cache ]  
[ Data Filtering Pipeline ]  
[ Cosine Recommender Engine ]


```

1. **Robust Data Ingestion (`data_loader.py`)**
   * Connects to the free StatsBomb API to fetch event streams for the entire WSL 2023/2024 season
   * Implements automated local caching via `.parquet` files using `pathlib` to avoid redundant network requests and maximize speed

2. **Tactical Profiling Pipeline (`filter_data`)**
   * **Dynamic Position Filter:** Scans the event records to extract unique player IDs assigned to authentic attacking roles (`Center Forward`, `Left/Right Wing`, `Secondary Striker` etc). This screens out center backs or defensive midfielders
   * **Organises data:** Organises thousands of match events into a single spreadsheet style matrix containing seasonal **Goals**, **Expected Goals (xG)**, **Shots**, and **Assists**.
   * **Sample Size Guard:** Filters out noise by dropping any player with fewer than **15 shots** across the season, eliminating low-minute substitutes and fluke statistical conversion rates.

3. **Mathematical Matcher (`get_similar_players`)**
   * **Min-Max Normalization:** Standardizes features to a strict `0.0 to 1.0` range using `scikit-learn`'s `MinMaxScaler`. This ensures high volume categories like *Shots* do not drown out low volume, high value metrics like *Expected Goals*.
   * **Cosine Similarity:** Uses angular vector metrics instead of straight line Euclidean distance. This evaluates the **shape and balance of a player's style** (e.g. goal-to-assist ratios) so top performers in struggling teams can still match perfectly with superstars in dominant teams.

---

## Project Structure


- ### data_loader.py          
   Fetches match events and manages local Parquet cache
- ### main.py          
   Filters positions, aggregates stats, and calculates similarities
- ### WSL_2023-2024.parquet   
   Local data cache created automatically on first run
- ### final.ipynb / predictor.py  
   Execution script or notebook to run scouting reports





##  Installation & Requirements

Ensure you have Python installed alongside the required data science and sports analytics libraries:

```bash
pip install pandas numpy scikit-learn statsbombpy pyarrow

```





## Example Execution Output

```python
# How to call your pipeline
raw_data = get_wsl_data()
scouting_matrix = filter_data(raw_data)

# Generate an algorithmic scouting report
recommend_striker_profile(scouting_matrix, "Lauren James")

```

**Expected Console Output Layout:**

```text
==========================================
 SCOUTING REPORT: LAUREN JAMES
==========================================
CURRENT PROFILE:
    Goals:   13
    xG:      9.20
    Shots:   45
    Assists: 5
------------------------------------------
MOST SIMILAR ALTERNATIVES:

1. Player X (94.2% Match)
    Goals:   11
    xG:      8.45
    Shots:   42
    Assists: 4

2. Player Y (89.7% Match)
    Goals:   14
    xG:      9.10
    Shots:   48
    Assists: 2

==========================================

```

---

## Design choice: Cosine vs Euclidean?

- **Euclidean Distance** measures the literal physical distance between data points. This creates a flaw where a world-class forward playing for a weaker team with fewer chances would never be recommended as a replacement for a striker playing in a dominant team due to the big difference in stats.
- **Cosine Similarity** measures the *angle of direction* from the origin. It tracks the mathematical balance and shape of the statistics. If two players possess an identical goal-to-assist or shot-to-goal ratio, Cosine Similarity identifies them as matches regardless of team strength.
