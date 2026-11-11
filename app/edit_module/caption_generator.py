import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip


class CaptionGenerator:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.briefs_dir = self.root_dir / "data" / "content_briefs"

    def _create_text_image(self, text: str, img_size=(1080, 200)) -> str:
        """Create a transparent image with stroked text using PIL and save as temporary png."""
        img = Image.new("RGBA", img_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        font = None
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ]
        for fpath in font_paths:
            if Path(fpath).exists():
                try:
                    font = ImageFont.truetype(fpath, size=52)
                    break
                except Exception:
                    pass

        if font is None:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        x = (img_size[0] - text_w) // 2
        y = (img_size[1] - text_h) // 2

        # Draw black outline/stroke
        stroke_width = 3
        for adj_x in range(-stroke_width, stroke_width + 1):
            for adj_y in range(-stroke_width, stroke_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=(0, 0, 0, 255))

        # Draw main yellow text
        draw.text((x, y), text, font=font, fill=(255, 255, 0, 255))

        temp_dir = self.root_dir / "media" / "temp_captions"
        temp_dir.mkdir(parents=True, exist_ok=True)
        out_path = temp_dir / f"caption_{abs(hash(text))}.png"
        img.save(out_path)
        return str(out_path)

    def generate_captions(self, script: str, duration: float, brief_filename: str = "brief_001.json") -> list:
        if not script:
            return []

        words = script.split()
        if not words:
            return []

        chunk_size = 3
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        
        if not chunks:
            return []

        time_per_chunk = duration / len(chunks)
        caption_clips = []

        for i, chunk in enumerate(chunks):
            start_t = i * time_per_chunk
            end_t = min(duration, (i + 1) * time_per_chunk)
            chunk_duration = max(0.5, end_t - start_t)

            img_path = self._create_text_image(chunk)
            
            clip = ImageClip(img_path).with_duration(chunk_duration).with_start(start_t)
            clip = clip.with_position(("center", 1250))
            caption_clips.append(clip)

        return caption_clips
