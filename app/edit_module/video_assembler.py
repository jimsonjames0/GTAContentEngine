import json
from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from asset_manager import AssetManager
from voice_generator import VoiceGenerator
from cut_sheet import CutSheetGenerator


class VideoAssembler:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.final_dir = self.root_dir / "media" / "final"
        self.final_dir.mkdir(parents=True, exist_ok=True)
        self.asset_manager = AssetManager()
        self.voice_generator = VoiceGenerator()
        self.cut_generator = CutSheetGenerator()

    def assemble(self, brief_filename: str = "brief_001.json", output_filename: str = "short_001_raw_assembly.mp4") -> Path:
        # 1. Ensure all raw assets exist
        self.asset_manager.ensure_assets_exist_from_brief(brief_filename)

        # 2. Generate voiceover and get duration
        voice_path, audio_duration = self.voice_generator.generate(brief_filename=brief_filename)

        # 3. Generate cut sheet timed to voice duration
        cut_sheet = self.cut_generator.generate(brief_filename=brief_filename, target_duration=audio_duration)
        timeline = cut_sheet["timeline"]

        clips = []
        for shot in timeline:
            tag = shot["footage_tag"]
            target_duration = shot["duration_sec"]
            asset_path = self.asset_manager.ensure_asset_exists(tag)

            clip = VideoFileClip(str(asset_path))
            
            # Resize / center crop to 1080x1920 vertical 9:16 format
            clip = clip.resized((1080, 1920))

            # Trim clip to target duration (ensuring placeholder is long enough)
            if clip.duration < target_duration:
                clip = clip.subclipped(0, clip.duration)
            else:
                clip = clip.subclipped(0, target_duration)

            clips.append(clip)

        # 4. Concatenate all shots sequentially
        final_video = concatenate_videoclips(clips, method="compose")

        # 5. Attach voiceover audio
        audio_clip = AudioFileClip(str(voice_path))
        
        if abs(final_video.duration - audio_clip.duration) > 0.1:
            final_video = final_video.with_duration(audio_clip.duration)

        final_video = final_video.with_audio(audio_clip)

        # 6. Render final assembly with explicit audio_fps for universal compatibility
        output_path = self.final_dir / output_filename
        final_video.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            audio_fps=44100,
            fps=30,
            preset="ultrafast",
            logger=None,
        )

        for c in clips:
            c.close()
        audio_clip.close()
        final_video.close()

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Video assembly rendering failed: {output_path}")

        return output_path


