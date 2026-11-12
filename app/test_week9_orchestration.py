import sys
import json
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = ROOT_DIR / "app"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(APP_DIR / "script_module"))
sys.path.insert(0, str(APP_DIR / "publish_module"))
sys.path.insert(0, str(APP_DIR / "analytics_module"))

from format_selector import FormatSelector
from metadata_generator import MetadataGenerator
from queue_manager import QueueManager
from quality_gate import QualityGate
from performance_tracker import PerformanceTracker


def test_week9_orchestration():
    print("=" * 64)
    print("      WEEK 9 — ORCHESTRATION, QUALITY GATE & MONETIZATION")
    print("=" * 64)

    # --- 9.1 Analytics Feedback Loop & Format Selection ---
    print("\n[Step 1/4] Verifying Analytics Feedback Loop...")
    tracker = PerformanceTracker()
    tracker.log_metrics("short_001", views=90000, likes=4500, comments=320, retention_pct=0.75)

    fs = FormatSelector()
    weights = fs._load_weights()
    assert "breakdown" in weights, "breakdown format weight should be present"
    print(f"  [PASS] FormatSelector loaded weights: {weights}")

    selected_fmt = fs.select("Grand Theft Auto VI release date milestone")
    assert selected_fmt["name"] == "breakdown"
    print(f"  [PASS] Feedback-boosted selection: {selected_fmt['name']}")

    # --- 9.2 Contextual Monetization & Affiliate CTAs ---
    print("\n[Step 2/4] Verifying Monetization & Affiliate CTA Generation...")
    meta_gen = MetadataGenerator()
    brief_data = {
        "title": "Grand Theft Auto VI: Preload File Sizes and Storage Requirements",
        "format": "breakdown",
        "hook": "Preload packages have hit backend stores ahead of the launch window.",
        "script": "Preload packages have hit backend stores ahead of the GTA VI launch window. Servers unlock soon."
    }
    meta = meta_gen.generate_metadata(brief_data, brief_id="short_test_mono")
    assert "monetization" in meta, "Monetization block missing from metadata"
    mono = meta["monetization"]
    assert mono["recommended_affiliate_category"] == "console_storage_expansion"
    assert "SSD" in mono["pinned_comment_cta"]
    print(f"  [PASS] Affiliate Category: {mono['recommended_affiliate_category']}")
    print(f"  [PASS] Pinned Comment CTA: {mono['pinned_comment_cta'][:65]}...")

    # --- 9.3 Quality Gate Queue Integration & Staging Security ---
    print("\n[Step 3/4] Verifying Quality Gate enforcement in QueueManager...")
    qm = QueueManager()

    # Case A: Passed video package
    passed_q_report = {"total_score": 100, "passed": True, "critical_passed": True}
    entry_pass = qm.register(
        short_id="short_test_pass",
        brief=brief_data,
        metadata=meta,
        quality_report=passed_q_report
    )
    assert entry_pass["status"] == "ready_to_publish"
    assert entry_pass["quality_score"] == 100
    print("  [PASS] Passed audit registered -> status: ready_to_publish (100/100)")

    # Case B: Failed quality audit must be blocked from publishing
    failed_q_report = {"total_score": 60, "passed": False, "critical_passed": False}
    entry_fail = qm.register(
        short_id="short_test_fail",
        brief=brief_data,
        metadata=meta,
        quality_report=failed_q_report
    )
    assert entry_fail["status"] == "held_by_quality_gate"
    assert entry_fail["quality_score"] == 60
    print("  [PASS] Defective audit blocked -> status: held_by_quality_gate (60/100)")

    # Verify cheatsheet output
    cs_path = qm.generate_copy_sheet()
    assert cs_path.exists()
    with open(cs_path, "r", encoding="utf-8") as f:
        sheet_text = f.read()
    assert "**Quality Gate:**" in sheet_text and "PASSED" in sheet_text
    assert "5. 💰 Monetization & Pinned Comment" in sheet_text
    print(f"  [PASS] UPLOAD_CHEATSHEET.md verified with Quality Gate and Monetization CTA")

    # --- 9.4 Revenue Calculation in Performance Tracker ---
    print("\n[Step 4/4] Verifying Channel Revenue Projections...")
    revenue_metrics = tracker.get_monetization_metrics()
    assert revenue_metrics["total_views"] >= 90000
    assert revenue_metrics["estimated_shorts_ad_revenue_usd"] > 0
    assert revenue_metrics["estimated_affiliate_revenue_usd"] > 0
    assert revenue_metrics["total_estimated_earnings_usd"] > revenue_metrics["estimated_shorts_ad_revenue_usd"]
    print(f"  [PASS] Total Views Tracked: {revenue_metrics['total_views']:,}")
    print(f"  [PASS] Est. Shorts Ad Rev: ${revenue_metrics['estimated_shorts_ad_revenue_usd']:,.2f}")
    print(f"  [PASS] Est. Affiliate Rev: ${revenue_metrics['estimated_affiliate_revenue_usd']:,.2f}")
    print(f"  [PASS] Total Est. Revenue: ${revenue_metrics['total_estimated_earnings_usd']:,.2f}")

    print("\n" + "=" * 64)
    print("      WEEK 9 ORCHESTRATION & MONETIZATION TEST PASSED")
    print("=" * 64)


if __name__ == "__main__":
    test_week9_orchestration()
