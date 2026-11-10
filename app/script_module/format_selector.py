import json
from pathlib import Path


class FormatSelector:

    FORMAT_KEYWORDS = {
        "theory": [
            "theory", "speculation", "what if", "predict", "prediction",
            "could", "might", "rumor", "connection", "mean"
        ],
        "breakdown": [
            "breakdown", "analysis", "explained", "frame", "gameplay",
            "mechanic", "feature", "comparison", "deep dive", "physics"
        ],
        "discovery": [
            "detail", "secret", "discovered", "found", "hidden",
            "noticed", "officially", "new", "leak", "background", "easter egg"
        ],
        "reaction": [
            "reaction", "react", "watching", "stream", "moment",
            "insane", "shocked", "live"
        ],
        "meme": [
            "meme", "funny", "bro", "crazy", "wild", "before gta 6",
            "joke", "humor", "coded", "be like"
        ],
    }

    def __init__(self):
        self.formats_dir = Path(__file__).resolve().parents[2] / "formats"
        self.formats = self._load_formats()

        if not self.formats:
            raise ValueError(f"No format definitions loaded from {self.formats_dir}")

    def _load_formats(self) -> dict:
        loaded = {}
        if not self.formats_dir.exists():
            raise FileNotFoundError(f"Formats directory not found: {self.formats_dir}")

        for file_path in self.formats_dir.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                name = data.get("name", file_path.stem).lower().strip()
                loaded[name] = data
                #loaded["breakdown"] = data in breakdown.json

        return loaded
 
    def select(self, trend_title: str) -> dict:
        title_lower = trend_title.lower()

        # Check keyword rules in priority order
        for format_name, keywords in self.FORMAT_KEYWORDS.items():
            if any(keyword in title_lower for keyword in keywords):
                if format_name in self.formats:
                    return self.formats[format_name]

        # Default fallback if no specific keyword matches
        return self.formats.get("discovery") or next(iter(self.formats.values()))