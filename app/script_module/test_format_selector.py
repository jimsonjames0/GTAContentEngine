import json
from pathlib import Path
from format_selector import FormatSelector

trends_path = Path(__file__).resolve().parents[2] / "data" / "trends" / "latest_trends.json"

with open(trends_path, "r", encoding="utf-8") as f:
    saved_trends = json.load(f)

selector = FormatSelector()

print(f"Loaded formats from disk: {list(selector.formats.keys())}\n")
print("Matched Formats for Saved Trends:")

for i, trend in enumerate(saved_trends, start=1):
    selected_format = selector.select(trend["title"])
    print(
        f"{i}. {trend['title']}\n"
        f"   -> Format: {selected_format['name']} "
        f"| Length: {selected_format['length']}s "
        f"| Example Hook: {selected_format['hook_styles'][0]}"
    )