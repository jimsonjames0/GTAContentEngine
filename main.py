import sys
from pathlib import Path

# Add project root and all module subdirectories to Python search path
ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = ROOT_DIR / "app"

sys.path.extend([
    str(ROOT_DIR),
    str(APP_DIR),
    str(APP_DIR / "trend_module"),
    str(APP_DIR / "script_module"),
    str(APP_DIR / "edit_module"),
])

from trend_module.reddit_collector import RedditCollector
from trend_module.storage import TrendStorage
from script_module.idea_generator import IdeaGenerator
from script_module.storage import IdeaStorage
from script_module.script_writer import ScriptWriter
from script_module.brief_storage import BriefStorage
from edit_module.cut_sheet import CutSheetGenerator


def run_pipeline():
    print("=" * 64)
    print("      GTA VI CONTENT ENGINE — AUTOMATED DAILY PIPELINE")
    print("=" * 64)

    # 1. Collect & Score Trends
    print("\n[Step 1/4] Scraping & ranking r/GTA6 trends...")
    collector = RedditCollector()
    trend_storage = TrendStorage()

    trends = collector.collect(limit=5)
    trend_file = trend_storage.save(trends)
    top_trend = trends[0]
    top_title = top_trend.title if hasattr(top_trend, "title") else top_trend.get("title", "")
    print(f"  ✓ Processed {len(trends)} trends -> {trend_file.name}")
    print(f"    Top Trend: '{top_title[:55]}...'")

    # 2. Match Formats & Generate Ideas
    print("\n[Step 2/4] Selecting format and generating hook concepts...")
    idea_gen = IdeaGenerator()
    idea_storage = IdeaStorage()

    ideas = idea_gen.generate_batch(trends)
    idea_file = idea_storage.save(ideas)
    top_idea = ideas[0]
    print(f"  ✓ Generated {len(ideas)} ideas -> {idea_file.name}")
    print(f"    Selected Format: {top_idea.format_name.upper()}")
    print(f"    Hook: \"{top_idea.hook}\"")

    # 3. Compile Context-Aware Script & Content Brief
    print("\n[Step 3/4] Writing script & saving production brief...")
    writer = ScriptWriter()
    brief_storage = BriefStorage()

    brief = writer.write_brief(top_idea)
    brief_file = brief_storage.save(brief, filename="brief_001.json")
    print(f"  ✓ Brief validated -> {brief_file.name}")
    print(f"    Required Media Tags: {brief.footage}")

    # 4. Generate Production Cut Sheet
    print("\n[Step 4/4] Building video editor cut sheet...")
    cut_generator = CutSheetGenerator()
    cut_sheet = cut_generator.generate(brief_filename="brief_001.json")
    print("  ✓ Cut sheet timeline generated.")

    # Production Summary
    print("\n" + "=" * 64)
    print("                  PRODUCTION RUN SUMMARY")
    print("=" * 64)
    print(f"Title:     {cut_sheet['title']}")
    print(f"Format:    {cut_sheet['format'].upper()} ({cut_sheet['total_duration_sec']}s total)")
    print(f"Hook:      \"{cut_sheet['hook']}\"")
    print("\nShot Breakdown:")
    for shot in cut_sheet["timeline"]:
        print(f"  [{shot['start_time_sec']:>4}s - {shot['end_time_sec']:>4}s] {shot['footage_tag']:<28} -> {shot['file_target']}")
    
    print("\nVoiceover Script:")
    print(f"\"{cut_sheet['full_script']}\"")
    print("=" * 64)
    print("Pipeline finished successfully. All assets ready for assembly.\n")


if __name__ == "__main__":
    run_pipeline()