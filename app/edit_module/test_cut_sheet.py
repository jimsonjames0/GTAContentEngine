import json
from cut_sheet import CutSheetGenerator

generator = CutSheetGenerator()
sheet = generator.generate("brief_001.json")

print(f"=== Production Cut Sheet: {sheet['title']} ===")
print(f"Format: {sheet['format'].upper()} | Total Duration: {sheet['total_duration_sec']}s\n")
print(f"Hook: \"{sheet['hook']}\"\n")
print("Shot Timeline:")
for shot in sheet["timeline"]:
    print(
        f"  Shot {shot['shot_index']} [{shot['start_time_sec']}s - {shot['end_time_sec']}s] "
        f"({shot['duration_sec']}s) -> {shot['footage_tag']} ({shot['file_target']})"
    )

print("\nVoiceover Script:")
print(f"\"{sheet['full_script']}\"")