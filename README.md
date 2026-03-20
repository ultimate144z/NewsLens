# NewsLens — Multi-Source News Sentiment & Bias Analyzer

<div align="center">

[![CI](https://github.com/ultimate144z/NewsLens/actions/workflows/ci.yml/badge.svg)](https://github.com/ultimate144z/NewsLens/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E.svg)](https://huggingface.co/transformers/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![spaCy](https://img.shields.io/badge/spaCy-NER-09A3D5.svg)](https://spacy.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**An end-to-end NLP pipeline that reveals how different news outlets frame the same stories.**

[Features](#features) • [Quick Start](#quick-start) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture) • [Docker](#docker) • [Contributing](#contributing)

</div>

---

## Overview

NewsLens is a **sentiment analysis and media bias detection system** that:

- Aggregates headlines from multiple RSS feeds (BBC, CNN, Al Jazeera, Reuters, Fox News, Guardian, NYT, Washington Post) and NewsAPI
- Classifies sentiment with a state-of-the-art RoBERTa transformer (`cardiffnlp/twitter-roberta-base-sentiment-latest`)
- Extracts named entities (people, organisations, locations) with spaCy NER
- Stores historical data in SQLite for temporal analysis
- Visualises trends and source-level bias in an interactive Streamlit dashboard

**Use Cases:** Data science portfolios · NLP research · media monitoring · bias detection · journalistic tooling.

---

## Features

### Multi-Source Data Aggregation
- **8 RSS Feeds** — BBC, CNN, Al Jazeera, Reuters, Fox News, Guardian, NYT, Washington Post
- **NewsAPI Integration** — 70,000+ additional sources worldwide
- **Configurable** — add or remove sources via a single YAML file

### Advanced NLP Analysis
- **Sentiment Classification** — positive / neutral / negative with per-class confidence scores
- **Named Entity Recognition** — people, organisations, geopolitical entities, dates, money
- **Keyword Extraction** — noun-phrase frequency analysis with spaCy
- **Confidence Scoring** — track model certainty for every prediction

### Interactive Analytics Dashboard
- **Sentiment Trends** — time-series charts of how coverage tone shifts day-by-day
- **Source Comparison** — side-by-side bias scores and sentiment profiles per outlet
- **Entity Tracking** — most-mentioned people, places, and organisations
- **Keyword Analysis** — frequency bar charts
- **Real-time Filtering** — by source, sentiment, date range, keyword, confidence threshold

### Trend & Comparison Engine
- `TrendAnalysis` — rolling sentiment momentum, keyword trends over time, volume by source
- `SourceComparison` — headline overlap detection, per-source entity focus, confidence comparison

### Robust Data Storage
- **SQLite** with optimised indexes for fast querying
- **CSV Export** — full articles, sentiment summaries, entity rankings
- **JSON Archives** — timestamped pipeline snapshots for reproducibility

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/ultimate144z/NewsLens.git
cd NewsLens

# 2. Install (Python 3.9+)
make install          # pip install + spaCy model + NLTK data

# 3. (Optional) add NewsAPI key
cp .env.template .env  # then edit .env: NEWSAPI_KEY=your_key

# 4. Run full pipeline
make run              # ingest → preprocess → analyze → store → analytics

# 5. Launch dashboard
make dashboard        # opens http://localhost:8501
```

Or with Docker — no Python setup required:

```bash
docker-compose up dashboard          # dashboard only
docker-compose run --rm pipeline     # full pipeline
```

---

## Installation

### Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.9 | 3.11 |
| RAM | 4 GB | 8 GB |
| Disk | 2 GB | 4 GB |
| NewsAPI key | optional | free tier |

### Step-by-step

```bash
# Clone the repository
git clone https://github.com/ultimate144z/NewsLens.git
cd NewsLens

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Download the spaCy language model
python -m spacy download en_core_web_sm

# Download NLTK data
python -m nltk.downloader punkt stopwords wordnet averaged_perceptron_tagger omw-1.4

# (Optional) configure NewsAPI
cp .env.template .env
# Edit .env and set: NEWSAPI_KEY=your_api_key_here
```

---

## Usage

### Makefile shortcuts (recommended)

```bash
make install       # Full setup
make run           # Complete pipeline
make dashboard     # Launch UI
make test          # Run test suite
make lint          # flake8
make format        # black
make help          # All commands
```

### Pipeline CLI

```bash
python run.py --full              # Complete pipeline
python run.py --full --dashboard  # Pipeline + launch dashboard
python run.py --ingest            # Ingest only
python run.py --dashboard         # Dashboard only
```

### Direct Streamlit

```bash
streamlit run app/dashboard.py
```

Dashboard opens at `http://localhost:8501`.

---

## Docker

No Python environment needed — just Docker.

```bash
# Build image
docker-compose build

# Start dashboard (http://localhost:8501)
docker-compose up dashboard

# Run full pipeline (writes to ./data)
docker-compose run --rm pipeline

# Pass a NewsAPI key
NEWSAPI_KEY=your_key docker-compose up dashboard
```

The `./data` directory is mounted as a volume so data persists between runs.

---

## Architecture

### Pipeline

```
RSS Feeds + NewsAPI
        │
        ▼
  Data Ingestion          src/ingestion/
  (feedparser + newsapi)
        │
        ▼
  Preprocessing           src/preprocessing/
  (NLTK clean + tokenise)
        │
        ▼
  NLP Analysis            src/analysis/
  (RoBERTa sentiment +
   spaCy NER)
        │
        ▼
  Storage                 src/storage/
  (SQLite + CSV)
        │
        ▼
  Analytics Engine        src/analytics/
  (trends + bias)
        │
        ▼
  Streamlit Dashboard     app/
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Collection** | feedparser, newsapi-python, requests | Multi-source aggregation |
| **NLP** | HuggingFace Transformers, spaCy, NLTK | Sentiment & entity analysis |
| **ML Framework** | PyTorch | Transformer inference |
| **Data Processing** | pandas, numpy | Analytics & manipulation |
| **Storage** | SQLite (via sqlite3) | Persistent article store |
| **Visualisation** | Streamlit, Plotly | Interactive dashboard |
| **Configuration** | PyYAML, python-dotenv | Settings management |
| **Logging** | loguru | Structured logging |
| **Testing** | pytest, pytest-cov | Unit tests & coverage |

---

## Project Structure

```
NewsLens/
│
├── app/                        # Streamlit dashboard
│   ├── dashboard.py            # Entry point
│   ├── utils.py                # Data loading & helpers
│   ├── components/
│   │   ├── charts.py           # Reusable Plotly chart functions
│   │   ├── filters.py          # Sidebar filter widgets + article filtering
│   │   └── tables.py           # Article and metric table renderers
│   └── pages/
│       ├── 1_Overview.py       # Key metrics & sentiment summary
│       ├── 2_Sentiment.py      # Sentiment deep-dive
│       └── 3_Sources.py        # Source comparison & bias
│
├── src/                        # Core logic
│   ├── ingestion/
│   │   ├── rss_scraper.py      # RSS feed scraper (8 sources)
│   │   └── newsapi_scraper.py  # NewsAPI client
│   ├── preprocessing/
│   │   └── preprocess.py       # Text cleaning pipeline
│   ├── analysis/
│   │   ├── sentiment.py        # RoBERTa sentiment analyser
│   │   └── entities.py         # spaCy NER + keyword extraction
│   ├── storage/
│   │   ├── database.py         # SQLite manager
│   │   └── csv_manager.py      # CSV export
│   └── analytics/
│       ├── analytics.py        # Core analytics & summary generator
│       ├── trend_analysis.py   # Temporal trend engine
│       └── compare_sources.py  # Source comparison engine
│
├── config/
│   ├── rss_feeds.yaml          # Feed URLs & scraping settings
│   ├── newsapi_config.yaml     # NewsAPI settings
│   └── model_config.yaml       # NLP model & preprocessing config
│
├── tests/                      # pytest suite (40+ tests)
├── utils/
│   ├── logger.py               # loguru setup
│   └── helpers.py              # Config loading & path helpers
│
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── run.py                      # Pipeline orchestrator CLI
├── quickstart.py               # Quick command wrapper
└── requirements.txt
```

---

## Testing

```bash
# Run all tests
make test

# With HTML coverage report
make test-cov
# then open htmlcov/index.html

# pytest directly
pytest tests/ -v --tb=short
```

Test suite: **40+ unit tests** across ingestion, preprocessing, analysis, storage, analytics, and dashboard modules.

---

## Configuration

| File | Purpose |
|------|---------|
| `config/rss_feeds.yaml` | Add/remove RSS sources, set timeout & retry |
| `config/newsapi_config.yaml` | Categories, language, page size |
| `config/model_config.yaml` | Sentiment model, spaCy model, preprocessing flags |
| `.env` | `NEWSAPI_KEY`, `LOG_LEVEL` |

---

## Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Write code with type hints and docstrings
4. Run `make test` and `make lint` — both must pass
5. Format: `make format`
6. Open a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Acknowledgements

- [Cardiff NLP](https://huggingface.co/cardiffnlp) — RoBERTa sentiment model
- [spaCy](https://spacy.io) — industrial-strength NLP
- [Streamlit](https://streamlit.io) — rapid dashboard framework
- [NewsAPI](https://newsapi.org) — news data API

---

<div align="center">

Developed by [Sarim Farooq](https://github.com/ultimate144z)

[Report Bug](https://github.com/ultimate144z/NewsLens/issues) · [Request Feature](https://github.com/ultimate144z/NewsLens/issues)

</div>
