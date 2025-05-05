# other_news.py

import time
import csv
import os
import helper
import requests
from config import API_KEY

CSV_FILE = "news_impact_log.csv"
HOLD_TICKS = 20


def initialize_session():
    session = requests.Session()
    session.headers.update({'X-API-Key': API_KEY})
    return session


def load_seen_ids():
    seen = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            if 'news_id' in reader.fieldnames:
                for row in reader:
                    seen.add(row['news_id'])
            else:
                print("[WARN] Existing CSV has no 'news_id' column. Starting fresh.")
    return seen


def save_to_csv(news_id, headline, start_price, end_price):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['news_id', 'headline', 'start', 'end'])
        writer.writerow([news_id, headline, start_price, end_price])


def main():
    session = initialize_session()
    seen_news_ids = load_seen_ids()
    pending = []

    print("[INFO] Starting tick-based news impact logger...")

    while True:
        try:
            current_tick = helper.get_tick(session)
            news_items = helper.get_latest_news(session)
            first_bid = helper.ticker_bid_ask(session, 'CL-2F')[0]  # Get only the bid

            # Add new unseen news items
            for news in news_items:
                news_id = news['news_id']
                headline = news.get('headline', '')
                if news_id not in seen_news_ids:
                    print(f"[NEW] {headline}")
                    seen_news_ids.add(news_id)
                    pending.append({
                        "headline": headline,
                        "start_tick": current_tick,
                        "start_price": first_bid,
                        "news_id": news_id
                    })

            # Process matured news entries
            still_pending = []
            for item in pending:
                if current_tick - item['start_tick'] >= HOLD_TICKS:
                    last_bid = helper.ticker_bid_ask(session, 'CL-2F')[0]  # Get only the bid
                    save_to_csv(item['news_id'], item['headline'], item['start_price'], last_bid)
                    print(f"[LOGGED] {item['headline']} | {item['start_price']} → {last_bid}")
                else:
                    still_pending.append(item)

            pending = still_pending
            time.sleep(0.5)

        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
