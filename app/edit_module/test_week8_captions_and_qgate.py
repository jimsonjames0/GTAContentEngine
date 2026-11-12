import sys
import json
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = ROOT_DIR / "app"
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(APP_DIR / "script_module"))
sys.path.insert(0, str(APP_DIR / "edit_module"))
sys.path.insert(0, str(APP_DIR / "publish_module"))

from voice_generator import VoiceGenerator
from caption_generator import CaptionGenerator
from quality_gate import QualityGate


def test_week8():
    print("=" * 64)
    print("      WEEK 8 — CAPTIONS & QUALITY GATE VERIFICATION")
    print("=" * 64)

    # --- 8.1 Word-Level Timestamps ---
    print("\n[Step 1/4] Word-level timestamp extraction...")
    vg = VoiceGenerator()
    script = "Preload packages have hit backend stores ahead of the GTA VI launch window. Servers unlock soon."
    voice_path, duration = vg.generate(script=script, filename="w8_test_voice.mp3")

    ts_path = ROOT_DIR / "media" / "voice" / "w8_test_voice_timestamps.json"
    assert ts_path.exists(), f"Timestamps file missing: {ts_path}"
    with open(ts_path, "r", encoding="utf-8") as f:
        timestamps = json.load(f)

    assert len(timestamps) >= 12, f"Expected >=12 word timestamps, got {len(timestamps)}"
    for i in range(len(timestamps) - 1):
        assert timestamps[i]["start_sec"] <= timestamps[i]["end_sec"]
        assert timestamps[i]["end_sec"] <= timestamps[i + 1]["start_sec"] + 0.05
    assert abs(timestamps[-1]["end_sec"] - duration) < 0.1
    print(f"  [PASS] Extracted {len(timestamps)} word timestamps matching duration {duration:.2f}s")

    # --- 8.2 CaptionGenerator Keyword Highlighting ---
    print("\n[Step 2/4] Caption phrase grouping & keyword highlighting...")
    cg = CaptionGenerator()
    clips = cg.generate_captions(script=script, duration=duration, brief_filename="brief_short_001_v2.json")

    timeline_path = ROOT_DIR / "media" / "temp_captions" / "caption_timeline.json"
    assert timeline_path.exists(), "caption_timeline.json missing"
    with open(timeline_path, "r", encoding="utf-8") as f:
        tdata = json.load(f)

    assert len(tdata["timeline"]) >= 3
    highlighted_all = []
    for entry in tdata["timeline"]:
        highlighted_all.extend(entry.get("highlighted_words", []))

    assert "Preload" in highlighted_all or "preload" in [w.lower() for w in highlighted_all]
    assert "GTA" in highlighted_all or "VI" in highlighted_all or "launch" in highlighted_all
    print(f"  [PASS] Generated {len(clips)} caption clips with highlighted keywords: {set(highlighted_all)}")

    # --- 8.3 QualityGate Evaluation on Master Asset ---
    print("\n[Step 3/4] QualityGate evaluation on master video package...")
    qg = QualityGate()

    master_video = ROOT_DIR / "media" / "final" / "short_001_master.mp4"
    brief_file = ROOT_DIR / "data" / "content_briefs" / "brief_short_001_v2.json"
    meta_file = ROOT_DIR / "media" / "staged" / "short_001" / "metadata.json"

    assert master_video.exists(), f"Master video missing: {master_video}"
    assert brief_file.exists(), f"Brief file missing: {brief_file}"

    report = qg.evaluate(
        short_id="short_001",
        brief_path=brief_file,
        video_path=master_video,
        metadata_path=meta_file if meta_file.exists() else None
    )

    print(f"  Quality Gate Score: {report['total_score']}/{report['max_score']}")
    print(f"  Passed: {report['passed']}")
    for cat, info in report["checks"].items():
        print(f"    • {cat}: {info['score']}/{info['max_score']} (passed={info['passed']})")

    assert report["passed"] is True, f"Quality gate failed: {report}"
    assert report["total_score"] >= 80

    report_file = ROOT_DIR / "data" / "quality_reports" / "short_001_quality_report.json"
    assert report_file.exists(), "Report file not saved"
    print(f"  [PASS] Quality report saved: {report_file.name}")

    # --- 8.4 QualityGate Rejection on Defective Brief ---
    print("\n[Step 4/4] QualityGate rejection on defective asset...")
    tmp = Path(tempfile.mkdtemp())
    bad_brief_path = tmp / "bad_brief.json"
    with open(bad_brief_path, "w", encoding="utf-8") as f:
        json.dump({
            "title": "Bad short",
            "format": "breakdown",
            "hook": "Nobody noticed this: Rockstar hid this in plain sight...",
            "script": "Nobody noticed this: Rockstar hid this in plain sight... Drop your thoughts below and stay tuned",
            "payoff": "Stay tuned."
        }, f)

    bad_report = qg.evaluate(
        short_id="bad_001",
        brief_path=bad_brief_path,
        video_path=master_video
    )
    assert bad_report["passed"] is False, "QualityGate should have failed bad brief"
    assert bad_report["critical_passed"] is False
    print(f"  [PASS] QualityGate correctly rejected defective brief (score={bad_report['total_score']}/100)")

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 64)
    print("      WEEK 8 CAPTIONS & QUALITY GATE VERIFICATION PASSED")
    print("=" * 64)


if __name__ == "__main__":
    test_week8()
