from dataclasses import dataclass


@dataclass
class Idea:
    trend_title: str
    trend_url: str
    source: str
    trend_score: int
    format_name: str
    hook: str
    concept: str
    recommended_length: str

    VALID_FORMATS = {"breakdown", "theory", "discovery", "meme", "reaction"}

    @classmethod
    def create(
        cls,
        trend_title: str,
        trend_url: str,
        source: str,
        trend_score: int,
        format_name: str,
        hook: str,
        concept: str,
        recommended_length: str,
    ):
        fmt = format_name.lower().strip()
        if fmt not in cls.VALID_FORMATS:
            raise ValueError(
                f"Invalid format '{format_name}'. Must be one of: {cls.VALID_FORMATS}"
            )

        if not source.strip():
            raise ValueError("Source cannot be empty.")

        if not hook.strip() or not concept.strip():
            raise ValueError("Hook and concept cannot be empty.")

        return cls(
            trend_title=trend_title.strip(),
            trend_url=trend_url.strip(),
            source=source.lower().strip(),
            trend_score=trend_score,
            format_name=fmt,
            hook=hook.strip(),
            concept=concept.strip(),
            recommended_length=recommended_length.strip(),
        )