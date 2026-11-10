from trend import Trend

class TrendCollector:

    def collect(self, raw_trends):
        trends = []

        for item in raw_trends:
            trend = Trend.create(
                title = item["title"],
                source = item["source"],
                url = item["url"],
                description = item["description"],
                velocity = item["velocity"],
                relevance = item["relevance"],
                novelty = item["novelty"]
            )

            trends.append(trend)

        return trends