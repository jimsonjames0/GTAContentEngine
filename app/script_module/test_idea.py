from idea import Idea

idea = Idea.create(
    trend_title="GTA VI preloading download has officially kicked off",
    trend_url="https://www.reddit.com/r/GTA6/comments/1xrovbe/",
    source="reddit",
    trend_score=720,
    format_name="discovery",
    hook="Nobody is talking about what just happened with GTA VI preloading...",
    concept="Show the official preload announcement, explain file size expectations, and highlight what players can see right now.",
    recommended_length="20-40",
)

print(idea)
print(f"Source: {idea.source} | Format: {idea.format_name} ({idea.recommended_length}s)")