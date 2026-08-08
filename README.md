# Weather Tracker

Weather app with CRUD operations on MongoDB Atlas, live weather data via OpenWeatherMap, contextual YouTube video results, and LLM-based location resolution (zip/city/coordinates).

> 🚧 **Currently a script-based prototype.** A Streamlit web interface is planned so the app can be deployed and used directly in the browser instead of the terminal — see [Roadmap](#roadmap).

## Overview

This project lets users look up weather for a location entered as a zip/postal code, city name, or GPS coordinates, and stores the results in a cloud-hosted MongoDB database. Location input is normalized using an LLM (via Groq) so users aren't restricted to one input format — the model resolves postal codes to city names while passing through city names or coordinates unchanged.

Beyond basic weather lookup, the app performs full CRUD on stored records (create, read, update, delete), supports CSV export of saved data, and enriches each result with the top 5 YouTube videos matching the city *and* current weather condition (e.g. "Delhi in monsoon weather" rather than a generic city search) — giving users a visual sense of what the location actually looks like in that weather.

## Features

- **Flexible location input** — accepts zip/postal code, city name, or `lat,lon` coordinates
- **LLM-based location resolution** — Groq-hosted LLM normalizes postal codes to city names before the weather lookup
- **Live weather data** — current conditions via the OpenWeatherMap API (temperature, feels-like, pressure, humidity, wind speed)
- **Contextual YouTube results** — top 5 videos matched to the city *and* current weather condition, via YouTube Data API v3
- **Full CRUD** — create, read, update, and delete stored weather records in MongoDB Atlas
- **CSV export** — export all stored records to a CSV file
- **Error handling** — handles invalid locations, malformed coordinates, and API/HTTP errors (rate limits, auth failures, not-found) for both external APIs

## Tech Stack

- **Language:** Python
- **Database:** MongoDB Atlas (via PyMongo)
- **LLM:** Groq (`openai/gpt-oss-120b`) via LangChain
- **APIs:** OpenWeatherMap, YouTube Data API v3
- **Data handling:** pandas

## Setup

1. Clone the repo
   ```bash
   git clone <repo-url>
   cd weather-tracker-mongodb
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root (see `.env.example`) with your own API keys:
   ```
   GROQ_API_KEY=your_groq_api_key
   DB_KEY=your_mongodb_atlas_connection_string
   WEATHER_API_KEY=your_openweathermap_api_key
   YT_API_KEY=your_youtube_data_api_key
   ```

   - Groq API key: [console.groq.com](https://console.groq.com)
   - MongoDB Atlas connection string: from your Atlas cluster's "Connect" dialog
   - OpenWeatherMap API key: [openweathermap.org/api](https://openweathermap.org/api)
   - YouTube Data API key: [Google Cloud Console](https://console.cloud.google.com/) (enable YouTube Data API v3)

4. Run the notebook (`Weather_app.ipynb`) and call the functions from the cells — e.g. `get_weather()`, `read_db()`, `update_db(...)`, `del_db(...)`, `export_to_csv()`.

## Usage

- `get_weather()` — prompts for a location and date range, fetches current weather, stores it in MongoDB, and prints matching YouTube video links
- `read_db(query_id=None)` — returns a specific record by ID, or all records if no ID is given
- `update_db(query_id, start_new, end_new)` — updates the stored date range for a record
- `del_db(query_id=None)` — deletes a specific record by ID, or all records if no ID is given
- `export_to_csv()` — exports all stored records to `exported_file.csv`

## Roadmap

- [ ] Deploy on **Streamlit** for a browser-based UI (in progress)
- [ ] Restructure into separate modules (`db.py`, `weather_api.py`, `youtube_api.py`, `llm_resolver.py`) instead of a single notebook

## Note on API keys

This repo does **not** include any real API keys or credentials. All secrets are loaded from a local `.env` file (see Setup above), which is excluded via `.gitignore`. You'll need your own free-tier keys for Groq, OpenWeatherMap, MongoDB Atlas, and the YouTube Data API to run this project.
