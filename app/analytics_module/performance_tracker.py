import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


class PerformanceTracker:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.analytics_dir = self.root_dir / "data" / "analytics"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.analytics_dir / "performance_log.json"
        self.weights_file = self.analytics_dir / "format_weights.json"
        self.queue_file = self.root_dir / "data" / "publishing_queue.json"
        self._ensure_files()

    def _ensure_files(self):
        if not self.log_file.exists():
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
        if not self.weights_file.exists():
            with open(self.weights_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

    def _load_json(self, path: Path, default: Any) -> Any:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _save_json(self, path: Path, data: Any):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _lookup_format(self, short_id: str) -> str:
        queue = self._load_json(self.queue_file, [])
        for item in queue:
            if item.get("id") == short_id:
                return item.get("format", "UNKNOWN").upper()
        return "UNKNOWN"

    def log_metrics(
        self,
        short_id: str,
        views: int,
        likes: int = 0,
        comments: int = 0,
        retention_pct: float = 0.0
    ) -> Dict[str, Any]:
        """Log performance metrics for a short and update format weights."""
        logs = self._load_json(self.log_file, [])
        fmt = self._lookup_format(short_id)
        now_iso = datetime.now(timezone.utc).isoformat()

        engagement_score = round(views * 1.0 + likes * 5.0 + comments * 10.0 + (retention_pct * 100), 2)

        entry = {
            "short_id": short_id,
            "format": fmt,
            "views": int(views),
            "likes": int(likes),
            "comments": int(comments),
            "retention_pct": float(retention_pct),
            "engagement_score": engagement_score,
            "logged_at": now_iso,
        }

        # Update existing or append
        updated = False
        for i, existing in enumerate(logs):
            if existing.get("short_id") == short_id:
                logs[i] = entry
                updated = True
                break
        if not updated:
            logs.append(entry)

        self._save_json(self.log_file, logs)
        self._update_format_weights(logs)
        return entry

    def _update_format_weights(self, logs: List[Dict[str, Any]]):
        aggregates = {}
        for item in logs:
            fmt = item.get("format", "UNKNOWN")
            if fmt not in aggregates:
                aggregates[fmt] = {
                    "count": 0,
                    "total_views": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_score": 0.0,
                }
            aggregates[fmt]["count"] += 1
            aggregates[fmt]["total_views"] += item.get("views", 0)
            aggregates[fmt]["total_likes"] += item.get("likes", 0)
            aggregates[fmt]["total_comments"] += item.get("comments", 0)
            aggregates[fmt]["total_score"] += item.get("engagement_score", 0.0)

        weights = {}
        for fmt, stats in aggregates.items():
            cnt = stats["count"]
            weights[fmt] = {
                "count": cnt,
                "total_views": stats["total_views"],
                "avg_views": round(stats["total_views"] / cnt, 1),
                "avg_likes": round(stats["total_likes"] / cnt, 1),
                "avg_comments": round(stats["total_comments"] / cnt, 1),
                "avg_engagement_score": round(stats["total_score"] / cnt, 1),
            }

        self._save_json(self.weights_file, weights)

    def get_report(self) -> str:
        """Print and return a formatted terminal analytics summary."""
        logs = self._load_json(self.log_file, [])
        weights = self._load_json(self.weights_file, {})

        total_videos = len(logs)
        total_views = sum(item.get("views", 0) for item in logs)
        total_likes = sum(item.get("likes", 0) for item in logs)

        lines = [
            "=" * 76,
            "              GTA VI CONTENT ENGINE — PERFORMANCE REPORT",
            "=" * 76,
            f"Total Videos Tracked: {total_videos}",
            f"Total Views:          {total_views:,}",
            f"Total Likes:          {total_likes:,}",
            "-" * 76,
            f"{'FORMAT':<16} {'VIDEOS':<8} {'AVG VIEWS':<14} {'AVG LIKES':<12} {'ENGAGEMENT'}",
            "-" * 76,
        ]

        if not weights:
            lines.append("  No performance metrics logged yet.")
        else:
            top_fmt = max(weights.items(), key=lambda x: x[1].get("avg_engagement_score", 0))
            for fmt, data in sorted(weights.items(), key=lambda x: x[1].get("avg_views", 0), reverse=True):
                lines.append(
                    f"{fmt:<16} {data['count']:<8} {data['avg_views']:<14,.1f} {data['avg_likes']:<12,.1f} {data['avg_engagement_score']:<,.1f}"
                )
            lines.append("-" * 76)
            lines.append(f"🏆 Top Performing Format: {top_fmt[0]} ({top_fmt[1]['avg_views']:,.0f} avg views | score: {top_fmt[1]['avg_engagement_score']:,.1f})")

        lines.append("=" * 76)
        report_str = "\n".join(lines)
        print(report_str)
        return report_str
