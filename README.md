# NewsLens — Multi-Source News Sentiment & Bias Analyzer

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.9.1-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/Transformers-4.57.3-FFD21E.svg)](https://huggingface.co/transformers/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.51.0-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![spaCy](https://img.shields.io/badge/spaCy-3.8.11-09A3D5.svg?logo=spacy&logoColor=white)](https://spacy.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**An end-to-end NLP-powered media analysis system that reveals how different news outlets frame the same stories.**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture) • [Documentation](#documentation)

</div>

---

## Overview

NewsLens is a production-ready **sentiment analysis and media bias detection system** that:
- Aggregates news from multiple sources (RSS feeds + NewsAPI)
- Analyzes sentiment using state-of-the-art transformer models
- Extracts named entities and keywords with spaCy
- Visualizes trends and bias patterns in an interactive dashboard
- Stores historical data for temporal analysis

**Use Cases:** Data science portfolios, NLP research, media monitoring, bias detection, trend analysis.

---

## Features

### Multi-Source Data Aggregation
- **RSS Feeds**: BBC, CNN, Al-Jazeera, Reuters, and more
- **NewsAPI Integration**: 70,000+ sources worldwide
- **Configurable Sources**: Easy YAML-based source management

### Advanced NLP Analysis
- **Sentiment Classification**: Using HuggingFace transformers (`cardiffnlp/twitter-roberta-base-sentiment-latest`)
- **Named Entity Recognition**: People, organizations, locations with spaCy
- **Keyword Extraction**: NLTK-powered noun phrase extraction
- **Confidence Scoring**: Track model certainty for each prediction

### Interactive Analytics Dashboard
- **Sentiment Trends**: Time-series visualization of news sentiment
- **Source Comparison**: Side-by-side outlet bias analysis
- **Entity Tracking**: Monitor mentions of people, places, organizations
- **Word Clouds**: Visual keyword frequency analysis
- **Real-time Filtering**: By source, sentiment, date range, keywords

### Robust Data Storage
- **SQLite Database**: Historical article tracking with full-text search
- **CSV Export**: Easy data export for further analysis
- **JSON Archives**: Structured data persistence

---

## Installation

### Prerequisites
- Python 3.13+ (tested with 3.13.9)
- 4GB RAM minimum (8GB recommended for transformer models)
- Optional: NewsAPI key for enhanced data collection

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/NewsLens.git
cd NewsLens

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# (Optional) Set up NewsAPI key
# Create .env file with: NEWSAPI_KEY=your_key_here
```

---

## Usage

### Option 1: Quick Commands (Recommended)

```bash
# Launch the dashboard
python quickstart.py dashboard

# Run tests
python quickstart.py tests

# Show help
python quickstart.py help
```

### Option 2: Full Pipeline

```bash
# Run complete analysis pipeline
python run.py --full

# Run specific components
python run.py --ingest    # Data collection only
python run.py --dashboard # Dashboard only
```

### Option 3: Manual Streamlit

```bash
streamlit run app/dashboard.py
```

The dashboard will open at `http://localhost:8501`

---

## Architecture

### System Pipeline

```
┌─────────────────────┐
│   Data Sources      │
│  (RSS + NewsAPI)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Ingestion     │
│  (RSS/API Scrapers) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Preprocessing      │
│  (NLTK + Cleaning)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  NLP Analysis       │
│  (Transformers +    │
│   spaCy NER)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Storage Layer      │
│  (SQLite + CSV)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Analytics Engine   │
│  (Trend Analysis)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Dashboard          │
│  (Streamlit UI)     │
└─────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Collection** | feedparser, newsapi-python, requests | Multi-source news aggregation |
| **NLP** | HuggingFace Transformers, spaCy, NLTK | Sentiment & entity analysis |
| **ML Framework** | PyTorch | Transformer model inference |
| **Data Processing** | pandas, numpy | Data manipulation & analytics |
| **Storage** | SQLAlchemy, SQLite | Persistent data storage |
| **Visualization** | Streamlit, Plotly, Matplotlib | Interactive dashboards |
| **Configuration** | PyYAML, python-dotenv | Settings management |
| **Testing** | pytest, pytest-cov | Unit testing & coverage |

---

## Project Structure

```
NewsLens/
│
├── app/                      # Streamlit dashboard application
│   ├── dashboard.py          # Main dashboard entry point
│   ├── components/           # Reusable UI components
│   │   ├── charts.py         # Chart visualizations
│   │   ├── tables.py         # Data tables
│   │   └── filters.py        # Filter controls
│   └── pages/                # Multi-page dashboard
│       ├── 1_latest_news.py  # Recent articles view
│       ├── 2_source_compare.py # Source bias comparison
│       ├── 3_trends.py       # Temporal trend analysis
│       └── 4_keywords.py     # Keyword analytics
│
├── src/                      # Core application logic
│   ├── ingestion/            # Data collection modules
│   │   ├── rss_scraper.py    # RSS feed scraper
│   │   └── newsapi_scraper.py # NewsAPI client
│   ├── preprocessing/        # Text preprocessing
│   │   └── preprocess.py     # Text cleaning pipeline
│   ├── analysis/             # NLP analysis
│   │   ├── sentiment.py      # Sentiment analyzer
│   │   └── entities.py       # Entity extractor
│   ├── storage/              # Data persistence
│   │   ├── database.py       # SQLite manager
│   │   └── csv_manager.py    # CSV operations
│   └── analytics/            # Analytics engine
│       ├── analytics.py      # Core analytics
│       ├── trend_analysis.py # Temporal patterns
│       └── compare_sources.py # Source comparison
│
├── config/                   # Configuration files
│   ├── rss_feeds.yaml        # RSS feed URLs
│   ├── newsapi_config.yaml   # NewsAPI settings
│   └── model_config.yaml     # ML model settings
│
├── data/                     # Data storage (gitignored)
│   ├── raw/                  # Raw scraped data
│   ├── processed/            # Processed data
│   └── newslens.db           # SQLite database
│
├── tests/                    # Unit tests
│   ├── test_ingestion.py     # Scraper tests
│   ├── test_preprocessing.py # Preprocessing tests
│   ├── test_analysis.py      # NLP tests
│   └── run_tests.py          # Test runner
│
├── docs/                     # Documentation
│   ├── DEVELOPMENT_LOG.md    # Development history
│   ├── OPTIMIZATION_GUIDE.md # Performance tuning
│   └── PROJECT_SUMMARY.md    # Project overview
│
├── utils/                    # Utility functions
│   ├── logger.py             # Logging setup
│   └── helpers.py            # Helper functions
│
├── run.py                    # Main pipeline runner
├── quickstart.py             # Quick command interface
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
python quickstart.py tests

# Or use pytest directly
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

Test coverage: **40+ test cases** across all modules.

---

## Project Statistics

- **Total Files**: 44 Python/config files
- **Lines of Code**: ~11,700
- **Test Coverage**: 40+ unit tests
- **Data Sources**: 8+ RSS feeds + NewsAPI
- **Supported Languages**: English (expandable to 100+)
- **Dashboard Pages**: 4 interactive pages
- **Database Tables**: 3 (articles, entities, keywords)

---

## Key Highlights

### Technical Excellence
- **Production-Quality Code**: Type hints, docstrings, comprehensive error handling
- **Industry Standards**: Modular architecture, separation of concerns
- **Comprehensive Testing**: pytest suite with coverage reporting
- **CI/CD Ready**: Black formatter, flake8 linting

### Real-World Application
- **Multi-Source Integration**: RSS feeds + REST APIs
- **State-of-the-Art NLP**: Transformer models + spaCy NER
- **Scalable Storage**: SQLite with optimized indexes
- **Interactive Visualization**: Streamlit dashboard with multi-page layout

### Professional Value
- **Full-Stack Data Science**: Data collection, ML processing, visualization
- **Best Practices**: Logging, configuration management, unit testing
- **Extensible Design**: Clear roadmap for enterprise features
- **Well-Documented**: 2,000+ lines of comprehensive documentation  

---

## Future Enhancements

### Phase 1: Quick Wins (1-2 weeks)
- [ ] Scheduled execution (Windows Task Scheduler / cron)
- [ ] Dashboard auto-refresh
- [ ] Enhanced error notifications
- [ ] Export analytics to PDF/CSV reports

### Phase 2: Advanced Features (1-2 months)
- [ ] Multi-language sentiment analysis (50+ languages)
- [ ] Topic clustering with LDA
- [ ] Full article text extraction
- [ ] Historical trend predictions
- [ ] Fake news detection

### Phase 3: Production Deployment (2-3 months)
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP/Azure)
- [ ] Real-time streaming ingestion
- [ ] User authentication system
- [ ] REST API for integrations

