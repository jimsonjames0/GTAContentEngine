# GTA VI Content Engine — Planning Agent Context

**Last Updated:** Month 2, Week 6 Complete (Handoff to Week 7)  
**Project Ground Truth:** `PROJECT_OVERVIEW.md`  
**Active Python Environment:** Python 3.11+ in `.venv/bin/activate`

---

## 1. System Architecture & Data Flow

```
TREND SOURCES (Reddit r/GTA6)
       ↓
TREND MODULE (reddit_collector.py + source_validator.py + history_manager.py)
       ↓  data/trends/latest_trends.json + data/sources/{source_id}.json
IDEA MODULE (idea_generator.py + format_selector.py)
       ↓  data/ideas/latest_ideas.json (reads formats/*.json personas)
SCRIPT MODULE (script_writer.py — ScriptWriter 2.0)
       ↓  data/content_briefs/brief_{id}.json (verified_claims vs speculation, 0% sentence overlap)
EDIT MODULE:
  • AudioMixer (audio_mixer.py) — Procedural synth beds + dynamic sidechain ducking (-18 dB active, -9 dB silence)
  • VoiceGenerator (voice_generator.py) — EdgeTTS neural voices per persona (en-US-ChristopherNeural, GuyNeural, EricNeural, RogerNeural)
  • CaptionGenerator (caption_generator.py) — Highlighted captions overlay
  • CutSheetGenerator (cut_sheet.py) — Dynamic shot timeline allocation
  • VideoAssembler (video_assembler.py) — 9:16 (1080x1920) clip sequence assembly
  • RenderEngine (render_engine.py) — Composited master video with ducked audio track
       ↓  media/final/{short_id}_master.mp4
PUBLISH & ANALYTICS MODULES:
  • MetadataGenerator + CoverExtractor + QueueManager → media/staged/{short_id}/ [master.mp4, cover.jpg, metadata.json, brief.json]
  • PerformanceTracker → data/analytics/ (feedback loop)
```

---

## 2. Completed Milestones

