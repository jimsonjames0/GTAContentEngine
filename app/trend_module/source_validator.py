from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class SourceRecord:
    source_id: str
    url: str
    source_type: str  # "official_rockstar" | "reddit_discovery" | "gaming_press"
    retrieval_date: str  # ISO-8601
    claim_summary: str
    verification_status: str  # "verified_official" | "community_observation" | "unverified_rumor"
    usage_permission_status: str  # "topic_discovery_only" | "fair_use_commentary" | "restricted_do_not_reproduce"
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SourceValidator:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.sources_dir = self.root_dir / "data" / "sources"
        self.sources_dir.mkdir(parents=True, exist_ok=True)

    def from_trend(self, trend: Any) -> SourceRecord:
        """Convert a scraped Reddit trend into a traceable SourceRecord.

        Reddit posts are classified as source_type="reddit_discovery" and
        usage_permission_status="topic_discovery_only" — they are used to discover
        what the community is talking about, never copied verbatim as scripts, and
        never treated as official Rockstar confirmation unless linked to an official
        announcement.
        """
        title = getattr(trend, "title", None)
        if title is None and isinstance(trend, dict):
            title = trend.get("title", "")
        url = getattr(trend, "url", None)
        if url is None and isinstance(trend, dict):
            url = trend.get("url", "")
        description = getattr(trend, "description", None)
        if description is None and isinstance(trend, dict):
            description = trend.get("description", "")

        source_id = self._generate_source_id(url, title)
        now_iso = datetime.now(timezone.utc).isoformat()

        record = SourceRecord(
            source_id=source_id,
            url=url,
            source_type="reddit_discovery",
            retrieval_date=now_iso,
            claim_summary=description or title,
            verification_status="community_observation",
            usage_permission_status="topic_discovery_only",
            notes=(
                "Reddit thread used for topic discovery only. "
                "Not official Rockstar confirmation unless linked to an official announcement. "
                "Never reproduce Reddit user comments verbatim in scripts."
            ),
        )
        return record

    def save_record(self, record: SourceRecord) -> Path:
        """Persist a SourceRecord to data/sources/{source_id}.json."""
        target_file = self.sources_dir / f"{record.source_id}.json"
        with open(target_file, "w", encoding="utf-8") as f:
            import json

            json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)
        return target_file

    def load_record(self, source_id: str) -> SourceRecord | None:
        target_file = self.sources_dir / f"{source_id}.json"
        if not target_file.exists():
            return None
        import json

        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SourceRecord(**data)

    def _generate_source_id(self, url: str, title: str) -> str:
        import hashlib

        base = f"{url}|{title}".encode("utf-8")
        return hashlib.sha256(base).hexdigest()[:16]