### Phase 4: Enterprise Scale (3-6 months)
- [ ] Microservices architecture
- [ ] Message queue (Kafka/RabbitMQ)
- [ ] Distributed processing
- [ ] Multi-tenant support
- [ ] Advanced bias detection algorithms

See [OPTIMIZATION_GUIDE.md](docs/OPTIMIZATION_GUIDE.md) for detailed implementation roadmap.

---

## Documentation

- **[OPTIMIZATION_GUIDE.md](docs/OPTIMIZATION_GUIDE.md)**: Performance tuning and scaling strategies
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines and development workflow

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes with proper docstrings and type hints
4. Run tests (`pytest tests/`)
5. Format code (`black .`)
6. Commit changes (`git commit -m 'Add AmazingFeature'`)
7. Push to branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact & Support

**Author**: Sarim Farooq  
**GitHub**: [@ultimate144z](https://github.com/ultimate144z)

### Getting Help
- Open an [issue](https://github.com/ultimate144z/NewsLens/issues) for bugs or feature requests
- Check [documentation](docs/) for detailed guides
- Star the repository if you find it useful

---

## Acknowledgments

- **HuggingFace**: Transformer models for sentiment analysis
- **spaCy**: Named entity recognition capabilities
- **Streamlit**: Rapid dashboard development framework
- **NewsAPI**: Comprehensive news data access
- **Open Source Community**: Various libraries and tools

---

## Development Roadmap

**Phase 0: Foundation** (Completed)
- Project setup & structure
- Core modules implementation
- Basic dashboard
- Testing framework

**Phase 1: Production Ready** (Completed)
- Enhanced error handling
- Comprehensive documentation
- Type hints & docstrings
- Optimized dependencies

**Phase 2: Automation** (Planned)
- Scheduled execution
- Email notifications
- Enhanced analytics

**Phase 3: Cloud Deployment** (Planned)
- Docker containerization
- CI/CD pipeline
- Production deployment

**Phase 4: Advanced Features** (Planned)
- Real-time processing
- ML model improvements
- REST API development

---

<div align="center">

**Developed by Sarim Farooq**

[Report Bug](https://github.com/ultimate144z/NewsLens/issues) · [Request Feature](https://github.com/ultimate144z/NewsLens/issues) · [Documentation](docs/)

</div>