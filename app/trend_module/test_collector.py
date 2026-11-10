from collector import TrendCollector

raw_trends = [
    {
        "title": "GTA VI detail discovered",
        "source": "reddit",
        "url": "https://example.com/1",
        "description": "Players discovered an interesting detail in the GTA VI trailer.",
        "velocity": 8,
        "relevance": 10,
        "novelty": 7,
    },
    {
        "title": "GTA VI gameplay discussion",
        "source": "youtube",
        "url": "https://example.com/2",
        "description": "Players are discussing a new gameplay mechanic.",
        "velocity": 6,
        "relevance": 10,
        "novelty": 8,
    },
    {
        "title": "GTA VI theory gains attention",
        "source": "reddit",
        "url": "https://example.com/3",
        "description": "A community theory is gaining attention.",
        "velocity": 9,
        "relevance": 9,
        "novelty": 8,
    },
]

collector = TrendCollector()

trends = collector.collect(raw_trends)

for trend in trends:
    print(trend)