from pathlib import Path
from moviepy import VideoFileClip
from PIL import Image


class CoverExtractor:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.staged_dir = self.root_dir / "media" / "staged"
        self.staged_dir.mkdir(parents=True, exist_ok=True)

    def extract_cover(
        self,
        video_path: Path,
        output_path: Path = None,
        timestamp_sec: float = 2.0
    ) -> Path:
        """Extract a high-contrast still frame from the rendered master video at timestamp_sec (default 2.0s)."""
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        if output_path is None:
            video_id = video_path.stem
            output_path = self.staged_dir / f"{video_id}_cover.jpg"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        clip = VideoFileClip(str(video_path))
        actual_time = min(timestamp_sec, max(0.5, clip.duration - 0.5))

        clip.save_frame(str(output_path), t=actual_time)
        clip.close()

        with Image.open(output_path) as img:
            if img.size != (1080, 1920):
                img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                img.save(output_path, "JPEG", quality=95)

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Cover extraction failed: {output_path}")

        return output_path
