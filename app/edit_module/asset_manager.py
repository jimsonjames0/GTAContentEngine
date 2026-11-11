import json
from pathlib import Path
from moviepy import ColorClip


class AssetManager:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.raw_dir = self.root_dir / "media" / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.briefs_dir = self.root_dir / "data" / "content_briefs"

    def ensure_asset_exists(self, tag: str) -> Path:
        asset_path = self.raw_dir / f"{tag}.mp4"
        if asset_path.exists():
            return asset_path

        # Generate a lightweight 9:16 fallback placeholder clip (1080x1920, 30fps, 15.0s)
        clip = ColorClip(size=(1080, 1920), color=(30, 40, 60), duration=15.0)
        clip.fps = 30
        clip.write_videofile(
            str(asset_path),
            codec="libx264",
            audio=False,
            fps=30,
            preset="ultrafast",
            logger=None,
        )
        clip.close()
        return asset_path

    def ensure_assets_exist_from_brief(self, brief_filename: str = "brief_001.json") -> list[Path]:
        brief_path = self.briefs_dir / brief_filename
        if not brief_path.exists():
            raise FileNotFoundError(f"Content brief not found at {brief_path}")

        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)

        footage_tags = brief.get("footage", ["gameplay_overview"])
        paths = []
        for tag in footage_tags:
            paths.append(self.ensure_asset_exists(tag))
        return paths

