import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Union, List, Dict, Any


class HistoryManager:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.history_file = self.root_dir / "data" / "trends" / "processed_history.json"
        self._ensure_history_file()

    def _ensure_history_file(self):
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            # Seed with any existing queue items if available
            seeded = []
            queue_path = self.root_dir / "data" / "publishing_queue.json"
            if queue_path.exists():
                try:
                    with open(queue_path, "r", encoding="utf-8") as f:
                        q_data = json.load(f)
                    for item in q_data:
                        title = item.get("title", "")
                        if title:
                            seeded.append({
                                "normalized_title": self._normalize_title(title),
                                "original_title": title,
                                "processed_at": item.get("created_at", datetime.now(timezone.utc).isoformat()),
                                "short_id": item.get("id", "")
                            })
                except Exception:
                    pass

            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(seeded, f, indent=2, ensure_ascii=False)

    def _load_history(self) -> List[Dict[str, Any]]:
        self._ensure_history_file()
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_history(self, history: List[Dict[str, Any]]):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _normalize_title(title: str) -> str:
        clean = re.sub(r"[^a-zA-Z0-9\s]", "", title.lower())
        return " ".join(clean.split())

    def _extract_title(self, trend: Union[Any, dict, str]) -> str:
        if isinstance(trend, str):
            return trend
        if isinstance(trend, dict):
            return trend.get("title", "") or trend.get("trend_title", "")
        if hasattr(trend, "title"):
            return trend.title
        if hasattr(trend, "trend_title"):
            return trend.trend_title
        return ""

    def is_processed(self, trend: Union[Any, dict, str]) -> bool:
        title = self._extract_title(trend)
        if not title:
            return False
        norm = self._normalize_title(title)
        history = self._load_history()
        return any(item.get("normalized_title") == norm for item in history)

    def mark_processed(self, trend: Union[Any, dict, str], short_id: str = ""):
        title = self._extract_title(trend)
        if not title:
            return
        norm = self._normalize_title(title)
        history = self._load_history()

        # Check if already present
        for item in history:
            if item.get("normalized_title") == norm:
                if short_id and not item.get("short_id"):
                    item["short_id"] = short_id
                    self._save_history(history)
                return

        history.append({
            "normalized_title": norm,
            "original_title": title,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "short_id": short_id
        })
        self._save_history(history)

    def filter_fresh(self, trends: list, force: bool = False) -> list:
        if force:
            return trends
        return [t for t in trends if not self.is_processed(t)]
