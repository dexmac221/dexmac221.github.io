#!/usr/bin/env python3
"""Refresh the article list from the Medium RSS feed.

Medium's feed only carries the latest 10 stories, so every story ever seen is kept in data/articles.json
and the list in index.html (between the ARTICLES markers) is rebuilt from that file.

    python3 tools/update_articles.py            fetch the feed, merge, rebuild
    python3 tools/update_articles.py --offline  rebuild the HTML from data/articles.json only

Exit code 1 if the feed cannot be read: the page is left as it is.
"""
import html
import json
import os
import re
import sys
import urllib.request
from email.utils import parsedate_to_datetime

FEED = "https://medium.com/feed/@gianlucabailo"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "articles.json")
PAGE = os.path.join(ROOT, "index.html")
START, END = "<!-- ARTICLES:START -->", "<!-- ARTICLES:END -->"
VENUES = {"pub.towardsai.net": "Towards AI", "medium.com": "Medium"}


def fetch_feed():
    req = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0 (compatible; personal-site-updater)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse(xml):
    out = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        def tag(pattern):
            m = re.search(pattern, item, re.S)
            return m.group(1).strip() if m else ""
        title = html.unescape(tag(r"<title><!\[CDATA\[(.*?)\]\]></title>"))
        link = tag(r"<link>(.*?)</link>").split("?")[0]
        date = parsedate_to_datetime(tag(r"<pubDate>(.*?)</pubDate>")).strftime("%Y-%m-%d")
        body = tag(r"<content:encoded><!\[CDATA\[(.*?)\]\]></content:encoded>")
        sub = re.search(r"<h4>(.*?)</h4>", body, re.S)
        subtitle = html.unescape(re.sub(r"<[^>]+>", "", sub.group(1))).strip() if sub else ""
        if title and link:
            out.append({"title": title, "link": link, "date": date, "subtitle": subtitle})
    return out


def venue(link):
    host = re.sub(r"^https?://([^/]+).*$", r"\1", link)
    return VENUES.get(host, "Medium")


def render(articles):
    rows = []
    for a in articles:
        y, m, _ = a["date"].split("-")
        label = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(m) - 1] + " " + y
        sub = f'\n            <p class="desc">{html.escape(a["subtitle"])}</p>' if a.get("subtitle") else ""
        rows.append(f'''        <li>
          <span class="date">{label}</span>
          <div>
            <a href="{html.escape(a["link"], quote=True)}">{html.escape(a["title"])}</a>{sub}
            <p>{venue(a["link"])}</p>
          </div>
        </li>''')
    return "\n".join(rows)


def main():
    known = json.load(open(DATA, encoding="utf-8")) if os.path.exists(DATA) else []
    if "--offline" not in sys.argv:
        try:
            fresh = parse(fetch_feed())
        except Exception as e:
            print(f"feed not reachable: {e}")
            return 1
        if not fresh:
            print("feed read but empty: nothing changed")
            return 1
        by_link = {a["link"]: a for a in known}
        for a in fresh:
            by_link[a["link"]] = {**by_link.get(a["link"], {}), **a}
        known = list(by_link.values())
    known.sort(key=lambda a: a["date"], reverse=True)
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(known, f, ensure_ascii=False, indent=2)
        f.write("\n")
    page = open(PAGE, encoding="utf-8").read()
    i, j = page.index(START) + len(START), page.index(END)
    new = page[:i] + "\n" + render(known) + "\n        " + page[j:]
    if new != page:
        open(PAGE, "w", encoding="utf-8").write(new)
    print(f"{len(known)} articles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
