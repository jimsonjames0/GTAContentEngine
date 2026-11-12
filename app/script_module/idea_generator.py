from format_selector import FormatSelector
from idea import Idea
import random


class IdeaGenerator:

    def __init__(self):
        self.selector = FormatSelector()

    def _generate_hook(self, trend_title: str, format_data: dict) -> str:
        hook_templates = format_data.get("hook_styles", [])
        if hook_templates:
            return random.choice(hook_templates)
        return "This GTA VI detail deserves closer attention."

    def _generate_concept(self, trend_title: str, format_data: dict) -> str:
        fmt_name = format_data.get("name", "discovery")
        structure = format_data.get("structure", [])
        structure_str = " -> ".join(structure)

        if fmt_name == "discovery":
            return (
                f"Break down the new discovery around '{trend_title}'. "
                f"Flow: {structure_str}. Highlight key visual evidence and what this means for players."
            )
        elif fmt_name == "reaction":
            return (
                f"React to the community moment '{trend_title}'. "
                f"Flow: {structure_str}. Showcase the funny/insane clip and give direct commentary."
            )
        elif fmt_name == "theory":
            return (
                f"Explore the community theory '{trend_title}'. "
                f"Flow: {structure_str}. Present the clues and ask viewers for their take."
            )
        elif fmt_name == "breakdown":
            return (
                f"Analyze the technical/gameplay details in '{trend_title}'. "
                f"Flow: {structure_str}. Deliver high-density frame analysis."
            )
        elif fmt_name == "meme":
            return (
                f"Fast-paced meme edit based on '{trend_title}'. "
                f"Flow: {structure_str}. Quick setup leading into punchline timing."
            )
        else:
            return f"Cover '{trend_title}' following format structure: {structure_str}."

    def generate_from_trend(self, trend) -> Idea:
        title = trend.title if hasattr(trend, "title") else trend.get("title", "")
        url = trend.url if hasattr(trend, "url") else trend.get("url", "")
        source = trend.source if hasattr(trend, "source") else trend.get("source", "reddit")
        score = trend.score if hasattr(trend, "score") else trend.get("score", 0)

        format_data = self.selector.select(title)

        hook = self._generate_hook(title, format_data)
        concept = self._generate_concept(title, format_data)

        return Idea.create(
            trend_title=title,
            trend_url=url,
            source=source,
            trend_score=score,
            format_name=format_data["name"],
            hook=hook,
            concept=concept,
            recommended_length=format_data.get("length", "20-40"),
        )

    def generate_batch(self, trends: list) -> list[Idea]:
        return [self.generate_from_trend(t) for t in trends]