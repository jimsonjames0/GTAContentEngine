import sys
import json
import tempfile
from pathlib import Path
import numpy as np
from moviepy import AudioFileClip

ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = ROOT_DIR / "app"
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(APP_DIR / "script_module"))
sys.path.insert(0, str(APP_DIR / "edit_module"))
sys.path.insert(0, str(APP_DIR / "trend_module"))

from voice_generator import VoiceGenerator
from audio_mixer import AudioMixer
from render_engine import RenderEngine


def test_week6_audio():
    print("=" * 64)
    print("      WEEK 6 — NEURAL VOICE & AUDIO DUCKING VERIFICATION")
    print("=" * 64)

    tmp = Path(tempfile.mkdtemp())

    # --- 6.1 Neural TTS voice generation (edge-tts) across multiple personas ---
    print("\n[Step 1/4] Neural TTS voice generation across format personas")
    vg = VoiceGenerator()
    assert vg._edge_tts_available, "edge-tts not available"

    test_formats = ["breakdown", "discovery", "theory"]
    voice_files = {}
    for fmt in test_formats:
        v_path, v_dur = vg.generate(
            script=f"This is a {fmt} format script testing neural voice persona and pacing.",
            filename=f"week6_{fmt}_voice.mp3",
            format_name=fmt
        )
        assert v_path.exists(), f"Voice file not created for {fmt}"
        assert v_path.stat().st_size > 0, f"Voice file empty for {fmt}"
        voice_files[fmt] = (v_path, v_dur)
        print(f"  [PASS] Persona '{fmt}' generated: {v_path.name} ({v_dur:.2f}s, {v_path.stat().st_size:,} bytes)")

    # --- 6.2 Background music generation for all format music styles ---
    print("\n[Step 2/4] Background music generation for each format style")
    am = AudioMixer()
    styles = ["subtle_background", "energetic", "mysterious_or_minimal", "funny_or_trending", "light_or_none"]
    for style in styles:
        music_path = am.ensure_music(style, duration_sec=5.0)
        assert music_path.exists(), f"Music file not created: {style}"
        assert music_path.stat().st_size > 0, f"Music file empty: {style}"
        print(f"  [PASS] Music generated: {style} ({music_path.stat().st_size:,} bytes)")

    # --- 6.3 Dynamic audio ducking verification ---
    print("\n[Step 3/4] Dynamic audio ducking verification")
    voice_path, voice_dur = voice_files["breakdown"]
    mixed_path, mixed_dur = am.mix_ducked_audio(
        voice_path,
        music_style="subtle_background",
        music_duration=max(10.0, voice_dur + 2.0)
    )
    assert mixed_path.exists(), "Mixed audio not created"
    assert mixed_path.stat().st_size > 0, "Mixed audio empty"
    mixed_clip = AudioFileClip(str(mixed_path))
    assert abs(mixed_clip.duration - voice_dur) < 0.2, f"Mixed duration {mixed_clip.duration} does not match voice {voice_dur}"
    mixed_clip.close()
    print(f"  [PASS] Dynamic ducking applied: {mixed_path.name} ({mixed_dur:.2f}s)")

    # --- 6.4 Full RenderEngine integration with ducked audio ---
    print("\n[Step 4/4] Full RenderEngine integration")
    v2_brief = ROOT_DIR / "data" / "content_briefs" / "brief_short_001_v2.json"
    if v2_brief.exists():
        render_engine = RenderEngine()
        render_engine.final_dir = tmp / "final"
        render_engine.final_dir.mkdir(parents=True, exist_ok=True)

        master = render_engine.render_master(
            brief_filename="brief_short_001_v2.json",
            output_filename="test_week6_master.mp4"
        )
        assert master.exists(), "Master video not created"
        assert master.stat().st_size > 0, "Master video empty"
        print(f"  [PASS] RenderEngine render_master() generated: {master.name} ({master.stat().st_size:,} bytes)")
    else:
        print("  [SKIP] brief_short_001_v2.json not found")

    # Cleanup temporary test directory
    if tmp.exists():
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 64)
    print("      WEEK 6 AUDIO VERIFICATION PASSED")
    print("=" * 64)


if __name__ == "__main__":
    test_week6_audio()

