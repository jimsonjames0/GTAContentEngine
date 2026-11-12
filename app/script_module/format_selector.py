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
        self.root_dir = Path(__file__).resolve().parents[2]
        self.formats_dir = self.root_dir / "formats"
        self.weights_file = self.root_dir / "data" / "analytics" / "format_weights.json"
        self.formats = self._load_formats()

        if not self.formats:
            raise ValueError(f"No format definitions loaded from {self.formats_dir}")

    def _load_weights(self) -> dict:
        """Load historical engagement weights from PerformanceTracker."""
        if self.weights_file.exists():
            try:
                with open(self.weights_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return {k.lower(): v.get("avg_engagement_score", 0.0) for k, v in data.items()}
            except Exception:
                pass
        return {}

    def _load_formats(self) -> dict:
        loaded = {}
        if not self.formats_dir.exists():
            raise FileNotFoundError(f"Formats directory not found: {self.formats_dir}")

        for file_path in self.formats_dir.glob("*.json"):
            if file_path.name == "editorial_style_guide.json":
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                name = data.get("name", file_path.stem).lower().strip()
                loaded[name] = data

        return loaded
 
    def select(self, trend_title: str) -> dict:
        """Select optimal format weighted by keyword relevance and historical engagement."""
        title_lower = trend_title.lower()
        weights = self._load_weights()

        candidates = {}
        for format_name, keywords in self.FORMAT_KEYWORDS.items():
            if format_name not in self.formats:
                continue
            matches = sum(1 for kw in keywords if kw in title_lower)
            if matches > 0:
                # Base score from keyword matches + performance boost from analytics feedback loop
                perf_boost = min(10.0, weights.get(format_name, 0.0) / 1000.0)
                score = matches * 10.0 + perf_boost
                candidates[format_name] = score

        if candidates:
            best_format = max(candidates.items(), key=lambda x: x[1])[0]
            return self.formats[best_format]

        # Default fallback: pick highest performing format if stats exist, else discovery
        if weights:
            available_weights = {k: v for k, v in weights.items() if k in self.formats}
            if available_weights:
                top_perf = max(available_weights.items(), key=lambda x: x[1])[0]
                return self.formats[top_perf]

        return self.formats.get("discovery") or next(iter(self.formats.values()))