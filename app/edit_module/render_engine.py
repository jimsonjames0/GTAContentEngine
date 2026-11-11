import json
from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
from video_assembler import VideoAssembler
from voice_generator import VoiceGenerator
from caption_generator import CaptionGenerator
from cut_sheet import CutSheetGenerator


class RenderEngine:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.final_dir = self.root_dir / "media" / "final"
        self.final_dir.mkdir(parents=True, exist_ok=True)
        self.briefs_dir = self.root_dir / "data" / "content_briefs"
        self.video_assembler = VideoAssembler()
        self.voice_generator = VoiceGenerator()
        self.caption_generator = CaptionGenerator()
        self.cut_generator = CutSheetGenerator()

    def render_master(self, brief_filename: str = "brief_001.json", output_filename: str = "short_001_master.mp4") -> Path:
        output_stem = Path(output_filename).stem
        output_path = self.final_dir / output_filename

        # 1. First build base raw video assembly with isolated temp filename
        raw_assembly_path = self.video_assembler.assemble(
            brief_filename=brief_filename,
            output_filename=f"temp_base_{output_stem}.mp4"
        )

        # 2. Get voiceover path and duration
        voice_path, duration = self.voice_generator.generate(brief_filename=brief_filename)

        # 3. Load brief for script
        brief_path = self.briefs_dir / brief_filename
        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)

        script = brief["script"]

        # 4. Generate dynamic caption clips
        caption_clips = self.caption_generator.generate_captions(script, duration, brief_filename=brief_filename)

        # 5. Load base video and audio
        base_video = VideoFileClip(str(raw_assembly_path))
        voiceover_audio = AudioFileClip(str(voice_path))

        # 6. Composite video with captions over base video
        if caption_clips:
            final_clip = CompositeVideoClip([base_video, *caption_clips])
        else:
            final_clip = base_video

        # Explicitly set audio and duration on the final composite clip
        if hasattr(final_clip, "set_audio"):
            final_clip = final_clip.set_audio(voiceover_audio)
            final_clip = final_clip.set_duration(voiceover_audio.duration)
        else:
            final_clip = final_clip.with_audio(voiceover_audio)
            final_clip = final_clip.with_duration(voiceover_audio.duration)

        # 7. Render final master deliverable with isolated temp audio file
        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            audio=True,
            temp_audiofile=f"temp-audio-{output_stem}.m4a",
            remove_temp=True,
            fps=30,
            preset="ultrafast",
            logger=None,
        )

        # Clean up
        base_video.close()
        voiceover_audio.close()
        final_clip.close()
        for c in caption_clips:
            c.close()

        # Clean up intermediate base video
        if raw_assembly_path.exists():
            try:
                raw_assembly_path.unlink()
            except Exception:
                pass

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Master render failed: {output_path}")

        return output_path


