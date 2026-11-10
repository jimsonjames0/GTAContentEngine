import json
from pathlib import Path


class CutSheetGenerator:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.briefs_dir = self.root_dir / "data" / "content_briefs"

    def generate(self, brief_filename: str = "brief_001.json") -> dict:
        brief_path = self.briefs_dir / brief_filename
        if not brief_path.exists():
            raise FileNotFoundError(f"Content brief not found at {brief_path}")

        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)

        total_length = brief["length"]
        footage_tags = brief["footage"]
        num_shots = len(footage_tags)

        # Allocate durations per clip
        base_duration = round(total_length / num_shots, 1)
        shots = []
        current_time = 0.0

        for i, tag in enumerate(footage_tags):
            # Give the last shot the remainder to match total_length exactly
            if i == num_shots - 1:
                duration = round(total_length - current_time, 1)
            else:
                duration = base_duration

            end_time = round(current_time + duration, 1)
            shots.append({
                "shot_index": i + 1,
                "footage_tag": tag,
                "file_target": f"media/raw/{tag}.mp4",
                "start_time_sec": current_time,
                "end_time_sec": end_time,
                "duration_sec": duration,
                "aspect_ratio": "9:16 (Center Crop 1080x1920)",
                "pacing": brief.get("voice", "energetic")
            })
            current_time = end_time

        cut_sheet = {
            "title": brief["title"],
            "format": brief["format"],
            "total_duration_sec": total_length,
            "hook": brief["hook"],
            "full_script": brief["script"],
            "timeline": shots,
        }

        return cut_sheet