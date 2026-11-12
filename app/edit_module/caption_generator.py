import json
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip

try:
    from voice_generator import VoiceGenerator
except ImportError:
    from edit_module.voice_generator import VoiceGenerator


class CaptionGenerator:

    GTA_KEYWORDS = {
        "gta", "vi", "gta6", "gtavi", "vice", "city", "rockstar", "preload", "pre-load",
        "ps5", "playstation", "xbox", "trailer", "leaks", "lucia", "jason",
        "rdr2", "servers", "milestone", "release", "preorder", "pre-order", "launch",
        "graphics", "physics", "density", "water", "mechanics", "map", "countdown"
    }

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.briefs_dir = self.root_dir / "data" / "content_briefs"
        self.temp_dir = self.root_dir / "media" / "temp_captions"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.voice_generator = VoiceGenerator()

    def _is_keyword(self, clean_word: str) -> bool:
        """Identify high-signal GTA VI terms and numerical stats for accent highlighting."""
        w = clean_word.lower()
        if w in self.GTA_KEYWORDS:
            return True
        if bool(re.search(r"\d", w)):
            return True
        return False

    def _get_font(self, size: int = 54):
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ]
        for fpath in font_paths:
            if Path(fpath).exists():
                try:
                    return ImageFont.truetype(fpath, size=size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def _create_text_image(self, words_with_flags: list[tuple[str, bool]], img_size=(1080, 220), accent_color=(255, 225, 0, 255)) -> str:
        """Render high-contrast captioned words with dynamic keyword highlighting and black outline."""
        img = Image.new("RGBA", img_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = self._get_font(size=54)

        space_bbox = draw.textbbox((0, 0), " ", font=font)
        space_w = space_bbox[2] - space_bbox[0]

        word_metrics = []
        total_w = 0
        max_h = 0
        for word, is_highlight in words_with_flags:
            bbox = draw.textbbox((0, 0), word, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            word_metrics.append((word, is_highlight, w, h))
            total_w += w + space_w
            max_h = max(max_h, h)

        total_w -= space_w
        start_x = max(20, (img_size[0] - total_w) // 2)
        y = max(10, (img_size[1] - max_h) // 2)

        # Draw heavy black stroke (width 4) for high readability over B-roll
        stroke_w = 4
        for adj_x in range(-stroke_w, stroke_w + 1):
            for adj_y in range(-stroke_w, stroke_w + 1):
                if adj_x != 0 or adj_y != 0:
                    curr_x = start_x
                    for word, _, w, _ in word_metrics:
                        draw.text((curr_x + adj_x, y + adj_y), word, font=font, fill=(0, 0, 0, 255))
                        curr_x += w + space_w

        # Draw text fill: accent color for keywords, white for standard words
        curr_x = start_x
        for word, is_highlight, w, _ in word_metrics:
            fill_color = accent_color if is_highlight else (255, 255, 255, 255)
            draw.text((curr_x, y), word, font=font, fill=fill_color)
            curr_x += w + space_w

        phrase_key = "_".join(w[0] for w in words_with_flags)
        out_path = self.temp_dir / f"caption_{abs(hash(phrase_key))}.png"
        img.save(out_path)
        return str(out_path)

    def _group_words_into_phrases(self, word_timestamps: list[dict], max_words: int = 4) -> list[dict]:
        """Group word-level timestamps into natural visual phrases bounded by punctuation."""
        phrases = []
        current_words = []

        for wt in word_timestamps:
            current_words.append(wt)
            word_text = wt.get("word", "")
            is_clause_boundary = bool(re.search(r"[,.!?;:—\-]$", word_text))

            if len(current_words) >= max_words or is_clause_boundary:
                phrases.append({
                    "words": current_words,
                    "text": " ".join(w["word"] for w in current_words),
                    "start_sec": current_words[0]["start_sec"],
                    "end_sec": current_words[-1]["end_sec"],
                    "duration_sec": round(current_words[-1]["end_sec"] - current_words[0]["start_sec"], 3)
                })
                current_words = []

        if current_words:
            phrases.append({
                "words": current_words,
                "text": " ".join(w["word"] for w in current_words),
                "start_sec": current_words[0]["start_sec"],
                "end_sec": current_words[-1]["end_sec"],
                "duration_sec": round(current_words[-1]["end_sec"] - current_words[0]["start_sec"], 3)
            })

        return phrases

    def generate_captions(self, script: str, duration: float, brief_filename: str = "brief_001.json") -> list:
        if not script:
            return []

        # 1. Resolve word timestamps
        stem = Path(brief_filename).stem
        word_timestamps = self.voice_generator.get_timestamps(
            filename=f"{stem}.mp3",
            fallback_text=script,
            duration=duration
        )

        # 2. Group into prosody-bounded phrases
        phrases = self._group_words_into_phrases(word_timestamps, max_words=4)
        if not phrases:
            return []

        # 3. Resolve accent color from format
        brief_path = self.briefs_dir / brief_filename
        accent_color = (255, 225, 0, 255)
        if brief_path.exists():
            try:
                with open(brief_path, "r", encoding="utf-8") as f:
                    brief_data = json.load(f)
                fmt_name = brief_data.get("format", "breakdown")
                fmt_file = self.root_dir / "formats" / f"{fmt_name}.json"
                if fmt_file.exists():
                    with open(fmt_file, "r", encoding="utf-8") as f:
                        fmt_spec = json.load(f)
                    cstyle = fmt_spec.get("editing_style", {}).get("caption_style", "")
                    if "comic" in cstyle or "reaction" in cstyle:
                        accent_color = (0, 240, 255, 255)  # Cyan accent for reaction/meme
                    elif "highlight" in cstyle:
                        accent_color = (255, 225, 0, 255)  # Gold/yellow accent for discovery/breakdown
            except Exception:
                pass

        # 4. Generate ImageClips and timeline metadata
        caption_clips = []
        caption_timeline = []

        for p in phrases:
            words_with_flags = []
            highlighted_words = []
            for w_info in p["words"]:
                clean = w_info.get("clean_word", re.sub(r"[^\w]", "", w_info["word"]))
                is_hl = self._is_keyword(clean)
                words_with_flags.append((w_info["word"], is_hl))
                if is_hl:
                    highlighted_words.append(clean)

            start_t = p["start_sec"]
            end_t = min(duration, p["end_sec"])
            clip_duration = max(0.4, round(end_t - start_t, 3))

            img_path = self._create_text_image(words_with_flags, accent_color=accent_color)
            clip = ImageClip(img_path).with_duration(clip_duration).with_start(start_t)
            clip = clip.with_position(("center", 1250))
            caption_clips.append(clip)

            caption_timeline.append({
                "phrase": p["text"],
                "start_sec": start_t,
                "end_sec": end_t,
                "duration_sec": clip_duration,
                "highlighted_words": highlighted_words
            })

        # 5. Persist timeline for Quality Gate validation
        timeline_path = self.temp_dir / "caption_timeline.json"
        with open(timeline_path, "w", encoding="utf-8") as f:
            json.dump({
                "brief_filename": brief_filename,
                "total_duration": duration,
                "num_phrases": len(caption_timeline),
                "timeline": caption_timeline
            }, f, indent=2)

        return caption_clips
