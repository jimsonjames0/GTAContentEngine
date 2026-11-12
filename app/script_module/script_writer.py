import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from content_brief import ContentBrief

load_dotenv()


class ScriptWriter:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.formats_dir = self.root_dir / "formats"
        self.ideas_path = self.root_dir / "data" / "ideas" / "latest_ideas.json"
        self.sources_dir = self.root_dir / "data" / "sources"
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
        self.style_guide = self._load_style_guide()
        self.banned_phrases = self.style_guide.get("banned_phrases", [])
        self.narrative_rules = self.style_guide.get("narrative_rules", {})
        self._source_validator = None

    @property
    def source_validator(self):
        if self._source_validator is None:
            from trend_module.source_validator import SourceValidator
            self._source_validator = SourceValidator()
        return self._source_validator

    def _load_style_guide(self) -> dict:
        style_guide_path = self.formats_dir / "editorial_style_guide.json"
        if not style_guide_path.exists():
            return {"banned_phrases": [], "narrative_rules": {}, "channel_identity": {}, "rejected_content_types": []}
        with open(style_guide_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_format_spec(self, format_name: str) -> dict:
        format_file = self.formats_dir / f"{format_name}.json"
        if not format_file.exists():
            raise FileNotFoundError(f"Format file not found: {format_file}")
        with open(format_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _register_source(self, title: str, url: str = "") -> str:
        trend_obj = type("TrendObj", (), {"title": title, "url": url, "description": ""})()
        record = self.source_validator.from_trend(trend_obj)
        self.source_validator.save_record(record)
        return record.source_id

    def _has_double_punctuation(self, text: str) -> bool:
        return bool(re.search(r"[.!?]{2,}", text))

    def _title_in_hook(self, hook: str, title: str) -> bool:
        if len(title.split()) <= 4:
            return False
        title_words = set(title.lower().split())
        hook_words = set(hook.lower().split())
        overlap = title_words.intersection(hook_words)
        return len(overlap) >= len(title_words) * 0.7

    def validate_editorial_quality(self, brief: ContentBrief) -> None:
        full_text = f"{brief.hook} {brief.script} {brief.payoff} {brief.central_angle}".lower()
        for phrase in self.banned_phrases:
            if phrase.lower() in full_text:
                raise ValueError(f"Banned phrase detected: '{phrase}' found in generated content.")
        for field_name, field_value in [("hook", brief.hook), ("script", brief.script), ("payoff", brief.payoff), ("central_angle", brief.central_angle)]:
            if self._has_double_punctuation(field_value):
                raise ValueError(f"Double punctuation artifact detected in {field_name}: '{field_value}'")
        if self._title_in_hook(brief.hook, brief.title):
            raise ValueError(f"Hook repeats the raw source title verbatim: '{brief.hook}' vs '{brief.title}'")
        if not brief.central_angle or not brief.central_angle.strip():
            raise ValueError("central_angle must be non-empty.")
        if not brief.payoff or not brief.payoff.strip():
            raise ValueError("payoff must be non-empty.")
        if not brief.verified_claims or len(brief.verified_claims) == 0:
            raise ValueError("verified_claims must contain at least 1 item.")
        if not brief.source_references or len(brief.source_references) == 0:
            raise ValueError("source_references must contain at least 1 source_id.")
        word_count = len(brief.script.split())
        if word_count < 55 or word_count > 95:
            raise ValueError(f"Script word count {word_count} is outside the 55-95 word range for 25-35s video.")

    def _determine_topic_type(self, title: str, concept: str) -> str:
        combined = f"{title} {concept}".lower()
        if any(w in combined for w in ["artwork", "leak", "theory", "rumor", "speculation", "concept art", "image"]):
            return "theory"
        elif any(w in combined for w in ["preload", "pre-load", "download", "size", "gb", "release", "date", "launch", "milestone", "pre-order", "preorder"]):
            return "milestone"
        elif any(w in combined for w in ["background", "site", "page", "rockstar", "logo", "url", "website", "web presence"]):
            return "website"
        elif any(w in combined for w in ["frame", "trailer", "detail", "car", "map", "physics", "water", "gameplay", "environmental", "npc"]):
            return "gameplay"
        return "general"

    def _get_contextual_footage(self, topic_type: str, structure: list) -> list[str]:
        footage_map = {
            "milestone": ["store_preload_screen", "download_queue_dashboard", "file_size_graphic", "community_reaction_thread", "countdown_timer_overlay", "vice_city_logo_outro"],
            "website": ["rockstar_homepage_scroll", "new_background_zoom", "inspect_element_code", "previous_site_comparison", "community_discussion", "gta6_title_card"],
            "gameplay": ["trailer_cinematic_intro", "trailer_frame_zoom", "slow_mo_physics_check", "side_by_side_comparison", "gameplay_overlay", "vice_city_skyline"],
            "general": ["news_headline_banner", "social_feed_reactions", "gameplay_cinematic_broll", "community_discussion", "speculation_graphic", "outro_subscribe_card"],
        }
        pool = footage_map.get(topic_type, footage_map["general"])
        return pool[: len(structure)]

    def _deterministic_synthesize(self, title: str, hook_input: str, concept: str, format_name: str, topic_type: str, structure: list, source_id: str) -> dict:
        clean_title = title.strip().rstrip(". ")
        fmt_spec = self._load_format_spec(format_name)
        persona = fmt_spec.get("persona", {})

        milestone_hooks = {
            "breakdown": "Preload packages have hit backend stores ahead of the GTA VI launch window.",
            "discovery": "Store-side preload infrastructure just moved into final staging.",
            "theory": "Preload data appearing on backend stores signals an imminent unlock.",
            "meme": "Preload packages hit stores before Rockstar says a word.",
            "reaction": "Preload packages have appeared ahead of launch.",
        }
        website_hooks = {
            "breakdown": "Rockstar quietly adjusted their web presence—and players spotted it immediately.",
            "discovery": "Subtle website changes hint at new marketing materials on the way.",
            "theory": "A background asset swap on Rockstar's site precedes a reveal.",
            "meme": "Rockstar updated their site and nobody announced it.",
            "reaction": "Rockstar quietly changed their web presence.",
        }
        gameplay_hooks = {
            "breakdown": "A single trailer frame reveals more about Vice City than most teasers show.",
            "discovery": "Frame analysis exposes deliberate world-building choices in Vice City.",
            "theory": "Trailer composition signals Rockstar's engineering intent.",
            "meme": "One frame detail changes how you'll read Vice City.",
            "reaction": "This trailer frame detail deserves closer scrutiny.",
        }
        theory_hooks = {
            "breakdown": "This visual anomaly points to intentional Rockstar placement.",
            "discovery": "A specific environmental clue suggests unseen Vice City locations.",
            "theory": "Community dissected detail signals Rockstar-level world-building.",
            "meme": "This anomaly may connect to broader Grand Theft Auto legacy.",
            "reaction": "Frame composition hints at unannounced mission mechanics.",
        }
        general_hooks = {
            "breakdown": "The GTA VI community is dissecting a detail that changes the conversation.",
            "discovery": "Players are rallying around a specific visual detail in Vice City.",
            "theory": "Community discussion reveals what players value most about GTA VI.",
            "meme": "This GTA VI detail says more than the headline does.",
            "reaction": "Community reaction to this Vice City detail is intense.",
        }

        hook_map = {
            "milestone": milestone_hooks,
            "website": website_hooks,
            "gameplay": gameplay_hooks,
            "theory": theory_hooks,
            "general": general_hooks,
        }
        hooks_for_topic = hook_map.get(topic_type, general_hooks)
        hook = hooks_for_topic.get(format_name, hooks_for_topic.get("breakdown", "This GTA VI detail deserves closer attention."))

        if topic_type == "milestone":
            if format_name == "breakdown":
                central_angle = "Store-side preload infrastructure is one of the final launch milestones—when backend stores begin distributing preload data, Rockstar is signaling the final countdown has begun."
                body = ("Preload files appearing on store platforms mean game data is being staged for day-one distribution. "
                        "This backend movement typically happens weeks before the official release date, giving players time to download before servers go live.")
                payoff = "Preparing your storage and connection now means you'll be ready the moment Rockstar unlocks the servers."
                call_to_action = "Check your store preload status and share your preorder plans below."
                verified_claims = ["Preload packages have appeared on digital storefronts ahead of GTA VI launch", "Store-side preload infrastructure is a standard final launch milestone"]
                speculation = ["Preload timing may indicate a release window within 2-4 weeks", "File size hints may suggest the final game scope on next-gen consoles"]
            elif format_name == "discovery":
                central_angle = "Preload staging on digital storefronts is Rockstar's quiet signal that the launch window is closing in."
                body = ("Store-side preload files appearing ahead of the release date indicate the game data is being prepared for day-one distribution. "
                        "Players can expect the download window to open weeks before servers go live.")
                payoff = "Preload packages appearing on storefronts a few days early tell you exactly when the servers will open."
                call_to_action = "Check your store's preload dashboard and find out when launch day opens."
                verified_claims = ["Preload packages have appeared on digital storefronts ahead of GTA VI launch", "Store-side preload infrastructure is a standard final launch milestone"]
                speculation = ["Preload timing may indicate a release window within 2-4 weeks", "File size hints may suggest the final game scope on next-gen consoles"]
            else:
                central_angle = "Preload infrastructure on backend stores marks the final stretch before GTA VI's launch window opens."
                body = ("Preload packages on digital storefronts mean Rockstar is staging game data for day-one distribution. "
                        "This backend milestone typically arrives weeks ahead of the official release date.")
                payoff = "Preload infrastructure moving weeks ahead of launch is your final cue to start downloading."
                call_to_action = "Check your store's preload status and start downloading the moment it's available."
                verified_claims = ["Preload packages have appeared on digital storefronts ahead of GTA VI launch", "Store-side preload infrastructure is a standard final launch milestone"]
                speculation = ["Preload timing may indicate a release window within 2-4 weeks", "File size hints may suggest the final game scope on next-gen consoles"]
        elif topic_type == "website":
            if format_name == "breakdown":
                central_angle = "Subtle website changes are often the first public signal of new marketing materials. When Rockstar adjusts background assets or page structure, preliminary marketing and new assets usually follow within days."
                body = ("Tracking web updates is how the community spots early indicators. Background changes, logo tweaks, or new page sections "
                        "often precede trailer drops or artwork releases by a short window.")
                payoff = "Subtle website shifts are the earliest way for fans to predict an upcoming Rockstar release."
                call_to_action = "Bookmark Rockstar's site and share any site changes you spot before they go mainstream."
                verified_claims = ["Rockstar's official web presence received observable updates", "Web changes often precede new marketing material releases"]
                speculation = ["Website updates may signal an imminent trailer or artwork reveal", "Background changes could hint at new Vice City locations"]
            else:
                central_angle = "Rockstar's web presence often shifts before new marketing material arrives."
                body = ("Community observers track background changes, logo tweaks, and new page sections as early indicators. "
                        "These updates typically precede trailer drops or artwork reveals by days.")
                payoff = "Web presence changes are the best early warning system for upcoming Rockstar releases."
                call_to_action = "Bookmark Rockstar's site and tell us which page changes you noticed first."
                verified_claims = ["Rockstar's official web presence received observable updates", "Web changes often precede new marketing material releases"]
                speculation = ["Website updates may signal an imminent trailer or artwork reveal", "Background changes could hint at new Vice City locations"]
        elif topic_type == "gameplay":
            if format_name == "breakdown":
                central_angle = "Every environmental detail in GTA VI's trailer frames serves a purpose—from water physics to NPC density, Rockstar engineers open worlds with layered intention that rewards close observation."
                body = ("Trailer frame analysis shows deliberate world-building choices: weather systems, vehicle density, and architectural details that mirror "
                        "Rockstar's approach in GTA V and Red Dead Redemption 2. These aren't random—they're calculations about how players will move through Vice City.")
                payoff = "Noticing these details changes how you'll experience Vice City at launch."
                call_to_action = "Which trailer frame detail stood out to you? Comment below."
                verified_claims = ["Trailer frames show specific environmental and physics details", "Rockstar's previous titles (GTA V, RDR2) established similar world-building patterns"]
                speculation = ["Trailer details may hint at Vice City locations not yet officially named", "Frame composition could suggest mission or gameplay mechanics"]
            else:
                central_angle = "Trailer frames contain deliberate world-building choices that reward close observation."
                body = ("Environmental details in trailer frames—weather, vehicle density, architecture—mirror Rockstar's established world-building patterns "
                        "from GTA V and Red Dead Redemption 2.")
                payoff = "Every Vice City detail you notice is a deliberate design choice from Rockstar."
                call_to_action = "Share the trailer frame detail that caught your eye."
                verified_claims = ["Trailer frames show specific environmental and physics details", "Rockstar's previous titles (GTA V, RDR2) established similar world-building patterns"]
                speculation = ["Trailer details may hint at Vice City locations not yet officially named", "Frame composition could suggest mission or gameplay mechanics"]
        elif topic_type == "theory":
            if format_name == "theory":
                central_angle = "Community theories around visual anomalies often point to intentional Rockstar placement, but they must be labeled as speculation until confirmed."
                body = ("Community discussions around this specific topic reveal patterns in what players value: authenticity, attention to detail, "
                        "and connection to the broader GTA legacy. These theories should be treated as community observation, not confirmed fact.")
                payoff = "Community theories give you a head start on the bigger picture—even when they remain unconfirmed."
                call_to_action = "Share your theory on this detail; what else might it connect to?"
                verified_claims = ["Community discussion has formed around this specific GTA VI topic", "Player engagement indicates genuine interest in the subject matter"]
                speculation = ["The detail may connect to broader Vice City world-building", "Community theories could align with official Rockstar plans"]
            else:
                central_angle = "When the community rallies around a specific visual detail, it usually points to something Rockstar intentionally placed."
                body = ("Community discussion around this specific topic reveals clear patterns in what players value most: "
                        "authenticity, attention to detail, and connection to the broader GTA legacy. Players are paying close attention.")
                payoff = "Community discussion turns a single visual detail into a lens for understanding Rockstar's design philosophy."
                call_to_action = "Join the conversation and tell us what this detail means to you."
                verified_claims = ["Community discussion has formed around this specific GTA VI topic", "Player engagement indicates genuine interest in the subject matter"]
                speculation = ["The detail may connect to broader Vice City world-building", "Community theories could align with official Rockstar plans"]
        else:
            if format_name == "breakdown":
                central_angle = "The GTA VI community is dissecting a detail that changes the conversation around Vice City's design."
                body = ("Community discussions around this topic reveal patterns in what players value most: authenticity, attention to detail, "
                        "and connection to the broader GTA legacy.")
                payoff = "A single detail tells a much bigger story about how Rockstar designs Vice City."
                call_to_action = "What does this detail say about Rockstar's design philosophy?"
                verified_claims = ["Community discussion has formed around this specific GTA VI topic", "Player engagement indicates genuine interest in the subject matter"]
                speculation = ["The detail may connect to broader Vice City world-building", "Community theories could align with official Rockstar plans"]
            elif format_name == "meme":
                central_angle = "One small Vice City detail says more about GTA VI than a dozen headlines."
                body = ("Players spotted this anomaly first. It's the kind of quiet detail Rockstar engineers into open worlds for observant fans to discover.")
                payoff = "The funniest details in GTA VI are often the most deliberate ones."
                call_to_action = "Share your favorite Vice City detail in the comments."
                verified_claims = ["Community discussion has formed around this specific GTA VI topic", "Player engagement indicates genuine interest in the subject matter"]
                speculation = ["The detail may connect to broader Vice City world-building", "Community theories could align with official Rockstar plans"]
            else:
                central_angle = "When the community rallies around a specific visual or mechanical detail, it usually points to something Rockstar intentionally placed."
                body = ("Community discussions around this topic reveal patterns in what players value most: authenticity, attention to detail, "
                        "and connection to the broader GTA legacy.")
                payoff = "One detail can reveal how much care and intention went into Vice City's design."
                call_to_action = "What does this detail tell you about Rockstar's design process?"
                verified_claims = ["Community discussion has formed around this specific GTA VI topic", "Player engagement indicates genuine interest in the subject matter"]
                speculation = ["The detail may connect to broader Vice City world-building", "Community theories could align with official Rockstar plans"]

        visual_cues = self._get_contextual_footage(topic_type, structure)
        full_script = f"{hook} {body} {payoff} {call_to_action}"

        return {
            "hook": hook,
            "central_angle": central_angle,
            "script": full_script,
            "narration": full_script,
            "verified_claims": verified_claims,
            "speculation": speculation,
            "payoff": payoff,
            "call_to_action": call_to_action,
            "visual_cues": visual_cues,
            "footage": visual_cues,
        }

    def _gemini_synthesize(self, title: str, hook_input: str, concept: str, format_name: str, topic_type: str, structure: list, source_id: str) -> dict:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(self.gemini_model)
            style_guide_str = json.dumps(self.style_guide, indent=2)
            format_spec_str = json.dumps(self._load_format_spec(format_name), indent=2)
            prompt = f"""
You are an expert scriptwriter for a GTA VI content channel.
CHANNEL IDENTITY:
{json.dumps(self.style_guide.get('channel_identity', {}), indent=2)}
NARRATIVE RULES:
{json.dumps(self.style_guide.get('narrative_rules', {}), indent=2)}
FORMAT SPEC ({format_name}):
{format_spec_str}
BANNED PHRASES (never use these):
{json.dumps(self.style_guide.get('banned_phrases', []), indent=2)}
TASK:
Write a complete script for a {format_name} format short-form video about:
- Title: {title}
- Concept: {concept}
- Structure: {json.dumps(structure)}
REQUIREMENTS:
1. Hook must open with a sharp observation, contrast, or specific anomaly - NEVER repeat the raw Reddit title verbatim.
2. No double punctuation artifacts (.., !!, ?.).
3. Include verified_claims (facts backed by official sources) and speculation (community theories).
4. Script must be 55-95 spoken words for a 25-35s video.
5. Body must include concrete mechanics, history parallels, or specific visual details.
6. Payoff must conclude with a concrete takeaway on why this matters to players.
7. Label community theories explicitly.
OUTPUT FORMAT (valid JSON only):
{{
  "hook": "string",
  "central_angle": "string",
  "script": "string",
  "narration": "string",
  "verified_claims": ["string"],
  "speculation": ["string"],
  "payoff": "string",
  "call_to_action": "string",
  "visual_cues": ["string"]
}}
"""
            response = model.generate_content(prompt)
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            result = json.loads(text)
            result.setdefault("hook", "")
            result.setdefault("central_angle", "")
            result.setdefault("script", "")
            result.setdefault("narration", result.get("script", ""))
            result.setdefault("verified_claims", [])
            result.setdefault("speculation", [])
            result.setdefault("payoff", "")
            result.setdefault("call_to_action", "")
            result.setdefault("visual_cues", self._get_contextual_footage(topic_type, structure))
            result["footage"] = result.get("visual_cues", self._get_contextual_footage(topic_type, structure))
            result["model_id"] = self.gemini_model
            return result
        except Exception:
            fallback = self._deterministic_synthesize(title, hook_input, concept, format_name, topic_type, structure, source_id)
            fallback["model_id"] = "scriptwriter-v2-deterministic"
            return fallback

    def _load_top_idea(self) -> dict:
        if not self.ideas_path.exists():
            raise FileNotFoundError(f"Ideas file not found at {self.ideas_path}")
        with open(self.ideas_path, "r", encoding="utf-8") as f:
            ideas_data = json.load(f)
        if not ideas_data:
            raise ValueError("No ideas found in latest_ideas.json")
        return ideas_data[0]

    def write_brief(self, idea=None) -> ContentBrief:
        if idea is None:
            idea_data = self._load_top_idea()
        elif isinstance(idea, dict):
            idea_data = idea
        else:
            idea_data = {
                "trend_title": getattr(idea, "trend_title", getattr(idea, "title", "")),
                "trend_url": getattr(idea, "trend_url", getattr(idea, "url", "")),
                "source": getattr(idea, "source", "reddit"),
                "format_name": getattr(idea, "format_name", getattr(idea, "format", "discovery")),
                "hook": getattr(idea, "hook", ""),
                "concept": getattr(idea, "concept", ""),
                "recommended_length": getattr(idea, "recommended_length", "20-40"),
            }

        trend_title = idea_data.get("trend_title", idea_data.get("title", ""))
        format_name = idea_data.get("format_name", idea_data.get("format", "discovery"))
        concept = idea_data.get("concept", "")

        fmt_data = self._load_format_spec(format_name)
        structure = fmt_data.get("structure", ["hook", "explain", "impact"])
        topic_type = self._determine_topic_type(trend_title, concept)
        trend_url = idea_data.get("trend_url", idea_data.get("url", ""))
        source_id = self._register_source(trend_title, trend_url)

        if self.gemini_api_key:
            synthesis = self._gemini_synthesize(trend_title, idea_data.get("hook", ""), concept, format_name, topic_type, structure, source_id)
        else:
            synthesis = self._deterministic_synthesize(trend_title, idea_data.get("hook", ""), concept, format_name, topic_type, structure, source_id)
        model_id = synthesis.get("model_id", "scriptwriter-v2-deterministic")

        brief = ContentBrief.create(
            title=trend_title,
            format=format_name,
            hook=synthesis["hook"],
            script=synthesis["script"],
            length=30,
            footage=synthesis["footage"],
            voice="energetic",
            central_angle=synthesis["central_angle"],
            narration=synthesis["narration"],
            verified_claims=synthesis.get("verified_claims", []),
            speculation=synthesis.get("speculation", []),
            source_references=[source_id],
            visual_cues=synthesis.get("visual_cues", synthesis["footage"]),
            payoff=synthesis["payoff"],
            call_to_action=synthesis["call_to_action"],
            model_id=model_id,
            prompt_version="v2.0-editorial",
            approval_status="pending_review",
        )

        self.validate_editorial_quality(brief)
        return brief

    write = write_brief
