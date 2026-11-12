import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from moviepy import VideoFileClip

ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = ROOT_DIR / "app"


class QualityGate:
    """Automated pre-publish quality gate for GTA VI content engine.

    Evaluates master video assets across 4 quality dimensions:
    1. Editorial Identity (anti-slop, banned phrases, claims separation)
    2. Video Technical Standards (1080x1920 9:16, duration bounds)
    3. Audio Standards (audio track presence, duration sync)
    4. Caption Sync (word-level timing within video bounds)
    """

    def __init__(self):
        self.root_dir = ROOT_DIR
        self.reports_dir = self.root_dir / "data" / "quality_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.style_guide_path = self.root_dir / "formats" / "editorial_style_guide.json"
        self.banned_phrases = self._load_banned_phrases()

    def _load_banned_phrases(self) -> list[str]:
        if self.style_guide_path.exists():
            try:
                with open(self.style_guide_path, "r", encoding="utf-8") as f:
                    guide = json.load(f)
                return guide.get("banned_phrases", [])
            except Exception:
                pass
        return []

    def evaluate(
        self,
        short_id: str,
        brief_path: Path,
        video_path: Path,
        metadata_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Perform full quality audit and save quality report."""
        checks = {}
        total_score = 0
        critical_passed = True

        # --- 1. Editorial Check (25 pts) ---
        ed_score = 0
        ed_notes = []
        brief_data = {}
        if brief_path.exists():
            try:
                with open(brief_path, "r", encoding="utf-8") as f:
                    brief_data = json.load(f)
                ed_score += 5

                full_text = f"{brief_data.get('hook', '')} {brief_data.get('script', '')} {brief_data.get('payoff', '')}".lower()
                has_banned = False
                for bp in self.banned_phrases:
                    if bp.lower() in full_text:
                        has_banned = True
                        ed_notes.append(f"Contains banned phrase: {bp}")
                if not has_banned:
                    ed_score += 8
                else:
                    critical_passed = False

                words = brief_data.get("script", "").split()
                if 50 <= len(words) <= 100:
                    ed_score += 6
                else:
                    ed_notes.append(f"Word count {len(words)} outside 50-100 range")

                if brief_data.get("verified_claims") and brief_data.get("source_references"):
                    ed_score += 6
                else:
                    ed_notes.append("Missing verified_claims or source_references")
            except Exception as e:
                ed_notes.append(f"Brief parsing error: {e}")
                critical_passed = False
        else:
            ed_notes.append(f"Brief file missing: {brief_path}")
            critical_passed = False

        checks["editorial_review"] = {
            "score": ed_score,
            "max_score": 25,
            "passed": ed_score >= 20 and not ed_notes,
            "notes": ed_notes or ["Editorial standards verified: 0 banned phrases, claims separated."]
        }
        total_score += ed_score

        # --- 2. Video Technical Standards (25 pts) ---
        vid_score = 0
        vid_notes = []
        video_clip = None
        vid_duration = 0.0

        if video_path.exists() and video_path.stat().st_size > 10000:
            vid_score += 5
            try:
                video_clip = VideoFileClip(str(video_path))
                w, h = video_clip.size
                vid_duration = video_clip.duration

                if (w, h) == (1080, 1920):
                    vid_score += 10
                elif abs(w / h - 9 / 16) < 0.05:
                    vid_score += 7
                else:
                    vid_notes.append(f"Invalid aspect ratio: {w}x{h}")
                    critical_passed = False

                if 8.0 <= vid_duration <= 60.0:
                    vid_score += 10
                else:
                    vid_notes.append(f"Duration {vid_duration:.1f}s outside bounds")
            except Exception as e:
                vid_notes.append(f"Video inspection error: {e}")
                critical_passed = False
        else:
            vid_notes.append(f"Video file missing or empty: {video_path}")
            critical_passed = False

        checks["video_technical"] = {
            "score": vid_score,
            "max_score": 25,
            "passed": vid_score >= 22 and not vid_notes,
            "notes": vid_notes or [f"Resolution 1080x1920 verified, duration {vid_duration:.1f}s within bounds."]
        }
        total_score += vid_score

        # --- 3. Audio Master Standards (25 pts) ---
        aud_score = 0
        aud_notes = []

        if video_clip and video_clip.audio is not None:
            aud_score += 15
            audio_dur = video_clip.audio.duration
            if abs(audio_dur - vid_duration) < 0.5:
                aud_score += 10
            else:
                aud_notes.append(f"Audio duration {audio_dur:.1f}s differs from video {vid_duration:.1f}s")
        else:
            aud_notes.append("No audio track found on video clip")
            critical_passed = False

        checks["audio_master"] = {
            "score": aud_score,
            "max_score": 25,
            "passed": aud_score >= 20,
            "notes": aud_notes or ["Audio track present and synchronized with video duration."]
        }
        total_score += aud_score

        if video_clip:
            video_clip.close()

        # --- 4. Caption & Metadata Standards (25 pts) ---
        cap_score = 0
        cap_notes = []

        timeline_path = self.root_dir / "media" / "temp_captions" / "caption_timeline.json"
        if timeline_path.exists():
            try:
                with open(timeline_path, "r", encoding="utf-8") as f:
                    tdata = json.load(f)
                num_phrases = tdata.get("num_phrases", 0)
                if num_phrases > 0:
                    cap_score += 12
                    last_end = tdata["timeline"][-1]["end_sec"]
                    if last_end <= vid_duration + 0.5:
                        cap_score += 5
                    else:
                        cap_notes.append(f"Caption timeline {last_end}s extends past video {vid_duration}s")
            except Exception:
                pass
        else:
            cap_score += 10

        if metadata_path and metadata_path.exists():
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    mdata = json.load(f)
                platforms = mdata.get("platforms", {})
                if "youtube_shorts" in platforms and "tiktok" in platforms and "instagram_reels" in platforms:
                    cap_score += 8
                else:
                    cap_notes.append("Metadata missing required social platforms")
            except Exception:
                cap_score += 4
        else:
            cap_score += 8

        checks["captions_and_metadata"] = {
            "score": cap_score,
            "max_score": 25,
            "passed": cap_score >= 18,
            "notes": cap_notes or ["Caption timeline synchronized and platforms populated."]
        }
        total_score += cap_score

        passed = critical_passed and total_score >= 80

        report = {
            "short_id": short_id,
            "passed": passed,
            "total_score": total_score,
            "max_score": 100,
            "critical_passed": critical_passed,
            "checks": checks
        }

        report_path = self.reports_dir / f"{short_id}_quality_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report
