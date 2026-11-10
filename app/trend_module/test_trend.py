from trend import Trend

trend = Trend.create(
    title = "GTA VI detail discovered",
    source="reddit",
    url="https://example.com",
    description = "Players discovered an interesting detail in the GTA VI trailer.",
    velocity = 8,
    relevance=10,
    novelty=7
)

print(trend)
print(f"Trend Score: {trend.score}")