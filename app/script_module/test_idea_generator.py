import json
from pathlib import Path
from idea_generator import IdeaGenerator
from storage import IdeaStorage

trends_path = Path(__file__).resolve().parents[2] / "data" / "trends" / "latest_trends.json"

with open(trends_path, "r", encoding="utf-8") as f:
    saved_trends = json.load(f)

generator = IdeaGenerator()
storage = IdeaStorage()

ideas = generator.generate_batch(saved_trends)

saved_path = storage.save(ideas)

print(f"Generated {len(ideas)} candidate ideas and saved to: {saved_path}\n")

for i, idea in enumerate(ideas, start=1):
    print(f"Idea {i} [{idea.format_name.upper()} - {idea.recommended_length}s] (Trend Score: {idea.trend_score})")
    print(f"  Title:   {idea.trend_title}")
    print(f"  Hook:    {idea.hook}")
    print(f"  Concept: {idea.concept}")
    print(f"  Source:  {idea.source} -> {idea.trend_url}\n")