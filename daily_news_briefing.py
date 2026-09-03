name: Daily News Briefing

on:
  schedule:
    - cron: "0 12 * * *"
  workflow_dispatch:

jobs:
  send-news-briefing:
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run briefing script
        env:
          SENDER_EMAIL: ${{ secrets.SENDER_EMAIL }}
          APP_PASSWORD: ${{ secrets.APP_PASSWORD }}
          RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
        run: python daily_news_briefing.py
