# Daily News & Weather

## Overview
A Python terminal application that allows users to read the latest news, search for specific topics, check weather information for different cities, and generate PDF reports.

## Features
- **Top News:** Displays the latest news articles.
- **Saudi News:** Retrieves news from Al Watan.
- **Sports News:** Displays sports-related news.
- **Technology News:** Shows the latest technology news.
- **Search News:** Finds articles using keywords.
- **Weather:** Displays weather information for a selected city.
- **PDF Report:** Saves collected news and weather information in a PDF file.
- **Exit:** Closes the application.

## Technologies
- Python
- Requests
- NewsAPI
- Open-Meteo
- RSS Feed
- Rich
- ReportLab

## Installation

1. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Add your NewsAPI key to the `.env` file:

   ```env
   NEWS_API_KEY=your_api_key_here
   ```

3. Run the application:

   ```bash
   python daily_assistant/main.py
   ```

## Project Structure
- `main.py` — Main menu and application control.
- `news.py` — News retrieval and search.
- `weather.py` — Weather information.
- `pdf_report.py` — PDF report generation.
- `ui.py` — Terminal interface components.

## Purpose
This project demonstrates Python programming, API integration, modular development, error handling, and PDF generation.