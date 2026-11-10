import xml.etree.ElementTree as ET
import requests
from trend import Trend


class RedditCollector:

    GTA_KEYWORDS = [
        "gta", "rockstar", "lucia", "jason", "vice city", "trailer"
    ]

    META_KEYWORDS = [
        "faq", "megathread", "[countdown]", "rules"
    ]

    DISCOVERY_KEYWORDS = [
        "detail", "secret", "theory", "officially", "discovered",
        "found", "leak", "gameplay", "breakdown", "hidden"
    ]

    def _score_entry(self, title: str, index: int):
        title_lower = title.lower()

        # 1. Velocity (1-10): Position in feed
        velocity = max(1, 10 - index)

        # 2. Relevance (1-10): Direct GTA VI mention vs general thread
        relevance = 10 if any(word in title_lower for word in self.GTA_KEYWORDS) else 8

        # 3. Novelty (1-10): Penalize mod/FAQ threads, boost news & discoveries
        if any(word in title_lower for word in self.META_KEYWORDS):
            novelty = 4
        elif any(word in title_lower for word in self.DISCOVERY_KEYWORDS):
            novelty = 9
        else:
            novelty = 7

        return velocity, relevance, novelty

    def collect(self, subreddit="GTA6", limit=10):
        headers = {
            "User-Agent": "linux:gtacontentengine:v0.1 (by /u/gtacontentengine)"
        }

        posts = []
        rss_url = f"https://www.reddit.com/r/{subreddit}/hot.rss"
        response = requests.get(rss_url, headers=headers, timeout=10)

        # 1. Primary: Direct Reddit RSS
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            for index, entry in enumerate(root.findall("atom:entry", ns)[:limit]):
                title = entry.findtext("atom:title", default="GTA VI Trend", namespaces=ns)
                link_el = entry.find("atom:link", ns)
                url = link_el.attrib.get("href", "") if link_el is not None else ""

                velocity, relevance, novelty = self._score_entry(title, index)

                trend = Trend.create(
                    title=title,
                    source="reddit",
                    url=url,
                    description=f"Trending post from r/{subreddit}",
                    velocity=velocity,
                    relevance=relevance,
                    novelty=novelty,
                )
                posts.append(trend)

            return posts

        # 2. Fallback: Used automatically if Reddit returns 429 (Rate Limit) or 403
        fallback_url = (
            f"https://news.google.com/rss/search?"
            f"q=site:reddit.com/r/{subreddit}+when:7d&hl=en-US&gl=US&ceid=US:en"
        )
        fb_response = requests.get(fallback_url, headers=headers, timeout=10)
        fb_response.raise_for_status()

        root = ET.fromstring(fb_response.text)
        for index, item in enumerate(root.findall(".//item")[:limit]):
            raw_title = item.findtext("title", default="GTA VI Trend")
            title = raw_title.removesuffix(" - Reddit")
            url = item.findtext("link", default="")

            velocity, relevance, novelty = self._score_entry(title, index)

            trend = Trend.create(
                title=title,
                source="reddit",
                url=url,
                description=f"Trending post from r/{subreddit}",
                velocity=velocity,
                relevance=relevance,
                novelty=novelty,
            )
            posts.append(trend)

        return posts