import json
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = ROOT_DIR / "app"

sys.path.insert(0, str(APP_DIR / "script_module"))
sys.path.insert(0, str(APP_DIR / "trend_module"))
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(APP_DIR / "edit_module"))

from script_writer import ScriptWriter
from content_brief import ContentBrief
from cut_sheet import CutSheetGenerator
from trend_module.source_validator import SourceValidator


def test_scriptwriter2():
    print("=" * 64)
    print("      WEEK 5 — SCRIPTWRITER 2.0 TEST & BASELINE COMPARISON")
    print("=" * 64)

    writer = ScriptWriter()

    baseline_topics = [
        {
            "trend_title": "PlayStation: \u201cGrand Theft Auto VI is the most pre-ordered game in PlayStation Store history!\u201d, PS5 features trailer.",
            "trend_url": "https://www.reddit.com/r/GTA6/comments/1xsq6qb/playstation_grand_theft_auto_vi_is_the_most/",
            "source": "reddit",
            "format_name": "breakdown",
            "hook": "Nobody noticed this: PlayStation pre-order milestone.",
            "concept": "Analyze the technical/gameplay details in pre-order milestone.",
            "recommended_length": "30-45",
        },
        {
            "trend_title": "Grand Theft Auto VI: Pre-Load Now Trailer",
            "trend_url": "https://www.reddit.com/r/GTA6/comments/1xsnl5x/grand_theft_auto_vi_preload_now_trailer/",
            "source": "reddit",
            "format_name": "discovery",
            "hook": "Look at this GTA VI detail: Pre-Load Now Trailer.",
            "concept": "Break down the new discovery around pre-load trailer.",
            "recommended_length": "20-40",
        },
        {
            "trend_title": "New GTA 6 Artwork",
            "trend_url": "https://www.reddit.com/r/GTA6/comments/1xsnry0/new_gta_6_artwork/",
            "source": "reddit",
            "format_name": "discovery",
            "hook": "I just found something interesting: New GTA 6 Artwork.",
            "concept": "Break down the new discovery around artwork.",
            "recommended_length": "20-40",
        },
    ]

    briefs = []

    for i, topic in enumerate(baseline_topics, start=1):
        short_id = f"short_{i:03d}"
        print(f"\n--- Generating v2.0 brief for {short_id} ---")

        brief = writer.write_brief(topic)

        writer.validate_editorial_quality(brief)
        print(f"  [PASS] validate_editorial_quality() passed")
        print(f"  Hook: {brief.hook[:70]}...")
        print(f"  Central Angle: {brief.central_angle[:70]}...")
        print(f"  Payoff: {brief.payoff[:70]}...")
        print(f"  Verified Claims: {brief.verified_claims}")
        print(f"  Speculation: {brief.speculation}")
        print(f"  Source References: {brief.source_references}")
        print(f"  Word Count: {len(brief.script.split())}")
        print(f"  Model: {brief.model_id}")
        print(f"  Format: {brief.format}")

        briefs_dir = ROOT_DIR / "data" / "content_briefs"
        briefs_dir.mkdir(parents=True, exist_ok=True)
        brief_path = briefs_dir / f"brief_{short_id}_v2.json"
        brief_dict = {
            "title": brief.title,
            "format": brief.format,
            "hook": brief.hook,
            "script": brief.script,
            "length": brief.length,
            "footage": brief.footage,
            "voice": brief.voice,
            "central_angle": brief.central_angle,
            "narration": brief.narration,
            "verified_claims": brief.verified_claims,
            "speculation": brief.speculation,
            "source_references": brief.source_references,
            "visual_cues": brief.visual_cues,
            "payoff": brief.payoff,
            "call_to_action": brief.call_to_action,
            "model_id": brief.model_id,
            "prompt_version": brief.prompt_version,
            "generated_at": brief.generated_at,
            "approval_status": brief.approval_status,
        }
        with open(brief_path, "w", encoding="utf-8") as f:
            json.dump(brief_dict, f, indent=2, ensure_ascii=False)

        print(f"  [SAVED] {brief_path.name}")
        briefs.append(brief)

    print("\n" + "=" * 64)
    print("      ASSERTIONS")
    print("=" * 64)

    for brief in briefs:
        writer.validate_editorial_quality(brief)
    print("  [PASS] All 3 briefs pass validate_editorial_quality()")

    hooks = [b.hook for b in briefs]
    angles = [b.central_angle for b in briefs]
    payoffs = [b.payoff for b in briefs]
    assert len(set(hooks)) == 3, "Hooks must be distinct"
    assert len(set(angles)) == 3, "Central angles must be distinct"
    assert len(set(payoffs)) == 3, "Payoffs must be distinct"
    print("  [PASS] All 3 hooks, central angles, and payoffs are distinct")

    for i in range(3):
        for j in range(i + 1, 3):
            sentences_i = set(briefs[i].script.split(". "))
            sentences_j = set(briefs[j].script.split(". "))
            overlap = sentences_i.intersection(sentences_j)
            assert len(overlap) == 0, f"Sentence overlap between short_{i+1:03d} and short_{j+1:03d}: {overlap}"
    print("  [PASS] 0% sentence overlap between all 3 scripts")

    sv = SourceValidator()
    for brief in briefs:
        for sid in brief.source_references:
            record = sv.load_record(sid)
            assert record is not None, f"Source record {sid} not found"
            assert record.source_id == sid
    print("  [PASS] All briefs link to valid source_ids in data/sources/")

    cut_gen = CutSheetGenerator()
    brief_data_v1 = {
        "title": briefs[0].title,
        "format": briefs[0].format,
        "length": briefs[0].length,
        "footage": briefs[0].footage,
        "hook": briefs[0].hook,
        "script": briefs[0].script,
        "voice": briefs[0].voice,
    }
    temp_dir = Path(tempfile.mkdtemp())
    temp_brief = temp_dir / "brief_001_v2.json"
    with open(temp_brief, "w", encoding="utf-8") as f:
        json.dump(brief_data_v1, f, indent=2)
    cut_sheet = cut_gen.generate(brief_filename=str(temp_brief))
    title_str = cut_sheet["title"]
    duration = cut_sheet["total_duration_sec"]
    shots = len(cut_sheet["timeline"])
    print(f"  [PASS] CutSheetGenerator processed v2.0 brief: {title_str[:50]}... ({duration}s)")
    print(f"         Shots: {shots}")

    print("\n" + "=" * 64)
    print("      WEEK 5 SCRIPTWRITER 2.0 TEST PASSED")
    print("=" * 64)

    return briefs


if __name__ == "__main__":
    test_scriptwriter2()
