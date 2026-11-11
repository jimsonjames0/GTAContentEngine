import json
import re
from pathlib import Path
from gtts import gTTS
from mutagen.mp3 import MP3


class VoiceGenerator:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.voice_dir = self.root_dir / "media" / "voice"
        self.briefs_dir = self.root_dir / "data" / "content_briefs"
        self.voice_dir.mkdir(parents=True, exist_ok=True)

    def _clean_text_for_speech(self, text: str) -> str:
        # Strip straight and curly quotation marks so TTS does not say "quote"
        cleaned = re.sub(r'["“”\'‘’`]', "", text)
        cleaned = re.sub(r"[#*_~]", "", cleaned)
        cleaned = re.sub(r"\.{2,}", ".", cleaned)
        cleaned = re.sub(r"-{2,}", " - ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def generate(
        self,
        script: str = None,
        brief_filename: str = None,
        filename: str = "voiceover.mp3",
    ) -> tuple[Path, float]:
        # 1. Resolve script from brief_filename if passed
        if brief_filename:
            brief_path = self.briefs_dir / brief_filename
            if not brief_path.exists():
                raise FileNotFoundError(f"Content brief not found at {brief_path}")
            with open(brief_path, "r", encoding="utf-8") as f:
                brief_data = json.load(f)
            script_text = brief_data.get("script", "")
        elif script:
            script_text = script
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

        tts = gTTS(text=spoken_text, lang="en", tld="com", slow=False)
        tts.save(str(output_path))

        # 3. Read duration
        audio = MP3(str(output_path))
        duration = float(audio.info.length)

        return output_path, duration