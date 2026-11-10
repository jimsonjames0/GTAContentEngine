from reddit_collector import RedditCollector
from collector import TrendCollector
from ranker import TrendRanker
from storage import TrendStorage

reddit = RedditCollector()
collector = TrendCollector()
ranker = TrendRanker()
storage = TrendStorage()

raw_trends = reddit.collect(subreddit="GTA6", limit=5)
trends = collector.collect(raw_trends)
top_trends = ranker.rank(trends, limit=3)
saved_path = storage.save(top_trends)

print("Top Ranked Reddit Trends:")
for i, trend in enumerate(top_trends, start=1):
    print(
        f"{i}. {trend.title} | Score: {trend.score} "
        f"(V:{trend.velocity} R:{trend.relevance} N:{trend.novelty})"
    )