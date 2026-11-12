import json
from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
from video_assembler import VideoAssembler
from voice_generator import VoiceGenerator
from caption_generator import CaptionGenerator
from cut_sheet import CutSheetGenerator
try:
    from audio_mixer import AudioMixer
except ImportError:
    from edit_module.audio_mixer import AudioMixer


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
        self.audio_mixer = AudioMixer()

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

        # 5. Load base video
        base_video = VideoFileClip(str(raw_assembly_path))

        # 6. Generate background music and apply dynamic ducking
        music_style = brief.get("format", "breakdown")
        music_style_file = self.root_dir / "formats" / f"{music_style}.json"
        if music_style_file.exists():
            with open(music_style_file, "r", encoding="utf-8") as f:
                music_style_data = json.load(f)
            music_style = music_style_data.get("editing_style", {}).get("music", "subtle_background")

        mixed_audio_path, mixed_audio_duration = self.audio_mixer.mix_ducked_audio(
            voice_path,
            music_style=music_style,
            music_duration=max(duration, 60.0)
        )
        mixed_audio = AudioFileClip(str(mixed_audio_path))
        audio_duration = min(float(mixed_audio.duration), duration)

        # 7. Composite video with captions over base video
        if caption_clips:
            final_clip = CompositeVideoClip([base_video, *caption_clips])
        else:
            final_clip = base_video

        # 8. Set the mastered audio (voiceover ducked over background music)
        if hasattr(final_clip, "set_audio"):
            final_clip = final_clip.set_audio(mixed_audio)
            final_clip = final_clip.set_duration(audio_duration)
        else:
            final_clip = final_clip.with_audio(mixed_audio)
            final_clip = final_clip.with_duration(audio_duration)

        # 9. Render final master deliverable with isolated temp audio file
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
        mixed_audio.close()
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


