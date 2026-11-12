import json
from pathlib import Path

try:
    from asset_manager import AssetManager
except ImportError:
    from edit_module.asset_manager import AssetManager


class CutSheetGenerator:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.briefs_dir = self.root_dir / "data" / "content_briefs"
        self.asset_manager = AssetManager()

    def generate(self, brief_filename: str = "brief_001.json", target_duration: float = None) -> dict:
        brief_path = self.briefs_dir / brief_filename
        if not brief_path.exists():
            raise FileNotFoundError(f"Content brief not found at {brief_path}")

        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)

        total_length = round(target_duration, 1) if target_duration is not None else float(brief.get("length", 30))
        footage_tags = brief.get("footage", [])
        num_shots = len(footage_tags)

        # Load format structure and editing pacing
        format_name = brief.get("format", "breakdown")
        fmt_path = self.root_dir / "formats" / f"{format_name}.json"
        structure = []
        editing_style = {}
        if fmt_path.exists():
            with open(fmt_path, "r", encoding="utf-8") as f:
                fmt_data = json.load(f)
            structure = fmt_data.get("structure", [])
            editing_style = fmt_data.get("editing_style", {})

        # Compute narrative pacing weights from catalog
        weights = []
        for i, tag in enumerate(footage_tags):
            meta = self.asset_manager.get_asset_metadata(tag)
            w = meta.get("pacing_weight", 0.25)
            if i == 0:
                w = min(w, 0.20)
            elif i == num_shots - 1:
                w = min(w, 0.22)
            weights.append(w)

        total_w = sum(weights) or 1.0
        norm_weights = [w / total_w for w in weights]

        shots = []
        current_time = 0.0

        for i, tag in enumerate(footage_tags):
            meta = self.asset_manager.get_asset_metadata(tag)
            section_name = structure[i] if i < len(structure) else f"shot_{i+1}"

            if i == num_shots - 1:
                duration = round(total_length - current_time, 1)
            else:
                duration = round(total_length * norm_weights[i], 1)
                duration = max(duration, 2.0)

            end_time = round(current_time + duration, 1)
            shots.append({
                "shot_index": i + 1,
                "section": section_name,
                "footage_tag": tag,
                "category": meta.get("category", "general"),
                "file_target": f"media/raw/{tag}.mp4",
                "start_time_sec": current_time,
                "end_time_sec": end_time,
                "duration_sec": duration,
                "aspect_ratio": "9:16 (Center Crop 1080x1920)",
                "camera_motion": meta.get("recommended_motion", "steady"),
                "zoom_intensity": meta.get("zoom_intensity", 1.0),
                "pacing": editing_style.get("pace", brief.get("voice", "energetic"))
            })
            current_time = end_time

        cut_sheet = {
            "title": brief.get("title", ""),
            "format": brief.get("format", ""),
            "total_duration_sec": total_length,
            "hook": brief.get("hook", ""),
            "full_script": brief.get("script", ""),
            "timeline": shots,
        }

        return cut_sheet