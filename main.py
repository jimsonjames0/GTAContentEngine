import sys
import shutil
import argparse
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = ROOT_DIR / "app"

sys.path.extend([
    str(ROOT_DIR),
    str(APP_DIR),
    str(APP_DIR / "trend_module"),
    str(APP_DIR / "script_module"),
    str(APP_DIR / "edit_module"),
    str(APP_DIR / "publish_module"),
    str(APP_DIR / "analytics_module"),
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
from analytics_module.performance_tracker import PerformanceTracker
from batch_runner import BatchRunner


def _get_next_short_index(staged_dir: Path, queue_mgr: QueueManager) -> int:
    existing_indices = []
    for item in queue_mgr.list_all():
        m = re.match(r"short_(\d+)", item.get("id", ""))
        if m:
            existing_indices.append(int(m.group(1)))
    for p in staged_dir.iterdir():
        if p.is_dir():
            m = re.match(r"short_(\d+)", p.name)
            if m:
                existing_indices.append(int(m.group(1)))
    return max(existing_indices, default=0) + 1


def run_single_pipeline(force: bool = False):
    print("=" * 64)
    print("      GTA VI CONTENT ENGINE — AUTOMATED DAILY PIPELINE")
    print("=" * 64)

    collector = RedditCollector()
    trend_storage = TrendStorage()
    history_mgr = HistoryManager()
    queue_mgr = QueueManager()
    staged_dir = ROOT_DIR / "media" / "staged"
    staged_dir.mkdir(parents=True, exist_ok=True)

    print("\n[Step 1/8] Scraping & ranking r/GTA6 trends...")
    raw_trends = collector.collect(limit=10)
    trend_storage.save(raw_trends)

    fresh_trends = history_mgr.filter_fresh(raw_trends, force=force)
    if not fresh_trends:
        if not force:
            print("  ℹ All scraped trends already processed. Use --force to re-process.")
            return
        fresh_trends = raw_trends

    top_trend = fresh_trends[0]
    top_title = top_trend.title if hasattr(top_trend, "title") else top_trend.get("title", "")
    short_idx = 1 if force else _get_next_short_index(staged_dir, queue_mgr)
    short_id = f"short_{short_idx:03d}"
    print(f"  ✓ Target: {short_id.upper()} | '{top_title[:45]}...'")

    print("\n[Step 2/8] Generating ideas & hooks...")
    idea_gen = IdeaGenerator()
    ideas = idea_gen.generate_batch([top_trend])
    top_idea = ideas[0]
    print(f"  ✓ Format: {top_idea.format_name.upper()} | Hook: \"{top_idea.hook}\"")

    print("\n[Step 3/8] Writing script & brief...")
    writer = ScriptWriter()
    brief_storage = BriefStorage()
    brief = writer.write_brief(top_idea)
    brief_file = brief_storage.save(brief, filename=f"brief_{short_idx:03d}.json")
    print(f"  ✓ Brief validated -> {brief_file.name}")

    print("\n[Step 4/8] Building cut sheet timeline...")
    cut_generator = CutSheetGenerator()
    cut_sheet = cut_generator.generate(brief_filename=f"brief_{short_idx:03d}.json")
    print(f"  ✓ Cut sheet timeline generated ({cut_sheet['total_duration_sec']}s total).")

    print("\n[Step 5/8] Synthesizing voiceover audio...")
    voice_gen = VoiceGenerator()
    voice_file, duration = voice_gen.generate(
        script=brief.script,
        brief_filename=f"brief_{short_idx:03d}.json",
        filename=f"voice_{short_idx:03d}.mp3"
    )
    print(f"  ✓ Voiceover generated -> {voice_file.name} ({duration:.2f}s)")

    print("\n[Step 6/8] Ensuring raw assets exist...")
    asset_mgr = AssetManager()
    asset_paths = asset_mgr.ensure_assets_exist_from_brief(f"brief_{short_idx:03d}.json")
    print(f"  ✓ Verified/Provisioned {len(asset_paths)} raw media assets.")

    print("\n[Step 7/8] Rendering master video with dynamic captions...")
    render_engine = RenderEngine()
    master_path = render_engine.render_master(
        brief_filename=f"brief_{short_idx:03d}.json",
        output_filename=f"{short_id}_master.mp4"
    )
    print(f"  ✓ Master video rendered -> {master_path.relative_to(ROOT_DIR)}")

    print(f"\n[Step 8/8] Packaging assets into media/staged/{short_id}/...")
    metadata_gen = MetadataGenerator()
    cover_extractor = CoverExtractor()

    metadata = metadata_gen.generate_metadata(brief_data=f"brief_{short_idx:03d}.json", brief_id=short_id)
    metadata_file = ROOT_DIR / "data" / "metadata" / f"{short_id}_metadata.json"
    cover_file = cover_extractor.extract_cover(video_path=master_path, output_path=staged_dir / f"{short_id}_cover.jpg")

    package_dir = staged_dir / short_id
    package_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master_path, package_dir / "master.mp4")
    shutil.copy2(cover_file, package_dir / "cover.jpg")
    shutil.copy2(metadata_file, package_dir / "metadata.json")
    shutil.copy2(brief_file, package_dir / "brief.json")

    queue_mgr.register(short_id=short_id, brief=brief, metadata=metadata, staged_dir=str(package_dir.relative_to(ROOT_DIR)))
    queue_mgr.generate_copy_sheet()

    print(f"  ✓ Staged package verified -> {package_dir.relative_to(ROOT_DIR)}/")
    print(f"  ✓ Registered in publishing queue -> status: ready_to_publish")
    print("  ✓ Cheatsheet updated: media/staged/UPLOAD_CHEATSHEET.md")

    print("\n" + "=" * 64)
    print("                  PRODUCTION RUN SUMMARY")
    print("=" * 64)
    print(f"ID:        {short_id}")
    print(f"Title:     {cut_sheet['title']}")
    print(f"Format:    {cut_sheet['format'].upper()} ({cut_sheet['total_duration_sec']}s total)")
    print(f"Output:    {package_dir.relative_to(ROOT_DIR)}/")
    print("=" * 64 + "\n")


def main():
    parser = argparse.ArgumentParser(description="GTA VI Content Engine Orchestrator")
    parser.add_argument("--batch", "-b", nargs="?", const=3, type=int, help="Batch process top N trends (default: 3)")
    parser.add_argument("--force", action="store_true", help="Ignore deduplication history when running")
    parser.add_argument("--queue", "-q", action="store_true", help="Display all videos in publishing queue registry")
    parser.add_argument("--publish", type=str, help="Mark video ID as published (e.g., short_001)")
    parser.add_argument("--log-stats", type=str, help="Log performance metrics for video ID (e.g., short_001)")
    parser.add_argument("--views", type=int, default=0, help="Views count for --log-stats")
    parser.add_argument("--likes", type=int, default=0, help="Likes count for --log-stats")
    parser.add_argument("--comments", type=int, default=0, help="Comments count for --log-stats")
    parser.add_argument("--retention", type=float, default=0.0, help="Retention percent for --log-stats")
    parser.add_argument("--report", action="store_true", help="Display analytics performance summary across formats")

    args = parser.parse_args()

    if args.queue:
        QueueManager().print_queue_table()
    elif args.publish:
        qm = QueueManager()
        if qm.mark_published(args.publish, platform="all"):
            print(f"✓ Video '{args.publish}' successfully marked as PUBLISHED across all platforms.")
            print(f"✓ Trend recorded in deduplication history.")
            print(f"✓ Cheatsheet refreshed -> media/staged/UPLOAD_CHEATSHEET.md")
        else:
            print(f"✗ Video ID '{args.publish}' not found in publishing queue.")
    elif args.log_stats:
        tracker = PerformanceTracker()
        entry = tracker.log_metrics(
            short_id=args.log_stats,
            views=args.views,
            likes=args.likes,
            comments=args.comments,
            retention_pct=args.retention
        )
        print(f"✓ Performance metrics logged for '{args.log_stats}':")
        print(f"  Format: {entry['format']} | Views: {entry['views']:,} | Likes: {entry['likes']:,} | Score: {entry['engagement_score']}")
    elif args.report:
        tracker = PerformanceTracker()
        tracker.get_report()
    elif args.batch is not None:
        BatchRunner().run_batch(limit=args.batch, force=args.force)
    else:
        run_single_pipeline(force=args.force)


if __name__ == "__main__":
    main()


