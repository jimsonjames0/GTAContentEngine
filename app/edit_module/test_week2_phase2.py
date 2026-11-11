from pathlib import Path
from render_engine import RenderEngine

def test_week2_phase2():
    print("=" * 64)
    print("      WEEK 2 PHASE 2 — MASTER RENDER ENGINE & AUDIO FIX")
    print("=" * 64)
    engine = RenderEngine()
    output_path = engine.render_master(brief_filename="brief_001.json", output_filename="short_001_master.mp4")
    print(f"Master render successful -> {output_path}")

if __name__ == "__main__":
    test_week2_phase2()
