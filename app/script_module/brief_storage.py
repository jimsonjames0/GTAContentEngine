import json
from dataclasses import asdict
from pathlib import Path
from content_brief import ContentBrief


class BriefStorage:

    def __init__(self):
        # Target: GTAContentEngine/data/content_briefs/
        self.briefs_dir = Path(__file__).resolve().parents[2] / "data" / "content_briefs"
        self.briefs_dir.mkdir(parents=True, exist_ok=True)

    def save(self, brief: ContentBrief, filename: str = "brief_001.json") -> Path:
        file_path = self.briefs_dir / filename
        data = asdict(brief)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return file_path
