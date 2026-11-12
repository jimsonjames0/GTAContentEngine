import json
from pathlib import Path
import numpy as np
from moviepy import AudioFileClip
import wave


class AudioMixer:
    """Background music synthesis and dynamic audio ducking for GTA VI content.

    Dynamic sidechain-style ducking: background music ducks (-18 dB) during
    active voiceover narration and swells to -9 dB during pauses, ensuring
    clear audio with cinematic background support.
    """

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.music_dir = self.root_dir / "media" / "music"
        self.music_dir.mkdir(parents=True, exist_ok=True)

    def _synthesize_bed(self, duration_sec: float, style: str = "subtle_background"):
        """Synthesize a background music bed for each style using sine waves."""
        sample_rate = 44100
        num_samples = int(sample_rate * duration_sec)
        t = np.linspace(0, duration_sec, num_samples, endpoint=False)

        if style == "subtle_background":
            bass = 0.5 * np.sin(2 * np.pi * 55 * t) + 0.3 * np.sin(2 * np.pi * 110 * t) + 0.15 * np.sin(2 * np.pi * 165 * t)
            pad_low = 0.5 * np.sin(2 * np.pi * 220 * t)
            pad_mid = 0.3 * np.sin(2 * np.pi * 330 * t)
            pad_high = 0.15 * np.sin(2 * np.pi * 440 * t)
            bed = bass + pad_low + pad_mid + pad_high
        elif style == "energetic":
            bass = 0.6 * np.sin(2 * np.pi * 60 * t)
            pulse = 0.3 * np.sin(2 * np.pi * 120 * t + np.cumsum(0.5 * np.random.randn(num_samples)))
            bed = bass + pulse
        elif style == "mysterious_or_minimal":
            bass = 0.4 * np.sin(2 * np.pi * 40 * t)
            layer = 0.15 * np.sin(2 * np.pi * 65.41 * t)
            bed = bass + layer
        elif style == "funny_or_trending":
            bass = 0.5 * np.sin(2 * np.pi * 70 * t)
            groove = 0.25 * np.sin(2 * np.pi * 140 * t + np.sin(2 * np.pi * 4 * t) * 1.5)
            bed = bass + groove
        else:  # light_or_none
            bed = np.zeros(num_samples)

        # Normalize to prevent clipping
        max_val = np.max(np.abs(bed))
        if max_val > 0:
            bed = bed / max_val * 0.7

        pcm = (bed * 32767).astype(np.int16)
        return pcm, sample_rate

    def ensure_music(self, music_style: str, duration_sec: float = 60.0) -> Path:
        """Generate reusable background music file for a format style."""
        target_path = self.music_dir / f"{music_style}.wav"
        pcm, sample_rate = self._synthesize_bed(duration_sec, style=music_style)
        wf = wave.open(str(target_path), "wb")
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
        wf.close()
        return target_path

    def _compute_voice_envelope(self, voice_path: Path, frames_per_window: int = 2205, attack: float = 0.03) -> np.ndarray:
        """Compute voice amplitude envelope for ducking control."""
        audio = AudioFileClip(str(voice_path))
        fps = audio.fps
        samples = audio.to_soundarray()
        if samples.ndim == 2:
            samples = np.mean(samples, axis=1)
        else:
            samples = samples.flatten()
        samples = samples[:len(samples) // frames_per_window * frames_per_window]
        num_windows = len(samples) // frames_per_window
        rms = np.zeros(num_windows)
        for i in range(num_windows):
            window = samples[i * frames_per_window:(i + 1) * frames_per_window]
            rms[i] = np.sqrt(np.mean(window ** 2) + 1e-8)
        max_rms = np.max(rms) if np.max(rms) > 0 else 1.0
        gain = rms / max_rms
        smoothed = np.zeros(num_windows)
        for i in range(num_windows):
            if i == 0:
                smoothed[i] = gain[i]
            elif gain[i] > smoothed[i - 1]:
                alpha = 1 - np.exp(-1 / (attack * 60))
                smoothed[i] = smoothed[i - 1] + (gain[i] - smoothed[i - 1]) * alpha
            else:
                alpha = 1 - np.exp(-1 / 0.3)
                smoothed[i] = smoothed[i - 1] * np.exp(-1 / 0.3)
        audio.close()
        return smoothed

    def _apply_ducking(self, voice_path: Path, music_path: Path, duck_db: float = 18.0, song_db: float = 9.0) -> Path:
        """Apply dynamic ducking to background music based on voice envelope."""
        voice = AudioFileClip(str(voice_path))
        fps = 44100
        voice_samples = voice.to_soundarray(fps=fps)
        if voice_samples.ndim == 2:
            voice_samples = np.mean(voice_samples, axis=1)
        voice_samples = voice_samples.astype(np.float64)

        with wave.open(str(music_path), "rb") as wf:
            raw = wf.readframes(wf.getnframes())
            music_samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0

        if len(music_samples) > len(voice_samples):
            music_samples = music_samples[:len(voice_samples)]
        elif len(music_samples) < len(voice_samples):
            repeat_times = int(np.ceil(len(voice_samples) / len(music_samples)))
            music_samples = np.tile(music_samples, repeat_times)[:len(voice_samples)]

        window_size = 2205  # ~50ms windows
        pad_len = (window_size - (len(voice_samples) % window_size)) % window_size
        voice_padded = np.pad(voice_samples, (0, pad_len)) if pad_len > 0 else voice_samples
        num_windows = len(voice_padded) // window_size
        windows = voice_padded.reshape(-1, window_size)
        rms = np.sqrt(np.mean(windows ** 2, axis=1) + 1e-8)
        max_rms = np.max(rms) if np.max(rms) > 0 else 1.0
        voice_gain = rms / max_rms

        smoothed_gain = np.zeros(num_windows)
        alpha_attack = 1.0 - np.exp(-1.0 / (0.05 * 20.0))
        alpha_release = 1.0 - np.exp(-1.0 / (0.4 * 20.0))
        for i in range(num_windows):
            if i == 0:
                smoothed_gain[i] = voice_gain[i]
            elif voice_gain[i] > smoothed_gain[i - 1]:
                smoothed_gain[i] = smoothed_gain[i - 1] + (voice_gain[i] - smoothed_gain[i - 1]) * alpha_attack
            else:
                smoothed_gain[i] = smoothed_gain[i - 1] - smoothed_gain[i - 1] * alpha_release

        voice_gain_curve = np.repeat(smoothed_gain, window_size)[:len(voice_samples)]

        duck_linear = 10.0 ** (-duck_db / 20.0)
        song_linear = 10.0 ** (-song_db / 20.0)
        music_gain_curve = song_linear + (duck_linear - song_linear) * voice_gain_curve

        mixed_audio = voice_samples + music_samples * music_gain_curve

        fade_len = int(0.5 * fps)
        if len(mixed_audio) > fade_len:
            fade = np.linspace(1.0, 0.0, fade_len)
            mixed_audio[-fade_len:] = voice_samples[-fade_len:] + (music_samples[-fade_len:] * music_gain_curve[-fade_len:]) * fade

        mixed_audio = np.clip(mixed_audio, -1.0, 1.0)
        pcm = (mixed_audio * 32767).astype(np.int16)

        voice.close()

        output_path = self.root_dir / "media" / "voice" / f"{voice_path.stem}_mixed.wav"
        wf = wave.open(str(output_path), "wb")
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fps)
        wf.writeframes(pcm.tobytes())
        wf.close()

        return output_path

    def mix_ducked_audio(self, voice_path: Path, music_style: str, music_duration: float = 60.0) -> tuple[Path, float]:
        """Full pipeline: generate music, apply ducking, return mixed audio."""
        music_path = self.ensure_music(music_style, duration_sec=music_duration)
        output_path = self._apply_ducking(voice_path, music_path)

        mixed_audio = AudioFileClip(str(output_path))
        duration = float(mixed_audio.duration)
        mixed_audio.close()

        return output_path, duration
