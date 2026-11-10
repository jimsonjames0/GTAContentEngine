from dataclasses import dataclass, field
from typing import List


@dataclass
class ContentBrief:
    title: str
    format: str
    hook: str
    script: str
    length: int
    footage: List[str]
    voice: str = "energetic"

    VALID_FORMATS = {"breakdown", "theory", "discovery", "meme", "reaction"}

    @classmethod
    def create(
        cls,
        title: str,
        format: str,
        hook: str,
        script: str,
        length: int,
        footage: List[str],
        voice: str = "energetic",
    ):
        fmt = format.lower().strip()
        if fmt not in cls.VALID_FORMATS:
            raise ValueError(
                f"Invalid format '{format}'. Must be one of: {cls.VALID_FORMATS}"
            )

        if not title or not title.strip():
            raise ValueError("Title cannot be empty.")

        if not hook or not hook.strip():
            raise ValueError("Hook cannot be empty.")

        if not script or not script.strip():
            raise ValueError("Script cannot be empty.")

        if not isinstance(footage, list) or len(footage) == 0:
            raise ValueError("Footage must contain at least 1 valid string tag.")

        for tag in footage:
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError("All footage tags must be non-empty strings.")

        if not isinstance(length, int) or not (10 <= length <= 60):
            raise ValueError(f"Length must be an integer between 10 and 60 seconds inclusive, got {length}.")

        if not voice or not voice.strip():
            raise ValueError("Voice cannot be empty.")

        return cls(
            title=title.strip(),
            format=fmt,
            hook=hook.strip(),
            script=script.strip(),
            length=length,
            footage=[tag.strip() for tag in footage],
            voice=voice.strip(),
        )
