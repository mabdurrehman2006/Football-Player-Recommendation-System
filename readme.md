


# WSL Striker Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4-F7931E.svg)

An intelligent, data-driven football scouting and recruitment platform that identifies similar attacking profiles in the Barclays Women's Super League (WSL). 

By leveraging raw event-level data from the **StatsBomb API** (2023/2024 season), the system isolates forward positions, aggregates season-long performance metrics, and uses **Cosine Similarity** to match player profiles based on tactical style rather than sheer team-volume output.

---

## 🚀 Project Evolution: From Local ML Script to Cloud Microservice

This project began as a standalone Python data analytics script using Pandas and Scikit-learn. To make the model accessible as a real-time scouting tool, it was re-architected into a modular, containerised REST API service:

* **Phase 1 (Data & ML Engine)**: ETL pipeline ingesting StatsBomb event data, Parquet local caching, Min-Max normalisation, and Cosine Similarity matching with a 15-shot Sample Size Guard.
* **Phase 2 (FastAPI Backend)**: Wrapped the recommender into an asynchronous REST API with strict Pydantic schemas, dynamic Enum dropdowns, and automatic Swagger UI docs.
* **Phase 3 (Containerisation)**: Packaged the full application and dependencies into a lightweight, secure Docker container running a non-root user.

---

## 🏗️ System Architecture

```
[ StatsBomb API ]
       │ (Initial fetch)
       ▼
[ data/WSL_2023-2024.parquet ] ──► [ src/data_loader.py ]
                                           │
                                           ▼ (Loaded into memory at boot)
                                  [ src/recommender.py ]
                                    • Attacking Position Filter
                                    • Sample Size Guard (>= 15 Shots)
                                    • Min-Max Normalisation
                                           │
                                           ▼
                                    [ src/main.py ]
                                    • FastAPI Routes (/status, /strikers, /recommend)
                                    • Pydantic Request & Response Validation
                                    • Dynamic Enum Dropdowns
                                           │
                                           ▼
                                  [ Docker Container / Swagger UI ]
```

### 1. Robust Data Ingestion (`src/data_loader.py`)
* Connects to the free StatsBomb API to fetch match events for the complete WSL 2023/2024 season.
* Implements automated local caching via compressed `.parquet` files using `pathlib.Path.resolve()` to avoid redundant API network requests and maximise startup speed.

### 2. Tactical Profiling Pipeline (`src/recommender.py`)
* **Dynamic Position Filter**: Extracts players assigned to authentic forward roles (`Center Forward`, `Left/Right Wing`, `Secondary Striker`, etc.), screening out defenders and midfielders.
* **Metric Aggregation**: Aggregates event streams into seasonal **Goals**, **Expected Goals (xG)**, **Shots**, and **Assists**.
* **Sample Size Guard**: Filters out statistical noise by dropping any player with fewer than **15 shots** across the season, eliminating low-minute substitutes and fluke conversion rates.

### 3. Mathematical Matcher (`src/recommender.py`)
* **Min-Max Normalisation**: Standardises features to a strict `0.0 to 1.0` range using `MinMaxScaler`. This ensures high-volume metrics like *Shots* do not drown out low-volume, high-value metrics like *xG* or *Assists*.
* **Cosine Similarity**: Evaluates the angular vector balance of a player's style (e.g. shot-to-goal conversion, goal-to-assist balance) so top performers in struggling teams match with superstars in dominant teams.

### 4. REST API & Validation Layer (`src/main.py`)
* **FastAPI Service**: Serves endpoints with sub-millisecond in-memory query lookups.
* **Pydantic Schemas (`SimilarToPlayer`, `ScoutingReport`)**: Strict data contracts validating input parameters and sanitising outgoing JSON dossiers.
* **Dynamic Enums**: Generates string Enums from the dataset index to render interactive dropdown selectors in the Swagger UI (`/docs`).

---

## 📂 Repository Structure

```text
Football-Player-Recommendation-System/
│
├── data/
│   └── WSL_2023-2024.parquet          # Compressed StatsBomb event data cache
│
├── src/
│   ├── __init__.py                    # Declares src as a regular Python package
│   ├── data_loader.py                 # Data ingestion & Parquet cache loader
│   ├── recommender.py                 # Core ML engine: filtering & Cosine Similarity
│   └── main.py                        # FastAPI web application & Pydantic schemas
│
├── Dockerfile                         # Production container recipe (Python 3.13-slim)
├── .dockerignore                      # Build exclusions (caches, git metadata, env)
├── requirements.txt                   # Pinned Python dependencies
├── .gitignore                         # Git tracking exclusions
└── readme.md                          # Project documentation
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description | Response Model |
| :--- | :--- | :--- | :--- |
| `GET` | `/status` | Health check probe for uptime monitoring. | `{"status": "...", "code": 200}` |
| `GET` | `/strikers` | Returns list of all eligible strikers in dataset. | `{"strikers": [...]}` |
| `POST` | `/recommend` | Generates a full scouting dossier with target stats & top matches. | `ScoutingReport` |

---

## 💻 Quickstart: How to Run

### Method A: Running Locally with Python & Uvicorn

1. **Clone the repository and install dependencies**:
   ```bash
   git clone https://github.com/mabdurrehman2006/Football-Player-Recommendation-System.git
   cd Football-Player-Recommendation-System
   pip install -r requirements.txt
   ```

2. **Start the FastAPI development server**:
   ```bash
   uvicorn src.main:app --reload
   ```

3. **Open the interactive Swagger UI documentation**:
   Visit [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

---

### Method B: Running with Docker (Recommended)

1. **Build the Docker container image**:
   ```bash
   docker build -t wsl-scouting-app .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8080:8080 wsl-scouting-app
   ```

3. **Access the live service**:
   Visit [http://localhost:8080/docs](http://localhost:8080/docs) in your browser.

---

## 📊 Example Scouting Dossier Output

When querying recommendations for a striker (e.g. `Lauren James`, `numberofrecs = 2`), the API returns a structured `ScoutingReport` JSON response:

```json
{
  "target_player_stats": {
    "Player": "Lauren James",
    "Similarity": 100.0,
    "Goals": 13,
    "Expected_Goals": 9.20,
    "Shots": 45,
    "Assists": 5
  },
  "recommendations": [
    {
      "Player": "Alessia Russo",
      "Similarity": 94.20,
      "Goals": 12,
      "Expected_Goals": 10.15,
      "Shots": 48,
      "Assists": 4
    },
    {
      "Player": "Lauren Hemp",
      "Similarity": 89.70,
      "Goals": 9,
      "Expected_Goals": 7.80,
      "Shots": 38,
      "Assists": 6
    }
  ]
}
```

---

## 🧠 Design Choice: Cosine Similarity vs Euclidean Distance

* **Euclidean Distance** measures the physical straight-line distance between data points. This creates a severe flaw where a world-class striker playing for a struggling club with fewer chances would never match with a forward playing for a dominant team due to the sheer volume gap.
* **Cosine Similarity** measures the angle of direction from the origin. It evaluates the mathematical balance and style ratios of the player (e.g. shot-to-goal conversion, assist-to-goal balance, xG efficiency). By dividing by the vector lengths, total team volume is cancelled out, allowing scouts to find authentic tactical matches regardless of team dominance.

