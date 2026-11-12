import sys
import shutil
import json
import argparse
from pathlib import Path

# Add project root and all module subdirectories to Python search path
ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "app"

sys.path.extend([
    str(ROOT_DIR),
    str(APP_DIR),
    str(APP_DIR / "trend_module"),
    str(APP_DIR / "script_module"),
    str(APP_DIR / "edit_module"),
    str(APP_DIR / "publish_module"),
])

from trend_module.reddit_collector import RedditCollector
from trend_module.storage import TrendStorage
from trend_module.history_manager import HistoryManager
from script_module.idea_generator import IdeaGenerator
from script_module.storage import IdeaStorage
from script_module.script_writer import ScriptWriter
from script_module.brief_storage import BriefStorage
from edit_module.cut_sheet import CutSheetGenerator
from edit_module.asset_manager import AssetManager
from edit_module.voice_generator import VoiceGenerator
from edit_module.render_engine import RenderEngine
from publish_module.metadata_generator import MetadataGenerator
from publish_module.cover_extractor import CoverExtractor
from publish_module.queue_manager import QueueManager
from publish_module.quality_gate import QualityGate
import re


class BatchRunner:

    def __init__(self):
        self.root_dir = ROOT_DIR
        self.staged_dir = self.root_dir / "media" / "staged"
        self.staged_dir.mkdir(parents=True, exist_ok=True)

        self.trend_collector = RedditCollector()
        self.trend_storage = TrendStorage()
        self.history_mgr = HistoryManager()
        self.idea_gen = IdeaGenerator()
        self.idea_storage = IdeaStorage()
        self.script_writer = ScriptWriter()
        self.brief_storage = BriefStorage()
        self.cut_gen = CutSheetGenerator()
        self.asset_mgr = AssetManager()
        self.voice_gen = VoiceGenerator()
        self.render_engine = RenderEngine()
        self.metadata_gen = MetadataGenerator()
        self.cover_extractor = CoverExtractor()
        self.queue_mgr = QueueManager()
        self.quality_gate = QualityGate()

    def _get_next_short_index(self) -> int:
        existing_indices = []
        queue = self.queue_mgr.list_all()
        for item in queue:
            m = re.match(r"short_(\d+)", item.get("id", ""))
            if m:
                existing_indices.append(int(m.group(1)))
        for p in self.staged_dir.iterdir():
            if p.is_dir():
                m = re.match(r"short_(\d+)", p.name)
                if m:
                    existing_indices.append(int(m.group(1)))
        return max(existing_indices, default=0) + 1

    def run_batch(self, limit: int = 3, force: bool = False) -> list[Path]:
        print("=" * 64)
        print(f"       GTA VI CONTENT ENGINE — BATCH PROCESSING (TOP {limit})")
        print("=" * 64)

        # 1. Fetch plenty of candidate trends
        fetch_count = max(15, limit * 3)
        raw_trends = self.trend_collector.collect(limit=fetch_count)
        self.trend_storage.save(raw_trends)

        # 2. Filter un-processed trends
        fresh_trends = self.history_mgr.filter_fresh(raw_trends, force=force)
        if not fresh_trends:
            if not force:
                print("  ℹ All scraped trends have already been processed.")
                print("  ℹ Use --force to re-process trends regardless of history.")
                return []
            fresh_trends = raw_trends

        top_trends = fresh_trends[:limit]
        ideas = self.idea_gen.generate_batch(top_trends)
        self.idea_storage.save(ideas)

        staged_dirs = []
        start_idx = 1 if force else self._get_next_short_index()

        for offset, (trend, idea) in enumerate(zip(top_trends, ideas)):
            idx = start_idx + offset
            short_id = f"short_{idx:03d}"
            print(f"\n[{offset + 1}/{len(top_trends)}] Processing {short_id.upper()}: {idea.trend_title[:45]}...")

            brief = self.script_writer.write_brief(idea)
            brief_file = self.brief_storage.save(brief, filename=f"brief_{idx:03d}.json")
            print(f"  ✓ Brief created: {brief_file.name}")

            voice_file, v_dur = self.voice_gen.generate(
                script=brief.script,
                filename=f"voice_{idx:03d}.mp3"
            )
            print(f"  ✓ Voiceover synthesized: {voice_file.name} ({v_dur:.2f}s)")

            self.asset_mgr.ensure_assets_exist_from_brief(f"brief_{idx:03d}.json")

            master_file = self.render_engine.render_master(
                brief_filename=f"brief_{idx:03d}.json",
                output_filename=f"{short_id}_master.mp4"
            )
            print(f"  ✓ Master video rendered: {master_file.name}")

            metadata = self.metadata_gen.generate_metadata(
                brief_data=f"brief_{idx:03d}.json",
                brief_id=short_id
            )
            metadata_file = self.root_dir / "data" / "metadata" / f"{short_id}_metadata.json"
            print(f"  ✓ Metadata generated: {metadata_file.name}")

            cover_file = self.cover_extractor.extract_cover(
                video_path=master_file,
                output_path=self.root_dir / "media" / "staged" / f"{short_id}_cover.jpg"
            )
            print(f"  ✓ Cover thumbnail extracted: {cover_file.name}")

            package_dir = self.staged_dir / short_id
            package_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(master_file, package_dir / "master.mp4")
            shutil.copy2(cover_file, package_dir / "cover.jpg")
            shutil.copy2(metadata_file, package_dir / "metadata.json")
            shutil.copy2(brief_file, package_dir / "brief.json")

            # Run Quality Gate
            q_report = self.quality_gate.evaluate(
                short_id=short_id,
                brief_path=brief_file,
                video_path=master_file,
                metadata_path=metadata_file
            )
            q_score = q_report.get("total_score", 0)
            q_passed = q_report.get("passed", False)
            report_file = self.root_dir / "data" / "quality_reports" / f"{short_id}_quality_report.json"
            if report_file.exists():
                shutil.copy2(report_file, package_dir / "quality_report.json")

            staged_rel_dir = str(package_dir.relative_to(self.root_dir))
            self.queue_mgr.register(
                short_id=short_id,
                brief=brief,
                metadata=metadata,
                staged_dir=staged_rel_dir,
                quality_report=q_report
            )
            reg_status = "ready_to_publish" if q_passed else "held_by_quality_gate"
            print(f"  ✓ Quality Gate: {q_score}/100 (passed={q_passed}) -> status={reg_status}")
            print(f"  ✓ Packaged into: {staged_rel_dir}/")
            staged_dirs.append(package_dir)

        # Generate / update cheatsheet
        self.queue_mgr.generate_copy_sheet()

        print("\n" + "=" * 64)
        print("               BATCH PROCESSING COMPLETED")
        print("=" * 64)
        for p in staged_dirs:
            print(f"  • {p.relative_to(self.root_dir)} [master.mp4, cover.jpg, metadata.json, brief.json]")
        print("  • Cheatsheet updated: media/staged/UPLOAD_CHEATSHEET.md")
        print("=" * 64 + "\n")

        return staged_dirs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GTA VI Content Engine Batch Runner")
    parser.add_argument("-n", "--count", type=int, default=3, help="Number of trends to batch process (default: 3)")
    parser.add_argument("--force", action="store_true", help="Ignore deduplication history filter")
    args = parser.parse_args()

    runner = BatchRunner()
    runner.run_batch(limit=args.count, force=args.force)


