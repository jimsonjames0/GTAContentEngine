import json
import re
import asyncio
from pathlib import Path
from gtts import gTTS
from mutagen.mp3 import MP3


class VoiceGenerator:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.voice_dir = self.root_dir / "media" / "voice"
        self.voice_dir.mkdir(parents=True, exist_ok=True)
        self.voice_dir.mkdir(parents=True, exist_ok=True)
        self.briefs_dir = self.root_dir / "data" / "content_briefs"
        self._edge_tts_available = self._check_edge_tts()

    def _check_edge_tts(self) -> bool:
        """Check if edge-tts is available for neural synthesis."""
        try:
            import edge_tts
            return True
        except ImportError:
            return False

    def _clean_text_for_speech(self, text: str) -> str:
        # Strip straight and curly quotation marks so TTS does not say "quote"
        cleaned = re.sub(r'["\u201c\u201d\'\u2018\u2019`]', "", text)
        cleaned = re.sub(r"[#*_~]", "", cleaned)
        cleaned = re.sub(r"\.{2,}", ".", cleaned)
        cleaned = re.sub(r"-{2,}", " - ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def generate(self, script: str = None, brief_filename: str = None, filename: str = "voiceover.mp3", format_name: str = None) -> tuple[Path, float]:
        # 1. Resolve script from brief_filename if passed
        if brief_filename:
            brief_path = self.briefs_dir / brief_filename
            if not brief_path.exists():
                raise FileNotFoundError(f"Content brief not found at {brief_path}")
            with open(brief_path, "r", encoding="utf-8") as f:
                brief_data = json.load(f)
            script_text = brief_data.get("script", "")
            # Auto-detect format so per-format neural voices are used even when callers omit format_name
            if not format_name:
                format_name = brief_data.get("format", "breakdown")
        elif script:
            script_text = script
            brief_data = None
        else:
            # Fallback default: load brief_001.json if neither is supplied
            default_brief = self.briefs_dir / "brief_001.json"
            if default_brief.exists():
                with open(default_brief, "r", encoding="utf-8") as f:
                    brief_data = json.load(f)
                script_text = brief_data.get("script", "")
            else:
                raise ValueError("No script text or brief_filename provided to VoiceGenerator.")

        # 2. Sanitize and synthesize speech
        spoken_text = self._clean_text_for_speech(script_text)
        output_path = self.voice_dir / filename

        # Resolve format-specific voice settings
        format_settings = {"voice": "en-US-ChristopherNeural", "rate": "+8%", "pitch": "-2Hz"}
        if format_name:
            fmt_path = self.root_dir / "formats" / f"{format_name}.json"
            if fmt_path.exists():
                with open(fmt_path, "r", encoding="utf-8") as f:
                    fmt_data = json.load(f)
                persona = fmt_data.get("persona", {})
                voice_profile = persona.get("voice_profile", {})
                neural_voice = persona.get("neural_voice", {})
                format_settings["voice"] = neural_voice.get("voice", "en-US-ChristopherNeural")
                format_settings["rate"] = neural_voice.get("rate", "+8%")
                format_settings["pitch"] = neural_voice.get("pitch", "-2Hz")

        # 3. Synthesize speech (edge-tts preferred, gTTS fallback)
        if self._edge_tts_available:
            try:
                import edge_tts
                async def _tts():
                    communicate = edge_tts.Communicate(
                        spoken_text,
                        voice=format_settings["voice"],
                        rate=format_settings["rate"],
                        pitch=format_settings["pitch"],
                    )
                    await communicate.save(str(output_path))
                asyncio.run(_tts())
            except Exception:
                # Offline / malformed edge-tts error: fall back to gTTS
                tts = gTTS(text=spoken_text, lang="en", tld="com", slow=False)
                tts.save(str(output_path))
        else:
            # gTTS fallback (edge-tts not installed)
            tts = gTTS(text=spoken_text, lang="en", tld="com", slow=False)
            tts.save(str(output_path))

        # 4. Read duration
        audio = MP3(str(output_path))
        duration = float(audio.info.length)

        # 5. Generate and persist word-level timestamps for caption sync
        timestamps = self._generate_weighted_timestamps(spoken_text, duration)
        ts_path = self.voice_dir / f"{output_path.stem}_timestamps.json"
        with open(ts_path, "w", encoding="utf-8") as f:
            json.dump(timestamps, f, indent=2)

        return output_path, duration

    def _generate_weighted_timestamps(self, text: str, duration: float) -> list[dict]:
        """Generate acoustic prosody-weighted word timestamps matching exact duration."""
        raw_words = text.split()
        if not raw_words or duration <= 0:
            return []

        weights = []
        pauses = []
        for w in raw_words:
            clean = re.sub(r"[^\w]", "", w)
            syllables = len(re.findall(r"[aeiouy]+", clean.lower())) or 1
            base_w = max(1.0, len(clean) * 0.4 + syllables * 0.6)

            pause = 0.0
            if re.search(r"[,;]$", w):
                pause = 0.12
            elif re.search(r"[.!?]$", w):
                pause = 0.25
            elif re.search(r"[:—\-]$", w):
                pause = 0.18
            weights.append(base_w)
            pauses.append(pause)

        total_pause = sum(pauses)
        speaking_time = max(duration * 0.6, duration - total_pause)
        total_w = sum(weights) or 1.0

        timeline = []
        curr = 0.0
        for i, w in enumerate(raw_words):
            dur = (weights[i] / total_w) * speaking_time + pauses[i]
            start_t = curr
            end_t = min(duration, curr + dur)
            timeline.append({
                "word": w,
                "clean_word": re.sub(r"[^\w]", "", w),
                "start_sec": round(start_t, 3),
                "end_sec": round(end_t, 3),
                "duration_sec": round(end_t - start_t, 3)
            })
            curr = end_t

        if timeline:
            timeline[-1]["end_sec"] = round(duration, 3)
            timeline[-1]["duration_sec"] = round(duration - timeline[-1]["start_sec"], 3)
        return timeline

    def get_timestamps(self, filename: str = "voiceover.mp3", fallback_text: str = "", duration: float = 0.0) -> list[dict]:
        """Retrieve persisted timestamps or generate on-the-fly."""
        stem = Path(filename).stem
        ts_path = self.voice_dir / f"{stem}_timestamps.json"
        if ts_path.exists():
            try:
                with open(ts_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        if fallback_text and duration > 0:
            return self._generate_weighted_timestamps(self._clean_text_for_speech(fallback_text), duration)
        return []
