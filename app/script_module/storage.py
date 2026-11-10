import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, List


class IdeaStorage:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.ideas_dir = self.root_dir / "data" / "ideas"
        self.ideas_dir.mkdir(parents=True, exist_ok=True)

    def save(self, ideas: List[Any], filename: str = "latest_ideas.json") -> Path:
        data = []
        for idea in ideas:
            if is_dataclass(idea):
                data.append(asdict(idea))
            elif isinstance(idea, dict):
                data.append(idea)
            elif hasattr(idea, "__dict__"):
                data.append(idea.__dict__)
            else:
                data.append(idea)

        target_file = self.ideas_dir / filename
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return target_file