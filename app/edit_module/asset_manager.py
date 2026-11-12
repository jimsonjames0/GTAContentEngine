import json
from pathlib import Path
from moviepy import ColorClip


class AssetManager:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.raw_dir = self.root_dir / "media" / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.briefs_dir = self.root_dir / "data" / "content_briefs"
        self.catalog_path = self.root_dir / "data" / "catalog" / "asset_catalog.json"
        self._catalog = self._load_catalog()

    def _load_catalog(self) -> dict:
        if self.catalog_path.exists():
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"assets": {}, "categories": []}

    def get_asset_metadata(self, tag: str) -> dict:
        """Return catalog entry for a footage tag with fallback defaults."""
        assets = self._catalog.get("assets", {})
        if tag in assets:
            return assets[tag]
        return {
            "tag": tag,
            "category": "general",
            "description": f"Generic footage asset for {tag}",
            "file_path": f"media/raw/{tag}.mp4",
            "theme_color_rgb": [30, 40, 60],
            "recommended_motion": "steady",
            "zoom_intensity": 1.0,
            "pacing_weight": 0.25,
            "min_duration_sec": 3.0,
        }

    def list_by_category(self, category: str) -> list[dict]:
        """Return list of assets matching a specific category."""
        assets = self._catalog.get("assets", {})
        return [meta for meta in assets.values() if meta.get("category") == category]

    def ensure_asset_exists(self, tag: str) -> Path:
        asset_path = self.raw_dir / f"{tag}.mp4"
        if asset_path.exists():
            return asset_path

        meta = self.get_asset_metadata(tag)
        color = tuple(meta.get("theme_color_rgb", [30, 40, 60]))

        # Generate a lightweight 9:16 color-coded fallback placeholder clip (1080x1920, 30fps, 15.0s)
        clip = ColorClip(size=(1080, 1920), color=color, duration=15.0)
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

