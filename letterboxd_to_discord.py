import logging
import time
from datetime import datetime, timedelta

import bs4
import feedparser
import pytz
import requests

POST_FREQUENCY_HRS = 1
DISCORD_WEBHOOK_URL = "<DISCORD WEBHOOK URL>"

feeds = [
    "https://letterboxd.com/<username1>/rss/",
    "https://letterboxd.com/<username2>/rss/",
    "https://letterboxd.com/<username3>/rss/",
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("<PATH TO LOG FILE>", "a+")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("{asctime} - {name} - {levelname} - {message}", style="{")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def convert_entry_to_webhook(entry):
    if entry.get('letterboxd_rewatch') == "Yes":
        watched_verbs = "Rewatched"
    else:
        watched_verbs = "Watched"

    stars = ""
    if entry.get('letterboxd_memberrating') is not None:
        stars = entry.get('title').split("-")[-1].strip().split(" ")[0]

    soup = bs4.BeautifulSoup(entry['summary'], 'html.parser')

    date_or_review = soup.find_all('p')[-1].text

    if "Watched on" not in date_or_review:
        review = date_or_review
        if "spoiler" in review:
            review = f"|| {review} ||"
    else:
        review = ""

    date_str = ""

    if entry.get('letterboxd_watcheddate'):
        watched_date = time.strptime(entry['letterboxd_watcheddate'], "%Y-%m-%d")

        day_of_week = time.strftime('%A', watched_date)
        month = time.strftime('%B', watched_date)
        day_of_month = int(time.strftime('%d', watched_date))
        year = int(time.strftime('%Y', watched_date))

        date_str = f" on {day_of_week} {month} {day_of_month}, {year}"

    image_url = soup.img["src"]

    description = f"{watched_verbs} {entry['letterboxd_filmtitle']} ({entry['letterboxd_filmyear']}){date_str}"

    webhook_obj = {"content": f"{entry['author']} on Letterboxd:"}

    embeds = []

    embed_entry = {
        "title": entry['title'],
        "description": description,
        "url": entry["link"],
        "image": {"url": image_url},
    }

    fields = []

    if stars:
        fields.append({
            "name": "Rating",
            "value": stars
        })
    if review:
        fields.append({
            "name": "Review",
            "value": f"> {review}"
        })

    embed_entry["fields"] = fields
    embeds.append(embed_entry)
    webhook_obj["embeds"] = embeds

    return webhook_obj


def main():
    for feed in feeds:
        d = feedparser.parse(feed)

        for entry in d["entries"]:
            published_struct = entry['published_parsed']
            published_time = datetime(*published_struct[:6], tzinfo=pytz.utc)
            current_time = datetime.now(tz=pytz.utc)
    
            if (current_time - published_time) < timedelta(hours=POST_FREQUENCY_HRS):
                webhook_obj = convert_entry_to_webhook(entry)
                r = requests.post(DISCORD_WEBHOOK_URL, json=webhook_obj)
                logger.info(f"Post found in feed {feed}, webhook status: {r.status_code}: {r.reason}")
    logger.info(f"Finished running script for {len(feeds)} feeds.")


if __name__ == "__main__":
    main()
