import os
import smtplib
import feedparser
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


NEWS_FEEDS = {
    "World News": [
        "https://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "Business News": [
        "https://feeds.bbci.co.uk/news/business/rss.xml"
    ],
    "Supply Chain News": [
        "https://www.supplychaindive.com/feeds/news/"
    ],
    "Technology News": [
        "https://www.technologyreview.com/feed/"
    ]
}

ARTICLES_PER_SECTION = 3

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


def clean_text(text):
    if not text:
        return "No summary available."

    text = text.replace("<p>", "").replace("</p>", "")
    text = text.replace("&nbsp;", " ")
    text = " ".join(text.split())

    if len(text) > 300:
        text = text[:300].rsplit(" ", 1)[0] + "..."

    return text


def why_it_matters(section):
    reasons = {
        "World News": "This matters because global events can affect politics, trade, security, and international relationships.",
        "Business News": "This matters because business trends can influence markets, jobs, prices, and consumer confidence.",
        "Supply Chain News": "This matters because supply chain issues can affect shipping, product availability, and costs.",
        "Technology News": "This matters because technology changes can affect work, education, privacy, and everyday life."
    }

    return reasons.get(section, "This matters because it may affect current events or decision-making.")


def get_articles():
    briefing = {}

    for section, feeds in NEWS_FEEDS.items():
        articles = []

        for feed_url in feeds:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:ARTICLES_PER_SECTION]:
                articles.append({
                    "headline": entry.get("title", "No headline available"),
                    "source": feed.feed.get("title", "Unknown source"),
                    "summary": clean_text(entry.get("summary", "")),
                    "link": entry.get("link", "No link available")
                })

        briefing[section] = articles[:ARTICLES_PER_SECTION]

    return briefing


def build_email(briefing):
    today = datetime.now().strftime("%B %d, %Y")

    body = f"Good morning,\n\nHere is your daily news briefing for {today}.\n\n"

    for section, articles in briefing.items():
        body += f"{section.upper()}\n"
        body += "-" * len(section) + "\n\n"

        if not articles:
            body += "No stories found today.\n\n"
            continue

        for i, article in enumerate(articles, start=1):
            body += f"{i}. {article['headline']}\n"
            body += f"Source: {article['source']}\n"
            body += f"Summary: {article['summary']}\n"
            body += f"Link: {article['link']}\n"
            body += f"Why it matters: {why_it_matters(section)}\n\n"

    body += "End of briefing.\n"

    return body


def send_email(subject, body):
    if not SENDER_EMAIL or not APP_PASSWORD or not RECIPIENT_EMAIL:
        raise ValueError("Missing email credentials. Check GitHub Secrets.")

    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(message)


def main():
    briefing = get_articles()
    today = datetime.now().strftime("%B %d, %Y")
    subject = f"Daily News Briefing - {today}"
    body = build_email(briefing)

    print(body)
    send_email(subject, body)


if __name__ == "__main__":
    main()
