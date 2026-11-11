from pathlib import Path
from asset_manager import AssetManager
from voice_generator import VoiceGenerator
from video_assembler import VideoAssembler


def test_week2_phase1():
    print("=" * 64)
    print("      WEEK 2 PHASE 1 — ASSET MOCK, VOICE & VIDEO ASSEMBLY")
    print("=" * 64)

    # 1. Asset Manager Test
    print("\n[Test 1/3] Ensuring raw assets exist...")
    asset_mgr = AssetManager()
    asset_paths = asset_mgr.ensure_assets_exist_from_brief("brief_001.json")
    for p in asset_paths:
        print(f"  ✓ Raw asset ready: {p.relative_to(asset_mgr.root_dir)}")

    # 2. Voice Generator Test
    print("\n[Test 2/3] Generating voiceover audio...")
    voice_gen = VoiceGenerator()
    voice_path, duration = voice_gen.generate(brief_filename="brief_001.json")
    print(f"  ✓ Voiceover generated: {voice_path.relative_to(voice_gen.root_dir)} ({duration:.2f}s)")

    # 3. Video Assembler Test
    print("\n[Test 3/3] Assembling and rendering final video...")
    assembler = VideoAssembler()
    output_path = assembler.assemble(brief_filename="brief_001.json", output_filename="short_001_raw_assembly.mp4")
    print(f"  ✓ Final video assembled: {output_path.relative_to(assembler.root_dir)}")
    print(f"    File Size: {output_path.stat().st_size / (1024 * 1024):.2f} MB")

    print("\n" + "=" * 64)
    print("      WEEK 2 PHASE 1 TESTS PASSED SUCCESSFULLY!")
    print("=" * 64)


if __name__ == "__main__":
    test_week2_phase1()