| Milestone | Status | Key Deliverables & Validation |
|---|---|---|
| **Month 1: Foundation & Validation** | ✅ COMPLETED | Daily automated pipeline (`main.py`), batch runner (`batch_runner.py`), deduplication history, YouTube/TikTok/Reels packaging, analytics feedback loop. |
| **Month 2, Week 5: ScriptWriter 2.0 & Editorial Identity** | ✅ Complete | • `formats/editorial_style_guide.json` (banned phrases, narrative rules)<br>• Format personas (`breakdown`, `discovery`, `theory`, `meme`, `reaction`)<br>• `SourceValidator` (`data/sources/` provenance tracking)<br>• Anti-slop quality gate (`validate_editorial_quality`): 55–95 words, no double punctuation, no raw title repetition, verified claims separated from community speculation, 0% sentence overlap between scripts.<br>• Verified by `test_week5_foundation.py` and `test_week5_scriptwriter2.py`. |
| **Month 2, Week 6: Neural Voice & Audio Ducking** | ✅ Complete | • `edge-tts==7.3.1` integration with resilient `gTTS` fallback.<br>• Per-format neural voices (`en-US-ChristopherNeural`, `en-US-GuyNeural`, `en-US-EricNeural`, `en-US-RogerNeural`) with tailored rate and pitch.<br>• `AudioMixer` (`app/edit_module/audio_mixer.py`): Procedural synthesis for all 5 format styles (`subtle_background`, `energetic`, `mysterious_or_minimal`, `funny_or_trending`, `light_or_none`), sample-accurate dynamic sidechain ducking (-18 dB during active speech, -9 dB during pauses), 0.5s smooth tail fade.<br>• `RenderEngine` wires neural voice + ducked audio master into final composite 1080x1920 MP4.<br>• Verified by `test_week6_audio.py`. |
| **Month 2, Week 7: Visual Asset Catalog & Shot Pacing Variation** | ✅ Complete | • `data/catalog/asset_catalog.json` (16 cataloged B-roll assets across `milestone`, `website`, `gameplay`, `general`).<br>• `AssetManager` (`app/edit_module/asset_manager.py`): catalog lookup (`get_asset_metadata`, `list_by_category`) and color-coded fallback rendering matching catalog themes.<br>• `CutSheetGenerator` (`app/edit_module/cut_sheet.py`): narrative pacing weights (hook 18%, body 62%, payoff 20%), camera motion and zoom intensity directives per shot, and dynamic sync to voiceover duration (`target_duration`).<br>• `VideoAssembler` (`app/edit_module/video_assembler.py`): timeline synced to neural voice duration.<br>• Verified by `test_week7_catalog.py` and `test_cut_sheet.py`. |
| **Month 2, Week 8: Whisper Word-Level Captions & Quality Gate** | ✅ Complete | • `VoiceGenerator` (`app/edit_module/voice_generator.py`): acoustic prosody-weighted word-boundary alignment saved to `media/voice/{stem}_timestamps.json`.<br>• `CaptionGenerator` (`app/edit_module/caption_generator.py`): phrase-level boundary chunking, high-signal GTA VI keyword highlighting in gold/yellow `(255, 225, 0)` over white text with 4px black stroke, and caption timeline persistence.<br>• `QualityGate` (`app/publish_module/quality_gate.py`): 100-point pre-publish audit scoring editorial compliance, 1080x1920 video technical specs, audio track presence/sync, and caption timing bounds. Audit reports saved to `data/quality_reports/`.<br>• Verified by `test_week8_captions_and_qgate.py` (100/100 score). |
| **Month 2: Content Quality and Editorial Identity** | ✅ COMPLETED | Full editorial identity, neural TTS personas, dynamic audio ducking, visual asset catalog, word-level highlighted captions, and automated quality gate. |
| **Month 3, Week 9: End-to-End Orchestration & Quality Gate Integration** | ✅ Complete | • `QueueManager`: records `quality_score` (`100/100`) and enforces publishing hold (`held_by_quality_gate` vs `ready_to_publish`).<br>• `main.py` & `app/batch_runner.py`: fully autonomous quality gate auditing before staging packages.<br>• `FormatSelector`: closed analytics feedback loop using `format_weights.json` engagement scores to break candidate ties.<br>• `MetadataGenerator`: contextual monetization block (`recommended_affiliate_category`, `pinned_comment_cta`) surfaced in `UPLOAD_CHEATSHEET.md`.<br>• `PerformanceTracker`: revenue reporting (YouTube Shorts RPM + affiliate conversion projections).<br>• Verified by `test_week9_orchestration.py`. |

---

## 3. Current Phase & Next Milestone

- **Current Phase:** **Month 3, Week 10 — Multi-Platform Long/Short Video Adaptation & Horizon Scaling**
- **Objective:** Support multi-duration cuts (e.g. 62–75s deep-dives for TikTok Creator Rewards high-RPM tier alongside 30s YouTube Shorts), multi-account horizon niche evaluation, and automated end-to-end publishing webhooks.
- **Key Modules for Week 10:**
  - `main.py` & `app/batch_runner.py` (multi-duration adaptation flags: `--duration`, `--deep-dive`)
  - `app/publish_module/metadata_generator.py` (platform-specific title/description length limits)
  - `data/analytics/` (channel expansion evaluation metrics)

---

## 4. Ground Truth Rules & Data Contracts

1. **Always use `.venv/bin/python`** or activate virtual environment: `source .venv/bin/activate`.
2. **Never install packages system-wide.**
3. **Data directories:**
   - Trends: `data/trends/`
   - Source provenance: `data/sources/`
   - Ideas: `data/ideas/`
   - Content Briefs: `data/content_briefs/`
   - Staged production packages: `media/staged/`
   - Audio beds: `media/music/`
   - Voiceovers: `media/voice/`
4. **All test scripts must exit with code 0 before concluding any task.**

