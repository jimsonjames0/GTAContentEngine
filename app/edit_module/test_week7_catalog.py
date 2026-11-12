import sys
import json
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = ROOT_DIR / "app"
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(APP_DIR / "script_module"))
sys.path.insert(0, str(APP_DIR / "edit_module"))
sys.path.insert(0, str(APP_DIR / "trend_module"))

from asset_manager import AssetManager
from cut_sheet import CutSheetGenerator
from video_assembler import VideoAssembler


def test_week7_catalog():
    print("=" * 64)
    print("      WEEK 7 — VISUAL ASSET CATALOG & PACING VERIFICATION")
    print("=" * 64)

    # --- 7.1 Catalog File Verification ---
    print("\n[Step 1/5] Verifying data/catalog/asset_catalog.json...")
    catalog_path = ROOT_DIR / "data" / "catalog" / "asset_catalog.json"
    assert catalog_path.exists(), f"Catalog file missing: {catalog_path}"
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    assert "assets" in catalog and len(catalog["assets"]) >= 16, f"Expected >=16 assets, got {len(catalog.get('assets', {}))}"
    expected_categories = {"milestone", "website", "gameplay", "general"}
    assert set(catalog.get("categories", [])) == expected_categories
    print(f"  [PASS] Catalog contains {len(catalog['assets'])} assets across {expected_categories}")

    # --- 7.2 AssetManager Metadata Lookup & Filtering ---
    print("\n[Step 2/5] Testing AssetManager catalog queries...")
    am = AssetManager()

    meta = am.get_asset_metadata("trailer_cinematic_intro")
    assert meta["category"] == "gameplay"
    assert meta["recommended_motion"] == "zoom_in"
    assert len(meta["theme_color_rgb"]) == 3
    print(f"  [PASS] Metadata for 'trailer_cinematic_intro': {meta['category']} | {meta['recommended_motion']} | rgb={meta['theme_color_rgb']}")

    gameplay_assets = am.list_by_category("gameplay")
    assert len(gameplay_assets) == 4
    milestone_assets = am.list_by_category("milestone")
    assert len(milestone_assets) == 4
    print(f"  [PASS] list_by_category: gameplay={len(gameplay_assets)}, milestone={len(milestone_assets)}")

    # --- 7.3 Shot Pacing Variation in CutSheetGenerator ---
    print("\n[Step 3/5] Testing CutSheetGenerator narrative pacing...")
    csg = CutSheetGenerator()
    cut_sheet = csg.generate("brief_001.json")
    timeline = cut_sheet["timeline"]

    assert len(timeline) == 4, f"Expected 4 shots, got {len(timeline)}"
    durations = [shot["duration_sec"] for shot in timeline]
    # Check pacing variation: Hook shot (Shot 1) must be shorter than Middle analytical shots
    assert durations[0] < durations[1], f"Expected hook {durations[0]}s < body {durations[1]}s"
    assert len(set(durations)) >= 3, f"Expected pacing variation in durations, got: {durations}"
    assert round(sum(durations), 1) == round(cut_sheet["total_duration_sec"], 1)

    for shot in timeline:
        assert "section" in shot
        assert "category" in shot
        assert "camera_motion" in shot
        assert "zoom_intensity" in shot
        assert "file_target" in shot
    print(f"  [PASS] Shot pacing variation: {durations} (total={sum(durations):.1f}s)")
    print(f"  [PASS] All shots enriched with camera_motion & category metadata")

    # --- 7.4 Target Duration Dynamic Sizing ---
    print("\n[Step 4/5] Testing dynamic target_duration sync...")
    custom_sheet = csg.generate("brief_001.json", target_duration=19.4)
    custom_durs = [s["duration_sec"] for s in custom_sheet["timeline"]]
    assert round(sum(custom_durs), 1) == 19.4, f"Expected sum 19.4, got {sum(custom_durs)}"
    print(f"  [PASS] Target duration 19.4s matched: {custom_durs} (sum={sum(custom_durs):.1f}s)")

    # --- 7.5 Full Video Assembly with Synchronized Pacing ---
    print("\n[Step 5/5] Testing VideoAssembler output...")
    tmp = Path(tempfile.mkdtemp())
    va = VideoAssembler()
    va.final_dir = tmp

    assembly_out = va.assemble("brief_001.json", output_filename="week7_assembly_test.mp4")
    assert assembly_out.exists() and assembly_out.stat().st_size > 0
    print(f"  [PASS] VideoAssembler produced: {assembly_out.name} ({assembly_out.stat().st_size:,} bytes)")

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 64)
    print("      WEEK 7 CATALOG & PACING VERIFICATION PASSED")
    print("=" * 64)


if __name__ == "__main__":
    test_week7_catalog()
