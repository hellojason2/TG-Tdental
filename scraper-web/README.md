# TDental Viewer & Scraper

A comprehensive tool suite for scraping, analyzing, and replicating the TDental dental clinic management system.

## Project Structure

```
scraper-web/
├── app/                    # Main application package
│   ├── api/                # API endpoints (Backend)
│   │   ├── auth.py         # Authentication logic
│   │   ├── routes.py       # Main API routes
│   │   └── deps.py         # API dependencies
│   ├── core/               # Core configurations and utilities
│   │   ├── config.py       # Environment variables and settings
│   │   ├── database.py     # Database connection logic
│   │   ├── security.py     # Security utilities (hashing)
│   │   └── utils.py        # Helper functions
│   ├── services/           # Business logic
│   │   ├── scraper.py      # SPA Scraper logic
│   │   ├── analyzer.py     # LLM Analysis logic
│   │   └── sync.py         # Data synchronization logic
│   └── main.py             # FastAPI entry point
├── static/                 # Static files (Frontend)
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   ├── tdental.html        # Main app page
│   └── login.html          # Login page
├── scripts/                # Standalone scripts
│   ├── run_scraper.py      # Script to run the scraper
│   └── migrate.py          # Script to migrate data to DB
├── data/                   # Scraped data storage
└── requirements.txt        # Python dependencies
```

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Set the following environment variables (or rely on defaults in `app/core/config.py`):
    - `DATABASE_URL`: PostgreSQL connection string.
    - `GROQ_API_KEY`: API key for Groq (if using LLM analysis).

3.  **Run the Application**:
    ```bash
    python -m app.main
    ```
    The application will be available at `http://localhost:8899`.

## Features

### 1. TDental Viewer (Web App)
A fully functional replica of the TDental dashboard, serving as the frontend for the system.
- **Login**: Secure authentication system.
- **Dashboard**: Overview of clinic statistics.
- **Customers**: Management of customer profiles and history.
- **Appointments**: Calendar view and appointment management.
- **Reports**: Detailed financial and operational reports.

### 2. Scraper (`app/services/scraper.py`)
An automated tool using Playwright to reverse-engineer the target SPA.
- Logs in automatically.
- Discovers routes and navigation.
- Captures API traffic and responses.
- Snapshots DOM structure and screenshots.

### 3. Analyzer (`app/services/analyzer.py`)
Uses LLM (Groq/OpenAI) to analyze scraped data.
- Generates database schema from API responses.
- Creates API specifications.
- Maps frontend components.

### 4. Sync Engine (`app/services/sync.py`)
Middleware that polls the live TDental API and synchronizes data to the local PostgreSQL database.

## Usage

### Running the Scraper
```bash
python scripts/run_scraper.py
```

### Migrating Data
```bash
python scripts/migrate.py
```

### Running the Sync Engine
You can run the sync logic via the `app.services.sync` module (requires custom script or integration).

## Development

- **Backend**: FastAPI (Python)
- **Frontend**: HTML/CSS/JS (Vanilla, extracted from source)
- **Database**: PostgreSQL
- **Browser Automation**: Playwright
