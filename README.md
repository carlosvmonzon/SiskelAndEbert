# Siskel & Ebert Episode Matcher

This project scrapes and reconciles episode lists of "Siskel & Ebert" (and related shows) from various sources (Web, YouTube, TVDB) to find matches, identify incomplete episodes, and generate statistics.

## Data Sources

- **YouTube Channel**: [The Misadventures of Siskel & Ebert](https://www.youtube.com/@TheMisadventuresofSiskelEbert/videos)
- **Website**: [Siskel & Ebert.org](https://siskelebert.org/)

## Project Structure

- `main.py`: The entry point of the application.
- `modules/`: Contains the scraping, processing, and reporting logic.
- `data/`: Stores the scraped text data.

## Installation

1. Clone the repository.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script:
```bash
python main.py
```