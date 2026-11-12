import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = ROOT_DIR / "app"
if str(APP_DIR / "trend_module") not in sys.path:
    sys.path.append(str(APP_DIR / "trend_module"))

from history_manager import HistoryManager


class QueueManager:

    def __init__(self):
        self.root_dir = ROOT_DIR
        self.queue_file = self.root_dir / "data" / "publishing_queue.json"
        self._ensure_queue_file()
        self.history_mgr = HistoryManager()

    def _ensure_queue_file(self):
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.queue_file.exists():
            with open(self.queue_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def _load_queue(self) -> List[Dict[str, Any]]:
        self._ensure_queue_file()
        try:
            with open(self.queue_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_queue(self, queue: List[Dict[str, Any]]):
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)

    def register(
        self,
        short_id: str,
        brief: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        staged_dir: Optional[str] = None,
        quality_report: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add or update an item in the publishing queue with Quality Gate audit results."""
        queue = self._load_queue()
        now_iso = datetime.now(timezone.utc).isoformat()

        # Handle dataclass or dict
        if hasattr(brief, "__dict__"):
            brief_dict = brief.__dict__
        else:
            brief_dict = brief or {}

        title = brief_dict.get("title", "")
        fmt = brief_dict.get("format", "breakdown").upper()
        if staged_dir is None:
            staged_dir = f"media/staged/{short_id}"

        # Evaluate quality gate outcome
        q_score = quality_report.get("total_score", 100) if quality_report else 100
        q_passed = quality_report.get("passed", True) if quality_report else True
        status = "ready_to_publish" if q_passed else "held_by_quality_gate"

        # Find existing item if present
        existing_item = None
        for item in queue:
            if item.get("id") == short_id:
                existing_item = item
                break

        if existing_item:
            existing_item["title"] = title
            existing_item["format"] = fmt
            existing_item["staged_dir"] = staged_dir
            existing_item["status"] = status
            existing_item["quality_score"] = q_score
            existing_item["quality_passed"] = q_passed
            entry = existing_item
        else:
            entry = {
                "id": short_id,
                "created_at": now_iso,
                "format": fmt,
                "title": title,
                "staged_dir": staged_dir,
                "status": status,
                "quality_score": q_score,
                "quality_passed": q_passed,
                "published_at": None,
                "platforms": {
                    "youtube": {"status": "pending"},
                    "tiktok": {"status": "pending"},
                    "instagram": {"status": "pending"}
                }
            }
            queue.append(entry)

        self._save_queue(queue)
        return entry

    def get_ready_queue(self) -> List[Dict[str, Any]]:
        """Return all staged bundles ready for posting."""
        queue = self._load_queue()
        return [item for item in queue if item.get("status") == "ready_to_publish"]

    def mark_published(self, short_id: str, platform: str = "all") -> bool:
        """Update platform status and mark overall status published if all complete."""
        queue = self._load_queue()
        found = False
        now_iso = datetime.now(timezone.utc).isoformat()

        for item in queue:
            if item.get("id") == short_id:
                found = True
                if platform == "all":
                    for p in item.get("platforms", {}):
                        item["platforms"][p]["status"] = "published"
                    item["status"] = "published"
                    item["published_at"] = now_iso
                else:
                    if "platforms" in item and platform in item["platforms"]:
                        item["platforms"][platform]["status"] = "published"

                    all_published = all(
                        p_info.get("status") == "published"
                        for p_info in item.get("platforms", {}).values()
                    )
                    if all_published:
                        item["status"] = "published"
                        item["published_at"] = now_iso

                title = item.get("title", "")
                if title:
                    self.history_mgr.mark_processed(title, short_id=short_id)
                break

        if found:
            self._save_queue(queue)
            self.generate_copy_sheet()
        return found

    def list_all(self) -> List[Dict[str, Any]]:
        return self._load_queue()

    def print_queue_table(self):
        queue = self.list_all()
        print("=" * 96)
        print("                           PUBLISHING QUEUE REGISTRY")
        print("=" * 96)
        if not queue:
            print("  Queue is currently empty.")
            print("=" * 96)
            return

        print(f"{'ID':<11} {'FORMAT':<12} {'STATUS':<20} {'QUALITY':<9} {'STAGED DIR':<22} {'TITLE'}")
        print("-" * 96)
        for item in queue:
            sid = item.get("id", "")
            fmt = item.get("format", "")[:10]
            status = item.get("status", "")[:18]
            q_score = item.get("quality_score", 100)
            q_str = f"{q_score}/100"
            staged = item.get("staged_dir", "")[:20]
            title = item.get("title", "")
            if len(title) > 22:
                title = title[:19] + "..."
            print(f"{sid:<11} {fmt:<12} {status:<20} {q_str:<9} {staged:<22} {title}")
        print("=" * 96)

    def generate_copy_sheet(self) -> Path:
        """Generate media/staged/UPLOAD_CHEATSHEET.md for all ready items."""
        queue = self.list_all()
        sheet_path = self.root_dir / "media" / "staged" / "UPLOAD_CHEATSHEET.md"
        sheet_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "# GTA VI Content Engine — Upload Cheatsheet",
            "*Auto-generated manual publishing guide containing exact copy-paste metadata and file paths.*",
            "",
            "---",
            ""
        ]

        ready_items = [item for item in queue if item.get("status") == "ready_to_publish"]
        items_to_display = ready_items if ready_items else queue

        if not items_to_display:
            lines.append("No videos currently staged for upload.")
        else:
            for item in items_to_display:
                short_id = item.get("id", "")
                staged_dir = self.root_dir / item.get("staged_dir", f"media/staged/{short_id}")
                metadata_path = staged_dir / "metadata.json"
                brief_path = staged_dir / "brief.json"

                metadata = {}
                brief = {}
                if metadata_path.exists():
                    try:
                        with open(metadata_path, "r", encoding="utf-8") as f:
                            metadata = json.load(f)
                    except Exception:
                        pass
                if brief_path.exists():
                    try:
                        with open(brief_path, "r", encoding="utf-8") as f:
                            brief = json.load(f)
                    except Exception:
                        pass

                platforms = metadata.get("platforms", {})
                yt = platforms.get("youtube_shorts", {})
                tt = platforms.get("tiktok", {})
                ig = platforms.get("instagram_reels", {})
                monetization = metadata.get("monetization", {})
                pinned_cta = monetization.get("pinned_comment_cta", "Will you be playing GTA VI on Day 1? Drop your thoughts below!")
                affiliate_cat = monetization.get("recommended_affiliate_category", "console_storage_expansion")

                q_score = item.get("quality_score", 100)
                q_status = "PASSED" if item.get("quality_passed", True) else "HELD"

                lines.extend([
                    f"## 🎬 Video Package: `{short_id}`",
                    f"- **Format:** `{item.get('format', 'UNKNOWN')}`",
                    f"- **Status:** `{item.get('status', 'ready_to_publish')}`",
                    f"- **Quality Gate:** `{q_status} ({q_score}/100)`",
                    f"- **Original Title:** {item.get('title', '')}",
                    f"- **Master Video File:** `{item.get('staged_dir', '')}/master.mp4`",
                    f"- **Cover Thumbnail File:** `{item.get('staged_dir', '')}/cover.jpg`",
                    "",
                    "### 1. YouTube Shorts",
                    "**Title:**",
                    "```text",
                    f"{yt.get('title', '')}",
                    "```",
                    "**Description:**",
                    "```text",
                    f"{yt.get('description', '')}",
                    "```",
                    f"**Tags:** `{', '.join(yt.get('tags', []))}`",
                    "",
                    "### 2. TikTok",
                    "**Caption:**",
                    "```text",
                    f"{tt.get('caption', '')}",
                    "```",
                    "",
                    "### 3. Instagram Reels",
                    "**Caption:**",
                    "```text",
                    f"{ig.get('caption', '')}",
                    "```",
                    "",
                    "### 4. Spoken Script",
                    f"*{brief.get('script', '')}*",
                    "",
                    "### 5. 💰 Monetization & Pinned Comment",
                    "**Copy-Paste Pinned Comment:**",
                    "```text",
                    f"{pinned_cta}",
                    "```",
                    f"**Affiliate Category:** `{affiliate_cat}`",
                    "",
                    "---",
                    ""
                ])

        with open(sheet_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return sheet_path

