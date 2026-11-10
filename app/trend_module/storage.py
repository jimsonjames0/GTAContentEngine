import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, List


class TrendStorage:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.trends_dir = self.root_dir / "data" / "trends"
        self.trends_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self, trends: List[Any], filename: str = "latest_trends.json"
    ) -> Path:
        data = []
        for trend in trends:
            if is_dataclass(trend):
                data.append(asdict(trend))
            elif isinstance(trend, dict):
                data.append(trend)
            elif hasattr(trend, "__dict__"):
                data.append(trend.__dict__)
            else:
                data.append(trend)

        target_file = self.trends_dir / filename
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return target_file