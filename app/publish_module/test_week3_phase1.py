import sys
import shutil
import json
from pathlib import Path

# Add project root and all module subdirectories to Python search path
ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = ROOT_DIR / "app"

sys.path.extend([
    str(ROOT_DIR),
    str(APP_DIR),
    str(APP_DIR / "trend_module"),
    str(APP_DIR / "script_module"),
    str(APP_DIR / "edit_module"),
    str(APP_DIR / "publish_module"),
])

from publish_module.metadata_generator import MetadataGenerator
from publish_module.cover_extractor import CoverExtractor


def test_week3_phase1():
    print("=" * 64)
    print("      WEEK 3 PHASE 1 — PUBLISHING PACKAGING & COVER EXTRACTION")
    print("=" * 64)

    brief_path = ROOT_DIR / "data" / "content_briefs" / "brief_001.json"
    master_video_path = ROOT_DIR / "media" / "final" / "short_001_master.mp4"

    assert brief_path.exists(), f"Content brief not found at: {brief_path}"
    assert master_video_path.exists(), f"Master video not found at: {master_video_path}"

    # 1. Test Metadata Generator
    print("\n[Test 1/3] Generating platform metadata for short_001...")
    meta_gen = MetadataGenerator()
    metadata = meta_gen.generate_metadata(brief_path, brief_id="short_001")
    metadata_file = ROOT_DIR / "data" / "metadata" / "short_001_metadata.json"
    assert metadata_file.exists() and metadata_file.stat().st_size > 0
    print(f"  ✓ Metadata file created: {metadata_file.relative_to(ROOT_DIR)}")
    print(f"    YouTube Title: {metadata['platforms']['youtube_shorts']['title']}")
    print(f"    TikTok Caption: {metadata['platforms']['tiktok']['caption']}")

    # 2. Test Cover Extractor
    print("\n[Test 2/3] Extracting 1080x1920 cover frame from short_001_master.mp4...")
    cover_extractor = CoverExtractor()
    cover_file = cover_extractor.extract_cover(
        video_path=master_video_path,
        output_path=ROOT_DIR / "media" / "staged" / "short_001_cover.jpg",
        timestamp_sec=2.0
    )
    assert cover_file.exists() and cover_file.stat().st_size > 0
    print(f"  ✓ Cover thumbnail created: {cover_file.relative_to(ROOT_DIR)}")
    print(f"    Cover Size: {cover_file.stat().st_size / 1024:.2f} KB")

    # 3. Test Staging Packaging for short_001
    print("\n[Test 3/3] Staging publishing package in media/staged/short_001/...")
    staged_package_dir = ROOT_DIR / "media" / "staged" / "short_001"
    staged_package_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(master_video_path, staged_package_dir / "master.mp4")
    shutil.copy2(cover_file, staged_package_dir / "cover.jpg")
    shutil.copy2(metadata_file, staged_package_dir / "metadata.json")
    shutil.copy2(brief_path, staged_package_dir / "brief.json")

    # Verify all staged assets
    required_files = ["master.mp4", "cover.jpg", "metadata.json", "brief.json"]
    for fname in required_files:
        fpath = staged_package_dir / fname
        assert fpath.exists() and fpath.stat().st_size > 0, f"Missing staged asset: {fpath}"
        print(f"  ✓ Staged file verified: {fpath.relative_to(ROOT_DIR)} ({fpath.stat().st_size / 1024:.2f} KB)")

    print("\n" + "=" * 64)
    print("      WEEK 3 PHASE 1 VERIFICATION PASSED SUCCESSFULLY!")
    print("=" * 64)


if __name__ == "__main__":
    test_week3_phase1()
