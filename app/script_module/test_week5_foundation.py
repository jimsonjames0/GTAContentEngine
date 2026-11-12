import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]

# Add module directories to path
sys.path.insert(0, str(ROOT_DIR / "app" / "trend_module"))
sys.path.insert(0, str(ROOT_DIR / "app" / "script_module"))

from source_validator import SourceValidator


def test_week5_foundation():
    print("=" * 64)
    print("      WEEK 5 FOUNDATION VERIFICATION")
    print("=" * 64)

    # 1. Verify docs exist and are non-empty
    baseline_path = ROOT_DIR / "docs" / "month1_baseline_review.md"
    style_guide_md_path = ROOT_DIR / "docs" / "EDITORIAL_STYLE_GUIDE.md"
    assert baseline_path.exists(), f"Missing: {baseline_path}"
    assert baseline_path.stat().st_size > 0, f"Empty: {baseline_path}"
    assert style_guide_md_path.exists(), f"Missing: {style_guide_md_path}"
    assert style_guide_md_path.stat().st_size > 0, f"Empty: {style_guide_md_path}"
    print("  [PASS] docs/month1_baseline_review.md exists and is non-empty")
    print("  [PASS] docs/EDITORIAL_STYLE_GUIDE.md exists and is non-empty")

    # 2. Load editorial_style_guide.json and validate required keys
    style_guide_path = ROOT_DIR / "formats" / "editorial_style_guide.json"
    assert style_guide_path.exists(), f"Missing: {style_guide_path}"
    with open(style_guide_path, "r", encoding="utf-8") as f:
        guide = json.load(f)

    required_keys = ["channel_identity", "narrative_rules", "banned_phrases", "rejected_content_types"]
    for key in required_keys:
        assert key in guide, f"Missing key in editorial_style_guide.json: {key}"

    assert isinstance(guide["banned_phrases"], list) and len(guide["banned_phrases"]) > 0
    assert isinstance(guide["rejected_content_types"], list) and len(guide["rejected_content_types"]) > 0
    assert "target_audience" in guide["channel_identity"]
    assert "tone" in guide["channel_identity"]
    assert "hook" in guide["narrative_rules"]
    assert "body" in guide["narrative_rules"]
    assert "payoff" in guide["narrative_rules"]

    print("  [PASS] formats/editorial_style_guide.json loaded with all required keys")
    print(f"         channel_identity keys: {list(guide['channel_identity'].keys())}")
    print(f"         narrative_rules keys: {list(guide['narrative_rules'].keys())}")
    print(f"         banned_phrases count: {len(guide['banned_phrases'])}")
    print(f"         rejected_content_types count: {len(guide['rejected_content_types'])}")

    # 3. Test SourceValidator.from_trend() using a sample trend
    trends_path = ROOT_DIR / "data" / "trends" / "latest_trends.json"
    assert trends_path.exists(), f"Missing: {trends_path}"
    with open(trends_path, "r", encoding="utf-8") as f:
        trends = json.load(f)
    assert len(trends) > 0, "No trends found in latest_trends.json"

    sample_trend = trends[0]
    validator = SourceValidator()
    record = validator.from_trend(sample_trend)

    assert record.source_type == "reddit_discovery"
    assert record.usage_permission_status == "topic_discovery_only"
    assert record.verification_status == "community_observation"
    assert record.retrieval_date.endswith("+00:00") or "Z" in record.retrieval_date
    assert record.source_id != ""

    # 4. Save source record
    saved_path = validator.save_record(record)
    assert saved_path.exists(), f"Source record not saved: {saved_path}"
    assert saved_path.stat().st_size > 0, f"Source record empty: {saved_path}"

    # Verify round-trip load
    loaded = validator.load_record(record.source_id)
    assert loaded is not None
    assert loaded.source_id == record.source_id
    assert loaded.url == record.url

    print(f"  [PASS] SourceValidator.from_trend() created SourceRecord:")
    print(f"         source_id={record.source_id}")
    print(f"         source_type={record.source_type}")
    print(f"         verification_status={record.verification_status}")
    print(f"         usage_permission_status={record.usage_permission_status}")
    print(f"  [PASS] Source record saved to: {saved_path.relative_to(ROOT_DIR)}")
    print(f"  [PASS] Round-trip load verified")

    print("\n" + "=" * 64)
    print("      WEEK 5 FOUNDATION VERIFICATION PASSED")
    print("=" * 64)


if __name__ == "__main__":
    test_week5_foundation()
