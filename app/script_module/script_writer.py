import json
from pathlib import Path
from content_brief import ContentBrief


class ScriptWriter:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.formats_dir = self.root_dir / "formats"
        self.ideas_path = self.root_dir / "data" / "ideas" / "latest_ideas.json"

    def _determine_topic_type(self, title: str, concept: str) -> str:
        combined = f"{title} {concept}".lower()
        if any(w in combined for w in ["preload", "download", "size", "gb", "release", "date", "launch", "milestone"]):
            return "milestone"
        elif any(w in combined for w in ["background", "site", "page", "rockstar", "logo", "url"]):
            return "website"
        elif any(w in combined for w in ["frame", "trailer", "detail", "car", "map", "physics", "water", "gameplay"]):
            return "gameplay"
        return "general"

    def _get_contextual_footage(self, topic_type: str, structure: list) -> list[str]:
        footage_map = {
            "milestone": [
                "store_preload_screen",
                "download_queue_dashboard",
                "file_size_graphic",
                "community_reaction_thread",
                "countdown_timer_overlay",
                "vice_city_logo_outro",
            ],
            "website": [
                "rockstar_homepage_scroll",
                "new_background_zoom",
                "inspect_element_code",
                "previous_site_comparison",
                "community_discussion",
                "gta6_title_card",
            ],
            "gameplay": [
                "trailer_cinematic_intro",
                "trailer_frame_zoom",
                "slow_mo_physics_check",
                "side_by_side_comparison",
                "gameplay_overlay",
                "vice_city_skyline",
            ],
            "general": [
                "news_headline_banner",
                "social_feed_reactions",
                "gameplay_cinematic_broll",
                "community_discussion",
                "speculation_graphic",
                "outro_subscribe_card",
            ],
        }
        pool = footage_map.get(topic_type, footage_map["general"])
        return pool[: len(structure)]

    def _compose_narration(
        self,
        title: str,
        hook: str,
        concept: str,
        topic_type: str,
        format_name: str,
    ) -> str:
        clean_title = title.rstrip(". ")

        concept_hint = ""
        if "highlight" in concept.lower():
            concept_hint = concept.lower().split("highlight")[-1].strip(" .")

        if format_name == "discovery":
            if topic_type == "milestone":
                final_line = (
                    f"Make sure to check {concept_hint} so you are ready when servers unlock."
                    if concept_hint
                    else "Make sure your storage is prepped so you're ready when servers go live."
                )
                lines = [
                    f"{hook}",
                    f"Reports and screenshots are confirming that {clean_title}.",
                    "Preload packages appearing on backend stores is widely considered one of the final milestones before launch.",
                    final_line,
                ]
            elif topic_type == "website":
                lines = [
                    f"{hook}",
                    f"Rockstar quietly pushed an update, and players discovered {clean_title}.",
                    "Tracking subtle web updates is usually how preliminary marketing and new assets slip out early.",
                    "Keep your eyes peeled as Rockstar adjusts their launch platforms.",
                ]
            else:
                lines = [
                    f"{hook}",
                    f"Take a closer look at {clean_title}.",
                    "Details like this demonstrate the level of density and attention being poured into Vice City.",
                    "It shows Rockstar's commitment to pushing next-gen immersion further.",
                ]
        else:
            lines = [
                f"{hook}",
                f"The community is actively discussing {clean_title}.",
                "This shifts how fans are viewing the current timeline.",
                "Drop your thoughts below and stay tuned as more develops.",
            ]

        return " ".join(lines)

    def write(self, idea=None) -> ContentBrief:
        # If no idea is explicitly passed, load top candidate from latest_ideas.json
        if idea is None:
            if not self.ideas_path.exists():
                raise FileNotFoundError(f"Ideas file not found at {self.ideas_path}")
            with open(self.ideas_path, "r", encoding="utf-8") as f:
                ideas_data = json.load(f)
            if not ideas_data:
                raise ValueError("No ideas found in latest_ideas.json")
            idea_dict = ideas_data[0]
            format_name = idea_dict.get("format_name", idea_dict.get("format", "discovery"))
            trend_title = idea_dict.get("trend_title", idea_dict.get("title", ""))
            hook = idea_dict.get("hook", "")
            concept = idea_dict.get("concept", "")
        elif isinstance(idea, dict):
            format_name = idea.get("format_name", idea.get("format", "discovery"))
            trend_title = idea.get("trend_title", idea.get("title", ""))
            hook = idea.get("hook", "")
            concept = idea.get("concept", "")
        else:
            format_name = getattr(idea, "format_name", getattr(idea, "format", "discovery"))
            trend_title = getattr(idea, "trend_title", getattr(idea, "title", ""))
            hook = getattr(idea, "hook", "")
            concept = getattr(idea, "concept", "")

        format_file = self.formats_dir / f"{format_name}.json"
        with open(format_file, "r", encoding="utf-8") as f:
            fmt_data = json.load(f)

        structure = fmt_data.get("structure", ["hook", "show_discovery", "explain", "impact"])
        topic_type = self._determine_topic_type(trend_title, concept)

        footage = self._get_contextual_footage(topic_type, structure)
        script = self._compose_narration(
            title=trend_title,
            hook=hook,
            concept=concept,
            topic_type=topic_type,
            format_name=format_name,
        )

        return ContentBrief.create(
            title=trend_title,
            format=format_name,
            hook=hook,
            script=script,
            length=30,
            footage=footage,
            voice="energetic",
        )

    # Alias to maintain backwards compatibility with earlier test scripts
    write_brief = write